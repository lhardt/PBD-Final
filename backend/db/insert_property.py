from datetime import datetime

def insert_property(db, property_details):
    try:
        collection = db['PropertyListing']
        result = collection.insert_one(property_details)
        print(f"Property inserted with _id: {result.inserted_id}")
        
        # Add a log entry to the CrawlerLog collection
        log_entry = {
            "timestamp": datetime.utcnow(),
            "property_id": result.inserted_id,
            "status": "success",
            "message": "Property successfully added to the database."
        }
        add_crawler_log(db, log_entry)
    except Exception as e:
        print(f"Failed to insert property data: {e}")
        # Log the failure
        log_entry = {
            "timestamp": datetime.utcnow(),
            "property_id": None,
            "status": "failure",
            "message": str(e)
        }
        add_crawler_log(db, log_entry)

def add_crawler_log(db, log_entry):
    try:
        log_collection = db['CrawlerLog']
        log_collection.insert_one(log_entry)
        print(f"Crawler log added with status: {log_entry['status']}")
    except Exception as e:
        print(f"Failed to add crawler log: {e}")

