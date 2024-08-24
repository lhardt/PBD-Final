# scripts/run_db_setup.py
import sys
sys.path.append('..')

from db.connection import get_db_client
from db.create_db import create_imoveisdb_collections

def main():
    client = get_db_client()
    if client:
        create_imoveisdb_collections(client)

if __name__ == "__main__":
    main()
