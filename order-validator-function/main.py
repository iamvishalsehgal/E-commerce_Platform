# order-validator-function/main.py
import os
import json
import base64
import requests
import logging
from google.cloud import pubsub_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pub/Sub client
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.environ.get("PROJECT_ID", "de2024-435420")
ORDER_EVENTS_TOPIC = os.environ.get("ORDER_EVENTS_TOPIC", "order-events")
order_topic_path = publisher.topic_path(PROJECT_ID, ORDER_EVENTS_TOPIC)

# Inventory service URL
INVENTORY_SERVICE_URL = os.environ.get(
    "INVENTORY_SERVICE_URL",
    "https://inventory-service-1070510678521.us-central1.run.app"
)

def order_validator(event, context):
    """Cloud Function triggered by Pub/Sub messages from order-events."""
    try:
        # Decode Pub/Sub message
        event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
        logger.info(f"Processing order event: {event_data}")

        event_type = event_data.get("event")

        # Only process OrderCreated events
        if event_type != "OrderCreated":
            logger.info(f"Ignoring non-OrderCreated event: {event_type}")
            return {"status": "skipped", "message": f"Ignored {event_type} event"}

        # Extract order details
        order_id = event_data.get("order_id")
        product_id = event_data.get("product_id")
        quantity = event_data.get("quantity")

        if not all([order_id, product_id, quantity]):
            raise ValueError("Missing required order data")

        # Step 1: Check inventory availability
        check_url = f"{INVENTORY_SERVICE_URL}/inventory/{product_id}"
        check_response = requests.get(check_url)

        if check_response.status_code != 200:
            logger.error(f"Inventory check failed: {check_response.text}")
            raise Exception("Inventory service unavailable")

        inventory_data = check_response.json()
        available_quantity = inventory_data.get("quantity", 0)

        # Step 2: Validate inventory
        if available_quantity < quantity:
            logger.warning(f"Insufficient inventory: Requested {quantity}, Available {available_quantity}")
            publish_validation_failed(order_id, product_id, "insufficient_inventory")
            return {
                "status": "failed",
                "message": f"Insufficient inventory for product {product_id}"
            }

        # Step 3: Reserve inventory (via event-driven choreography)
        reserve_response = requests.post(
            f"{INVENTORY_SERVICE_URL}/inventory/{product_id}/reserve",
            json={"quantity": quantity, "order_id": order_id}
        )

        if not reserve_response.ok:
            logger.error(f"Inventory reservation failed: {reserve_response.text}")
            publish_validation_failed(order_id, product_id, "reservation_failed")
            return {"status": "error", "message": "Inventory reservation failed"}

        # Step 4: Publish validation success
        validation_event = {
            "event": "OrderValidated",
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "validation_status": "success"
        }
        publisher.publish(order_topic_path, json.dumps(validation_event).encode("utf-8"))
        
        logger.info(f"Order {order_id} validated successfully")
        return {
            "status": "success",
            "order_id": order_id,
            "product_id": product_id,
            "message": "Order validated"
        }

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}", exc_info=True)
        publish_validation_failed(order_id, product_id, str(e))
        return {"status": "error", "message": str(e)}

def publish_validation_failed(order_id, product_id, reason):
    """Helper to publish validation failure events"""
    try:
        event_data = {
            "event": "OrderValidationFailed",
            "order_id": order_id,
            "product_id": product_id,
            "reason": reason
        }
        publisher.publish(order_topic_path, json.dumps(event_data).encode("utf-8"))
        logger.info(f"Published validation failed event for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to publish failure event: {str(e)}")