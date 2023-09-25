from helpers import Helpers
from scraping import Scraping
from fastapi import APIRouter

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure


config = Helpers.config_get()
router = APIRouter(
    prefix="/api/db",
    tags=["db"]
)

client = MongoClient(config["db_uri"])
db = client[config["db_name"]]
archive = db[config["db_collection_name"]]


def db_conn():
    try:
        client.admin.command("ping")
    except ConnectionFailure:
        return False
    
    return True


@router.get("/insert/{id}")
async def db_insert(id):
    id = id.strip()

    if Scraping.is_valid_id(id) == False:
        return {"response": 422, "data": []}
    
    data = Scraping.scrape_paste_content(id, use_cache=False)
    if not data:
        return {"response": 422, "data": []}
    
    # make sure we're not ending up with duplicates in our DB
    if archive.find_one({"id": id}):
        replace = True
        archive.find_one_and_replace({"id": id}, data)
    else:
        archive.insert_one(data)
        replace = False
        
    # sometimes an ObjectID instance ends up in our dict but it's not serializable
    if "_id" in data:
        data["_id"] = str(data["_id"])
        
    return {"response": 200, "replaced": replace, "data": [data]}

@router.get("/status")
async def db_up():
    try:
        client.admin.command("ping")
    except ConnectionFailure:
        return {"response": 503}
    
    return {"response": 200}