import os
import uuid
import json
import logging
import requests
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import ContainerGroup, Container, ResourceRequirements, ResourceRequests, EnvironmentVariable
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
import azure.functions as func

# Configure structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = func.FunctionApp()

REQUIRED_ENV_VARS = [
    "CONNECTION_STRING", "AZURE_CONTAINER_NAME",
    "AZURE_SUBSCRIPTION_ID", "AZURE_RESOURCE_GROUP",
    "AZURE_IMAGE_NAME", "ACR_SERVER", 
    "ACR_USERNAME", "ACR_PASSWORD", "API_KEY"
]

def validate_environment():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

class StorageManager:
    def __init__(self):
        self.connection_string = os.getenv("CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_CONTAINER_NAME")
        self.blob_service = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service.get_container_client(self.container_name)
        
        if not self.container_client.exists():
            self.container_client.create_container()
            logger.info(f"Created storage container: {self.container_name}")

    def upload_blob(self, blob_name: str, data: bytes) -> str:
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Uploaded blob: {blob_name}")
            return blob_name
        except Exception as e:
            logger.error(f"Blob upload failed: {str(e)}")
            raise

    def delete_blob(self, blob_name: str):
        try:
            self.container_client.delete_blob(blob_name)
            logger.info(f"Deleted blob: {blob_name}")
        except ResourceNotFoundError:
            logger.warning(f"Blob not found during deletion: {blob_name}")
        except Exception as e:
            logger.error(f"Blob deletion failed: {str(e)}")
            raise

class ContainerOrchestrator:
    def __init__(self):
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.image_name = os.getenv("AZURE_IMAGE_NAME")
        self.credential = DefaultAzureCredential()
        self.client = ContainerInstanceManagementClient(self.credential, self.subscription_id)
        
    def create_container_group(self, blob_name: str) -> ContainerGroup:
        container_group_name = f"ghidra-{uuid.uuid4()}"
        logger.info(f"Creating container group: {container_group_name}")

        environment_vars = [
            EnvironmentVariable(name="AZURE_CONTAINER_NAME", value=os.getenv("AZURE_CONTAINER_NAME")),
            EnvironmentVariable(name="CONNECTION_STRING", value=os.getenv("CONNECTION_STRING")),
            EnvironmentVariable(name="BLOB_NAME", value=blob_name)
        ]

        container = Container(
            name=container_group_name,
            image=self.image_name,
            resources=ResourceRequirements(
                requests=ResourceRequests(
                    cpu=1.0,
                    memory_in_gb=2.0
                )
            ),
            environment_variables=environment_vars
        )

        container_group = ContainerGroup(
            location="eastus",
            containers=[container],
            os_type="Linux",
            restart_policy="Never",
            image_registry_credentials=[{
                "server": os.getenv("ACR_SERVER"),
                "username": os.getenv("ACR_USERNAME"),
                "password": os.getenv("ACR_PASSWORD")
            }]
        )

        try:
            poller = self.client.container_groups.begin_create_or_update(
                self.resource_group,
                container_group_name,
                container_group
            )
            return poller.result()
        except Exception as e:
            logger.error(f"Container creation failed: {str(e)}")
            raise

    def monitor_container(self, container_group_name: str) -> str:
        for attempt in range(1, 21):
            try:
                cg = self.client.container_groups.get(self.resource_group, container_group_name)
                state = cg.instance_view.state if cg.instance_view else "Unknown"
                logger.info(f"Container state [{attempt}/20]: {state}")

                if state == "Succeeded":
                    return "Succeeded"
                if state in ("Failed", "Stopped"):
                    raise RuntimeError(f"Container failed with state: {state}")
                
            except ResourceNotFoundError:
                logger.warning("Container group not found yet")
            
            time.sleep(25)
        
        raise TimeoutError("Container did not complete within 500 seconds")

    def cleanup(self, container_group_name: str):
        try:
            logger.info(f"Deleting container group: {container_group_name}")
            poller = self.client.container_groups.begin_delete(
                self.resource_group,
                container_group_name
            )
            poller.wait()
        except Exception as e:
            logger.error(f"Container cleanup failed: {str(e)}")

class AIService:
    GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY environment variable not set")

    def analyze_code(self, code: str) -> str:
        prompt = f"""Analyze the following decompiled code and provide:
        1. Function relationship map
        2. Control flow analysis
        3. Security observations
        4. Inline documentation
        
        Code:
        {code}"""

        try:
            response = requests.post(
                f"{self.GEMINI_ENDPOINT}?key={self.api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return self._parse_response(result)
        except requests.RequestException as e:
            logger.error(f"AI API request failed: {str(e)}")
            raise

    def _parse_response(self, data: dict) -> str:
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return "Could not parse AI response"

@app.route(route="decompile", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def decompile(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Decompilation request received")
    
    try:
        validate_environment()
        
        file = req.files.get('file')
        if not file or not file.filename:
            return func.HttpResponse(
                json.dumps({"success": False, "message": "No file provided"}),
                status_code=400,
                mimetype="application/json"
            )

        if '.' not in file.filename:
            return func.HttpResponse(
                json.dumps({"success": False, "message": "Invalid file name"}),
                status_code=400,
                mimetype="application/json"
            )

        file_content = file.read()
        if len(file_content) > 5 * 1024 * 1024:
            return func.HttpResponse(
                json.dumps({"success": False, "message": "File size exceeds 5MB"}),
                status_code=400,
                mimetype="application/json"
            )

        unique_id = uuid.uuid4().hex
        original_blob_name = f"{unique_id}_{file.filename}"
        output_blob_name = original_blob_name.rsplit('.', 1)[0] + ".c"

        storage = StorageManager()
        orchestrator = ContainerOrchestrator()
        ai_service = AIService()

        storage.upload_blob(original_blob_name, file_content)
        container_group = orchestrator.create_container_group(original_blob_name)
        final_state = orchestrator.monitor_container(container_group.name)
        
        if final_state != "Succeeded":
            raise RuntimeError(f"Container execution failed with state: {final_state}")

        # Verify output exists
        output_blob_client = storage.blob_service.get_blob_client(
            container=storage.container_name,
            blob=output_blob_name
        )
        
        retries = 0
        while not output_blob_client.exists() and retries < 5:
            logger.info("Waiting for output file...")
            time.sleep(10)
            retries += 1

        if not output_blob_client.exists():
            raise FileNotFoundError(f"Output file {output_blob_name} not found")

        # Process results
        decompiled_code = output_blob_client.download_blob().readall().decode('utf-8')
        analysis = ai_service.analyze_code(decompiled_code)

        # Cleanup
        storage.delete_blob(original_blob_name)
        storage.delete_blob(output_blob_name)
        orchestrator.cleanup(container_group.name)

        return func.HttpResponse(
            body=analysis.encode('utf-8'), 
            status_code=200,               
            headers={
                "Content-Type": "text/plain"
            }
        )

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "message": "Processing failed",
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
    
@app.route(route="translate", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def translate(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Decompilation request received")
    
    if req.method != "POST":
        return func.HttpResponse(
            json.dumps({"success": False, "message": "Method not allowed"}),
            status_code=405,
            mimetype="application/json"
        )
    
    try:
        request_body = req.get_json()
        pseudo_code = request_body.get("pseudo_code", "")
        method = request_body.get("method", "")
        lang = request_body.get("lang", "")

        if not pseudo_code or not method:
            return func.HttpResponse(
                json.dumps({"success": False, "message": "Missing required fields: pseudo_code or method"}),
                status_code=400,
                mimetype="application/json"
            )

        prompt = ""
        if method == "recode":
            prompt = f"""Recode the following code snippet in {lang}:
            {pseudo_code}"""
        elif method == "translate":
            if not lang:
                return func.HttpResponse(
                    json.dumps({"success": False, "message": "Missing required field: lang"}),
                    status_code=400,
                    mimetype="application/json"
                )
            prompt = f"""Translate the following code snippet to {lang}:
            {pseudo_code}"""
        else:
            return func.HttpResponse(
                json.dumps({"success": False, "message": "Invalid method"}),
                status_code=400,
                mimetype="application/json"
            )

        ai_service = AIService()
        ai_response = ai_service.analyze_code(f"{prompt}\n{pseudo_code}")
        
        return func.HttpResponse(
            body=ai_response.encode('utf-8'), 
            status_code=200,               
            headers={"Content-Type": "text/plain"}
        )

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "message": "Processing failed",
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
            