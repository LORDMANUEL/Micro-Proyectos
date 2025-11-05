import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import subprocess

# Base directory of the app
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret_key_for_flashing'
# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'printers.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Printer model
class Printer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    ip_address = db.Column(db.String(15), unique=True, nullable=False)
    is_rented = db.Column(db.Boolean, default=False)
    consumables = db.Column(db.String(200)) # e.g., "Toner: TN-2420, Drum: DR-2400"
    status = db.Column(db.String(50), default='Unknown')

    def __repr__(self):
        return f'<Printer {self.name}>'

@app.route('/')
def index():
    printers = Printer.query.all()
    return render_template('p_index.html', printers=printers)

@app.route('/add', methods=['GET', 'POST'])
def add_printer():
    if request.method == 'POST':
        new_printer = Printer(
            name=request.form['name'],
            model=request.form['model'],
            location=request.form['location'],
            ip_address=request.form['ip_address'],
            is_rented='is_rented' in request.form,
            consumables=request.form['consumables']
        )
        db.session.add(new_printer)
        db.session.commit()
        flash(f"Printer '{new_printer.name}' added successfully!", 'success')
        return redirect(url_for('index'))
    return render_template('p_add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_printer(id):
    printer = Printer.query.get_or_404(id)
    if request.method == 'POST':
        printer.name = request.form['name']
        printer.model = request.form['model']
        printer.location = request.form['location']
        printer.ip_address = request.form['ip_address']
        printer.is_rented = 'is_rented' in request.form
        printer.consumables = request.form['consumables']
        db.session.commit()
        flash(f"Printer '{printer.name}' updated successfully!", 'success')
        return redirect(url_for('index'))
    return render_template('p_edit.html', printer=printer)

@app.route('/delete/<int:id>')
def delete_printer(id):
    printer_to_delete = Printer.query.get_or_404(id)
    db.session.delete(printer_to_delete)
    db.session.commit()
    flash(f"Printer '{printer_to_delete.name}' deleted successfully!", 'info')
    return redirect(url_for('index'))

@app.route('/validate/<int:id>')
def validate_printer(id):
    printer = Printer.query.get_or_404(id)
    # Simple ping check for validation
    try:
        # Using -c 1 for a single packet, -W 1 for a 1-second timeout
        subprocess.check_output(["ping", "-c", "1", "-W", "1", printer.ip_address])
        printer.status = 'Online'
        flash(f"Success! Printer '{printer.name}' is online.", 'success')
    except subprocess.CalledProcessError:
        printer.status = 'Offline'
        flash(f"Error! Printer '{printer.name}' is offline or unreachable.", 'danger')

    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5008, debug=True)
