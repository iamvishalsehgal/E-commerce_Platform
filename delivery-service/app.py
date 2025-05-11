import os
from flask import Flask, request
from db import Base, engine
from resources.delivery import Delivery

app = Flask(__name__)
app.config["DEBUG"] = True
Base.metadata.create_all(engine)

@app.route("/deliveries/register", methods=["POST"])
def register_delivery():
    req_data = request.get_json()
    return Delivery.create(req_data)

@app.route("/deliveries/<delivery_id>", methods=["GET"])
def get_delivery(delivery_id):
    return Delivery.get(delivery_id)

@app.route("/deliveries/<delivery_id>/status", methods=["PUT"])
def update_delivery_status(delivery_id):
    status = request.args.get('status')
    return Delivery.update_status(delivery_id, status)

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5004)), host='0.0.0.0', debug=True)