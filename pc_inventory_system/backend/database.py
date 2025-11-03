import sqlite3

def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create computers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS computers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serial_number TEXT NOT NULL UNIQUE,
        brand TEXT,
        model TEXT,
        purchase_date DATE,
        purchase_price REAL,
        status TEXT,
        location TEXT,
        assigned_to TEXT
    )
    ''')

    # Create software table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS software (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        computer_id INTEGER,
        name TEXT NOT NULL,
        license_key TEXT,
        install_date DATE,
        FOREIGN KEY (computer_id) REFERENCES computers (id)
    )
    ''')

    # Create policies table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos inicializada correctamente.")
