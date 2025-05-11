import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1
from threading import Thread
from db import Base, engine
from resources.inventory import Inventory
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)
Base.metadata.create_all(engine)

# Configure Pub/Sub subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    os.environ.get("PROJECT_ID", "de2024-435420"),
    "order-events-sub"
)

# Create a thread-safe session factory
Session = scoped_session(sessionmaker(bind=engine))

def handle_order_event(message):
    """Process order validation events to deduct inventory"""
    try:
        event_data = message.data.decode()
        if "OrderValidated" in event_data:
            _, product_id, quantity = event_data.split(":")
            session = Session()
            
            # Deduct inventory
            inventory = session.query(Inventory).filter_by(product_id=product_id).first()
            if inventory:
                inventory.quantity -= int(quantity)
                session.commit()
                print(f"Deducted {quantity} units from {product_id}")
            
            message.ack()
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        message.nack()
    finally:
        Session.remove()

# Start Pub/Sub listener in background thread
Thread(target=lambda: subscriber.subscribe(subscription_path, callback=handle_order_event)).start()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))