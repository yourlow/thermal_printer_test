#!/bin/bash
if [ "$ENVIRONMENT" = "development" ] 
then
    python3 app.py
elif [ "$ENVIRONMENT" = "production" ] 
then
    gunicorn --bind 0.0.0.0:8080 src.run:app
else

    echo "ENVIRONMENT: environment variable not set correctly. Must be either development || production"
fi