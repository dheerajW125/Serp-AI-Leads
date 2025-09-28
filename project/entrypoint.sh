#!/bin/bash

# Run Django crontab add
echo "Adding crontab jobs..."
python manage.py crontab add

# Start cron
echo "Starting cron..."
echo "Starting cron in foreground..."
cron -f

# Start Django dev server (for testing)
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000
