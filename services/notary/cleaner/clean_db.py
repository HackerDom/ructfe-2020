#!/usr/bin/env python3

import os
import time
import datetime

import psycopg2


def clean_db(database_uri, table_names, interval):
    connection = psycopg2.connect(database_uri)
    cursor = connection.cursor()

    for table_name in table_names:
        query = f"DELETE FROM {table_name} WHERE timestamp < NOW() - INTERVAL '{interval}' RETURNING id"
        cursor.execute(query)

        count = len(cursor.fetchall())
        print(f"DELETED {count} ROWS FROM '{table_name}' TABLE")

    connection.commit()


def main():
    database_uri = os.getenv('DATABASE_URI')
    clean_interval = os.getenv('CLEAN_INTERVAL')
    sleep_seconds = int(os.getenv('SLEEP_SECONDS'))

    time.sleep(10)

    table_names = [
        'public.User', 
        'public.Document',
    ]

    while True:
        print(f"STARTED CLEANING AT {datetime.datetime.utcnow()}")

        clean_db(database_uri, table_names, clean_interval)
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()
