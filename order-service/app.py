import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import Base, engine
from resources.order import Order

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
Base.metadata.create_all(engine)

# CORE: Order Management
@app.route("/orders", methods=["POST"])
def create_order():
    """Create new order"""
    return Order.create(request.get_json())

@app.route("/orders/<order_id>", methods=["GET"])
def get_status(order_id):
    """Get order status"""
    return Order.get(order_id)

@app.route("/orders/<order_id>/cancel", methods=["PUT"])
def cancel_order(order_id):
    """Cancel an order"""
    return Order.update_status(order_id, "cancelled")

@app.route("/orders/<order_id>/validate", methods=["PUT"])
def validate_order(order_id):
    """Validate order for processing"""
    return Order.update_status(order_id, "validated")

@app.route("/orders/<order_id>/delivery", methods=["PUT"])
def update_delivery(order_id):
    """Update delivery status"""
    return Order.update_delivery_status(
        order_id,
        request.args.get("status")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5004)))