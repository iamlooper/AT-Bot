import os
from collections import OrderedDict
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import (
    MYSQL_HOST, 
    MYSQL_PORT, 
    MYSQL_USER, 
    MYSQL_PASSWORD, 
    MYSQL_DATABASE
)

_Base = declarative_base()
_Engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
_DBSession = sessionmaker(bind=_Engine)

@contextmanager
def create_dbsession(**kw):
    session = _DBSession(**kw)
    try:
        yield session
    finally:
        session.close()

class Saved(_Base):
    __tablename__ = "amt_bot"
    ID = Column(String(255), primary_key=True, nullable=False)
    FULL_NAME = Column(String(255), nullable=False)
    LATEST_VERSION = Column(String(255))
    BUILD_TYPE = Column(String(255))
    BUILD_VERSION = Column(String(255))
    BUILD_DATE = Column(String(255))
    BUILD_CHANGELOG = Column(String(255))
    FILE_MD5 = Column(String(255))
    FILE_SHA1 = Column(String(255))
    FILE_SHA256 = Column(String(255))
    DESCRIPTION = Column(String(255))     
    DOWNLOAD_TEXT = Column(String(255)) 
    DOWNLOAD_LINK = Column(String(255)) 
    ALT_DOWNLOAD_LINK = Column(String(255))     
    FILE_SIZE = Column(String(255))

    def get_kv(self):
        # Returns a key-value dictionary of the Saved object's attributes
        return OrderedDict([
            (k, getattr(self, k))
            for k in (
                "ID FULL_NAME LATEST_VERSION BUILD_TYPE BUILD_VERSION "
                "BUILD_DATE BUILD_CHANGELOG FILE_MD5 FILE_SHA1 FILE_SHA256 "
                "DESCRIPTION DOWNLOAD_TEXT DOWNLOAD_LINK ALT_DOWNLOAD_LINK FILE_SIZE"
            ).split()
        ])

    @classmethod
    def get_saved_info(cls, name):
        """
        Queries and returns the stored data in the database based on the name
        Returns None if the data doesn't exist
        :param name: Name of the CheckUpdate subclass
        :return: Saved object or None
        """
        with create_dbsession() as session:
            return session.query(cls).filter(cls.ID == name).one()

_Base.metadata.create_all(_Engine)
