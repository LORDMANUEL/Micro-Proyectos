#!/bin/bash
echo "--- Installing Minimalist Video Player dependencies ---"
source venv/bin/activate
pip install -r minimalist_video_player/backend/requirements.txt
python minimalist_video_player/backend/database.py
echo "--- Installation complete ---"
