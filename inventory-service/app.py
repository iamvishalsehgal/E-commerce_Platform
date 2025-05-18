import os
import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from resources.inventory import Inventory
import logging
from db import Base, engine

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
INVENTORY_SUBSCRIPTION = "inventory-order-events-sub"
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
    quantity = request.json.get("quantity", 1)
    success, remaining = Inventory.deduct_inventory(product_id, quantity)  # Unpack tuple
    if success:
        return jsonify({
            "status": "success", 
            "message": f"Deducted {quantity}. Remaining: {remaining}"
        }), 200
    else:
        return jsonify({
            "status": "failure",
            "message": "Failed to deduct inventory"
        }), 400

def process_order_event(message):
    """Process Pub/Sub messages from order-events topic."""
    logger.info(f"[PUBSUB] Received message ID: {message.message_id}")
    
    try:
        # Decode and log raw message
        raw_data = message.data.decode('utf-8')
        logger.debug(f"[DEBUG] Raw message data: {raw_data}")
        
        # Parse JSON payload
        event = json.loads(raw_data)
        logger.debug(f"[DEBUG] Parsed event:\n{json.dumps(event, indent=2)}")

        # Validate event type
        if event.get('event') != 'OrderValidated':
            logger.warning(f"Ignoring non-OrderValidated event: {event.get('event')}")
            message.ack()
            return

        # Validate required fields
        required_fields = ['product_id', 'quantity']
        missing_fields = [field for field in required_fields if field not in event]
        if missing_fields:
            logger.error(f"Missing required fields {missing_fields} in event: {event}")
            message.nack()
            return

        # Extract parameters
        product_id = event['product_id']
        quantity = int(event['quantity'])
        order_id = event.get('order_id', 'unknown')
        
        logger.info(f"Processing deduction - Product: {product_id}, Qty: {quantity}, Order: {order_id}")

        # Execute deduction
        success, remaining = Inventory.deduct_inventory(product_id, quantity, order_id)
        
        if success:
            logger.info(f"Deduction successful! Remaining quantity: {remaining}")
            message.ack()
        else:
            logger.error("Deduction failed!")
            message.nack()

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        logger.error(f"Invalid message content: {raw_data}")
        message.nack()
        
    except ValueError as e:
        logger.error(f"Invalid quantity format: {str(e)}")
        message.nack()
        
    except KeyError as e:
        logger.error(f"Missing key in event data: {str(e)}")
        message.nack()
        
    except Exception as e:
        logger.error(f"Unexpected error processing message: {str(e)}", exc_info=True)
        message.nack()

def start_subscriber():
    try:
        logger.info("[SUBSCRIBER-STARTED] Starting Pub/Sub subscriber thread...")
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(PROJECT_ID, INVENTORY_SUBSCRIPTION)
        logger.info(f"[SUBSCRIBER-ACTIVE] Subscribing to: {subscription_path}")
        
        streaming_pull_future = subscriber.subscribe(
            subscription_path, callback=process_order_event
        )
        logger.info("🟢 Subscriber is running...")
        streaming_pull_future.result()  # Block indefinitely

    except Exception as e:
        logger.error(f"[SUBSCRIBER-FAILED] Subscriber thread crashed: {str(e)}", exc_info=True)
        raise  # Ensure the error is visible in logs

if __name__ == '__main__':
    # Start the subscriber in a background thread
    subscriber_thread = threading.Thread(target=start_subscriber)
    subscriber_thread.daemon = True
    subscriber_thread.start()
    
    logging.info("Starting inventory service...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))