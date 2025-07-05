#!/bin/bash

cp /usr/src/covid_detection/docker/config.py /usr/src/covid_detection/

python /usr/src/covid_detection/app.py

exec "$@"