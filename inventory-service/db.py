import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


db_url = "bigquery://de2024-435420/group2_inventorydb"
engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)