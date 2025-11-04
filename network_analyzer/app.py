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

@app.route('/api/analyze', methods=['POST'])
def analyze_ip():
    data = request.json
    ip_address = data.get('ip')

    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    try:
        # OSINT analysis
        ipinfo_response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        ipinfo_data = ipinfo_response.json()

        # AI summary
        prompt = f"Analyze the following OSINT data for IP address {ip_address} and provide a brief summary of the potential device or user: {json.dumps(ipinfo_data)}"
        ollama_response = requests.post(OLLAMA_API_URL, json={'model': OLLAMA_MODEL, 'prompt': prompt})
        ollama_data = ollama_response.json()

        return jsonify({
            'osint': ipinfo_data,
            'ai_summary': ollama_data.get('response')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
