from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.orm import relationship, backref
from db import Base

class InventoryDAO(Base):
    __tablename__ = 'inventory'
    product_id = Column(String, primary_key=True)  # Unique product identifier
    quantity = Column(Integer)
    location = Column(String)
    last_updated = Column(TIMESTAMP)

    def __init__(self, product_id, quantity, location, last_updated):
        self.product_id = product_id
        self.quantity = quantity
        self.location = location
        self.last_updated = last_updated