from datetime import datetime, timezone
from flask import jsonify, request
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
                last_updated=datetime.now(timezone.utc)
            )
            session.add(new_inventory)
            session.commit()
            session.refresh(new_inventory)
            session.close()
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
                inventory.quantity = quantity
                inventory.location = location
                inventory.last_updated = datetime.now(timezone.utc)
                session.commit()
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
    def add_inventory():
        session = Session()
        try:
            data = request.get_json()
            inventory = InventoryDAO(
                product_id=data['product_id'],
                quantity=data['quantity'],
                location=data.get('location', 'warehouse'),
                last_updated=datetime.now(timezone.utc)
            )
            session.add(inventory)
            session.commit()
            return jsonify({"product_id": data['product_id'], "status": "added"}), 201
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()

    @staticmethod
    def update_stock(product_id):
        session = Session()
        try:
            data = request.get_json()
            inventory = session.query(InventoryDAO).filter(InventoryDAO.product_id == product_id).first()
            if inventory:
                inventory.quantity = data['quantity']
                inventory.last_updated = datetime.now(timezone.utc)
                session.commit()
                return jsonify({"product_id": product_id, "new_stock": data['quantity']}), 200
            return jsonify({"error": "Product not found"}), 404
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            session.close()