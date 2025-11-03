#!/bin/bash

# A simple installation script for the Network Analyzer on Debian/Ubuntu.

echo "Starting the installation of the Network Analyzer..."

# This script assumes the main venv is in the root of the micro-projects suite.
# It will activate it and install the specific dependencies for this project.

VENV_DIR="../../venv" # Assuming this script is run from its own directory

# --- 1. Activate Virtual Environment ---
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Main virtual environment not found. Please run the install script for the first project (ticket_system) first."
    exit 1
fi

echo "[1/3] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# --- 2. Install Python Dependencies ---
echo "[2/3] Installing Python dependencies for the Network Analyzer..."
pip install -r backend/requirements.txt

# --- 3. Completion ---
echo "[3/3] Installation complete!"
echo ""
echo "To run the application, follow these steps:"
echo "1. Activate the virtual environment from the root: source venv/bin/activate"
echo "2. Start the Flask server: python3 network_analyzer/backend/app.py"
echo "3. Open your browser and go to http://127.0.0.1:5001"
echo ""
