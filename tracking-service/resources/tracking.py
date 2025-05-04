from datetime import datetime

from flask import jsonify

# from constant import STATUS_CREATED
from daos.tracking_dao import TrackingDAO
from db import Session

class Tracking:
    @staticmethod
    def create(body):
        session = Session()
        t_id = body['id']
        tracking = session.query(TrackingDAO).filter(TrackingDAO.id == int(body['id'])).first()
        if tracking:
            session.close()
            return jsonify({'message': f'There is already tracking with id {t_id}'}), 403
        else:
            tracking = TrackingDAO(body['id'], body['latitude'], body['longitude'], datetime.now())
            session.add(tracking)
            session.commit()
            session.refresh(tracking)
            session.close()
        return jsonify({'tracking_id': tracking.id}), 200

    @staticmethod
    def get(t_id):
        session = Session()
        # https://docs.sqlalchemy.org/en/14/orm/query.html
        # https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_using_query.htm
        tracking = session.query(TrackingDAO).filter(TrackingDAO.id == int(t_id)).first()

        if tracking:
            text_out = {
                "tracking_id": tracking.id,
                "latitude": tracking.latitude,
                "longitude": tracking.longitude,
                "update_time": tracking.update_time
            }
            session.close()
            return jsonify(text_out), 200
        else:
            session.close()
            return jsonify({'message': f'There is no tracking with id {t_id}'}), 404

    @staticmethod
    def put(t_id, latitude, longitude):
        session = Session()
        tracking = session.query(TrackingDAO).filter(TrackingDAO.id == int(t_id)).first()

        if tracking:
            tracking.latitude = latitude
            tracking.longitude = longitude
            tracking.update_time = datetime.now()
            session.commit()
            session.close()
            return jsonify({'message': 'Tracking info updated'}), 200
        else:
            session.close()
            return jsonify({'message': f'There is no tracking with id {t_id}'}), 404