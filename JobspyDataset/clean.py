from pymongo import MongoClient
import re

# MONGODB
client = MongoClient("mongodb://localhost:27017")
db = client["jobspy"]

raw_col = db["raw_jobs"]
clean_col = db["clean_jobs"]

clean_col.delete_many({})

inserted = 0
seen = set()

for job in raw_col.find():
    title = job.get("title")
    company = job.get("company")
    description = job.get("description")

    # VALIDATION
    if not isinstance(title, str):
        continue
    if not isinstance(company, str):
        continue
    if not isinstance(description, str):
        continue

    # NORMALIZATION
    job["title"] = title.strip().lower()
    job["company"] = company.strip().lower()

    location = job.get("location")
    job["location"] = location.strip().lower() if isinstance(location, str) else ""

    job["description"] = re.sub(r"\s+", " ", description)

    # DEDUPLICATION
    dedup_key = (
        job["title"],
        job["company"],
        job["location"],
        job.get("country"),
    )

    if dedup_key in seen:
        continue

    seen.add(dedup_key)
    # INSERT
    clean_col.insert_one(job)
    inserted += 1

print(f" Cleaning complete")
