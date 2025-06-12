# databricks-job-tracker

## Purpose 
Python script that uploads current jobs offered at Databricks into sql db

### How To Run As Container
Create env file with following info
```
DB_HOST=**
DB_PORT=**
DB_NAME=**
DB_USER=**
DB_PASSWORD=***
```
Build Image
```bash
docker build -t db-job-tracker .
```

Run Container
```bash
docker run --rm --env-file .env db-job-tracker
```

If you do not want to use containers, you can just run file
```
python fetch_data.py
```



