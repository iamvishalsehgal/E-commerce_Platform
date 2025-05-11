from datetime import datetime
from flask import jsonify, request
from google.cloud import pubsub_v1
from daos.order_dao import OrderDAO
from db import Session


publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("de2024-435420", "order-events")

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
            
            # Publish creation event
            publisher.publish(topic_path, f"OrderCreated:{order_id}".encode("utf-8"))
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
                order.status = new_status
                session.commit()
                
                # Publish status change event
                event_type = "OrderValidated" if new_status == "validated" else "OrderCancelled"
                publisher.publish(topic_path, f"{event_type}:{o_id}".encode("utf-8"))
                return jsonify({'status': new_status}), 200
            return jsonify({'error': 'Order not found'}), 404
        except Exception as e:
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
                
                order.status = new_status
                session.commit()
                
                # Publish delivery event
                event_map = {
                    "shipped": "OrderShipped",
                    "out_for_delivery": "OrderOutForDelivery",
                    "delivered": "OrderDelivered"
                }
                publisher.publish(
                    topic_path, 
                    f"{event_map[new_status]}:{order_id}".encode("utf-8")
                )
                return jsonify({"status": new_status}), 200
            return jsonify({"error": "Order not found"}), 404
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()