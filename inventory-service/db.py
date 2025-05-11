import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# Use BigQuery in production
db_url = os.environ.get('DB_URL', 'sqlite:///inventory.db')
engine = create_engine(db_url)
if not database_exists(engine.url):
    create_database(engine.url)

Session = sessionmaker(bind=engine)
Base = declarative_base()