docker run --name pg \
 -e POSTGRES_PASSWORD=123456 \
 -e POSTGRES_USER=kori \
 -e POSTGRES_DB=traffic \
 -p 5432:5432 \
 -d postgis/postgis 