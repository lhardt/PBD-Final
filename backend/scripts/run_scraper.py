import sys
sys.path.append('..')
sys.path.append('../..')

import aiohttp
import asyncio
from db.connection import get_db_client
from db.insert_property import insert_property
from scraping.extract_property import extract_property_details

async def process_reference(session, db, ref):
    url = f'https://www.auxiliadorapredial.com.br/imovel/venda/{ref}'
    property_details = await extract_property_details(session, url)
    if property_details:
        insert_property(db, property_details)

async def main():
    # Read references from file
    with open('../../scraping/property_references.txt', 'r') as file:
        refs = [line.strip().replace("ref:", "").strip() for line in file.readlines()]

    # Connect to MongoDB
    client = get_db_client()
    if not client:
        print("Failed to connect to the database.")
        return
    db = client['ImoveisDB']


    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(100*60)) as session:
        tasks = [process_reference(session, db, ref) for ref in refs]
        await asyncio.gather(*tasks)

    client.close()

# Run the async main function
asyncio.run(main())