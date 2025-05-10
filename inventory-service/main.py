import json
from flask import Flask

# Use the existing Flask app
app = Flask(__name__)

inventory = {1: {"stock": 10}}  # In-memory inventory

def handle_order_event(event, context):
    """Triggered by Pub/Sub when an order is created."""
    event_data = event['data'].decode('utf-8')
    if "OrderCreated" in event_data:
        product_id = int(event_data.split(":")[1])  # Extract product ID
        print(f"Order created for product {product_id}")

        # Deduct inventory stock
        if inventory.get(product_id, {}).get("stock", 0) > 0:
            inventory[product_id]["stock"] -= 1
            print(f"Inventory updated: {inventory}")
        else:
            print(f"Product {product_id} is out of stock!")