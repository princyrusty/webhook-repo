from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

MONGO_URI = mongodb+srv://webhookuser:<db_password>@githook.5hhcs1j.mongodb.net/?appName=GitHook
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
    action = ""

    if event == "push":
        action = "PUSH"
        author = data["pusher"]["name"]
        from_branch = data["ref"].split("/")[-1]
        to_branch = from_branch
        request_id = data.get("after")

    elif event == "pull_request":
        pr = data["pull_request"]
        author = pr["user"]["login"]
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]
        request_id = pr["id"]

        if data["action"] == "closed" and pr["merged"]:
            action = "MERGE"
        else:
            action = "PULL_REQUEST"

    else:
        return jsonify({"msg": "ignored"}), 200

    doc = {
        "request_id": str(request_id),
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
        e["timestamp"] = e["timestamp"].isoformat()
    return jsonify(events)

if __name__ == "__main__":
    app.run(port=5000)
