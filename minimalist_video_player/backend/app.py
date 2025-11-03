import os
import sqlite3
import json
import requests
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

# --- Ollama AI Configuration ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

# --- App Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'player.db')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'html'}

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, '..', 'frontend'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database Connection ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Add to database
        file_type = filename.rsplit('.', 1)[1].lower()
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO media_files (filename, file_type) VALUES (?, ?)", (filename, file_type))
            conn.commit()
        except sqlite3.IntegrityError:
            # File already exists in DB
            pass
        conn.close()

        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/files', methods=['GET'])
def get_files():
    conn = get_db_connection()
    files = conn.execute("SELECT * FROM media_files").fetchall()
    conn.close()
    return jsonify([dict(row) for row in files])

@app.route('/api/playlists', methods=['GET'])
def get_playlists():
    conn = get_db_connection()
    playlists = conn.execute("SELECT * FROM playlists").fetchall()
    conn.close()
    return jsonify([dict(row) for row in playlists])

@app.route('/api/playlists', methods=['POST'])
def create_playlist():
    data = request.get_json()
    name = data.get('name')
    items = json.dumps(data.get('items', [])) # Store items as a JSON string

    if not name:
        return jsonify({'error': 'Playlist name is required'}), 400

    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO playlists (name, items) VALUES (?, ?)", (name, items))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Playlist name already exists'}), 409
    finally:
        conn.close()

    return jsonify({'message': 'Playlist created successfully'}), 201

@app.route('/api/generate_html', methods=['POST'])
def generate_html():
    data = request.get_json()
    prompt_text = data.get('prompt')
    filename = data.get('filename')

    if not prompt_text or not filename:
        return jsonify({'error': 'Prompt and filename are required'}), 400

    if not filename.lower().endswith('.html'):
        filename += '.html'

    secure_name = secure_filename(filename)

    # --- Prompt Engineering ---
    prompt = f"""
    Create a single, self-contained HTML file based on the following description.
    The HTML should be simple, with inline CSS for styling. Do not include any external files.
    The content should fill the entire page.

    Description: "{prompt_text}"
    HTML:
    """

    # --- Call Ollama to generate HTML ---
    try:
        headers = {"Content-Type": "application/json"}
        ollama_data = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

        response = requests.post(OLLAMA_API_URL, headers=headers, json=ollama_data, timeout=45)
        response.raise_for_status()

        response_data = response.json()
        html_content = response_data.get("response", "").strip()

        # Cleanup potential markdown
        if html_content.startswith("```html"):
            html_content = html_content[7:]
        if html_content.endswith("```"):
            html_content = html_content[:-3]

        # --- Save the file and update DB ---
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        with open(file_path, 'w') as f:
            f.write(html_content)

        conn = get_db_connection()
        conn.execute("INSERT INTO media_files (filename, file_type) VALUES (?, ?)", (secure_name, 'html'))
        conn.commit()
        conn.close()

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Failed to connect to Ollama: {e}"}), 500
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500

    return jsonify({'message': 'HTML generated successfully', 'filename': secure_name}), 201

# --- Player View ---
@app.route('/view/<int:playlist_id>')
def view_playlist(playlist_id):
    conn = get_db_connection()
    playlist = conn.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,)).fetchone()

    if not playlist:
        return "Playlist not found", 404

    item_ids = json.loads(playlist['items'])
    if not item_ids:
        return "Playlist is empty", 404

    placeholders = ','.join('?' for _ in item_ids)

    query = f"SELECT * FROM media_files WHERE id IN ({placeholders})"
    media_items_unordered = conn.execute(query, item_ids).fetchall()

    media_items_dict = {item['id']: dict(item) for item in media_items_unordered}
    media_items = [media_items_dict[item_id] for item_id in item_ids if item_id in media_items_dict]

    conn.close()

    return render_template("player.html", playlist=dict(playlist), items=media_items)

# --- Static File Serving for Media ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Frontend Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    # Running on port 5004
    app.run(debug=True, host='0.0.0.0', port=5004)
