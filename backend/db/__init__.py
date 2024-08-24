# db/__init__.py
from .connection import get_db_client
from .create_db import create_imoveisdb_collections
from .insert_property import insert_property