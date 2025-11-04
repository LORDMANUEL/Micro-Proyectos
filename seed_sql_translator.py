import sqlite3

conn = sqlite3.connect('sql_translator/database.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT
)
""")

cursor.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    amount REAL
)
""")

cursor.execute("INSERT INTO customers (name, country) VALUES (?, ?)", ('John Doe', 'USA'))
cursor.execute("INSERT INTO customers (name, country) VALUES (?, ?)", ('Jane Smith', 'Canada'))
cursor.execute("INSERT INTO orders (customer_id, amount) VALUES (?, ?)", (1, 100.0))
cursor.execute("INSERT INTO orders (customer_id, amount) VALUES (?, ?)", (2, 200.0))

conn.commit()
conn.close()
