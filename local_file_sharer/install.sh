#!/bin/bash
echo "--- Installing Local File Sharer dependencies ---"
source venv/bin/activate
pip install -r local_file_sharer/backend/requirements.txt
echo "--- Installation complete ---"
