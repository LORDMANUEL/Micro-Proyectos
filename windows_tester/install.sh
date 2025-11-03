#!/bin/bash
echo ">>> Installing dependencies for Windows Tester..."
source venv/bin/activate
pip install -r windows_tester/backend/requirements.txt
