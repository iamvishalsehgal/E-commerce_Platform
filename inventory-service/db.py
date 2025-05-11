import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# Use environment variable for DB connection
if 'DB_URL' in os.environ:
    db_url = os.environ['DB_URL']
else:
    db_url = 'sqlite:///inventory.db'  # Local fallback

engine = create_engine(db_url)
if not database_exists(engine.url):
    create_database(engine.url)

Session = sessionmaker(bind=engine)
Base = declarative_base()