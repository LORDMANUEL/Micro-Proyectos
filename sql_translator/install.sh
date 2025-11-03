#!/bin/bash

# A simple installation script for the SQL Translator on Debian/Ubuntu.

echo "Starting the installation of the SQL Translator..."

# This script is intended to be run from the root of the repository.
VENV_DIR="venv"

# --- 1. Activate Virtual Environment ---
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Main virtual environment not found. Please run the install script for the first project (ticket_system) first from the root directory."
    exit 1
fi

echo "[1/3] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# --- 2. Install Python Dependencies ---
echo "[2/3] Installing Python dependencies for the SQL Translator..."
pip install -r sql_translator/backend/requirements.txt

# --- 3. Database Initialization ---
echo "[3/3] Initializing the SQLite database..."
python3 sql_translator/backend/database.py

# --- 4. Completion ---
echo "Installation complete!"
echo ""
echo "To run the application, follow these steps:"
echo "1. Activate the virtual environment from the root: source venv/bin/activate"
echo "2. Start the Flask server: python3 -m flask --app sql_translator.backend.app run"
echo "3. Open your browser and go to http://127.0.0.1:5003"
echo ""
