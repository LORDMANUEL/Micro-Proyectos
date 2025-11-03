import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from datetime import datetime

app = Flask(__name__, static_folder=os.path.abspath('printer_management_platform/frontend'))
CORS(app)

DATABASE = 'printer_management_platform/backend/printer_management.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Printer Endpoints ---
@app.route('/api/printers', methods=['GET'])
def get_printers():
    conn = get_db_connection()
    printers = conn.execute('SELECT * FROM printers').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in printers])

@app.route('/api/printers', methods=['POST'])
def add_printer():
    new_printer = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO printers (name, model, ip_address, location, purchase_date, purchase_price, driver_url, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (new_printer['name'], new_printer['model'], new_printer['ip_address'], new_printer['location'], new_printer['purchase_date'], new_printer['purchase_price'], new_printer['driver_url'], new_printer['notes']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/printers/<int:printer_id>', methods=['GET'])
def get_printer(printer_id):
    conn = get_db_connection()
    printer = conn.execute('SELECT * FROM printers WHERE id = ?', (printer_id,)).fetchone()
    conn.close()
    if printer is None:
        return jsonify({'error': 'Printer not found'}), 404
    return jsonify(dict(printer))

@app.route('/api/printers/<int:printer_id>', methods=['DELETE'])
def delete_printer(printer_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM printers WHERE id = ?', (printer_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Printer deleted successfully'})

# --- Toner Cartridge Endpoints (for defining toner types) ---
@app.route('/api/toner_cartridges', methods=['GET'])
def get_toner_cartridges():
    conn = get_db_connection()
    cartridges = conn.execute('SELECT * FROM toner_cartridges').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in cartridges])

@app.route('/api/toner_cartridges', methods=['POST'])
def add_toner_cartridge():
    new_cartridge = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO toner_cartridges (model, color, yield) VALUES (?, ?, ?)',
                 (new_cartridge['model'], new_cartridge['color'], new_cartridge['yield']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

# --- Toner Inventory Endpoints (for managing stock) ---
@app.route('/api/toner_inventory', methods=['GET'])
def get_toner_inventory():
    conn = get_db_connection()
    inventory = conn.execute('''
        SELECT ti.id, tc.model, tc.color, ti.quantity
        FROM toner_inventory ti
        JOIN toner_cartridges tc ON ti.cartridge_id = tc.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in inventory])

@app.route('/api/toner_inventory', methods=['POST'])
def add_to_toner_inventory():
    data = request.get_json()
    conn = get_db_connection()
    # Check if this cartridge is already in inventory
    item = conn.execute('SELECT id, quantity FROM toner_inventory WHERE cartridge_id = ?', (data['cartridge_id'],)).fetchone()
    if item:
        # Update quantity
        new_quantity = item['quantity'] + data['quantity']
        conn.execute('UPDATE toner_inventory SET quantity = ? WHERE id = ?', (new_quantity, item['id']))
    else:
        # Insert new record
        conn.execute('INSERT INTO toner_inventory (cartridge_id, quantity) VALUES (?, ?)', (data['cartridge_id'], data['quantity']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Inventory updated successfully'}), 201

# --- Toner Usage Log Endpoints ---
@app.route('/api/printers/<int:printer_id>/toner_logs', methods=['POST'])
def log_toner_change(printer_id):
    data = request.get_json()
    conn = get_db_connection()
    # Log the change
    conn.execute('INSERT INTO toner_usage_logs (printer_id, cartridge_id, change_date) VALUES (?, ?, ?)',
                 (printer_id, data['cartridge_id'], data['change_date']))
    # Decrement inventory
    conn.execute('UPDATE toner_inventory SET quantity = quantity - 1 WHERE cartridge_id = ?', (data['cartridge_id'],))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Toner change logged successfully'}), 201

# --- AI Endpoints ---
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")

def ask_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return f"Error: No se pudo contactar al servicio de IA. Detalles: {e}"

@app.route('/api/printers/<int:printer_id>/depreciation', methods=['GET'])
def get_depreciation(printer_id):
    conn = get_db_connection()
    printer = conn.execute('SELECT purchase_price, purchase_date FROM printers WHERE id = ?', (printer_id,)).fetchone()
    conn.close()

    if printer is None:
        return jsonify({'error': 'Printer not found'}), 404

    purchase_price = printer['purchase_price']
    purchase_date = datetime.strptime(printer['purchase_date'], '%Y-%m-%d')

    # Assuming 7 years useful life for a printer, 0 salvage value
    useful_life = 7
    annual_depreciation = purchase_price / useful_life

    years_owned = (datetime.now() - purchase_date).days / 365.25
    current_value = max(0, purchase_price - (annual_depreciation * years_owned))

    return jsonify({
        'annual_depreciation': round(annual_depreciation, 2),
        'years_owned': round(years_owned, 2),
        'current_book_value': round(current_value, 2)
    })

@app.route('/api/printers/<int:printer_id>/predict_toner', methods=['GET'])
def predict_toner_change(printer_id):
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT tl.change_date
        FROM toner_usage_logs tl
        WHERE tl.printer_id = ?
        ORDER BY tl.change_date DESC
    ''', (printer_id,)).fetchall()
    conn.close()

    if not logs:
        return jsonify({'prediction': 'No hay suficientes datos para una predicción.'})

    log_dates = [row['change_date'] for row in logs]
    prompt = (f"Basado en el siguiente historial de fechas de cambio de tóner para una impresora: {', '.join(log_dates)}. "
              f"Calcula el intervalo promedio en días entre cambios y predice la próxima fecha de cambio de tóner. "
              f"Proporciona una explicación breve y la fecha estimada en formato AAAA-MM-DD.")

    prediction = ask_ollama(prompt)
    return jsonify({'prediction': prediction})

@app.route('/api/printers/<int:printer_id>/profitability', methods=['GET'])
def analyze_profitability(printer_id):
    conn = get_db_connection()
    printer = conn.execute('SELECT model, purchase_price FROM printers WHERE id = ?', (printer_id,)).fetchone()
    toner_info = conn.execute('''
        SELECT AVG(tc.yield) as avg_yield
        FROM toner_usage_logs tl
        JOIN toner_cartridges tc ON tl.cartridge_id = tc.id
        WHERE tl.printer_id = ?
    ''', (printer_id,)).fetchone()
    conn.close()

    if not printer:
        return jsonify({'error': 'Printer not found'}), 404

    prompt = (f"Analiza la rentabilidad de una impresora modelo '{printer['model']}' con un costo de compra de ${printer['purchase_price']}. "
              f"El rendimiento promedio del tóner utilizado es de {toner_info['avg_yield'] or 'N/A'} páginas por cartucho. "
              f"Considerando estos datos y tu conocimiento general sobre impresoras, ¿es este un modelo rentable para una pequeña o mediana empresa? "
              f"Justifica tu respuesta brevemente.")

    analysis = ask_ollama(prompt)
    return jsonify({'analysis': analysis})

@app.route('/api/printers/<int:printer_id>/repairability', methods=['GET'])
def analyze_repairability(printer_id):
    conn = get_db_connection()
    printer = conn.execute('SELECT model FROM printers WHERE id = ?', (printer_id,)).fetchone()
    conn.close()

    if not printer:
        return jsonify({'error': 'Printer not found'}), 404

    prompt = (f"Proporciona un resumen sobre la facilidad de reparación (reparabilidad) de la impresora modelo '{printer['model']}'. "
              f"Menciona si las piezas de repuesto son fáciles de encontrar, si existen problemas comunes conocidos "
              f"y si es un modelo que generalmente se considera fiable y fácil de mantener.")

    analysis = ask_ollama(prompt)
    return jsonify({'analysis': analysis})

# --- Serve Frontend ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007, debug=True)
