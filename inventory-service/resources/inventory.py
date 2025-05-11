from datetime import datetime
from flask import jsonify
from daos.inventory_dao import InventoryDAO
from db import Session

class Inventory:
    @staticmethod
    def create(body):
        session = Session()
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == body['product_id']).first()
        if inventory:
            session.close()
            return jsonify({'message': f'Product {body["product_id"]} already exists'}), 403
        else:
            inventory = InventoryDAO(
                body['product_id'],
                body['stock'],
                datetime.now()
            )
            session.add(inventory)
            session.commit()
            session.refresh(inventory)
            session.close()
            return jsonify({'product_id': inventory.product_id}), 200

    @staticmethod
    def get(product_id):
        session = Session()
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
        if inventory:
            response = {
                "product_id": inventory.product_id,
                "stock": inventory.stock,
                "last_updated": inventory.last_updated.isoformat()
            }
            session.close()
            return jsonify(response), 200
        else:
            session.close()
            return jsonify({'message': f'Product {product_id} not found'}), 404

    @staticmethod
    def update_stock(product_id, new_stock):
        session = Session()
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
        if inventory:
            inventory.stock = new_stock
            inventory.last_updated = datetime.now()
            session.commit()
            session.close()
            return jsonify({'message': 'Inventory stock updated'}), 200
        else:
            session.close()
            return jsonify({'message': f'Product {product_id} not found'}), 404