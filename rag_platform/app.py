import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import chromadb
from PyPDF2 import PdfReader
import uuid

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
OLLAMA_API_URL = "http://host.docker.internal:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://host.docker.internal:11434/api/generate"
CHROMA_PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "local_rag_collection_chroma"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), UPLOAD_FOLDER)

# --- ChromaDB Client ---
# This will create the directory if it doesn't exist and persist the data there.
chroma_client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(os.path.abspath(__file__)), CHROMA_PERSIST_DIR))

# Get or create the collection
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_embedding(text):
    """Get embedding for a text chunk from Ollama."""
    try:
        response = requests.post(OLLAMA_API_URL, json={"model": "mxbai-embed-large", "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting embedding from Ollama: {e}")
        return None

def process_and_store(filepath):
    """Process a file, create embeddings, and store them in ChromaDB."""
    filename = os.path.basename(filepath)
    text = ""
    if filepath.lower().endswith('.pdf'):
        with open(filepath, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    else: # txt
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

    # Simple chunking
    chunks = [text[i:i + 500] for i in range(0, len(text), 400)]

    embeddings = []
    documents = []
    metadatas = []
    ids = []

    for chunk in chunks:
        embedding = get_embedding(chunk)
        if embedding:
            embeddings.append(embedding)
            documents.append(chunk)
            metadatas.append({"source": filename})
            ids.append(str(uuid.uuid4()))

    if embeddings:
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(embeddings)} chunks to ChromaDB.")

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            process_and_store(filepath)

            return render_template('rag_index.html', message=f"File '{filename}' processed and indexed.")

    return render_template('rag_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided."}), 400

    # 1. Get embedding for the user's question
    question_embedding = get_embedding(user_question)
    if not question_embedding:
        return jsonify({"error": "Could not get embedding for the question."}), 500

    # 2. Search ChromaDB for relevant context
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    context = "\n".join(results['documents'][0])

    # 3. Generate a response with Ollama using the context
    prompt = f"Using the following context, answer the question.\n\nContext:\n{context}\n\nQuestion: {user_question}"

    try:
        response = requests.post(OLLAMA_CHAT_URL, json={"model": "llama3", "prompt": prompt, "stream": False})
        response.raise_for_status()

        return jsonify({"answer": response.json()['response']})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to get response from Ollama: {e}"}), 500

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(host='0.0.0.0', port=5012, debug=True)
