#!/bin/bash

java -jar ./build/libs/fs-1.0-SNAPSHOT.jar &
sleep 20 && java -jar ./build/libs/keeper-1.0-SNAPSHOT.jar
