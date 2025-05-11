from datetime import datetime
from flask import jsonify
from daos.delivery_dao import DeliveryDAO
from db import Session

class Delivery:
    @staticmethod
    def create(body):
        session = Session()
        delivery_id = body['id']
        delivery = session.query(DeliveryDAO).filter(DeliveryDAO.id == int(body['id'])).first()
        if delivery:
            session.close()
            return jsonify({'message': f'Delivery with id {delivery_id} already exists'}), 403
        else:
            delivery = DeliveryDAO(
                body['id'],
                body['customer_id'],
                body['provider_id'],
                body['package_id'],
                datetime.now(),
                body.get('status', 'pending')
            )
            session.add(delivery)
            session.commit()
            session.refresh(delivery)
            session.close()
        return jsonify({'delivery_id': delivery.id}), 200

    @staticmethod
    def get(d_id):
        session = Session()
        delivery = session.query(DeliveryDAO).filter(DeliveryDAO.id == int(d_id)).first()
        if delivery:
            text_out = {
                "delivery_id": delivery.id,
                "customer_id": delivery.customer_id,
                "provider_id": delivery.provider_id,
                "package_id": delivery.package_id,
                "delivery_time": delivery.delivery_time,
                "status": delivery.status
            }
            session.close()
            return jsonify(text_out), 200
        else:
            session.close()
            return jsonify({'message': f'No delivery with id {d_id}'}), 404

    @staticmethod
    def update_status(d_id, status):
        session = Session()
        delivery = session.query(DeliveryDAO).filter(DeliveryDAO.id == int(d_id)).first()
        if delivery:
            delivery.status = status
            session.commit()
            session.close()
            return jsonify({'message': 'Delivery status updated'}), 200
        else:
            session.close()
            return jsonify({'message': f'No delivery with id {d_id}'}), 404