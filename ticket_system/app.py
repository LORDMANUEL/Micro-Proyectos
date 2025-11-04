from flask import Flask, request, jsonify, g, send_from_directory
from database import get_db_connection, init_db
import os
import requests
import json
import threading

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "ollama") # Default key, change if needed
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2") # Default model

# The static folder is set to the 'frontend' directory.
app = Flask(__name__, static_folder='frontend')

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

        # Directly parse the JSON response
        response_data = response.json()
        category = response_data.get("response", "Other").strip()

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
            SELECT
                t.id, t.title, t.description, t.status, t.priority, t.category, t.created_at,
                c.username as created_by,
                a.username as assigned_to,
                d.name as department
            FROM tickets t
            JOIN users c ON t.created_by_id = c.id
            LEFT JOIN users a ON t.assigned_to_id = a.id
            JOIN departments d ON t.department_id = d.id
            ORDER BY t.created_at ASC -- FIFO order
            """
        ).fetchall()

        # Convert ticket rows to a list of dictionaries
        ticket_list = [dict(ticket) for ticket in tickets]

        return jsonify(ticket_list), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# API endpoint to close a ticket
@app.route('/api/tickets/<int:ticket_id>/close', methods=['PUT'])
def close_ticket(ticket_id):
    try:
        db = get_db()
        # Also update the updated_at timestamp
        db.execute(
            "UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            ('Closed', ticket_id)
        )
        db.commit()
        return jsonify({'message': f'Ticket {ticket_id} closed successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# API endpoint to assign a ticket to a specific admin
@app.route('/api/tickets/<int:ticket_id>/assign', methods=['PUT'])
def assign_ticket(ticket_id):
    data = request.get_json()
    assignee_id = data.get('assignee_id')

    if not assignee_id:
        return jsonify({'error': 'Assignee ID is required'}), 400

    try:
        db = get_db()
        # First, check if the user is an admin
        user_role = db.execute("SELECT role FROM users WHERE id = ?", (assignee_id,)).fetchone()
        if not user_role or user_role['role'] != 'admin':
            return jsonify({'error': 'Invalid assignee ID or user is not an admin'}), 400

        db.execute(
            "UPDATE tickets SET assigned_to_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (assignee_id, ticket_id)
        )
        db.commit()

        assignee_user = db.execute("SELECT username FROM users WHERE id = ?", (assignee_id,)).fetchone()

        return jsonify({
            'message': f'Ticket {ticket_id} assigned to {assignee_user["username"]}',
            'assigned_to': assignee_user["username"]
        }), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# API endpoint to get all admin users (IT staff)
@app.route('/api/admins', methods=['GET'])
def get_admins():
    try:
        db = get_db()
        admins = db.execute("SELECT id, username FROM users WHERE role = 'admin'").fetchall()
        admin_list = [dict(s) for s in admins]
        return jsonify(admin_list), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Route to serve the client-facing HTML page
@app.route('/')
def serve_client_page():
    return send_from_directory(app.static_folder, 'client.html')

# API endpoint to get all client users
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        db = get_db()
        users = db.execute("SELECT id, username FROM users WHERE role = 'client'").fetchall()
        user_list = [dict(user) for user in users]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Route to serve the IT staff-facing HTML page
@app.route('/it')
def serve_it_page():
    return send_from_directory(app.static_folder, 'it.html')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
