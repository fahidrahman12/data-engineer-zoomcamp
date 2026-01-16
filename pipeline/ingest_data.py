#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm

# -----------------------------
# Config
# -----------------------------
YEAR = 2021
MONTH = 1

PG_USER = "root"
PG_PASSWORD = "root"
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "ny_taxi"

TABLE_NAME = "yellow_taxi_data"
CHUNK_SIZE = 100_000

PREFIX = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/"

DTYPE = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

PARSE_DATES = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


# -----------------------------
# Helpers
# -----------------------------
def make_url(year: int, month: int) -> str:
    return f"{PREFIX}yellow_tripdata_{year}-{month:02d}.csv.gz"


def make_engine():
    url = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    return create_engine(url)


def ingest_csv_to_postgres(csv_url: str, table_name: str, engine, chunk_size: int) -> None:
    reader = pd.read_csv(
        csv_url,
        dtype=DTYPE,
        parse_dates=PARSE_DATES,
        iterator=True,
        chunksize=chunk_size,
    )

    first_chunk = True

    for chunk in tqdm(reader, desc="Ingesting", unit="chunk"):
        if first_chunk:
            # Create table with correct schema (no data yet)
            chunk.head(0).to_sql(table_name, con=engine, if_exists="replace", index=False)
            first_chunk = False

        # Append chunk
        chunk.to_sql(table_name, con=engine, if_exists="append", index=False)


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    engine = make_engine()
    csv_url = make_url(YEAR, MONTH)
    ingest_csv_to_postgres(csv_url, TABLE_NAME, engine, CHUNK_SIZE)
    print(f"Done: loaded {csv_url} into {PG_DATABASE}.{TABLE_NAME}")
