#!/bin/bash

sleep 5

dd if=/dev/urandom of=/tmp/secret.key bs=16 count=1 status=none

python3 create_db.py

gunicorn --bind 0.0.0.0:8080 --workers 8 --worker-connections 1024 app:app
