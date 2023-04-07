
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:anhtuan2003@localhost/health_advice?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    birthday= db.Column(db.Date,unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    diseases_past= db.Column(db.Text, nullable=True)
    diseases_present = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    def __str__(self):
        return self.email
    
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
            return redirect(url_for('admin'))
        else:
             return redirect(url_for('register'))
    else:
        return render_template('index.html')


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
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # flash('Email already exists, please choose another one.')
            return redirect(url_for('register'))
        else:
            user = User(username=username,birthday=birthday,gender=gender, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.email
            return redirect(url_for('admin'))
    else:
        return render_template('index.html')

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
            db.session.execute(text("ALTER TABLE user AUTO_INCREMENT = 1"))
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

@app.route('/admin')
def admin():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user.is_admin:
            users = User.query.all()
            return render_template('users.html', users=users)
        else:
            # Người dùng không phải admin, chuyển hướng về trang profile
            return redirect(url_for('profile'))
    else:
        # Người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
        return redirect(url_for('login'))
    
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Kiểm tra xem người dùng hiện tại có phải là admin hay không
    if 'user' in session:
        admin_user = User.query.filter_by(email=session['user'], is_admin=True).first()
        if admin_user:
            # Xóa người dùng
            user = User.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()
            db.session.execute(text("ALTER TABLE user AUTO_INCREMENT = 1"))
            db.session.commit()
    # Chuyển hướng về trang quản trị
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
