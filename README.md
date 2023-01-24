# Foodgram


1. Чтобы развернуть проект зайдите в папку /infra и выполните команду запуска фоновой сборки.
```bash
docker-compose up -d --build
```
2. После успешного запуска контейнеров выполниете команда и создайте суперпользоателя.
```bash
docker-compose exec backend python manage.py migrate 
docker-compose exec backend python manage.py createsuperuser 
docker-compose exec backend python manage.py collectstatic --no-input
```
3. Спецификация api доступна по адресу
```http
http://localhost/api/docs/redoc.html
```





