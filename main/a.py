from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from passlib.hash import sha256_crypt
import os

app = Flask(__name__)

# Kết nối MySQL
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "anhtuan2003"
app.config['MYSQL_DB'] = 'health_advice'


mysql = MySQL(app)

# Thiết lập mã bảo mật
app.secret_key = os.urandom(24)

# Tạo class cho form đăng ký tài khoản


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    email = StringField(
        'Email Address', [validators.Length(min=6, max=50), validators.Email()])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')

# Tạo class cho form đăng nhập


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Login')

# Trang chủ


@app.route('/')
def index():
    return render_template('index.html')

# Trang đăng ký tài khoản


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Thực hiện truy vấn để thêm tài khoản vào cơ sở dữ liệu
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
                    (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Trang đăng nhập


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        # Thực hiện truy vấn để lấy thông tin tài khoản từ cơ sở dữ liệu
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT * FROM users WHERE username = %s", [username])

    if result > 0:
        data = cur.fetchone()
        password = data['password']

        # Kiểm tra mật khẩu
        if sha256_crypt.verify(password_candidate, password):
            session['logged_in'] = True
            session['username'] = username
 
            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid login'
            return render_template('login.html', form=form, error=error)
        cur.close()
    else:
        error = 'Username not found'
        return render_template('login.html', form=form, error=error)

    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard():

    if 'logged_in' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))



app.run(debug=True)