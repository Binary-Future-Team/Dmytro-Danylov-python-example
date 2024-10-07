#!/usr/bin/env bash
./entrypoints/components.local
rm celerybeat-schedule

if [[ $DEBUG == 'True' ]];
then
    echo "Running celery worker in debug mode"
    echo "==================================="
    watchmedo auto-restart --directory=./ --pattern=*.py --recursive \
             -- celery -A *** beat -ldebug --loglevel=$LOGLEVEL
else
    echo "Running celery worker in production mode"
    celery -A *** beat -ldebug --loglevel=$LOGLEVEL
fi
