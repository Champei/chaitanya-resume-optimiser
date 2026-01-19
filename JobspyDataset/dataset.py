from jobspy import scrape_jobs
from pymongo import MongoClient
from datetime import datetime
import time
SITE_NAMES = ["indeed", "linkedin", "google", "zip_recruiter"]

SEARCH_TERMS = [
    "software engineer",
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "backend developer",
    "frontend developer",
]

COUNTRIES = {
    "USA": ["New York, NY", "San Francisco, CA", "Austin, TX"],
    "UK": ["London", "Manchester"],
    "IN": ["Bangalore", "Hyderabad", "Delhi"],
    "CA": ["Toronto", "Vancouver"],
    "AU": ["Sydney", "Melbourne"],
    "DE": ["Berlin", "Munich"],
}

RESULTS_WANTED = 25
HOURS_OLD = 72
SLEEP_SECONDS = 5
# MONGODB
client = MongoClient("mongodb://localhost:27017")
db = client["jobspy"]
raw_jobs = db["raw_jobs"]

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
                job["scraped_at"] = datetime.utcnow()

            raw_jobs.insert_many(records)
            print(f" Inserted {len(records)} jobs")

            time.sleep(SLEEP_SECONDS)

