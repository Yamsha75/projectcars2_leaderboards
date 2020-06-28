from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models_base import BaseMixin
from settings import DB_CONNECT_STR

Base = declarative_base(cls=BaseMixin)
Engine = create_engine(DB_CONNECT_STR)
Session = sessionmaker(bind=Engine, autocommit=False, autoflush=False)()
