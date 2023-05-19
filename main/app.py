
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
    __tablename__ = 'user'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    birthday= db.Column(db.Date,unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    diseases_past= db.Column(db.Text, nullable=True)
    diseases_present = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    def __str__(self):
        return self.email
    
class  Diseases(db.Model):
    __tablename__ = 'disease'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    diseases_name= db.Column(db.Text, nullable=True)
    diseases_symptom = db.Column(db.Text, nullable=True)
    def __str__(self):
        return self.diseases_symptom


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(255), nullable=False)
    workplace = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, email, name, experience, age, specialization, workplace, password):
        self.email = email
        self.name = name
        self.experience = experience
        self.age = age
        self.specialization = specialization
        self.workplace = workplace
        self.password = password

def get_doctor_count():
    with app.app_context():
        return Doctor.query.count()

def get_user_count():
    with app.app_context():
        return User.query.count()


userscount = get_user_count()
doctorscount =  get_doctor_count()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

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
            return render_template('profile.html', user=user)
        return render_template('update_diseases.html', user=user)
    else:
        return redirect(url_for('login'))
@app.route('/admin')
def admin():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user.is_admin:
            users = User.query.all()
            return render_template('users.html', users=users, user=user, users_count= userscount,doctors_count=doctorscount)  # Thêm biến user vào hàm render_template
        else:
            return render_template('home.html', user=user)  # Thêm biến user vào hàm render_template
    else:
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
@app.route('/home/search', methods=['POST'])
def search():
    symptom = request.form['text']
    diseases = Diseases.query.filter_by( diseases_symptom=symptom).first()
    return render_template('diseases.html', diseases=diseases)

@app.route('/doctor')
def doctor():
    doctors= Doctor.query.all()
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user.is_admin:
            return render_template('doctors.html', doctors=doctors, user=user,users_count= userscount,doctors_count=doctorscount)  # Thêm biến user vào hàm render_template
        else:
            return render_template('doctor.html', doctors=doctors)  # Thêm biến user vào hàm render_template
    else:
        return redirect(url_for('login'))
...

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user.is_admin:
            if request.method == 'POST':
                email = request.form['email']
                name = request.form['name']
                experience = request.form['experience']
                age = request.form['age']
                specialization = request.form['specialization']
                workplace = request.form['workplace']
                password = request.form['password']
                
                doctor = Doctor(email=email, name=name, experience=experience, age=age, specialization=specialization, workplace=workplace, password=password)
                db.session.add(doctor)
                db.session.commit()
                
                return redirect(url_for('doctor'))
                
            return render_template('add_doctor.html', user=user)
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))



@app.route('/delete-doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user.is_admin:
            doctor = Doctor.query.get(doctor_id)
            if doctor:
                db.session.delete(doctor)
                db.session.commit()
            
    return redirect(url_for('doctor'))




if __name__ == '__main__':
    app.run(debug=True)
