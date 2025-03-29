from flask import Flask, render_template, request, redirect, url_for, g
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

MONGO_URI = "mongodb+srv://sojupingale:swip2004@swip.b9vgs6y.mongodb.net/?retryWrites=true&w=majority&appName=swip"

def get_db():
    """Ensure a fresh MongoDB connection per request."""
    if 'client' not in g:
        g.client = MongoClient(MONGO_URI)  # Create a new client per request
        g.db = g.client["todoDB"]
    return g.db["tasks"]

@app.route("/")
def home():
    task_collection = get_db()
    tasks = list(task_collection.find())
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    task_collection = get_db()
    task = request.form.get("task")
    if task:
        task_collection.insert_one({"task": task, "status": "Pending"})
    return redirect(url_for("home"))

@app.route("/update/<task_id>")
def update_task(task_id):
    task_collection = get_db()
    task_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": "Completed"}})
    return redirect(url_for("home"))

@app.route("/delete/<task_id>")
def delete_task(task_id):
    task_collection = get_db()
    task_collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for("home"))

@app.teardown_appcontext
def close_db(exception=None):
    """Close the MongoDB connection after request is complete."""
    client = g.pop('client', None)
    if client is not None:
        client.close()

if __name__ == "__main__":
    app.run(debug=True)
