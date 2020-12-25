#!/usr/bin/env python3

import os
import sys
import time
import psycopg2


def clean_db(database_uri, table_names, interval):
    connection = psycopg2.connect(database_uri)
    cursor = connection.cursor()

    for table_name in table_names:
        query = f"DELETE FROM {table_name} WHERE timestamp < NOW() - INTERVAL '{interval}' RETURNING id"
        cursor.execute(query)

        count = len(cursor.fetchall())
        print(f"DELETED {count} ROWS FROM '{table_name}' TABLE", file=sys.stderr)

    connection.commit()


def main():
    database_uri = os.getenv('DATABASE_URI')
    clean_interval = os.getenv('CLEAN_INTERVAL')
    sleep_seconds = int(os.getenv('SLEEP_SECONDS'))

    time.sleep(10)

    table_names = [
        'public.Document',
        'public.User', 
    ]

    while True:
        clean_db(database_uri, table_names, clean_interval)
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()
