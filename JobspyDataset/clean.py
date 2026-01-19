import sqlite3
import pandas as pd
import re

DB_NAME = "jobs.db"
RAW_TABLE = "raw_jobs"
CLEAN_TABLE = "clean_jobs"

conn = sqlite3.connect(DB_NAME)

df = pd.read_sql(f"SELECT * FROM {RAW_TABLE}", conn)
print(f"Loaded {len(df)} raw rows")

if df.empty:
    print("No data found")
    conn.close()
    exit()

critical_cols = ["title", "company", "description"]
existing_critical = [c for c in critical_cols if c in df.columns]
df = df.dropna(subset=existing_critical)

for col in ["title", "company", "location"]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
        )

df["description"] = (
    df["description"]
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
)

if "date_posted" in df.columns:
    df["date_posted"] = pd.to_datetime(
        df["date_posted"], errors="coerce"
    ).dt.date.astype(str)

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

if "salary" in df.columns:
    df["salary_min"], df["salary_max"] = zip(
        *df["salary"].apply(parse_salary)
    )
else:
    df["salary_min"] = None
    df["salary_max"] = None

dedup_keys = [c for c in ["title", "company", "location"] if c in df.columns]
df = df.drop_duplicates(subset=dedup_keys)

print(f"After cleaning: {len(df)} rows")

df.to_sql(
    CLEAN_TABLE,
    conn,
    if_exists="replace",  
    index=False
)

conn.close()
print(" Clean data saved ")
