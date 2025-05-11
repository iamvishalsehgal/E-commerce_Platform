import os
from flask import Flask, request
from db import Base, engine
from resources.inventory import Inventory

app = Flask(__name__)
app.config["DEBUG"] = True
Base.metadata.create_all(engine)

@app.route("/inventory/register", methods=["POST"])
def register_inventory():
    req_data = request.get_json()
    return Inventory.create(req_data)

@app.route("/inventory/<product_id>", methods=["GET"])
def get_inventory(product_id):
    return Inventory.get(product_id)

@app.route("/inventory/<product_id>", methods=["PUT"])
def update_inventory_stock(product_id):
    new_stock = request.args.get('stock')
    return Inventory.update_stock(product_id, int(new_stock))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5005))
    app.run(host='0.0.0.0', port=port, debug=False)