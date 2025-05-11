import os
from flask import Flask
from flask_cors import CORS
from db import Base, engine
from resources.inventory import Inventory

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
Base.metadata.create_all(engine)

@app.route("/inventory/check/<product_id>", methods=["GET"])
def check_inventory(product_id):
    return Inventory.check_availability(product_id)

@app.route("/inventory/add", methods=["POST"])
def add_inventory():
    return Inventory.add_inventory()

@app.route("/inventory/update/<product_id>", methods=["PUT"])
def update_inventory(product_id):
    return Inventory.update_stock(product_id)

@app.route("/inventory/<product_id>", methods=["GET"])
def get_inventory_details(product_id):
    return Inventory.get(product_id)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)