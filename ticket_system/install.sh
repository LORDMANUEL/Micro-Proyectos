#!/bin/bash

# A simple installation script for the ticket system on Debian/Ubuntu.

echo "Starting the installation of the IT Ticket System..."

# --- 1. System Dependency Check & Installation ---
echo "[1/4] Updating package lists and checking for Python..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# --- 2. Python Virtual Environment & Dependencies ---
echo "[2/4] Setting up Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists. Skipping creation."
else
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies from requirements.txt..."
pip install -r ticket_system/backend/requirements.txt

# --- 3. Database Initialization ---
echo "[3/4] Initializing the SQLite database..."
# The script needs to be run from the context of the backend folder
python3 ticket_system/backend/database.py

# --- 4. Completion ---
echo "[4/4] Installation complete!"
echo ""
echo "To run the application, follow these steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the Flask server: python3 -m flask --app ticket_system.backend.app run"
echo "3. Open your browser and go to http://127.0.0.1:5000"
echo ""
echo "Thank you for installing the IT Ticket System."
