import sqlite3

def init_db():
    conn = sqlite3.connect('printer_management.db')
    cursor = conn.cursor()

    # Create printers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS printers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        ip_address TEXT,
        location TEXT,
        purchase_date DATE,
        purchase_price REAL,
        driver_url TEXT,
        notes TEXT
    )
    ''')

    # Create toner cartridges table (defines toner types)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS toner_cartridges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT NOT NULL UNIQUE,
        color TEXT, -- e.g., Black, Cyan, Magenta, Yellow
        yield INTEGER -- Estimated number of pages
    )
    ''')

    # Create toner inventory table (our internal stock)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS toner_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cartridge_id INTEGER,
        quantity INTEGER NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cartridge_id) REFERENCES toner_cartridges (id)
    )
    ''')

    # Create toner usage logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS toner_usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        printer_id INTEGER,
        cartridge_id INTEGER,
        change_date DATE NOT NULL,
        FOREIGN KEY (printer_id) REFERENCES printers (id),
        FOREIGN KEY (cartridge_id) REFERENCES toner_cartridges (id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de datos de gestión de impresoras inicializada correctamente.")
