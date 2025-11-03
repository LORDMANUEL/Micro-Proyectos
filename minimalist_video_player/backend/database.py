import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'player.db')

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Create Tables ---
    # Media files table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS media_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL UNIQUE,
        file_type TEXT NOT NULL
    );
    """)

    # Playlists table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        items TEXT NOT NULL
    );
    """)

    # --- Insert Sample Data (for demonstration) ---
    try:
        cursor.execute("INSERT INTO media_files (filename, file_type) VALUES (?, ?)", ('sample_video.mp4', 'video'))
        cursor.execute("INSERT INTO media_files (filename, file_type) VALUES (?, ?)", ('sample_page.html', 'html'))
    except sqlite3.IntegrityError:
        # Data might already exist
        pass

    try:
        # Items are stored as a JSON string of media_file IDs
        cursor.execute("INSERT INTO playlists (name, items) VALUES (?, ?)", ('Default Playlist', '[1, 2]'))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    initialize_database()
