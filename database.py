import os
import hashlib
import time
from collections import OrderedDict
from contextlib import contextmanager
from config import DROPBOX_ACCESS_TOKEN

from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dropbox
from dropbox.exceptions import AuthError, ApiError
from dropbox.files import WriteMode

_Base = declarative_base()

_Engine = create_engine('sqlite:///at_bot_database.db')

_DBSession = sessionmaker(bind=_Engine)

DROPBOX_FILENAME = "/at_bot_database.db"
LOCAL_FILENAME = "at_bot_database.db"

@contextmanager
def create_dbsession(**kw):
    session = _DBSession(**kw)
    try:
        yield session
    finally:
        session.close()

class Saved(_Base):
    __tablename__ = "main_table"
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

def get_dropbox_file_hash(filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(4 * 1024 * 1024)  # Read in 4MB blocks
            if not chunk:
                break
            block_hash = hashlib.sha256(chunk).digest()
            hasher.update(block_hash)
    return hasher.hexdigest()

def upload_to_dropbox(dbx):
    with open(LOCAL_FILENAME, "rb") as f:
        try:
            dbx.files_upload(f.read(), DROPBOX_FILENAME, mode=WriteMode("overwrite"))
            print(f"Database uploaded to Dropbox: {DROPBOX_FILENAME}")
        except ApiError as e:
            print(f"Error uploading database to Dropbox: {str(e)}")

def download_from_dropbox(dbx):
    try:
        _, response = dbx.files_download(DROPBOX_FILENAME)
        with open(LOCAL_FILENAME, "wb") as f:
            f.write(response.content)
        print(f"Database downloaded from Dropbox: {DROPBOX_FILENAME}")
        return True
    except ApiError as e:
        print(f"Error downloading database from Dropbox: {str(e)}")
        return False

def sync_database():
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    except AuthError:
        print("Invalid access token. Please check your Dropbox access token.")
        return
    
    if not os.path.exists(LOCAL_FILENAME):
        if not download_from_dropbox(dbx):
            print("Creating new local database.")
            _Base.metadata.create_all(_Engine)
        return

    local_hash = get_dropbox_file_hash(LOCAL_FILENAME)
    try:
        metadata = dbx.files_get_metadata(DROPBOX_FILENAME)
        dropbox_hash = metadata.content_hash
    except ApiError as e:
        print(f"Error getting file metadata: {str(e)}")
        dropbox_hash = None

    if dropbox_hash is None or local_hash != dropbox_hash:
        upload_to_dropbox(dbx)

def periodic_sync(interval=300):  # Default interval: 5 minutes
    while True:
        sync_database()
        time.sleep(interval)

# Initialize database and start periodic sync
sync_database()
import threading
sync_thread = threading.Thread(target=periodic_sync, daemon=True)
sync_thread.start()