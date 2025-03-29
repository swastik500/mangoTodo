from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# MongoDB Atlas connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://sojupingale:swip2004@swip.b9vgs6y.mongodb.net/?retryWrites=true&w=majority&appName=swip")
client = MongoClient(MONGO_URI)
db = client["todoDB"]
collection = db["tasks"]

@app.route('/')
def index():
    tasks = list(collection.find())  # Fetch all tasks
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_content = request.form.get('task')
    if task_content:
        collection.insert_one({"task": task_content, "status": "Pending"})
    return redirect(url_for('index'))

@app.route('/update/<task_id>')
def update_task(task_id):
    collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "Completed"}})
    return redirect(url_for('index'))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
