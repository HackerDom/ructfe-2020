#!/bin/bash

chown -R mumbler: /app/storage
chmod 700 /app/storage

su mumbler -s /bin/bash -c 'python main.py'
