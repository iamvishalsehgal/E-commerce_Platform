import os
import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from db import Base, engine
from resources.order import Order
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
Base.metadata.create_all(engine)

# Pub/Sub configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'de2024-435420')
ORDER_EVENTS_TOPIC = os.environ.get('ORDER_EVENTS_TOPIC', 'order-events')
INVENTORY_EVENTS_TOPIC = os.environ.get('INVENTORY_EVENTS_TOPIC', 'inventory-events')
ORDER_SUBSCRIPTION = os.environ.get('ORDER_SUBSCRIPTION', 'order-inventory-events-sub')

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

# Event handling for inventory events
def process_inventory_event(message):
    """Process events from the inventory service"""
    try:
        event_data = json.loads(message.data.decode('utf-8'))
        logger.info(f"Received inventory event: {event_data}")
        
        event_type = event_data.get("event")
        
        # Handle different inventory event types
        if event_type == "InventoryReserved":
            order_id = event_data.get("order_id")
            product_id = event_data.get("product_id")
            
            logger.info(f"Inventory reserved for Order {order_id}, Product {product_id}")
            # Update order status based on this reservation event
            Order.update_status(order_id, "inventory_reserved")
            
        elif event_type == "ReservationFailed":
            order_id = event_data.get("order_id")
            reason = event_data.get("reason")
            
            logger.info(f"Inventory reservation failed for Order {order_id}: {reason}")
            # Update order status to reflect inventory problem
            Order.update_status(order_id, "inventory_failed")
            
        elif event_type == "InsufficientInventory":
            # This could affect multiple orders - we might get the order ID from the event
            # or we might need to look up orders that need this product
            logger.info(f"Insufficient inventory notification: {event_data}")
        
        # Acknowledge message
        message.ack()
        
    except Exception as e:
        logger.error(f"Error processing inventory event: {str(e)}")
        # Handle error, possibly nack the message
        message.nack()

def start_subscriber():
    """Start the Pub/Sub subscriber in a separate thread"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, ORDER_SUBSCRIPTION)
    
    logger.info(f"Starting subscriber for inventory events on {subscription_path}")
    
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=process_inventory_event
    )
    
    # Keep the thread alive
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
    except Exception as e:
        logger.error(f"Exception in subscriber thread: {str(e)}")

if __name__ == '__main__':
    # Start the subscriber in a background thread
    subscriber_thread = threading.Thread(target=start_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()
    
    logger.info("Starting order service...")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5004)))