Собрать:

```docker-compose up -d --build```

Если не вышло:

```docker-compose -f docker-compose_2.yml up -d --build```

Запустить тесты:

```docker exec -it web bash```

```python manage.py test```
