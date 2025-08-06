![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

# Foodgram — Социальная сеть для обмена рецептами

**Foodgram** — это веб-сервис, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять блюда в избранное и формировать список покупок.

## Функционал

-  Публикация рецептов с фото, ингредиентами и описанием
-  Подписка на авторов
-  Добавление рецептов в избранное
-  Добавление рецептов в список покупок
-  Фильтрация рецептов по тегам: завтрак, обед, ужин
-  Автоматическое объединение ингредиентов в списке покупок
-  Скачивание списка покупок в PDF
-  Аутентификация через JWT-токены
-  Документация API (Redoc)
-  Автоматический деплой через GitHub Actions

## Установка 

1. Клонируйте репозиторий на свой компьютер:

    ```bash
    git clone https://github.com/PletnevDaniil/foodgram.git
    ```
    ```bash
    cd foodgram
    ```
2. Создайте файл .env в корне проекта. Пример:

    ```
    DB_NAME=foodgram # Имя базы данных
    POSTGRES_DB=foodgram
    POSTGRES_USER=foodgram_user # Логин подключения к базе данных
    POSTGRES_PASSWORD=your_strong_password # пароль подключения к базе данных
    DB_HOST=db # Название контейнера базы данных
    DB_PORT=5432 # Порт подключения к базе данных

    ALLOWED_HOST= 127.0.0.1, localhost
    SECRET_KEY=your_django_secret_key
    DEBUG=0
    ```

### Создание Docker-образов

1.  Создание Docker-образов (Замените username на ваш логин на DockerHub):

    ```bash
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```

2. Загрузите образы на DockerHub (Замените username на ваш логин на DockerHub):

    ```bash
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway

### Деплой на сервере

1. Подключитесь к удаленному серверу

    ```bash
    ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
    ```

2. Создайте на сервере директорию foodgram через терминал

    ```bash
    mkdir foodgram
    ```

3. Установка docker compose на сервер:

    ```bash
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
    ```

4. В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

    ```bash
    scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/kittygram/docker-compose.production.yml
    * ath_to_SSH — путь к файлу с SSH-ключом.
    * SSH_name — имя файла с SSH-ключом.
    * username — ваше имя пользователя на сервере.
    * server_ip — IP вашего сервера.
    * Убедитесь, что .env на сервере содержит правильные SECRET_KEY, POSTGRES_PASSWORD.
    ```

5. Запустите docker compose в режиме демона:

    ```bash
    sudo docker compose -f docker-compose.production.yml up -d
    ```

6. Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

    ```bash
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /app/static/
    ```

7. Заполните базу тестовыми данными:

    ```bash
    docker-compose exec backend python manage.py import_data
    ```

8. На сервере в редакторе nano откройте конфиг Nginx:

    ```bash
    sudo nano /etc/nginx/sites-enabled/default
    ```

9. Измените настройки location в секции server:

    ```bash
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:7000;
    }
    ```

10. Проверьте работоспособность конфига Nginx:

    ```bash
    sudo nginx -t
    ```
    Если ответ в терминале такой, значит, ошибок нет:
    ```bash
    nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
    nginx: configuration file /etc/nginx/nginx.conf test is successful
    ```

11. Перезапускаем Nginx
    ```bash
    sudo service nginx reload
    ```
### Документация API

Доступна по адресу:
https://your_domain/redoc/

Содержит:

-  Описание всех эндпоинтов
-  Примеры запросов и ответов
-  Модели данных
-  Права доступа

### Особенности реализации

-  Base64ImageField — из drf_extra_fields для загрузки изображений
-  Пагинация — кастомная с ?limit=
-  Фильтрация — по тегам, избранному, списку покупок
-  Оптимизация — prefetch_related, bulk_create, only()
-  PDF-генерация — списка покупок

### Автор
[Плетнев Даниил Михайлович](https://github.com/PletnevDaniil)

    ```
    ip - 51.250.27.26
    Домен - https://foodgrampletnev.zapto.org/
    superuser:
    email - pletnev@mail.ru
    pass - megapass4556
    ```