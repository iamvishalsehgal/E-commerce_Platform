import os
import json
import base64
import requests
import logging
from google.cloud import pubsub_v1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pub/Sub configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'de2024-435420')
ORDER_EVENTS_TOPIC = os.environ.get('ORDER_EVENTS_TOPIC', 'order-events')
publisher = pubsub_v1.PublisherClient()
order_topic_path = publisher.topic_path(PROJECT_ID, ORDER_EVENTS_TOPIC)

def order_validator(event, context):
    try:
        # Get message data directly from event['data']
        encoded_data = event.get('data', '')
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_data = json.loads(decoded_bytes)
        
        logger.info(f"Processing order event: {decoded_data}")
        
        event_type = decoded_data.get("event")
        
        # Only process OrderCreated events
        if event_type == "OrderCreated":
            order_id = decoded_data.get("order_id")
            product_id = decoded_data.get("product_id")
            quantity = decoded_data.get("quantity")
            
            if not all([order_id, product_id, quantity]):
                raise ValueError("Missing required order data")
            
            # Get inventory service URL from environment variables
            inventory_service_url = os.environ.get("INVENTORY_SERVICE_URL", 
                                                  "https://inventory-service-1070510678521.us-central1.run.app")
            
            # First check if inventory is available
            check_url = f"{inventory_service_url}/inventory/{product_id}"
            check_response = requests.get(check_url)
            
            if check_response.status_code != 200:
                logger.error(f"Failed to check inventory: {check_response.text}")
                publish_validation_failed(order_id, product_id, "inventory_check_failed")
                return {"status": "error", "message": "Failed to check inventory"}
            
            inventory_data = check_response.json()
            available_quantity = inventory_data.get("quantity", 0)
            
            if available_quantity < quantity:
                logger.warning(f"Insufficient inventory for order {order_id}: requested {quantity}, available {available_quantity}")
                publish_validation_failed(order_id, product_id, "insufficient_inventory")
                return {"status": "error", "message": "Insufficient inventory"}
            
            # Try to reserve the inventory
            logger.info(f"Attempting to reserve inventory for order {order_id}")
            
            # We won't directly deduct inventory here, just verify and initiate a reservation
            # The actual choreography flow will handle the actual inventory deduction later
            
            # Publish validation success event
            validation_event = json.dumps({
                "event": "OrderValidated",
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "validation_status": "success"
            })
            
            publisher.publish(order_topic_path, validation_event.encode('utf-8'))
            logger.info(f"Order {order_id} validated successfully")
            
            return {
                "status": "success", 
                "order_id": order_id,
                "product_id": product_id,
                "message": "Order validated successfully"
            }
            
        else:
            logger.info(f"Ignoring non-OrderCreated event: {event_type}")
            return {"status": "skipped", "message": f"Not processing {event_type} events"}
            
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        
        # Try to extract order details for error reporting
        order_id = None
        product_id = None
        try:
            order_id = decoded_data.get("order_id")
            product_id = decoded_data.get("product_id")
            
            # Publish validation failed event if we have order ID
            if order_id:
                publish_validation_failed(order_id, product_id, str(e))
        except:
            pass
            
        return {"status": "error", "message": str(e)}

def publish_validation_failed(order_id, product_id, reason):
    """Publish order validation failed event to Pub/Sub"""
    try:
        if not order_id:
            return
            
        validation_failed_event = json.dumps({
            "event": "OrderValidationFailed",
            "order_id": order_id,
            "product_id": product_id,
            "reason": reason
        })
        
        publisher.publish(order_topic_path, validation_failed_event.encode('utf-8'))
        logger.info(f"Published validation failed event for order {order_id}")
    except Exception as e:
        logger.error(f"Failed to publish validation failed event: {e}")