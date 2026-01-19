import jobspy
from jobspy import scrape_jobs
import pandas as pd
import sqlite3
import time
from datetime import datetime

SEARCH_TERMS = [
    "data analyst",
    "data scientist",
    "machine learning engineer",
    "business analyst",
    "software engineer"
]

LOCATION = "United States"
SITE = ["indeed"]

RESULTS_PER_BATCH = 100
MAX_BATCHES = 20
SLEEP_SECONDS = 3

DB_NAME = "jobs.db"
RAW_TABLE = "raw_jobs"

conn = sqlite3.connect(DB_NAME)

for term in SEARCH_TERMS:
    print(f"\n Scraping: {term}")

    for batch in range(MAX_BATCHES):
        print(f"  Batch {batch + 1}")

        jobs_df = scrape_jobs(
            site_name=SITE,
            search_term=term,
            location=LOCATION,
            results_wanted=RESULTS_PER_BATCH,
            hours_old=24 * (batch + 1)
        )

        if jobs_df is None or jobs_df.empty:
            print(" No more jobs.")
            break

        df = jobs_df.copy()
        df["search_term"] = term
        df["scraped_at"] = datetime.utcnow().isoformat()

        df.to_sql(
            RAW_TABLE,
            conn,
            if_exists="append",
            index=False
        )

        print(f" Saved {len(df)} raw jobs")
        time.sleep(SLEEP_SECONDS)

conn.close()
print("\n Raw scraping completed.")
