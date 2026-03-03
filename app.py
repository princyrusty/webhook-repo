from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# 🔹 MongoDB Connection (Your Provided URI)
MONGO_URI = "mongodb+srv://webhookuser:webhookpass123@githook.5hhcs1j.mongodb.net/github_webhooks?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client.github_webhooks
collection = db.events


def format_timestamp(timestamp_str):
    """
    Convert GitHub UTC timestamp to required format:
    01 April 2021 - 09:30 PM UTC
    """
    dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%d %B %Y - %I:%M %p UTC")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    # ================= PUSH EVENT =================
    if event_type == "push":
        if data.get("head_commit") is None:
            return jsonify({"message": "No head commit"}), 200

        author = data["pusher"]["name"]
        to_branch = data["ref"].split("/")[-1]
        timestamp = format_timestamp(data["head_commit"]["timestamp"])

        document = {
            "request_id": data["head_commit"]["id"],
            "author": author,
            "action": "PUSH",
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        collection.insert_one(document)

    # ================= PULL REQUEST EVENT =================
    elif event_type == "pull_request":
        pr = data["pull_request"]

        # Detect MERGE
        if data["action"] == "closed" and pr["merged"]:
            action_type = "MERGE"
        else:
            action_type = "PULL_REQUEST"

        document = {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": action_type,
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": format_timestamp(pr["created_at"])
        }

        collection.insert_one(document)

    return jsonify({"status": "success"}), 200


@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(events)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
