#!/bin/bash
cd /app
export PYTHONUNBUFFERED=1
tail -f /dev/null
if [ "$IS_DEV" == "1" ]; then
    echo "--- DEV MODE -----"
    python3 /app/manage.py runserver 0.0.0.0:3031

fi
if [ "$APP_MODULE" != "" ]; then
    echo "--- UWSGI LIVE MODE -----"
    uwsgi --socket 0.0.0.0:3031 \
        --module $APP_MODULE \
        --master \
        --workers $WORKERS
fi