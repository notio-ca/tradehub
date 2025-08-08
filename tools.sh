
if [ -n "$1" ]; then
    Q="$1"
else
    echo "r) Restart Container"
    echo "w) Dev Web Server"
    echo "d) Database Migrations"
    echo "l)" Container logs
    echo "c)" Collect Static
    echo "exec) Enter Container"
    echo "cron) Run Cron"
    echo "build) Build Container"

    read -p "--- Command > " Q
fi

sudo chown -R ubuntu:ubuntu .

if [ "$Q" == "r" ]; then
    docker restart tradehub
fi

if [ "$Q" == "w" ]; then
    docker exec -ti tradehub python3 /app/manage.py runserver 0.0.0.0:3031
fi

if [ "$Q" == "d" ]; then
    docker exec -ti tradehub python3 /app/manage.py makemigrations

    read -p "--- Apply Migrations? [Y/n] " Q
    if [ "$Q" == "y" ]; then
        docker exec -ti tradehub python3 /app/manage.py migrate
    fi
fi

if [ "$Q" == "l" ]; then
    docker logs -f tradehub --tail 1000
fi

if [ "$Q" == "exec" ]; then
    docker exec -ti tradehub bash
fi

if [ "$Q" == "c" ]; then
    docker exec -ti tradehub python3 /app/manage.py collectstatic --clear
    sudo chown -R ubuntu:ubuntu ./static/
fi

if [ "$Q" == "cron" ]; then
    docker exec -ti tradehub python3 /app/manage.py cron
fi

if [ "$Q" == "build" ]; then
    cd docker/
    docker-compose build
    docker-compose up -d
fi







