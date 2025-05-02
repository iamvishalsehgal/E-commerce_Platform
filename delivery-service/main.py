from google.cloud import pubsub_v1

def handle_delivery_request(event, context):
    """Triggered by Pub/Sub topic."""
    event_data = event['data'].decode('utf-8')
    order_id = event_data.split(":")[1]
    print(f"Processing delivery for order {order_id}")
    return {"status": "Delivery requested"}

def generate_shipping_label(event, context):
    """Generate shipping label for an order."""
    event_data = event['data'].decode('utf-8')
    order_id = event_data.split(":")[1]
    print(f"Label generated for order {order_id}")
    return {"label_id": f"label_{order_id}"}