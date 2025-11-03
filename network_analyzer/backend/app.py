from flask import Flask, request, jsonify, send_from_directory
import requests
import whois
import os
import json

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

# --- Flask App Configuration ---
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))

def get_ai_summary(ip_info):
    """
    Analyzes the collected IP data with Ollama to generate a human-readable summary.
    """
    prompt = f"""
    Based on the following technical data for the IP address {ip_info['ip_address']},
    provide a brief, easy-to-understand summary.
    Infer the likely type of device or usage (e.g., 'corporate server', 'mobile device', 'home internet connection').
    Keep the summary to 2-3 sentences.

    Technical Data:
    - Country: {ip_info['geolocation']['country']}
    - City: {ip_info['geolocation']['city']}
    - ISP: {ip_info['isp']['name']}
    - WHOIS Organization: {ip_info['whois'].get('organization', 'N/A')}

    Summary:
    """

    headers = {"Content-Type": "application/json"}
    data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=20)
        response.raise_for_status()

        full_response = response.json()
        summary = full_response.get("response", "AI analysis could not be completed.").strip()
        return summary
    except requests.exceptions.RequestException as e:
        return f"Could not connect to the AI service: {e}"
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error parsing AI response: {e}"

@app.route('/api/analyze', methods=['POST'])
def analyze_ip():
    data = request.get_json()
    ip_address = data.get('ip_address')

    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    # Geolocalization
    geo_data = {}
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
        response.raise_for_status()
        geo_data = response.json()
        if geo_data.get('status') == 'fail':
            return jsonify({'error': f"Failed to analyze IP: {geo_data.get('message')}"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to retrieve geolocation data: {e}'}), 500

    # WHOIS
    whois_data = {}
    try:
        w = whois.whois(ip_address)
        whois_data = {
            'registrar': w.registrar,
            'organization': w.org,
            'creation_date': w.creation_date,
            'emails': w.emails,
        }
    except Exception:
        whois_data = {'error': 'Could not retrieve WHOIS data.'}

    # Prepare response
    analysis_result = {
        'ip_address': ip_address,
        'geolocation': {
            'country': geo_data.get('country'),
            'city': geo_data.get('city'),
        },
        'isp': {
            'name': geo_data.get('isp'),
        },
        'whois': whois_data
    }

    # AI Summary
    analysis_result['ai_summary'] = get_ai_summary(analysis_result)

    return jsonify(analysis_result), 200

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with the ticket system (port 5000)
    app.run(debug=True, port=5001)
