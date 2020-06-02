from sqlalchemy import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def get_base():
    return Base


def create_new_session(db_engine: engine):
    return sessionmaker(bind=db_engine)()
