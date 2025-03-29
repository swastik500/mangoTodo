from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Change this in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong"

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://sojupingale:swip2004@swip.b9vgs6y.mongodb.net/?retryWrites=true&w=majority&appName=swip")
client = MongoClient(MONGO_URI)
db = client["todoDB"]
users_collection = db["users"]
tasks_collection = db["tasks"]


# User Class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user["_id"]), user["username"])
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()  # ✅ Avoids KeyError
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Username and password are required!", "danger")
            return redirect(url_for('register'))  # Redirect instead of returning 400

        # Check if user already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Try a different one.", "danger")
            return redirect(url_for('register'))

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')  # Show the form if GET request


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Request form data:", request.form)  # Debugging line
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Missing username or password!", "danger")
            return redirect(url_for('login'))

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            login_user(User(str(user["_id"]), user["username"]))
            flash("Login successful!", "success")
            return redirect(url_for('index'))

        flash("Invalid credentials!", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    tasks = list(tasks_collection.find({"user_id": current_user.id}))  # Fetch tasks for the logged-in user
    return render_template('index.html', tasks=tasks, username=current_user.username)


@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_content = request.form.get('task', '').strip()

    if task_content:
        tasks_collection.insert_one({"task": task_content, "status": "Pending", "user_id": current_user.id})
        flash("Task added successfully!", "success")
    else:
        flash("Task cannot be empty!", "warning")

    return redirect(url_for('index'))


@app.route('/update/<task_id>')
@login_required
def update_task(task_id):
    result = tasks_collection.update_one({"_id": ObjectId(task_id), "user_id": current_user.id},
                                         {"$set": {"status": "Completed"}})

    if result.modified_count > 0:
        flash("Task marked as completed!", "success")
    else:
        flash("Task not found!", "warning")

    return redirect(url_for('index'))


@app.route('/delete/<task_id>')
@login_required
def delete_task(task_id):
    result = tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": current_user.id})

    if result.deleted_count > 0:
        flash("Task deleted successfully!", "success")
    else:
        flash("Task not found!", "warning")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
