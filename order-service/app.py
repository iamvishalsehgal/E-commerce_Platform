import os
from flask import Flask, request
from flask_cors import CORS
from db import Base, engine
from resources.order import Order

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app) 
Base.metadata.create_all(engine)

@app.route("/order/create", methods=["POST"])
def create_order():
    req_data = request.get_json()
    return Order.create(req_data)

@app.route("/order/status/<int:order_id>", methods=["GET"])
def get_order_status(order_id):
    return Order.get(order_id)

@app.route("/order/cancel/<int:order_id>", methods=["PUT"])
def cancel_order(order_id):
    return Order.update_status(order_id, "cancelled")

@app.route("/order/validate/<int:order_id>", methods=["PUT"])
def validate_order(order_id):
    return Order.update_status(order_id, "validated")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5004)), debug=False)