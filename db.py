from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models_base import BaseMixin
from settings import DB_CONNECT_STR

base = declarative_base(cls=BaseMixin)
engine = create_engine(DB_CONNECT_STR)
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
