import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use environment variable for DB connection
db_url = os.getenv("DB_URL", "bigquery://de2024-435420/group2_inventorydb")
engine = create_engine(db_url, echo=True)

# Session factory
Session = sessionmaker(bind=engine)

# Base class for models
Base = declarative_base()