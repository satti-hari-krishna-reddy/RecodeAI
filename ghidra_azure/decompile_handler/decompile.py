import os
import uuid
import json
import logging
import requests
import time
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.storage.blob import BlobServiceClient

logging.basicConfig(level=logging.INFO)

def handle_error(e):
    logging.error(e)
    raise e

def upload_to_blob_storage(blob_name, file_bytes):
    try:
        connection_string = os.getenv("CONNECTION_STRING")
        container_name = os.getenv("AZURE_CONTAINER_NAME")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        if not container_client.exists():
            container_client.create_container()

        logging.info(f"Uploading blob: {blob_name}")
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file_bytes, overwrite=True)
    except Exception as e:
        handle_error(e)

def delete_blob(container_name, blob_name):
    try:
        connection_string = os.getenv("CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        logging.info(f"Blob {blob_name} deleted successfully.")
    except Exception as e:
        handle_error(e)

def download_blob(container_name, blob_name):
    try:
        connection_string = os.getenv("CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        blob_client = container_client.get_blob_client(blob_name)
        download_stream = blob_client.download_blob()
        logging.info(f"Blob {blob_name} downloaded successfully.")
        return download_stream.readall()
    except Exception as e:
        handle_error(e)

def trigger_azure_container(blob_name):
    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        image_name = os.getenv("AZURE_IMAGE_NAME")
        container_group_name = f"container-{uuid.uuid4()}"

        credential = DefaultAzureCredential()
        client = ContainerInstanceManagementClient(credential, subscription_id)

        container_resource_requests = {
            "cpu": 1.0,
            "memory_in_gb": 1.0
        }
        container_environment_variables = [
            {"name": "AZURE_CONTAINER_NAME", "value": os.getenv("AZURE_CONTAINER_NAME")},
            {"name": "CONNECTION_STRING", "value": os.getenv("CONNECTION_STRING")},
            {"name": "BLOB_NAME", "value": blob_name},
        ]
        container = {
            "name": container_group_name,
            "properties": {
                "image": image_name,
                "resources": {"requests": container_resource_requests},
                "environment_variables": container_environment_variables
            }
        }
        container_group = {
            "location": "eastus",
            "properties": {
                "containers": [container],
                "os_type": "Linux",
                "restart_policy": "Never",
                "image_registry_credentials": [{
                    "server": os.getenv("ACR_SERVER"),
                    "username": os.getenv("ACR_USERNAME"),
                    "password": os.getenv("ACR_PASSWORD"),
                }]
            }
        }

        logging.info("Creating container group...")
        poller = client.container_groups.begin_create_or_update(
            resource_group, container_group_name, container_group
        )
        result = poller.result()

        logging.info("Polling container status...")
        for _ in range(5):
            state = client.container_groups.get(resource_group, container_group_name).instance_view.state
            if state == "Succeeded":
                logging.info("Container execution completed successfully.")
                break
            elif state == "Failed":
                logging.error("Container execution failed.")
                break
            time.sleep(25)
        else:
            logging.warning("Container execution did not complete in time.")

        logging.info("Deleting container group...")
        client.container_groups.begin_delete(resource_group, container_group_name)
    except Exception as e:
        handle_error(e)

def invoke_ai(api_key, prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return "No content found in the response."
    except Exception as e:
        handle_error(e)

def decompile_handler(file, filename):
    try:
        # Limit file size to 5MB
        if len(file) > 5 * 1024 * 1024:
            raise ValueError("File size exceeds 5MB")

        unique_id = str(uuid.uuid4())
        unique_filename = f"{unique_id}_{filename}"
        upload_to_blob_storage(unique_filename, file)

        trigger_azure_container(unique_filename)

        delete_blob(os.getenv("AZURE_CONTAINER_NAME"), unique_filename)

        # Download the blob with the same name but with `.c` extension
        downloaded_data = download_blob(
            os.getenv("AZURE_CONTAINER_NAME"),
            unique_filename.replace(".exe", ".c")
        )

        # AI Prompt
        prompt = (
            "Generate a **function relationship map** for the given code with:\n"
            "1. Function Name\n"
            "2. Variables: List with brief roles.\n"
            "3. Return Value: What it returns and why.\n"
            "4. Relationships: Variable/function interactions (e.g., calls, return usage).\n"
            "**Rules**: No code modifications.\n"
            "Then, add inline comments/documentation for the following code. Comments should describe the purpose "
            "of each block of code or important lines without altering the original structure or indentation."
        )
        ai_input = f"{prompt}\n{downloaded_data.decode('utf-8')}"
        api_key = os.getenv("API_KEY")
        ai_response = invoke_ai(api_key, ai_input)

        return {"success": True, "message": "Decompilation successful", "decompiled_code": ai_response}
    except Exception as e:
        return {"success": False, "message": str(e)}

# Flask API Server
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/decompile", methods=["POST"])
def api_decompile():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "message": "No file part"}), 400
        file = request.files["file"]
        if not file.filename:
            return jsonify({"success": False, "message": "No selected file"}), 400

        file_content = file.read()
        response = decompile_handler(file_content, file.filename)
        return jsonify(response)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
    app.run(host="0.0.0.0", port=port)
