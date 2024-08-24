# app/main.py
import sys
sys.path.append('.')
from db.connection import get_db_client

def main():
    client = get_db_client()
    if client:
        db = client['ImoveisDB']
        property_listing = db['PropertyListing']
        
        #for doc in property_listing.find():
        #   print(doc)

if __name__ == "__main__":
    main()
