from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory inventory
inventory = {1: {"stock": 10}}

@app.route("/inventory/check/<int:product_id>", methods=["GET"])
def check_inventory(product_id):
    available = inventory.get(product_id, {}).get("stock", 0) > 0
    return jsonify({"product_id": product_id, "available": available})

@app.route("/inventory/add", methods=["POST"])
def add_inventory():
    data = request.json
    product_id = data["product_id"]
    inventory[product_id] = {"stock": data["stock"]}
    return jsonify({"product_id": product_id, "status": "added"})

@app.route("/inventory/update/<int:product_id>", methods=["PUT"])
def update_inventory(product_id):
    data = request.json
    if product_id in inventory:
        inventory[product_id]["stock"] = data["quantity"]
        return jsonify({"product_id": product_id, "new_stock": data["quantity"]})
    return jsonify({"error": "Product not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)