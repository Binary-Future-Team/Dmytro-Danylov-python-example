./entrypoints/components.local


if [[ $DEBUG == 'True' ]];
then
    echo "Running app in debug mode"
    echo "========================="
    python ./manage.py collectstatic --noinput
    python ./manage.py runserver 0.0.0.0:$APP_INTERNAL_PORT

else
    echo "Running app in production mode"
    python ./manage.py collectstatic --noinput
    gunicorn --config ./***/gunicorn_config.py ***.wsgi
fi
