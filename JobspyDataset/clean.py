from pymongo import MongoClient
from datetime import datetime
import re

client = MongoClient("mongodb://localhost:27017")
db = client["jobspy"]

raw_col = db["raw_jobs"]
clean_col = db["clean_jobs"]

clean_col.delete_many({})

def parse_salary(s):
    if not isinstance(s, str):
        return None, None

    nums = re.findall(r"\d+", s.replace(",", ""))
    nums = [int(n) for n in nums]

    if len(nums) == 1:
        return nums[0], nums[0]
    elif len(nums) >= 2:
        return min(nums), max(nums)
    return None, None

# CLEANING LOOP
inserted = 0
seen = set()  

for job in raw_col.find():
    title = job.get("title")
    company = job.get("company")
    description = job.get("description")

    if not title or not company or not description:
        continue

    # NORMALIZATION
    job["title"] = title.strip().lower()
    job["company"] = company.strip().lower()
    job["location"] = job.get("location", "").strip().lower()

    job["description"] = re.sub(r"\s+", " ", description)

    # DATE NORMALIZATION
    if "date_posted" in job:
        job["date_posted_clean"] = str(job["date_posted"])

    if "salary" in job:
        job["salary_min"], job["salary_max"] = parse_salary(job["salary"])
    else:
        job["salary_min"] = None
        job["salary_max"] = None

    job["cleaned_at"] = datetime.utcnow()

    # DEDUPLICATION
    dedup_key = (
        job.get("title"),
        job.get("company"),
        job.get("location"),
        job.get("country"),
    )

    if dedup_key in seen:
        continue

    seen.add(dedup_key)

    clean_col.insert_one(job)
    inserted += 1

