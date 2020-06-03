from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from settings import DB_CONNECT_STR

Base = declarative_base()
Engine = create_engine(DB_CONNECT_STR)


def get_base():
    return Base


def get_engine():
    return Engine


def get_session():
    return sessionmaker(bind=Engine, autocommit=False, autoflush=False)()
