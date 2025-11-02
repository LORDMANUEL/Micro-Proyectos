from flask import Flask, request, jsonify, g, send_from_directory
from .database import get_db_connection
import os
import requests
import json
import threading

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "ollama") # Default key, change if needed
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2") # Default model

# The static folder is set to the 'frontend' directory.
# The relative path is calculated from the location of this script (backend).
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Function to get the database connection and store it in the application context
def get_db():
    if 'db' not in g:
        g.db = get_db_connection()
    return g.db

# --- AI Integration ---
def categorize_ticket_with_ai(ticket_id, title, description):
    """
    Uses Ollama to categorize a ticket and updates the database.
    This runs after the ticket is created, so it doesn't slow down the user's request.
    """
    prompt = f"""
    Based on the following IT ticket, classify it into one of these categories:
    "Hardware", "Software", "Network", or "Other".
    Return only the category name as a single word.

    Title: {title}
    Description: {description}
    Category:
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()

        # The response from Ollama is a stream of JSON objects, we need to parse the final one
        full_response_text = response.text
        # Split by newline and filter out empty lines
        json_objects = [line for line in full_response_text.strip().split('\n') if line]
        # Parse the last JSON object
        final_json_object = json.loads(json_objects[-1])

        category = final_json_object.get("response", "Other").strip()

        # A simple validation to ensure the category is one of the expected ones
        valid_categories = ["Hardware", "Software", "Network", "Other"]
        if category not in valid_categories:
            category = "Other"

        # Update the ticket in the database with a direct connection
        conn = None
        try:
            conn = get_db_connection()
            conn.execute("UPDATE tickets SET category = ? WHERE id = ?", (category, ticket_id))
            conn.commit()
            print(f"Successfully categorized ticket {ticket_id} as '{category}'")
        finally:
            if conn:
                conn.close()

    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing Ollama response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during categorization: {e}")


# Teardown function to close the database connection after each request
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# API endpoint to create a new ticket
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'description', 'created_by_id', 'department_id')):
        return jsonify({'error': 'Missing data. Required fields: title, description, created_by_id, department_id'}), 400

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO tickets (title, description, created_by_id, department_id)
            VALUES (?, ?, ?, ?)
            """,
            (data['title'], data['description'], data['created_by_id'], data['department_id'])
        )
        db.commit()
        ticket_id = cursor.lastrowid

        # Start AI categorization in a background thread
        ai_thread = threading.Thread(
            target=categorize_ticket_with_ai,
            args=(ticket_id, data['title'], data['description'])
        )
        ai_thread.start()

        return jsonify({'message': 'Ticket created successfully', 'ticket_id': ticket_id}), 201
    except Exception as e:
        # In a real app, log the error
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# API endpoint to get all tickets (for the IT view)
@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    try:
        db = get_db()
        tickets = db.execute(
            """
            SELECT t.id, t.title, t.status, t.priority, t.category, t.created_at, u.username as created_by, d.name as department
            FROM tickets t
            JOIN users u ON t.created_by_id = u.id
            JOIN departments d ON t.department_id = d.id
            ORDER BY t.created_at ASC -- FIFO order
            """
        ).fetchall()

        # Convert ticket rows to a list of dictionaries
        ticket_list = [dict(ticket) for ticket in tickets]

        return jsonify(ticket_list), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Route to serve the client-facing HTML page
@app.route('/')
def serve_client_page():
    return send_from_directory(app.static_folder, 'client.html')

# Route to serve the IT staff-facing HTML page
@app.route('/it')
def serve_it_page():
    return send_from_directory(app.static_folder, 'it.html')


if __name__ == '__main__':
    # It's recommended to run Flask using a WSGI server like Gunicorn in production,
    # but the dev server is fine for our purposes.
    app.run(debug=True)
