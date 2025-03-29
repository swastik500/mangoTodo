from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI",
                      "mongodb+srv://sojupingale:swip2004@swip.b9vgs6y.mongodb.net/?retryWrites=true&w=majority&appName=swip")
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
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        if users_collection.find_one({"username": username}):
            return "User already exists!"

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user in MongoDB
        user_id = users_collection.insert_one({"username": username, "password": hashed_pw}).inserted_id
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            login_user(User(str(user["_id"]), user["username"]))
            return redirect(url_for('index'))
        return "Invalid credentials!"

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    tasks = list(tasks_collection.find({"user_id": current_user.id}))  # Fetch tasks for the logged-in user
    return render_template('index.html', tasks=tasks, username=current_user.username)


@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_content = request.form.get('task')
    if task_content:
        tasks_collection.insert_one({"task": task_content, "status": "Pending", "user_id": current_user.id})
    return redirect(url_for('index'))


@app.route('/update/<task_id>')
@login_required
def update_task(task_id):
    tasks_collection.update_one({"_id": ObjectId(task_id), "user_id": current_user.id},
                                {"$set": {"status": "Completed"}})
    return redirect(url_for('index'))


@app.route('/delete/<task_id>')
@login_required
def delete_task(task_id):
    tasks_collection.delete_one({"_id": ObjectId(task_id), "user_id": current_user.id})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
