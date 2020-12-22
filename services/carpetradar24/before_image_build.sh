#!/bin/bash

docker-compose -f docker-compose-build.yaml up --build --remove-orphans --force-recreate
docker-compose -f docker-compose-build.yaml down
