from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Config database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    bday = db.Column(db.String(10))
    address = db.Column(db.String(200))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(120))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pw = request.form['password']
        user = User.query.filter_by(username=uname, password=pw).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        return 'Invalid credentials'
    # GET request returns the login page
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if username already exists
        existing_user = User.query.filter_by(username=request.form['username']).first()
        if existing_user:
            return "Username already taken, please choose another.", 400

        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_user = User(
            name=request.form['name'],
            bday=request.form['bday'],
            address=request.form['address'],
            username=request.form['username'],
            password=request.form['password'],
            image=filename
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return redirect(url_for('home'))  # redirect back to login page after registering

    return render_template('register.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)


@app.route('/logout', methods=['POST'])
def logout():
    session.clear() 
    return redirect(url_for('login')) 

if __name__ == '__main__':
    app.run(debug=True)
