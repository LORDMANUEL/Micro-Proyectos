from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import json
import sqlite3

app = Flask(__name__, static_folder='frontend')

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema = "\n".join([row[0] for row in cursor.fetchall()])
    conn.close()
    return schema

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/translate', methods=['POST'])
def translate_sql():
    data = request.json
    natural_language_query = data.get('query')

    if not natural_language_query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        schema = get_db_schema()
        prompt = f"Translate the following natural language query to SQL, given the database schema:\n\nSchema:\n{schema}\n\nQuery: {natural_language_query}"

        ollama_response = requests.post(OLLAMA_API_URL, json={'model': OLLAMA_MODEL, 'prompt': prompt})
        ollama_data = ollama_response.json()
        sql_query = ollama_data.get('response')

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()

        return jsonify({
            'sql_query': sql_query,
            'results': results,
            'columns': column_names
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
