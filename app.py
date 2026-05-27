from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# ======================================
# CONFIGURATION
# ======================================

app.config['SECRET_KEY'] = 'securetasksecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

UPLOAD_FOLDER = 'static/uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ======================================
# DATABASE MODELS
# ======================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.String(500))
    filename = db.Column(db.String(300))


# ======================================
# ROUTES
# ======================================

@app.route('/')
def home():

    return redirect(url_for('login'))


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            return redirect(url_for('dashboard'))

    return render_template('login.html')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():

    tasks = Task.query.all()

    return render_template(
        'dashboard.html',
        tasks=tasks
    )


# ADD TASK
@app.route('/add_task', methods=['POST'])
def add_task():

    title = request.form['title']
    description = request.form['description']

    filename = ''

    uploaded_file = request.files.get('file')

    if uploaded_file and uploaded_file.filename != '':

        filename = secure_filename(uploaded_file.filename)

        uploaded_file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

    new_task = Task(
        title=title,
        description=description,
        filename=filename
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('dashboard'))


# EDIT TASK
@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):

    task = Task.query.get(id)

    if request.method == 'POST':

        task.title = request.form['title']
        task.description = request.form['description']

        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template(
        'edit_task.html',
        task=task
    )


# DELETE TASK
@app.route('/delete_task/<int:id>')
def delete_task(id):

    task = Task.query.get(id)

    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('dashboard'))


# LOGOUT
@app.route('/logout')
def logout():

    return redirect(url_for('login'))


# ======================================
# MAIN
# ======================================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)