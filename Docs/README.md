#Создать докер сеть \
docker network create myNetwork

#Создание образа БД \
docker run --name booking_db \
    -p 6432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=09876543210hh \
    -e POSTGRES_DB=Booking \
    --network=myNetwork \
    --volume pg-booking-data:/var/lib/postgresql/data \
    -d postgres:16

#Создание образа Redis \
docker run --name booking_cache \
    -p 7379:6379 \
    --network=myNetwork \
    -d redis:7.4

#Эти комманды можно не запускать, \
а запустить docker compose up --build \
docker run --name booking_back \
    -p 8080:8080 \
    --network=myNetwork \
    booking_image

#Эти комманды можно не запускать, \
а запустить docker compose up --build \
docker run --name booking_celery_worker \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO

#Эти комманды можно не запускать, \
а запустить docker compose up --build \
docker run --name booking_celery_beat \
    --network=myNetwork \
    booking_image \
    celery --app=src.tasks.celery_app:celery_instance beat -l INFO -B

#Запуск nginx на windows \
docker run \
--name booking_nginx \
--volume "${PWD}/nginx.conf:/etc/nginx/nginx.conf"\
--network=myNetwork \
--rm \
-p 80:80 \
nginx

#Запуск ngixn в linux на сервере \
docker run \ 
--name booking_nginx \
--volume ./nginx.conf:/etc/nginx/nginx.conf \
--volume /etc/letsencrypt:/etc/letsencrypt \
--volume /var/lib/letsencrypt:/var/lib/letsencrypt \
--network=myNetwork \
-d \
-p 443:443 \        
nginx

#Сборка образа бекенда \
docker build -t booking_image  . 