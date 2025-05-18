import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

if 'DB_URL' in os.environ:
    db_url = os.getenv("DB_URL", "bigquery://de2024-435420/group2_orderdb")
else:
    db_url = 'sqlite:///order.db' 

engine = create_engine(db_url)
if not database_exists(engine.url):
    create_database(engine.url)

Session = sessionmaker(bind=engine)
Base = declarative_base()