import os
import csv
import random
from datetime import datetime
from io import StringIO
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-neon-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dashboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
scheduler = APScheduler()

# --- Database Models ---
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(20), unique=True, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(10), nullable=False) # Big / Small
    color = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# --- Background Task to Auto-Generate Records every minute ---
def generate_period_record():
    with app.app_context():
        now = datetime.utcnow()
        period_str = now.strftime("%Y%m%d%H%M")
        
        # Check if period exists
        if not Record.query.filter_by(period=period_str).first():
            number = random.randint(0, 9)
            size = "Big" if number >= 5 else "Small"
            color = "Green" if number in [1,3,7,9] else ("Red" if number in [2,4,6,8] else "Violet")
            
            new_record = Record(period=period_str, number=number, size=size, color=color)
            db.session.add(new_record)
            db.session.commit()

scheduler.add_job(id='Generate Record', func=generate_period_record, trigger='interval', seconds=60)
scheduler.start()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

# --- REST APIs ---
@app.route('/api/records', methods=['GET'])
def get_records():
    search = request.args.get('search', '')
    query = Record.query.order_by(Record.timestamp.desc())
    
    if search:
        query = query.filter(Record.period.contains(search))
        
    records = query.limit(50).all()
    data = [{
        'period': r.period,
        'number': r.number,
        'size': r.size,
        'color': r.color,
        'time': r.timestamp.strftime("%H:%M:%S")
    } for r in records]
    return jsonify(data)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_history = Record.query.count()
    # Mock win/loss logic for UI representation
    total_win = int(total_history * 0.45) 
    total_loss = total_history - total_win
    return jsonify({'total': total_history, 'win': total_win, 'loss': total_loss})

@app.route('/api/export')
@login_required
def export_csv():
    records = Record.query.order_by(Record.timestamp.desc()).all()
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        writer.writerow(('Period', 'Number', 'Size', 'Color', 'Time'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        for r in records:
            writer.writerow((r.period, r.number, r.size, r.color, r.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=history.csv"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            hashed_pw = generate_password_hash('admin123') # Default password
            admin = Admin(username='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, port=5000)
    