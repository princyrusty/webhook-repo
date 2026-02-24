from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB Atlas URI
MONGO_URI = "mongodb+srv://webhookuser:<db_password>@githook.5hhcs1j.mongodb.net/?appName=GitHook"
client = MongoClient(MONGO_URI)
db = client["github_webhooks"]
collection = db["events"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def github_webhook():
    data = request.json
    event = request.headers.get("X-GitHub-Event")

    author = ""
    from_branch = ""
    to_branch = ""
    action = event.upper()

    # PUSH EVENT
    if event == "push":
        author = data["pusher"]["name"]
        from_branch = data["ref"].split("/")[-1]
        to_branch = from_branch

    # PULL REQUEST EVENT
    elif event == "pull_request":
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]

    # MERGE DETECTION
    if event == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
        action = "MERGE"

    doc = {
        "request_id": data.get("after", data.get("pull_request", {}).get("id", "")),
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(doc)
    return jsonify({"status": "stored"}), 200

@app.route("/api/events")
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)

if __name__ == "__main__":
    app.run()
