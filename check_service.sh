#!/bin/bash

set -e
service=$1

echo "Trying to build and run service $service"
(cd ./services/$service && docker-compose pull && docker-compose build && docker-compose up --build -d)

echo "waiting a little bit for service to start"
sleep 5

echo "Trying to execute checker"
echo "TODO"
