import os
from flask import Flask, request
from db import Base, engine
from resources.order import Order

app = Flask(__name__)
app.config["DEBUG"] = True
Base.metadata.create_all(engine)

@app.route("/orders/register", methods=["POST"])
def register_order():
    req_data = request.get_json()
    return Order.create(req_data)

@app.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    return Order.get(int(order_id))

@app.route("/orders/<order_id>", methods=["PUT"])
def update_order_status(order_id):
    status = request.args.get('status')
    return Order.update(int(order_id), status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5004)), debug=False) 