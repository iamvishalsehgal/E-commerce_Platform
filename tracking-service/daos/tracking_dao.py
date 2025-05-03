from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship, backref

from db import Base

class TrackingDAO(Base):
    __tablename__ = 'tracking'
    id = Column(Integer, primary_key=True)  # Auto generated primary key
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    update_time = Column(DateTime)

    def __init__(self, id, latitude, longitude, update_time):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.update_time = update_time