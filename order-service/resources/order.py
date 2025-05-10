from datetime import datetime
from flask import jsonify
from daos.order_dao import OrderDAO
from db import Session

class Order:
    @staticmethod
    def create(body):
        session = Session()
        order = session.query(OrderDAO).filter(OrderDAO.id == body['id']).first()
        if order:
            session.close()
            return jsonify({'message': f'Order {body["id"]} already exists'}), 403
        else:
            order = OrderDAO(
                body['id'],
                body['customer_id'],
                body['product_id'],
                body['quantity'],
                datetime.fromisoformat(body['order_date']),
                body.get('status', 'Pending')
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            session.close()
            return jsonify({'order_id': order.id}), 200

    @staticmethod
    def get(o_id):
        session = Session()
        order = session.query(OrderDAO).filter(OrderDAO.id == o_id).first()
        if order:
            response = {
                "id": order.id,
                "customer_id": order.customer_id,
                "product_id": order.product_id,
                "quantity": order.quantity,
                "order_date": order.order_date.isoformat(),
                "status": order.status
            }
            session.close()
            return jsonify(response), 200
        else:
            session.close()
            return jsonify({'message': f'Order {o_id} not found'}), 404

    @staticmethod
    def update(o_id, status):
        session = Session()
        order = session.query(OrderDAO).filter(OrderDAO.id == o_id).first()
        if order:
            order.status = status
            session.commit()
            session.close()
            return jsonify({'message': 'Order status updated'}), 200
        else:
            session.close()
            return jsonify({'message': f'Order {o_id} not found'}), 404