from flask import Blueprint, jsonify, request, Response 
import requests

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/chat")
OLLAMA_URL = "http://localhost:11434/api"

@chat_bp.route("/health", methods=["GET"])
def chat_health():
    try:
        response = requests.get(f"{OLLAMA_URL}/tags", timeout=3)
        if response.status_code == 200:
            return jsonify({"available": True})
        return jsonify({"available": False})
    except Exception:
        return jsonify({"available": False})


@chat_bp.route("/message", methods=["POST"])
def chat_message():
    try:
        data  = request.json
        user_message = data.get("message", "")

        ollama_payload = {
            "model":  "phi3:latest",
            "stream": True,
            "messages": [
                {
                    "role":    "system",
                    "content": (
                        "You are a helpful environmental AI assistant embedded in a "
                        "satellite land-use analysis tool. You help users understand "
                        "land cover types (agricultural, desert, forest/tree, urban, "
                        "water), deforestation, urbanization trends, satellite imagery "
                        "analysis, and environmental monitoring. Keep answers concise "
                        "and relevant."
                    )
                },
                {
                    "role":    "user",
                    "content": user_message
                }
            ]
        }
        def generate():
            with requests.post(
                f"{OLLAMA_URL}/chat",
                json=ollama_payload,
                stream=True,
                timeout=60
            ) as ollama_response:
                for chunk in ollama_response.iter_lines():
                    if chunk:
                        yield chunk.decode("utf-8") + "\n"

        return Response(generate(), mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500