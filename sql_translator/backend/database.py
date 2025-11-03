import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'sap_b1_example.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using the schema.sql file."""
    if os.path.exists(DATABASE_PATH):
        print("Database already exists. Deleting and re-initializing for a clean state.")
        os.remove(DATABASE_PATH)

    print("Initializing database...")
    try:
        conn = get_db_connection()
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized successfully with SAP B1 schema.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
