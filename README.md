# Databricks Job Tracker

## Overview

A Python script that collects current job postings from Databricks and uploads them into a PostgreSQL database.

---

## Requirements

- Python 3.10 or Docker
- PostgreSQL database
- Required environment variables:

```env
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

---

## Running as a Docker Container

1. **Create an `.env` file** with your PostgreSQL connection details as shown above.

2. **Build the Docker image:**

```bash
docker build -t databricks-job-tracker .
```

3. **Run the container:**

```bash
docker run --rm --env-file .env databricks-job-tracker
```

---

## Running Without Docker

If you prefer not to use Docker:

1. Install required Python dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure your environment variables are set.

3. Run the script:

```bash
python fetch_data.py
```

---

## Notes

- Make sure your database allows incoming connections from the machine or container running this script.
- This script uses environment variables for configuration to avoid hardcoding sensitive information.
