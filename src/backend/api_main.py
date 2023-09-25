from scraping import Scraping
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api_db


app = FastAPI()
origins = [
    "http://localhost:3000",
    "localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(api_db.router)


@app.get("/api/id_valid/{id}")
async def id_valid(id):
    return {"response:": Scraping.is_valid_id(id)}