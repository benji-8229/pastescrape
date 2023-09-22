import logging, helpers
from scraping import Scraping

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

config = helpers.Helpers.validate_config()

client = MongoClient(config["db_uri"])
db = client.main
archive = db.archive

for id in Scraping.scrape_ids():
    data = Scraping.scrape_paste_content(id)
    if data:
        print(id)
        archive.insert_one(data)
        