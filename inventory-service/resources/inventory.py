from datetime import datetime
from flask import jsonify
from daos.inventory_dao import InventoryDAO
from db import Session

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
                last_updated=datetime.now()
            )
            session.add(new_inventory)
            session.commit()
            session.refresh(new_inventory)
            session.close()
            return jsonify({'product_id': new_inventory.product_id}), 200

    @staticmethod
    def get(product_id):
        session = Session()
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
        if inventory:
            response = {
                "product_id": inventory.product_id,
                "quantity": inventory.quantity,
                "location": inventory.location,
                "last_updated": inventory.last_updated
            }
            session.close()
            return jsonify(response), 200
        else:
            session.close()
            return jsonify({'message': f'Product {product_id} not found'}), 404

    @staticmethod
    def update(product_id, quantity, location):
        session = Session()
        inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
        if inventory:
            inventory.quantity = quantity
            inventory.location = location
           