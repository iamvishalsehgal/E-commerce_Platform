from datetime import datetime, timezone
import json
import os
from flask import jsonify, request
from google.cloud import pubsub_v1
from daos.inventory_dao import InventoryDAO
from db import Session
import logging

logger = logging.getLogger(__name__)

# Pub/Sub configuration
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = os.environ.get('PROJECT_ID', 'de2024-435420')
INVENTORY_EVENTS_TOPIC = os.environ.get('INVENTORY_EVENTS_TOPIC', 'inventory-events')
inventory_topic_path = publisher.topic_path(PROJECT_ID, INVENTORY_EVENTS_TOPIC)

class Inventory:
    @staticmethod
    def create(body):
        session = Session()
        product_id = body['product_id']
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
        if inventory:
            session.close()
            return jsonify({'message': f'Product {product_id} already exists'}), 403
        else:
            new_inventory = InventoryDAO(
                product_id=product_id,
                quantity=body['quantity'],
                location=body['location'],
                last_updated=datetime.now(timezone.utc)
            )
            session.add(new_inventory)
            session.commit()
            session.refresh(new_inventory)
            session.close()
            
            # Publish inventory created event
            event_data = json.dumps({
                "event": "InventoryCreated",
                "product_id": product_id,
                "quantity": body['quantity'],
                "location": body['location']
            })
            publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
            
            return jsonify({'product_id': new_inventory.product_id}), 200

    @staticmethod
    def get(product_id):
        session = Session()
        try:
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            if inventory:
                return jsonify({
                    "product_id": inventory.product_id,
                    "quantity": inventory.quantity,
                    "location": inventory.location,
                    "last_updated": inventory.last_updated.isoformat()
                }), 200
            return jsonify({'message': f'Product {product_id} not found'}), 404
        finally:
            session.close()

    @staticmethod
    def update(product_id, quantity, location):
        session = Session()
        try:
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            if inventory:
                previous_quantity = inventory.quantity
                inventory.quantity = quantity
                inventory.location = location
                inventory.last_updated = datetime.now(timezone.utc)
                session.commit()
                
                # Publish inventory updated event
                event_data = json.dumps({
                    "event": "InventoryUpdated",
                    "product_id": product_id,
                    "previous_quantity": previous_quantity,
                    "new_quantity": quantity,
                    "location": location
                })
                publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
                
                return jsonify({"product_id": product_id, "new_quantity": quantity}), 200
            return jsonify({"error": "Product not found"}), 404
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()

    @staticmethod
    def check_availability(product_id):
        session = Session()
        try:
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            available = inventory.quantity > 0 if inventory else False
            return jsonify({"product_id": product_id, "available": available}), 200
        finally:
            session.close()

    @staticmethod
    def deduct(product_id):
        session = Session()
        try:
            data = request.get_json()
            deduct_quantity = data['quantity']
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            
            if inventory:
                if inventory.quantity < deduct_quantity:
                    # Publish insufficient inventory event
                    event_data = json.dumps({
                        "event": "InsufficientInventory",
                        "product_id": product_id,
                        "requested": deduct_quantity,
                        "available": inventory.quantity
                    })
                    publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
                    
                    return jsonify({"error": "Insufficient stock"}), 400
                    
                previous_quantity = inventory.quantity
                inventory.quantity -= deduct_quantity
                inventory.last_updated = datetime.now(timezone.utc)
                session.commit()
                
                # Publish inventory deducted event
                event_data = json.dumps({
                    "event": "InventoryDeducted",
                    "product_id": product_id,
                    "deducted": deduct_quantity,
                    "previous_quantity": previous_quantity,
                    "new_quantity": inventory.quantity
                })
                publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
                
                return jsonify({"product_id": product_id, "new_quantity": inventory.quantity}), 200
                
            return jsonify({"error": "Product not found"}), 404
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()

    @staticmethod
    def reserve_inventory(product_id, quantity, order_id):
        """Reserve inventory for an order without immediately deducting"""
        session = Session()
        try:
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            
            if not inventory:
                logger.warning(f"Product {product_id} not found for reservation")
                return False, "Product not found"
                
            if inventory.quantity < quantity:
                logger.warning(f"Insufficient stock for product {product_id}: requested {quantity}, available {inventory.quantity}")
                
                # Publish insufficient inventory event
                event_data = json.dumps({
                    "event": "ReservationFailed",
                    "product_id": product_id,
                    "order_id": order_id,
                    "requested": quantity,
                    "available": inventory.quantity,
                    "reason": "insufficient_stock"
                })
                publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
                
                return False, "Insufficient stock"
            
            # We don't actually reduce quantity yet, just publish a reservation event
            event_data = json.dumps({
                "event": "InventoryReserved",
                "product_id": product_id,
                "order_id": order_id,
                "quantity": quantity,
                "available": inventory.quantity
            })
            publisher.publish(inventory_topic_path, event_data.encode('utf-8'))
            
            return True, "Inventory reserved"
            
        except Exception as e:
            logger.error(f"Error reserving inventory: {str(e)}")
            return False, str(e)
        finally:
            session.close()