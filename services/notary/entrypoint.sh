#!/bin/bash

sleep 5

python3 create_db.py

dd if=/dev/urandom of=secret.txt bs=16 count=1 status=none

gunicorn --bind 0.0.0.0:8080 --workers 8 --worker-connections 1024 app:app
