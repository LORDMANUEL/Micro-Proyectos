from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import json

app = Flask(__name__, static_folder='frontend')

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/generate', methods=['POST'])
def generate_email():
    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        ollama_response = requests.post(OLLAMA_API_URL, json={'model': OLLAMA_MODEL, 'prompt': prompt})
        ollama_data = ollama_response.json()

        return jsonify({'email': ollama_data.get('response')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
