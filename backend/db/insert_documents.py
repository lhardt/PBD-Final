# db/insert_documents.py

def insert_property_listing(db, property_listing_data):
    """Insert a document into the PropertyListing collection."""
    property_listing = db['PropertyListing']
    result = property_listing.insert_one(property_listing_data)
    print(f"Inserted Property Listing with _id: {result.inserted_id}")

def insert_crawler_log(db, crawler_log_data):
    """Insert a document into the CrawlerLog collection."""
    crawler_log = db['CrawlerLog']
    result = crawler_log.insert_one(crawler_log_data)
    print(f"Inserted Crawler Log with _id: {result.inserted_id}")
