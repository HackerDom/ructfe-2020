#!/bin/bash

chown -R mumbler: /app/storage
chmod 700 /app/storage

exec gosu mumbler python main.py
