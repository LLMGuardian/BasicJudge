import requests
from flask import Flask, jsonify, request

import postprocess
import preprocess

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process_request():
    data = request.get_json()
    if not data or "prompt" not in data or "chat" not in data:
        return (
            jsonify({"error": "Invalid input, 'prompt' and 'chat' are required"}),
            400,
        )

    enriched_prompt = preprocess.add_template(prompt=data["prompt"], chat=data["chat"])
    # TODO: model name not be fixated and must be fetched from the DB
    model_name = "llama3.1"
    outgoing_payload = {"model": model_name, "prompt": enriched_prompt, "stream": False}

    # TODO: Referee URL cannot be fixated and must be fetched from the DB
    url = "http://localhost:11434/api/generate"
    response = requests.post(url=url, json=outgoing_payload)

    if response.status_code != 200:
        return (
            jsonify({"error": "Internal server error. Failed to get response from external service"}),
            response.status_code,
        )

    response_data = response.json()
    if "response" not in response_data:
        return (
            jsonify({"error": "Internal server error. Missing 'response' field in external API response"}),
            500,
        )

    response_text = response_data.get("response", "")
    # TODO: Log other parameters in the response
    try:
        result = postprocess.process_response(result=response_text)
        return jsonify({"status": result}), 200
    except postprocess.NumberNotFoundException:
        # TODO: Send the crude response back to the caller
        return (
            jsonify({"error": "Internal server error. No number in the range [0, 100] found in response"}),
            500,
        )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
