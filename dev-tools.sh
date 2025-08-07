echo "r) Restart Container"
echo "w) Dev Web Server"
echo "d) Database Migrations"
echo "l)" Container logs
echo "c)" Collect Static
echo "exec) Enter Container"
echo "build) Build Container"

# echo "inspect) Inpect Database"
read -p "--- Command > " Q

sudo chown -R ubuntu:ubuntu .

# Nginx conf backup
# cp -rap /websrv/data/nginx/conf.d /websrv/tradehub/stack/nginx/

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

if [ "$Q" == "c" ]; then
    docker exec -ti tradehub python3 /app/manage.py collectstatic --clear
    sudo chown -R ubuntu:ubuntu ./static/
fi

if [ "$Q" == "exec" ]; then
    docker exec -ti tradehub bash
fi

if [ "$Q" == "build" ]; then
    cd docker/
    docker-compose build
    docker-compose up -d
fi







