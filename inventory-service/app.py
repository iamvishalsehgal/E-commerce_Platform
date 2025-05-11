import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import Base, engine
from resources.inventory import Inventory

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
Base.metadata.create_all(engine)

# CORE: Product Inventory Management
@app.route("/inventory", methods=["POST"])
def add_product():
    """Add product to inventory"""
    return Inventory.create(request.get_json())

@app.route("/inventory/<product_id>", methods=["GET"])
def check_stock(product_id):
    """Check current stock levels"""
    return Inventory.get(product_id)

@app.route("/inventory/<product_id>", methods=["PUT"])
def update_stock(product_id):
    """Update stock quantity"""
    return Inventory.update(
        product_id,
        request.json.get("quantity"),
        request.json.get("location", "")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))