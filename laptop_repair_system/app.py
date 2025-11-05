import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_for_laptop_repair'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'repairs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RepairTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    laptop_model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Received', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<RepairTicket {self.id} for {self.customer_name}>'

STATUS_CHOICES = [
    'Received',
    'In Diagnostics',
    'Awaiting Parts',
    'In Repair',
    'Repair Complete',
    'Ready for Pickup',
    'Delivered'
]

@app.route('/')
def index():
    tickets = RepairTicket.query.order_by(RepairTicket.created_at.desc()).all()
    return render_template('lr_index.html', tickets=tickets)

@app.route('/create', methods=['GET', 'POST'])
def create_ticket():
    if request.method == 'POST':
        new_ticket = RepairTicket(
            customer_name=request.form['customer_name'],
            laptop_model=request.form['laptop_model'],
            serial_number=request.form['serial_number'],
            issue_description=request.form['issue_description']
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash('New repair ticket created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('lr_create.html')

@app.route('/ticket/<int:id>', methods=['GET', 'POST'])
def view_ticket(id):
    ticket = RepairTicket.query.get_or_404(id)
    if request.method == 'POST':
        ticket.status = request.form['status']
        db.session.commit()
        flash(f'Ticket #{ticket.id} status updated to "{ticket.status}".', 'info')
        return redirect(url_for('view_ticket', id=id))
    return render_template('lr_view.html', ticket=ticket, statuses=STATUS_CHOICES)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5011, debug=True)
