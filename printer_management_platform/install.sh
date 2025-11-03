#!/bin/bash
echo ">>> Installing dependencies for Printer Management Platform..."
source venv/bin/activate
pip install -r printer_management_platform/backend/requirements.txt
