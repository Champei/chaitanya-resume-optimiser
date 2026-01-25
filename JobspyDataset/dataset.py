from jobspy import scrape_jobs
from pymongo import MongoClient
from datetime import date, datetime
import time

# CONFIG
SITE_NAMES = ["indeed", "linkedin", "zip_recruiter"]  

SEARCH_TERMS = [
    "software engineer",
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "backend developer",
    "frontend developer",
]

COUNTRIES = {
    "united states": ["New York, NY", "San Francisco, CA", "Austin, TX"],
    "united kingdom": ["London", "Manchester"],
    "india": ["Bangalore", "Hyderabad", "Delhi"],
    "canada": ["Toronto", "Vancouver"],
    "australia": ["Sydney", "Melbourne"],
    "germany": ["Berlin", "Munich"],
}

RESULTS_WANTED = 25
HOURS_OLD = 72
SLEEP_SECONDS = 5

# MONGODB

client = MongoClient("mongodb://localhost:27017")
db = client["jobspy"]
raw_jobs = db["raw_jobs"]

def remove_datetime(obj):
    if isinstance(obj, dict):
        return {
            k: remove_datetime(v)
            for k, v in obj.items()
            if not isinstance(v, (datetime, date))
        }
    elif isinstance(obj, list):
        return [remove_datetime(v) for v in obj]
    else:
        return obj
# SCRAPING LOOP
for country, locations in COUNTRIES.items():
    for location in locations:
        for term in SEARCH_TERMS:
            print(f"\n {country} |  {location} |  {term}")

            google_search_term = f"{term} jobs in {location}"

            jobs_df = scrape_jobs(
                site_name=SITE_NAMES,
                search_term=term,
                google_search_term=google_search_term,
                location=location,
                results_wanted=RESULTS_WANTED,
                hours_old=HOURS_OLD,
                country_indeed=country
            )

            if jobs_df is None or jobs_df.empty:
                print(" No jobs found")
                continue

            records = jobs_df.to_dict(orient="records")

            for job in records:
                job["search_term"] = term
                job["country"] = country
                job["location_query"] = location

            clean_records = [remove_datetime(job) for job in records]

            raw_jobs.insert_many(clean_records)
            print(f" Inserted {len(clean_records)} jobs")

            time.sleep(SLEEP_SECONDS)

print("\n Scraping completed successfully")
