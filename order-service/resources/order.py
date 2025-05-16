from datetime import datetime
import json
import os
from flask import jsonify, request
from google.cloud import pubsub_v1
from daos.order_dao import OrderDAO
from db import Session
import logging

logger = logging.getLogger(__name__)

# Pub/Sub configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'de2024-435420')
ORDER_EVENTS_TOPIC = os.environ.get('ORDER_EVENTS_TOPIC', 'order-events')

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, ORDER_EVENTS_TOPIC)

class Order:
    @staticmethod
    def create(body):
        session = Session()
        try:
            # Generate sequential ID if not provided
            order_id = body.get('id', session.query(OrderDAO).count() + 1)
            
            order = OrderDAO(
                id=order_id,
                customer_id=body['customer_id'],
                product_id=body['product_id'],
                quantity=body['quantity'],
                order_date=datetime.fromisoformat(body['order_date']),
                status="created"
            )
            
            session.add(order)
            session.commit()
            
            # Publish detailed order created event with full order details
            event_data = json.dumps({
                "event": "OrderCreated",
                "order_id": order_id,
                "customer_id": body['customer_id'],
                "product_id": body['product_id'],
                "quantity": body['quantity'],
                "timestamp": datetime.now().isoformat()
            })
            publisher.publish(topic_path, event_data.encode('utf-8'))
            
            return jsonify({'order_id': order.id}), 200
            
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            session.close()

    @staticmethod
    def get(o_id):
        session = Session()
        try:
            order = session.query(OrderDAO).get(o_id)
            if order:
                return jsonify({
                    "id": order.id,
                    "status": order.status,
                    "customer_id": order.customer_id,
                    "product_id": order.product_id,
                    "quantity": order.quantity
                }), 200
            return jsonify({'message': 'Order not found'}), 404
        finally:
            session.close()

    @staticmethod
    def update_status(o_id, new_status):
        session = Session()
        try:
            order = session.query(OrderDAO).get(o_id)
            if order:
                logger.info(f"Updating order {o_id} status from {order.status} to {new_status}")
                previous_status = order.status
                order.status = new_status
                session.commit()
                
                # Log event data
                logger.info(f"Publishing OrderStatusChanged event for order {o_id}")
                
                # Publish detailed status change event
                event_data = json.dumps({
                    "event": "OrderStatusChanged",
                    "order_id": o_id,
                    "previous_status": previous_status,
                    "new_status": new_status,
                    "product_id": order.product_id,
                    "quantity": order.quantity,
                    "timestamp": datetime.now().isoformat()
                })
                publisher.publish(topic_path, event_data.encode('utf-8'))
                
                # Special case events
                if new_status == "validated":
                    logger.info(f"Publishing OrderValidated event for order {o_id}")
                    validated_event = json.dumps({
                        "event": "OrderValidated",
                        "order_id": o_id,
                        "product_id": order.product_id,
                        "quantity": order.quantity
                    })
                    publisher.publish(topic_path, validated_event.encode('utf-8'))
                elif new_status == "cancelled":
                    logger.info(f"Publishing OrderCancelled event for order {o_id}")
                    cancelled_event = json.dumps({
                        "event": "OrderCancelled",
                        "order_id": o_id,
                        "product_id": order.product_id,
                        "quantity": order.quantity
                    })
                    publisher.publish(topic_path, cancelled_event.encode('utf-8'))
                return jsonify({'status': new_status}), 200
            logger.warning(f"Order {o_id} not found for status update")
            return jsonify({'error': 'Order not found'}), 404
        except Exception as e:
            logger.error(f"Error updating order {o_id}: {str(e)}", exc_info=True)
            session.rollback()
            return jsonify({'error': str(e)}), 400
        finally:
            session.close()

    @staticmethod
    def update_delivery_status(order_id, new_status):
        session = Session()
        try:
            order = session.query(OrderDAO).get(order_id)
            if order:
                # Validate allowed status transitions
                valid_statuses = ["shipped", "out_for_delivery", "delivered"]
                if new_status not in valid_statuses:
                    return jsonify({"error": "Invalid delivery status"}), 400
                
                previous_status = order.status
                order.status = new_status
                session.commit()
                
                # Publish delivery event
                event_data = json.dumps({
                    "event": f"Order{new_status.capitalize()}",
                    "order_id": order_id,
                    "previous_status": previous_status,
                    "customer_id": order.customer_id,
                    "product_id": order.product_id,
                    "timestamp": datetime.now().isoformat()
                })
                publisher.publish(topic_path, event_data.encode('utf-8'))
                
                return jsonify({"status": new_status}), 200
            return jsonify({"error": "Order not found"}), 404
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()