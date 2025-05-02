from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1

app = Flask(__name__)
CORS(app)

# In-memory storage
orders = {}
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("adaass1", "order-events")

@app.route("/order/create", methods=["POST"])
def create_order():
    data = request.json
    order_id = len(orders) + 1
    orders[order_id] = {"user": data["user"], "status": "created"}
    publisher.publish(topic_path, f"OrderCreated:{order_id}".encode("utf-8"))
    return jsonify({"order_id": order_id})

@app.route("/order/status/<int:order_id>", methods=["GET"])
def get_order_status(order_id):
    return jsonify(orders.get(order_id, {"error": "Not found"}))

@app.route("/order/cancel/<int:order_id>", methods=["PUT"])
def cancel_order(order_id):
    if order_id in orders:
        orders[order_id]["status"] = "cancelled"
        return jsonify({"status": "cancelled"})
    return jsonify({"error": "Order not found"}), 404

@app.route("/order/validate/<int:order_id>", methods=["PUT"])
def validate_order(order_id):
    if order_id in orders:
        orders[order_id]["status"] = "validated"
        return jsonify({"status": "validated"})
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)