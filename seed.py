import sqlite3

def seed_data():
    conn = sqlite3.connect('printer_management_platform/backend/printer_management.db')
    cursor = conn.cursor()

    # Add a sample printer
    cursor.execute("""
    INSERT INTO printers (name, model, ip_address, location, purchase_date, purchase_price, driver_url, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('HP LaserJet Pro M404dn', 'M404dn', '192.168.1.100', 'Oficina Principal', '2023-01-15', 400.00, 'http://hp.com/drivers', 'Impresora láser monocromática'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    seed_data()
    print("Datos de ejemplo insertados correctamente.")
