import json
import requests
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import execute_values


def fetch_databricks_job_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def extract_unique_jobs(jobs):
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
                "id": internal_id,
                "title": job.get("title"),
                "locations": locations,
                "department": department,
                "updated_at": job.get("updated_at"),
                "collected_at": timestamp,
            }
        )

    return filtered


def connect_db():
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
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id BIGINT PRIMARY KEY,
                title TEXT NOT NULL,
                locations TEXT,
                department TEXT,
                updated_at TIMESTAMPTZ NOT NULL,
                collected_at TIMESTAMPTZ NOT NULL
            );
            """
        )
        conn.commit()


def upsert_jobs(conn, jobs):
    with conn.cursor() as cur:
        # Prepare data for batch insert
        records = [
            (
                job["id"],
                job["title"],
                job["locations"],
                job["department"],
                job["updated_at"],
                job["collected_at"],
            )
            for job in jobs
        ]

        # Upsert query: Insert or update on conflict of primary key
        sql = """
            INSERT INTO jobs (id, title, locations, department, updated_at, collected_at)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                locations = EXCLUDED.locations,
                department = EXCLUDED.department,
                updated_at = EXCLUDED.updated_at,
                collected_at = EXCLUDED.collected_at
        """

        execute_values(cur, sql, records)
        conn.commit()


def view_rows(conn, limit=10):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, title, locations, department, updated_at, collected_at
            FROM databricks_jobs
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
    url = "https://www.databricks.com/careers-assets/page-data/company/careers/open-positions/page-data.json"

    data = fetch_databricks_job_data(url)
    jobs = data["result"]["pageContext"]["data"]["allGreenhouseJob"]["nodes"]
    filtered_jobs = extract_unique_jobs(jobs)

    conn = connect_db()
    create_table(conn)
    upsert_jobs(conn, filtered_jobs)
    # view_rows(conn)
    conn.close()

    print(f"✅ Uploaded {len(filtered_jobs)} jobs to the database.")


if __name__ == "__main__":
    main()
