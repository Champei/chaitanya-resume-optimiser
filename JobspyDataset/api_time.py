from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
import time

app = FastAPI(title="JobSpy Job API")

client = MongoClient("mongodb://localhost:27017")
db = client["jobspy"]

COLLECTION = db["enriched_jobs"]  

class JobQuery(BaseModel):
    months: int = 1   
    limit: int = 50   

def objectid_from_days(days: int):
    seconds = days * 24 * 60 * 60
    ts = int(time.time()) - seconds
    return ObjectId.from_datetime(
        time.gmtime(ts)
    )

@app.post("/jobs")
def get_jobs(query: JobQuery):
    days = query.months * 30
    cutoff_id = objectid_from_days(days)

    cursor = (
        COLLECTION
        .find({"_id": {"$gte": cutoff_id}}, {"_id": 0})
        .limit(query.limit)
    )

    jobs = list(cursor)

    return {
        "months": query.months,
        "count": len(jobs),
        "jobs": jobs
    }
