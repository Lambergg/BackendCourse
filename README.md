
docker network create myNetwork

docker run --name booking_db \
    -p 6432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=09876543210hh \
    -e POSTGRES_DB=Booking \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:16

docker run --name booking_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis:7.4

docker run --name booking_back \
    -p 8080:8080 \
    --network=myNetwork \
    booking_image

docker run --name booking_celery_worker \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO

docker run --name booking_celery_beat \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance beat -l INFO -B

docker run \
--name booking_nginx \
-v "$((Get-Location).Path)\nginx.conf:/etc/nginx/nginx.conf" \
--network=myNetwork \
--rm \
-p 8080:8080 \
nginx

docker run --name booking_nginx \
           -v "./nginx.conf:/etc/nginx/nginx.conf" \
           --network=myNetwork \
           -d \
           -p 80:80 \
           nginx

docker build -t booking_image  . 