from datetime import datetime, timezone
import json
import os
from flask import jsonify, request
from google.cloud import pubsub_v1
from daos.inventory_dao import InventoryDAO
from db import Session
import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

PROJECT_ID = "de2024-435420"
DATASET_ID = "group2_inventorydb"
TABLE_ID = "inventory"

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
                last_updated=datetime.now(timezone.utc).astimezone(timezone.utc)
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
                inventory.last_updated = datetime.now(timezone.utc).astimezone(timezone.utc)
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
    def deduct_inventory(product_id, deduct_quantity, order_id=None):
        """
        Deduct inventory in a transactional way with proper error handling and event publishing.
        No timestamp validation or time-based restrictions.
        """
        bq_client = None
        try:
            if deduct_quantity <= 0:
                logger.error(f"Invalid deduction quantity: {deduct_quantity}")
                return False, 0

            bq_client = bigquery.Client()
            table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

            # Use transaction for atomic operation
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("product_id", "STRING", product_id),
                    bigquery.ScalarQueryParameter("deduct_quantity", "INT64", deduct_quantity)
                ]
            )

            # Atomic update operation - no timestamp checks
            update_query = f"""
                UPDATE `{table_ref}`
                SET quantity = GREATEST(quantity - @deduct_quantity, 0),
                    last_updated = CURRENT_TIMESTAMP()
                WHERE product_id = @product_id
            """
            update_job = bq_client.query(update_query, job_config=job_config)
            update_job.result()

            if update_job.num_dml_affected_rows == 0:
                logger.warning(f"No inventory affected - product {product_id} not found or quantity zero")
                Inventory._publish_deduction_event(
                    "DeductionFailed",
                    product_id,
                    deduct_quantity,
                    0,
                    order_id,
                    "no_inventory_found"
                )
                return False, 0

            # Get updated quantity
            get_query = f"""
                SELECT quantity 
                FROM `{table_ref}`
                WHERE product_id = @product_id
            """
            get_job = bq_client.query(get_query, job_config=job_config)
            result = next(get_job.result())
            remaining_quantity = result.quantity

            # Publish success event - no time constraints
            Inventory._publish_deduction_event(
                "InventoryDeducted",
                product_id,
                deduct_quantity,
                remaining_quantity,
                order_id
            )

            logger.info(f"Deducted {deduct_quantity} from {product_id}. Remaining: {remaining_quantity}")
            return True, remaining_quantity

        except Exception as e:
            logger.error(f"Deduction failed for {product_id}: {str(e)}", exc_info=True)
            Inventory._publish_deduction_event(
                "DeductionFailed",
                product_id,
                deduct_quantity,
                0,
                order_id,
                str(e)
            )
            return False, 0
        finally:
            if bq_client:
                try:
                    bq_client.close()
                except Exception as e:
                    logger.warning(f"Error closing BigQuery client: {str(e)}")

    @staticmethod
    def _publish_deduction_event(event_type, product_id, deducted, remaining, order_id=None, error_msg=None):
        """Helper method to publish inventory deduction events - without time filters"""
        event_data = {
            "event": event_type,
            "product_id": product_id,
            "deducted_quantity": deducted,
            "remaining_quantity": remaining,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "order_id": order_id,
            "immediate_processing": True  # Flag to indicate this should be processed immediately
        }
        
        if error_msg:
            event_data["error"] = error_msg
        
        try:
            publisher.publish(inventory_topic_path, json.dumps(event_data).encode('utf-8'))
            logger.debug(f"Published {event_type} event for {product_id}")
        except Exception as e:
            logger.error(f"Failed to publish {event_type} event: {str(e)}")