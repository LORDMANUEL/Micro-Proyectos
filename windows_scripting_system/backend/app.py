import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder=os.path.abspath('windows_scripting_system/frontend'))
CORS(app)

DATABASE = 'windows_scripting_system/backend/scripts.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Script Endpoints ---
@app.route('/api/scripts', methods=['GET'])
def get_scripts():
    conn = get_db_connection()
    scripts = conn.execute('SELECT * FROM scripts ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in scripts])

@app.route('/api/scripts', methods=['POST'])
def add_script():
    new_script = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scripts (title, description, script_type, content) VALUES (?, ?, ?, ?)',
                 (new_script['title'], new_script['description'], new_script['script_type'], new_script['content']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/scripts/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM scripts WHERE id = ?', (script_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Script deleted successfully'})

# --- AI Endpoints ---
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

@app.route('/api/generate-script', methods=['POST'])
def generate_script():
    data = request.get_json()
    user_prompt = data.get('prompt')
    script_type = data.get('script_type', 'powershell') # Default to powershell

    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    # RAG: Find relevant scripts in our DB
    conn = get_db_connection()
    search_terms = user_prompt.split()
    query = "SELECT * FROM scripts WHERE (" + " OR ".join(["description LIKE ?"] * len(search_terms)) + ") AND script_type = ? LIMIT 3"
    params = [f"%{term}%" for term in search_terms] + [script_type]

    relevant_scripts = conn.execute(query, params).fetchall()
    conn.close()

    context = "Aquí hay algunos scripts de ejemplo:\n"
    for script in relevant_scripts:
        context += f"--- Ejemplo de script '{script['title']}' ---\n{script['content']}\n"

    final_prompt = (f"Actúa como un experto en scripting de Windows. "
                    f"Basado en los siguientes ejemplos:\n{context}\n\n"
                    f"Genera un script de tipo '{script_type}' para la siguiente tarea: '{user_prompt}'. "
                    f"El script debe ser completo, funcional y seguro. No incluyas explicaciones, solo el código.")

    generated_script = ask_ollama(final_prompt)
    return jsonify({'generated_script': generated_script})

# --- Serve Frontend ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
