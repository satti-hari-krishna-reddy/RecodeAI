import os
import logging
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def invoke_ai(prompt):
    api_key = os.getenv("API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    # Request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        response_data = response.json()

        if (
            "candidates" in response_data and
            len(response_data["candidates"]) > 0 and
            "content" in response_data["candidates"][0] and
            "parts" in response_data["candidates"][0]["content"] and
            len(response_data["candidates"][0]["content"]["parts"]) > 0
        ):
            return response_data["candidates"][0]["content"]["parts"][0]["text"]

        return ""

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

@app.route("/api/translate", methods=["POST"])
def translation_handler():
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405

    try:
        # Parse JSON body
        request_body = request.get_json()
        pseudo_code = request_body.get("pseudo_code", "")
        method = request_body.get("method", "")
        lang = request_body.get("lang", "")

        if not pseudo_code or not method:
            return jsonify({"error": "Missing required fields: pseudo_code or method"}), 400

        prompt = ""
        if method == "recode":
            prompt = (
                "Reconstruct the following code while maintaining its original logic. "
                "The goal is to improve its readability, structure, and clarity, as though it were written from scratch in a cleaner and more modern style. "
                "Do not alter the core logic of the code, only refactor the way it is written without commentary."
            )
        elif method == "translate":
            if not lang:
                return jsonify({"error": "Missing required field: lang for translation method"}), 400
            prompt = (
                f"Translate the following code into {lang}. "
                "Ensure that the logic remains exactly the same and that the translated code adheres to the syntax and conventions of the target language."
            )
        else:
            return jsonify({"error": "Invalid method"}), 400

        ai_input = f"{prompt}\n{pseudo_code}"
        ai_response = invoke_ai(ai_input)

        if not ai_response:
            return jsonify({
                "success": False,
                "message": "AI invocation failed",
                "decompiled_code": f"// AI invocation failed\n{pseudo_code}"
            }), 200

        return jsonify({
            "success": True,
            "message": "Decompilation successful",
            "decompiled_code": ai_response
        }), 200

    except Exception as e:
        logging.error(f"Error handling request: {e}")
        return jsonify({"error": "Invalid JSON body"}), 400

if __name__ == "__main__":
    port = os.getenv("FUNCTIONS_CUSTOMHANDLER_PORT", "8080")
    app.run(host="0.0.0.0", port=int(port))
