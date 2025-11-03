from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import json

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

# --- Flask App Configuration ---
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# --- API Endpoint ---
@app.route('/api/generate_email', methods=['POST'])
def generate_email_handler():
    data = request.get_json()
    if not data or not all(k in data for k in ['recipient', 'objective', 'tone', 'key_points']):
        return jsonify({'error': 'Missing required fields'}), 400

    # --- Prompt Engineering ---
    # Create a detailed prompt for the AI
    key_points_formatted = "- " + data['key_points'].replace('\n', '\n- ')

    prompt = f"""
    Please write a professional email with the following characteristics:

    - To: {data['recipient']}
    - Objective: {data['objective']}
    - Tone: {data['tone']}
    - Key Points to include:
    {key_points_formatted}

    Generate only the body of the email.
    """

    # --- Call Ollama AI ---
    try:
        headers = {"Content-Type": "application/json"}
        data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        response_data = response.json()
        generated_email = response_data.get("response", "Sorry, I couldn't generate an email.").strip()

    except requests.exceptions.RequestException:
        # If Ollama isn't running, return a sample email for frontend verification.
        generated_email = f"""
Subject: {data['objective']}

Dear {data['recipient']},

This is a sample email generated because the AI service could not be reached.

Here are the key points you wanted to include:
{key_points_formatted}

Best regards,
AI Assistant
"""
    except (json.JSONDecodeError, KeyError):
        generated_email = "There was an issue processing the AI's response. Please try again."

    return jsonify({'email': generated_email.strip()})

# --- Frontend Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Running on port 5002 to avoid conflicts
    app.run(debug=True, port=5002)
