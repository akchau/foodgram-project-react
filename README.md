[Перейти к остальным проектам](https://github.com/akchau/akchau/blob/main/README.md#проекты)

# Foodgram
![.github/workflows/main.yml](https://github.com/akchau/foodgram-project-react/actions/workflows/workflow.yml/badge.svg)

Адресс проекта - http://51.250.70.35
email admin@admin.ru
login admin
pass admin

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
http://51.250.70.35/api/docs/redoc.html
```
