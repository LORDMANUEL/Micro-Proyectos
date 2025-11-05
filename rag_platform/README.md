# Local RAG Platform

This project is a self-contained Retrieval-Augmented Generation (RAG) platform. You can upload your own documents (PDFs and TXT files) and then ask questions about them using a local AI model (Ollama).

## Current Implementation (ChromaDB)

This version runs without Docker, making it easy to set up. It uses ChromaDB, a local, file-based vector database.

### How to Run:
1.  **Ensure Ollama is running:** This platform requires a running instance of Ollama to generate embeddings and provide chat responses. Make sure you have the `mxbai-embed-large` model for embeddings and `llama3` for chat.
2.  **Install Python Dependencies:** Make sure all dependencies from the root `requirements.txt` are installed in your virtual environment. The key dependencies for this project are `flask`, `chromadb`, and `pypdf2`.
3.  **Start the Application:** Run the Flask server:
    ```bash
    python rag_platform/app.py
    ```
4.  **Access the UI:** Open your browser and navigate to `http://127.0.0.1:5012`.
5.  **Upload Documents:** Use the web interface to upload your files. They will be processed, converted to embeddings, and stored locally in the `rag_platform/chroma_db` directory.
6.  **Chat:** Use the chat interface to ask questions. The system will retrieve relevant information from your documents to generate an answer.

---

## Alternative Implementation (Docker + Qdrant)

This version was originally designed to use Qdrant, a powerful vector database that runs in a Docker container. This is a more robust solution for larger-scale applications.

### Requirements:
*   Docker installed and running.

### How to Run:
1.  **Start Qdrant:** Navigate to the `rag_platform` directory and run Docker Compose:
    ```bash
    cd rag_platform
    docker-compose up -d
    ```
    This will start the Qdrant database and expose its UI on port `6334`.
2.  **Adapt `app.py`:** You would need to modify the `app.py` file to use the `qdrant-client` instead of `chromadb`. This would involve:
    *   Installing the client: `pip install qdrant-client`
    *   Changing the client initialization to connect to Qdrant (`QdrantClient(host="localhost", port=6333)`).
    *   Updating the `process_and_store` function to use `qdrant_client.upsert(...)`.
    *   Updating the `chat` function to use `qdrant_client.search(...)`.
    *(The original, pre-ChromaDB version of `app.py` in the agent's memory contains the precise code for these changes.)*
3.  **Run the App:** Start the Flask server as usual. The application will then connect to the Qdrant container for all vector database operations.
