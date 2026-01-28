# Ingests data into the DB

## csv_to_sql.py
- Directly converts a csv into a .sql file ready for ingestion and stores it in database/
- Usage:
```
python3 csv_to_sql.py data/refined/<filename>.csv
```

## dataset_cleaning/
- Set of scripts to clean datasets into .sql ingestible formats
- Stores the files in data/refined/
