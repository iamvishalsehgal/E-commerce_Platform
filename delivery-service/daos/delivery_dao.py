from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship, backref
from db import Base

class DeliveryDAO(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String)
    provider_id = Column(String)
    package_id = Column(String)
    delivery_time = Column(String)  # Use String for BigQuery compatibility
    status = Column(String)
    def __init__(self, id, customer_id, provider_id, package_id, delivery_time, status="pending"):
        self.id = id
        self.customer_id = customer_id
        self.provider_id = provider_id
        self.package_id = package_id
        self.delivery_time = delivery_time
        self.status = status