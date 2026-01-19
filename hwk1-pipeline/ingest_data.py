#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

zones_dtypes= {
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64"}


parse_dates = [
    "lpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for reading CSV')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    """Ingest green taxi trips data into PostgreSQL database."""
    gt_filepath = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'

    zones_filepath = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    green_taxi_df = pd.read_parquet(
    path=gt_filepath)

    zones= pd.read_csv(
    zones_filepath,
    dtype= zones_dtypes
    )

    # 1️⃣ Take the first chunk
    first_chunk = green_taxi_df.iloc[:chunksize]

    # 2️⃣ Create table + insert first rows
    first_chunk.to_sql(
        name=target_table,
        con=engine,
        if_exists="replace",
        index=False
    )

    # 3️⃣ Append the rest
    for i in range(chunksize, len(green_taxi_df), chunksize):
        green_taxi_df.iloc[i:i+chunksize].to_sql(
        name=target_table,
        con=engine,
        if_exists="append",
        index=False)

    zones.to_sql(
        name="zones",
        con=engine,
        if_exists="replace",
        index=False
    )
    

if __name__ == '__main__':
        run()