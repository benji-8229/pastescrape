from helpers import Helpers
from scraping import Scraping
from typing import Optional
from json import loads, dumps

from fastapi import APIRouter, HTTPException
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
collection = db[config["db_collection_name"]]


@router.put("/insert_or_replace/", summary="Inserts the paste with id {id} into the database, replacing it and updating it if it already exists")
async def db_insert(id: str) -> dict:
    """Inserts the paste with id {id} into the database, replacing it and updating it if it already exists

    Args:\n
        id (str): The id of the paste to insert or replace

    Raises:\n
        HTTPException 400: Paste ID provided was not valid\n
        HTTPException 422: Paste ID was valid but could not be scraped\n
        HTTPException 504: Connection to database dead\n

    Returns:\n
        dict: The paste added to the database
    """
    id = id.strip()

    if not Scraping.is_valid_id(id):
        raise HTTPException(status_code=400, detail=f"Paste ID {id} is not valid")
    
    data = Scraping.scrape_paste_content(id, use_cache=False)
    if not data:
        raise HTTPException(status_code=422, detail=f"Paste ID {id} could not be scraped")
    
    Helpers.cache_append(id)
    
    # make sure we're not ending up with duplicates in our DB
    try:
        if collection.find_one({"id": id}):
            collection.find_one_and_replace({"id": id}, data)
        else:
            collection.insert_one(data)
    except ConnectionFailure:
        raise HTTPException(status_code=504, detail=f"Database request timed out")

    # sometimes an ObjectID instance ends up in our dict but it's not serializable
    if "_id" in data:
        data["_id"] = str(data["_id"])
    
    return data


@router.put("/insert_latest", summary="Insert the latest public pastes into the database")
async def db_insert_latest():
    """Insert the latest public pastes into the database

    Raises:\n
        HTTPException 504: Connection to database dead\n

    Returns:\n
        pastes_added (int): The amount of pastes added to the db\n
        ids_added (list of tuples): List of tuples for every added paste where element 0 is the paste ID and element 1 is the _id (db id)\n
    """
    ids = Scraping.scrape_ids()
    added_ids = []
    
    z = 0

    for id in ids:
        try:
            if collection.find_one({"id": id}):
                continue
            
            data = Scraping.scrape_paste_content(id)
            if data:
                collection.insert_one(data)
                added_ids.append((id, str(data["_id"])))
                z += 1
        except ConnectionFailure:
            # we wouldn't generally want to cancel the entire request based on one timeout, but pymongo 
            # seems to be pretty good about reconnection attempts, so if it fails it really failed
            raise HTTPException(status_code=504, detail=f"Database request timed out")
        
        
    return {"pastes_added": z, "ids_added": added_ids}


@router.get("/fetch", summary="Fetch archived paste from database if it exists")
async def db_fetch(id: str) -> dict:
    """Fetch archived paste from database if it exists

    Args:\n
        id (str): ID of paste to return

    Raises:\n
        HTTPException 400: Requested ID was not in valid format\n
        HTTPException 404: Requested ID was valid but not in database\n
        HTTPException 504: Connection to database dead\n

    Returns:\n
        dict: JSON data of archived paste
    """

    # we don't check for 404 incase we archived the paste before it was deleted
    if not Scraping.is_valid_id(id, check_404=False):
        raise HTTPException(status_code=400, detail=f"Paste ID {id} is not valid")
    
    try:
        data = collection.find_one({"id": id})
        if data:
            data["_id"] = str(data["_id"])
            return data
        else:
            raise HTTPException(status_code=404, detail=f"Paste ID {id} not found in DB")
    except ConnectionFailure:
        raise HTTPException(status_code=504, detail=f"Database request timed out")


@router.get("/fetch_many", summary=f"Retrieve {config['fetch_many_lim']} pastes from the database, with easy recursion to retrieve the entire database", response_model=None)
async def db_fetch_many(filter: Optional[str] = "null", ind: Optional[int] = 0, limit: Optional[int] = config["fetch_many_lim"]):
    try:
        if filter != "null":
            print(filter)
            filter = loads(filter)
            data = collection.find(filter).sort("_id", -1)[ind:]
        else:
            data = collection.find().sort("_id", -1)[ind:]
    except ConnectionFailure:
        raise HTTPException(status_code=504, detail=f"Database request timed out")
            
            
    if not ind == 0:
        ind /= limit
        
    ret_list = []
    
    for x in data:
        if "_id" in x:
            x["_id"] = str(x["_id"])
        ret_list.append(x)
        
        if len(ret_list) >= limit:
            break

    return {"cur_list": ret_list, "next_request": f"http://localhost:8000/api/db/fetch_many?filter={dumps(filter) if filter != 'null' else 'null'}&limit={limit}&ind={int((ind+1) * limit)}"}


@router.get("/status", summary="Check if connection to database is alive")
async def db_up():
    """Check if connection to database is alive

    Raises:\n
        HTTPException 503: Database connection dead\n

    Returns:\n
        alive (bool): Database connection status
    """
    try:
        client.admin.command("ping")
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail=f"Database connection dead")
    
    return {"alive": True}
