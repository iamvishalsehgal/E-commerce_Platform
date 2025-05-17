from sqlalchemy import Column, String, Integer, TIMESTAMP
from db import Base
from sqlalchemy import TIMESTAMP

class InventoryDAO(Base):
    __tablename__ = 'inventory'
    __table_args__ = {
        'bigquery_dataset': 'group2_inventorydb',  # Match your dataset
        'bigquery_project': 'de2024-435420'        # Your project ID
    }

    product_id = Column(String(50), primary_key=True)
    quantity = Column(Integer)
    location = Column(String(50))
    last_updated = Column(TIMESTAMP(timezone=True))

    def __init__(self, product_id, quantity, location, last_updated):
        self.product_id = product_id
        self.quantity = quantity
        self.location = location
        self.last_updated = last_updated