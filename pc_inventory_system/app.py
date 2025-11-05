import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Base directory of the app
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configure the database URI. It will be created in the instance folder.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the PC model for the database
class PC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False, unique=True)
    owner = db.Column(db.String(100), nullable=False)
    ram = db.Column(db.String(50))
    cpu = db.Column(db.String(100))
    storage = db.Column(db.String(100))
    os = db.Column(db.String(100))

    def __repr__(self):
        return f'<PC {self.hostname}>'

@app.route('/')
def index():
    pcs = PC.query.all()
    return render_template('index.html', pcs=pcs)

@app.route('/add', methods=['GET', 'POST'])
def add_pc():
    if request.method == 'POST':
        hostname = request.form['hostname']
        owner = request.form['owner']
        ram = request.form['ram']
        cpu = request.form['cpu']
        storage = request.form['storage']
        os_system = request.form['os']

        new_pc = PC(
            hostname=hostname,
            owner=owner,
            ram=ram,
            cpu=cpu,
            storage=storage,
            os=os_system
        )

        db.session.add(new_pc)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_pc.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_pc(id):
    pc = PC.query.get_or_404(id)
    if request.method == 'POST':
        pc.hostname = request.form['hostname']
        pc.owner = request.form['owner']
        pc.ram = request.form['ram']
        pc.cpu = request.form['cpu']
        pc.storage = request.form['storage']
        pc.os = request.form['os']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_pc.html', pc=pc)

@app.route('/delete/<int:id>')
def delete_pc(id):
    pc_to_delete = PC.query.get_or_404(id)
    db.session.delete(pc_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5007, debug=True)
