#!/usr/bin/env bash
./entrypoints/components.local


if [[ $DEBUG == 'True' ]];
then
    echo "Running celery worker in debug mode"
    echo "==================================="
    watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- \
        celery -A *** worker -ldebug --loglevel=$LOGLEVEL --concurrency=1
else
    echo "Running celery worker in production mode"
    celery -A *** worker -ldebug --loglevel=$LOGLEVEL
fi
