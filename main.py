from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
import time
from config import Config
from models import db, Intern, Attendance, Admin, Task
app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)

# Home 
@app.route('/')
def intern():
    return "Welcome Intern"

# Register the intern
@app.route('/register', methods=['GET', 'POST'])
def register_intern():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([name, email, password]):
            return "Please fill in all fields.", 400

        if Intern.query.filter_by(email=email).first():
            return "Intern with this email already exists.", 409

        hashed_password = generate_password_hash(password)
        new_intern = Intern(name=name, email=email, password=hashed_password)
        db.session.add(new_intern)
        db.session.commit()

        return "Intern registered successfully!"

    # HTML form
    html_form = '''
    <h2>Register Intern</h2>
    <form method="POST">
        Name: <input type="text" name="name" required><br><br>
        Email: <input type="email" name="email" required><br><br>
        Password: <input type="password" name="password" required><br><br>
        <input type="submit" value="Register">
    </form>
    '''
    return render_template_string(html_form)


# Intern login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        intern_id = request.form.get('id')
        
        if not intern_id:
            return "Intern ID is required", 400

        intern = Intern.query.get(intern_id)
        if not intern:
            return "Intern not found", 404

        
        today = datetime.today().date()
        existing_attendance = Attendance.query.filter_by(intern_id=intern_id, date=today).first()

        if existing_attendance:
            return "You have already logged in today", 400

        
        login_time = datetime.now().time()
        new_attendance = Attendance(intern_id=intern_id, date=today, login_time=login_time)
        db.session.add(new_attendance)
        db.session.commit()

        return f"Logged in successfully! Login time: {login_time}"

    # HTML form 
    html_form = '''
    <h2>Login Intern</h2>
    <form method="POST">
        Intern ID: <input type="text" name="id" required><br><br>
        <input type="submit" value="Login">
    </form>
    '''
    return render_template_string(html_form)

# Intern Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        intern_id = request.form.get('id')
        
        if not intern_id:
            return "Intern ID is required", 400

        intern = Intern.query.get(intern_id)
        if not intern:
            return "Intern not found", 404

        today = datetime.today().date()
        attendance = Attendance.query.filter_by(intern_id=intern_id, date=today).first()

        if not attendance:
            return "You must log in first!", 400

        if attendance.logout_time:
            return "You have already logged out today!", 400

        
        logout_time = datetime.now().time()
        login_time = datetime.combine(datetime.today(), attendance.login_time)
        logout_time_full = datetime.combine(datetime.today(), logout_time)

        
        total_duration = logout_time_full - login_time
        total_duration_seconds = total_duration.total_seconds()
        total_duration_time = time.strftime('%H:%M:%S', time.gmtime(total_duration_seconds))

        
        attendance.logout_time = logout_time
        attendance.total_duration = total_duration_time
        db.session.commit()

        return f"Logged out successfully! Logout time: {logout_time}, Total Duration: {total_duration_time}"

    # HTML form 
    html_form = '''
    <h2>Logout Intern</h2>
    <form method="POST">
        Intern ID: <input type="text" name="id" required><br><br>
        <input type="submit" value="Logout">
    </form>
    '''
    return render_template_string(html_form)


# Admin Registration 
@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        
        if not all([name, email, password]):
            return "Please fill in all fields.", 400

        
        if Admin.query.filter_by(email=email).first():
            return "Admin with this email already exists.", 409

        
        hashed_password = generate_password_hash(password)

        
        new_admin = Admin(name=name, email=email, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        return "Admin registered successfully!"

    
    html_form = '''
    <h2>Register Admin</h2>
    <form method="POST">
        Name: <input type="text" name="name" required><br><br>
        Email: <input type="email" name="email" required><br><br>
        Password: <input type="password" name="password" required><br><br>
        <input type="submit" value="Register">
    </form>
    '''
    return render_template_string(html_form)

# Admin assign task to interns 
@app.route('/admin/task', methods=['GET', 'POST'])
def admin_assign_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assigned_by = request.form.get('admin_id')
        assigned_to = request.form.get('intern_id')

        if not all([title, assigned_by, assigned_to]):
            return "Missing required fields", 400

        task = Task(
            title=title,
            description=description,
            assigned_by=int(assigned_by),
            assigned_to=int(assigned_to)
        )
        db.session.add(task)
        db.session.commit()
        return "Task assigned successfully!"

    html = '''
    <h2>Assign Task (Admin)</h2>
    <form method="POST">
        Admin ID: <input type="number" name="admin_id" required><br><br>
        Intern ID: <input type="number" name="intern_id" required><br><br>
        Task Title: <input type="text" name="title" required><br><br>
        Description: <textarea name="description"></textarea><br><br>
        <input type="submit" value="Assign Task">
    </form>
    '''
    return render_template_string(html)

# Intern views and marks task completed
@app.route('/intern/task', methods=['GET', 'POST'])
def intern_tasks():
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        task = Task.query.get(task_id)

        if task and task.status == 'pending':
            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            db.session.commit()
            return f"Task {task_id} marked as completed!"
        return "Invalid task ID or task already completed.", 400

    intern_id = request.args.get('intern_id')
    if not intern_id:
        return '''
        <form method="GET">
            Enter Intern ID: <input type="number" name="intern_id">
            <input type="submit" value="View Tasks">
        </form>
        '''

    tasks = Task.query.filter_by(assigned_to=intern_id).all()
    html = f"<h2>Tasks for Intern ID {intern_id}</h2>"
    for task in tasks:
        html += f"<p><strong>{task.title}</strong> - {task.status}<br>{task.description}<br>"
        if task.status == 'pending':
            html += f'''
            <form method="POST">
                <input type="hidden" name="task_id" value="{task.id}">
                <input type="submit" value="Mark as Completed">
            </form>
            '''
        html += "</p><hr>"
    return render_template_string(html)

# Run server
if __name__ == "__main__":
    app.run(debug=True)
