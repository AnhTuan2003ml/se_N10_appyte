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
    diseases_past= db.Column(db.Text, nullable=True)
    diseases_present = db.Column(db.Text, nullable=True)

    
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
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="anhtuan2003",
            database="health_advice"
            )

            # Thực hiện truy vấn SQL
            mycursor = mydb.cursor()

            mycursor.execute("SELECT * FROM user")

            myresult = mycursor.fetchall()
            check= False
            for x in myresult:
                if x[4]==email:
                    check=True
                    break
            if check==True:
                return redirect(url_for('login'))
            else:
                return redirect(url_for('register'))
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
        if user.diseases_past is None and user.diseases_present is None:
            return render_template('profile.html', user=user)
        else:
            return render_template('newprofile.html', user=user)
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

@app.route('/update_diseases', methods=['GET', 'POST'])
def update_diseases():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if request.method == 'POST':
            user.diseases_past = request.form['diseases_past']
            user.diseases_present = request.form['diseases_present']
            db.session.commit()
            return render_template('newprofile.html', user=user)
        return render_template('update_diseases.html', user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
