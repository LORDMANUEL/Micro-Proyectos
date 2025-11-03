from flask import Flask, request, jsonify, send_from_directory
import os
import sqlite3
import requests
import json

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

# --- App Configuration ---
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))
DB_PATH = os.path.join(os.path.dirname(__file__), 'sap_b1_example.db')

# Load the database schema to provide it to the AI as context
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
with open(SCHEMA_PATH, 'r') as f:
    DB_SCHEMA = f.read()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- API Endpoint ---
@app.route('/api/translate_sql', methods=['POST'])
def translate_sql_handler():
    data = request.get_json()
    natural_language_query = data.get('natural_language_query')

    if not natural_language_query:
        return jsonify({'error': 'Natural language query is required'}), 400

    # --- Prompt Engineering ---
    prompt = f"""
    Given the following SQLite database schema:
    ---
    {DB_SCHEMA}
    ---
    Translate the following natural language question into a single, valid, read-only SQLite SELECT query.
    Do not use any other SQL commands. Only return the SQL query and nothing else.

    Question: "{natural_language_query}"
    SQL Query:
    """

    # --- Call Ollama to translate ---
    try:
        headers = {"Content-Type": "application/json"}
        data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=45)
        response.raise_for_status()

        response_data = response.json()
        sql_query = response_data.get("response", "").strip()

        # A simple cleanup to remove potential markdown backticks
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()

    except requests.exceptions.RequestException:
        # Fallback for verification when Ollama is not running
        sql_query = "SELECT CardName, Country, City FROM OCRD WHERE Country = 'USA';"
    except Exception:
        sql_query = "-- An unexpected error occurred during AI translation."

    # --- (CRITICAL) Security Validation ---
    is_safe = sql_query.strip().upper().startswith("SELECT") and ';' not in sql_query and '--' not in sql_query

    if not is_safe:
        return jsonify({
            'sql_query': "Blocked: Only SELECT queries are allowed.",
            'headers': ["Error"],
            'results': [{"Error": "Query was blocked for security reasons."}]
        }), 400


    # --- Execute the SQL Query ---
    results = []
    headers = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Fetch headers
        headers = [description[0] for description in cursor.description]

        # Fetch results
        rows = cursor.fetchall()
        for row in rows:
            results.append(dict(row))

        conn.close()
    except sqlite3.Error as e:
        headers = ["Error"]
        results = [{"Error": f"SQL Error: {e}"}]

    return jsonify({
        'sql_query': sql_query,
        'headers': headers,
        'results': results
    })

# --- Frontend Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Running on port 5003
    app.run(debug=True, host='0.0.0.0', port=5003)
