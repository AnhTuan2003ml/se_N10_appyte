from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:anhtuan2003@localhost/health_advice'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    birthday= db.Column(db.Date,unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.email
            return redirect(url_for('profile'))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        birthday = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username,birthday=birthday,gender=gender, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.email
        return redirect(url_for('profile'))
    else:
        return render_template('register.html')
    
@app.route('/profile')
def profile():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/delete-account', methods=['GET', 'POST'])
def delete_account():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if request.method == 'POST':
            db.session.delete(user)
            db.session.commit()
            session.pop('user', None)
            return redirect(url_for('index'))
        return render_template('delete_account.html', user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
