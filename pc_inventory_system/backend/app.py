import sqlite3
import qrcode
from io import BytesIO
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os

app = Flask(__name__, static_folder=os.path.abspath('pc_inventory_system/frontend'))
CORS(app)

DATABASE = 'pc_inventory_system/backend/inventory.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/computers', methods=['GET'])
def get_computers():
    conn = get_db_connection()
    computers = conn.execute('SELECT * FROM computers').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in computers])

@app.route('/api/computers', methods=['POST'])
def add_computer():
    new_computer = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO computers (serial_number, brand, model, purchase_date, purchase_price, status, location, assigned_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (new_computer['serial_number'], new_computer['brand'], new_computer['model'], new_computer['purchase_date'], new_computer['purchase_price'], new_computer['status'], new_computer['location'], new_computer['assigned_to']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/computers/<int:computer_id>', methods=['GET'])
def get_computer(computer_id):
    conn = get_db_connection()
    computer = conn.execute('SELECT * FROM computers WHERE id = ?', (computer_id,)).fetchone()
    conn.close()
    if computer is None:
        return jsonify({'error': 'Computer not found'}), 404
    return jsonify(dict(computer))

@app.route('/api/computers/<int:computer_id>', methods=['PUT'])
def update_computer(computer_id):
    updated_computer = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE computers SET serial_number = ?, brand = ?, model = ?, purchase_date = ?, purchase_price = ?, status = ?, location = ?, assigned_to = ? WHERE id = ?',
                 (updated_computer['serial_number'], updated_computer['brand'], updated_computer['model'], updated_computer['purchase_date'], updated_computer['purchase_price'], updated_computer['status'], updated_computer['location'], updated_computer['assigned_to'], computer_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Computer updated successfully'})

@app.route('/api/computers/<int:computer_id>', methods=['DELETE'])
def delete_computer(computer_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM computers WHERE id = ?', (computer_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Computer deleted successfully'})

# Software Endpoints
@app.route('/api/computers/<int:computer_id>/software', methods=['GET'])
def get_software_for_computer(computer_id):
    conn = get_db_connection()
    software = conn.execute('SELECT * FROM software WHERE computer_id = ?', (computer_id,)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in software])

@app.route('/api/software', methods=['POST'])
def add_software():
    new_software = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO software (computer_id, name, license_key, install_date) VALUES (?, ?, ?, ?)',
                 (new_software['computer_id'], new_software['name'], new_software['license_key'], new_software['install_date']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/software/<int:software_id>', methods=['DELETE'])
def delete_software(software_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM software WHERE id = ?', (software_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Software deleted successfully'})

# Policies Endpoints
@app.route('/api/policies', methods=['GET'])
def get_policies():
    conn = get_db_connection()
    policies = conn.execute('SELECT * FROM policies').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in policies])

@app.route('/api/policies', methods=['POST'])
def add_policy():
    new_policy = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO policies (title, content) VALUES (?, ?)',
                 (new_policy['title'], new_policy['content']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/api/policies/<int:policy_id>', methods=['DELETE'])
def delete_policy(policy_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM policies WHERE id = ?', (policy_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Policy deleted successfully'})

# Business Logic Endpoints
@app.route('/api/computers/<int:computer_id>/depreciation', methods=['GET'])
def get_depreciation(computer_id):
    conn = get_db_connection()
    computer = conn.execute('SELECT purchase_price, purchase_date FROM computers WHERE id = ?', (computer_id,)).fetchone()
    conn.close()

    if computer is None:
        return jsonify({'error': 'Computer not found'}), 404

    from datetime import datetime

    purchase_price = computer['purchase_price']
    purchase_date = datetime.strptime(computer['purchase_date'], '%Y-%m-%d')

    # Straight-line depreciation: (cost - salvage_value) / useful_life
    # Assuming 5 years useful life and 0 salvage value
    useful_life = 5
    annual_depreciation = purchase_price / useful_life

    years_owned = (datetime.now() - purchase_date).days / 365.25
    current_value = max(0, purchase_price - (annual_depreciation * years_owned))

    return jsonify({
        'annual_depreciation': round(annual_depreciation, 2),
        'years_owned': round(years_owned, 2),
        'current_book_value': round(current_value, 2)
    })

@app.route('/api/computers/<int:computer_id>/qr', methods=['GET'])
def get_qr_code(computer_id):
    # For a real-world app, you'd probably encode a URL
    # that links to the asset's page in your web app.
    # For simplicity, we'll just encode the computer's ID.
    qr_data = str(computer_id)

    img = qrcode.make(qr_data)
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

# Serve frontend
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)
