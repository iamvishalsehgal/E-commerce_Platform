from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship, backref
from db import Base

class InventoryDAO(Base):
    __tablename__ = 'inventory'
    product_id = Column(String(50), primary_key=True)
    stock = Column(Integer)
    last_updated = Column(DateTime)

    def __init__(self, product_id, stock, last_updated):
        self.product_id = product_id
        self.stock = stock
        self.last_updated = last_updated