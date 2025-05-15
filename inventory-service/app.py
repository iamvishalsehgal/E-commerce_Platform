import os
import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from db import Base, engine, Session
from resources.inventory import Inventory
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
INVENTORY_SUBSCRIPTION = os.environ.get('INVENTORY_SUBSCRIPTION', 'inventory-order-events-sub')

# Publisher client for inventory events
publisher = pubsub_v1.PublisherClient()
inventory_topic_path = publisher.topic_path(PROJECT_ID, INVENTORY_EVENTS_TOPIC)

# REST API Endpoints
@app.route("/inventory", methods=["POST"])
def add_product():
    return Inventory.create(request.get_json())

@app.route("/inventory/<product_id>", methods=["GET"])
def check_stock(product_id):
    return Inventory.get(product_id)

@app.route("/inventory/<product_id>", methods=["PUT"])
def update_stock(product_id):
    return Inventory.update(
        product_id,
        request.json.get("quantity"),
        request.json.get("location", "")
    )

@app.route("/inventory/<product_id>/deduct", methods=["POST"])
def deduct_inventory(product_id):
    return Inventory.deduct(product_id)

# Event handling logic
def process_order_event(message):
    try:
        event_data = message.data.decode('utf-8')
        logger.info(f"Received order event: {event_data}")
        event_json = json.loads(event_data)
        event_type = event_json.get("event")
        
        if event_type == "OrderValidated":
            product_id = event_json.get("product_id")
            quantity = event_json.get("quantity")
            order_id = event_json.get("order_id")
            if product_id and quantity:
                logger.info(f"Attempting to deduct {quantity} of product {product_id} for order {order_id}")
                success = Inventory.deduct_inventory(product_id, quantity)
                if success:
                    logger.info(f"Successfully deducted inventory for order {order_id}")
                else:
                    logger.warning(f"Failed to deduct inventory for order {order_id}")
        message.ack()
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        message.nack()

def start_subscriber():
    """Start the Pub/Sub subscriber in a separate thread"""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, INVENTORY_SUBSCRIPTION)
    
    logger.info(f"Starting subscriber on {subscription_path}")
    
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=process_order_event
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
    
    logging.info("Starting inventory service...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))