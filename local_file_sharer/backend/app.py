import os
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename

# --- App Configuration ---
# Calculate paths relative to the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'uploads')
# It's good practice to ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, '..', 'frontend'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Optional: Set a limit for the upload size, e.g., 10GB
# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024

# --- API Endpoints ---

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    filename = secure_filename(file.filename)
    # The file is saved to the 'uploads' directory
    destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(destination)
    except Exception as e:
        return jsonify({'error': f'An error occurred while saving the file: {e}'}), 500

    return jsonify({'message': 'File successfully uploaded', 'filename': filename}), 201

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        # We'll also get file sizes for the frontend
        file_details = []
        for f in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f)
            if os.path.isfile(file_path):
                file_details.append({
                    'name': f,
                    'size': os.path.getsize(file_path)
                })
        return jsonify(file_details), 200
    except Exception as e:
        return jsonify({'error': f'Could not list files: {e}'}), 500

# --- File Serving Endpoint ---

@app.route('/files/<path:filename>')
def download_file(filename):
    try:
        # Use send_from_directory for security
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# --- Frontend Serving ---

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    # Running on port 5005
    app.run(debug=True, host='0.0.0.0', port=5005)
