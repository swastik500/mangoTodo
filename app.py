from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Use MongoDB Atlas instead of localhost
MONGO_URI = "mongodb+srv://sojupingale:swip2004@swip.b9vgs6y.mongodb.net/?retryWrites=true&w=majority&appName=swip"
client = MongoClient(MONGO_URI)
db = client["todoDB"]
task_collection = db["tasks"]

@app.route("/")
def home():
    tasks = list(task_collection.find())
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    task = request.form.get("task")
    if task:
        task_collection.insert_one({"task": task, "status": "Pending"})
    return redirect(url_for("home"))

@app.route("/update/<task_id>")
def update_task(task_id):
    task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "Completed"}})
    return redirect(url_for("home"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    task_collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
