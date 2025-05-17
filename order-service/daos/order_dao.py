from sqlalchemy import Column, String, Integer, DateTime, Numeric
from sqlalchemy.orm import relationship, backref
from db import Base
from sqlalchemy import TIMESTAMP

class OrderDAO(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(50))
    product_id = Column(String(50))
    quantity = Column(Integer)
    order_date = Column(TIMESTAMP(timezone=True))
    status = Column(String(20))

    def __init__(self, id, customer_id, product_id, quantity, order_date, status="Pending"):
        self.id = id
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.order_date = order_date
        self.status = status