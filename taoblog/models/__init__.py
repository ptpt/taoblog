__all__ = ['Base', 'Session', 'ModelError', 'bind_engine']

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()
Session = scoped_session(sessionmaker())


class ModelError(Exception):
    def __init__(self, message, model=None):
        Exception.__init__(self, message)
        self.model = model


def bind_engine(database, echo=False):
    engine = create_engine(database, echo=echo)
    Base.metadata.bind = engine
    Session.bind = engine
