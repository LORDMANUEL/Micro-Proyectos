from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder=os.path.abspath('windows_tester/frontend'))
CORS(app)

# --- AI Endpoint ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

def ask_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return f"Error: No se pudo contactar al servicio de IA. Detalles: {e}"

@app.route('/api/diagnose', methods=['POST'])
def diagnose_issue():
    data = request.get_json()
    problem_description = data.get('problem')

    if not problem_description:
        return jsonify({'error': 'La descripción del problema es requerida'}), 400

    prompt = (f"Actúa como un técnico experto en diagnóstico de sistemas operativos Windows. "
              f"Un usuario reporta el siguiente problema: '{problem_description}'.\n\n"
              f"Genera una guía de diagnóstico paso a paso, clara y ordenada, para que un técnico pueda seguirla. "
              f"La guía debe enfocarse en identificar posibles causas de malware o drivers defectuosos. "
              f"Usa un lenguaje técnico pero fácil de seguir. Estructura la respuesta con encabezados claros para cada sección (ej: '1. Análisis de Malware', '2. Verificación de Drivers').")

    diagnostic_guide = ask_ollama(prompt)
    return jsonify({'diagnostic_guide': diagnostic_guide})

# --- Serve Frontend ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
