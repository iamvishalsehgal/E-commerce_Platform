import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use environment variable for DB connection
db_url = os.environ["DB_URL"]  # Remove default value
engine = create_engine(db_url)
Base = declarative_base()
Session = sessionmaker(bind=engine)