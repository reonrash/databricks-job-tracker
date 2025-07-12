import json
import requests
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import execute_values


def fetch_databricks_job_data(url):
    """Fetch job data JSON from the given Databricks careers URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def extract_unique_jobs(jobs):
    """
    Filter unique jobs by internal ID and format job fields.

    Note: 'unique' here means within the current fetch only to avoid duplicates
    in this batch, but duplicates can still exist in the database.
    """
    seen_ids = set()
    filtered = []
    timestamp = datetime.utcnow().isoformat()

    for job in jobs:
        internal_id = job.get("internal_job_id")
        if internal_id in seen_ids:
            continue
        seen_ids.add(internal_id)

        locations = job.get("location", {}).get("name", "")
        departments = job.get("departments", [])
        department = departments[0]["name"] if departments else None

        filtered.append(
            {
                "job_id": internal_id,
                "title": job.get("title"),
                "locations": locations,
                "department": department,
                "updated_at": job.get("updated_at"),
                "collected_at": timestamp,
            }
        )

    return filtered


def connect_db():
    """Establish a connection to the PostgreSQL database using environment variables."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
    )
    return conn


def create_table(conn):
    """Create the jobs table in the database if it does not already exist."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                job_id BIGINT NOT NULL,
                title TEXT NOT NULL,
                locations TEXT,
                department TEXT,
                updated_at TIMESTAMPTZ NOT NULL,
                collected_at TIMESTAMPTZ NOT NULL
            );
            """
        )
        conn.commit()


def insert_jobs(conn, jobs):
    """Insert jobs into the database allowing duplicates."""
    with conn.cursor() as cur:
        records = [
            (
                job["job_id"],
                job["title"],
                job["locations"],
                job["department"],
                job["updated_at"],
                job["collected_at"],
            )
            for job in jobs
        ]

        sql = """
            INSERT INTO jobs (job_id, title, locations, department, updated_at, collected_at)
            VALUES %s
        """

        execute_values(cur, sql, records)
        conn.commit()


def view_rows(conn, limit=10):
    """Retrieve and print the latest job rows from the database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, job_id, title, locations, department, updated_at, collected_at
            FROM jobs
            ORDER BY collected_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        print(f"\n📦 First {limit} rows from database:")
        for row in rows:
            print(row)


def main():
    """Main execution flow: fetch, process, and upload Databricks job data."""
    url = "https://www.databricks.com/careers-assets/page-data/company/careers/open-positions/page-data.json"

    data = fetch_databricks_job_data(url)
    jobs = data["result"]["pageContext"]["data"]["allGreenhouseJob"]["nodes"]
    filtered_jobs = extract_unique_jobs(jobs)

    conn = connect_db()
    create_table(conn)
    insert_jobs(conn, filtered_jobs)
    # view_rows(conn)
    conn.close()

    print(f"✅ Inserted {len(filtered_jobs)} jobs into the database.")


if __name__ == "__main__":
    main()
