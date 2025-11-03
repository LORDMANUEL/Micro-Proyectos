import sqlite3

def init_db():
    conn = sqlite3.connect('scripts.db')
    cursor = conn.cursor()

    # Create scripts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        script_type TEXT NOT NULL, -- e.g., 'powershell', 'batch'
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos de scripts inicializada correctamente.")
