from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory tracking
tracking = {}

@app.route("/tracking/register", methods=["POST"])
def register_tracking():
    data = request.json
    tracking_id = len(tracking) + 1
    tracking[tracking_id] = {"order_id": data["order_id"], "status": "registered"}
    return jsonify({"tracking_id": tracking_id})

@app.route("/tracking/status/<int:tracking_id>", methods=["GET"])
def get_tracking_status(tracking_id):
    return jsonify(tracking.get(tracking_id, {"error": "Not found"}))

@app.route("/tracking/update/<int:tracking_id>", methods=["PUT"])
def update_tracking_status(tracking_id):
    data = request.json
    if tracking_id in tracking:
        tracking[tracking_id]["status"] = data["status"]
        return jsonify({"status": "updated"})
    return jsonify({"error": "Tracking not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5003)