from flask import Flask, render_template, jsonify, send_from_directory,request
from datetime import datetime
import queue
from flask import Response
import json
import time

app = Flask(__name__)

SAVE_DIR = "static/images"

# default settings for spots
total_spots = 10
available_spots = 10

latest_entry = {
    "plateNumber": "",
    "confidence": 0,
    "imageUrl": "",
    "entry_time": "",
    "exit_time": "",
    "cost": 0.0
}

@app.route("/api/update-available", methods=["POST"])
def update_available():
    global available_spots

    data = request.json
    available_spots = data.get("availableSpots", available_spots)

    return jsonify({"status": "success"})

@app.route("/")
def index():
    return render_template("dashboard.html")

subscribers = []

@app.route("/stream")
def stream():
    def event_stream():
        q = queue.Queue()
        subscribers.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            subscribers.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")

def notify_clients():
    data = {
        "totalSpots": total_spots,
        "availableSpots": available_spots,
        "occupiedSpots": total_spots - available_spots,
        "lastEntry": latest_entry
    }
    for q in subscribers:
        q.put(data)

@app.route("/api/parking-data")
def parking_data_api():
    occupied_spots = total_spots - available_spots
    return jsonify({
        "totalSpots": total_spots,
        "availableSpots": available_spots,
        "occupiedSpots": occupied_spots,
        "lastEntry": latest_entry
    })

@app.route("/static/images/<filename>")
def serve_image(filename):
    return send_from_directory(SAVE_DIR, filename)


@app.route("/api/update-entry", methods=["POST"])
def update_entry():
    global available_spots,latest_entry
    data = request.json
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "exit" not in data:
        latest_entry = {
            "plateNumber": data.get("plateNumber", ""),
            "confidence": data.get("confidence", 0),
            "imageUrl": data.get("imageUrl", ""),
            "entry_time": data.get("entry_time", now),
            "exit_time": "",
            "cost": 0.0
        }
        if available_spots > 0:
            available_spots -= 1
    else:
        latest_entry["exit_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        latest_entry["confidence"] = data.get("confidence", 0.0)
        latest_entry["imageUrl"] = data.get("imageUrl", "")
        latest_entry["cost"] = data.get("cost", 0.0)
        if available_spots < total_spots:
            available_spots += 1

    notify_clients()
    return jsonify({"status": "success"})

def run_dashboard():
    app.run(debug=False, use_reloader=False)

if __name__ == "__main__":
    run_dashboard()
