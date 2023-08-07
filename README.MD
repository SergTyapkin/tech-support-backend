# TechSupport backend v1.0
Пример деплоя и подробная инструкция: https://github.com/SergTyapkin/tech-support-deploy

Для определения местоположения входов нужно скачать базу данных IP-адресов: https://git.io/GeoLite2-City.mmdb, и положить в папку `configs` 

---
### Запуск для разработки:
Нужна версия Python >= 3.10
```shell
pip install -r requirements.txt
python main.py
```
---
### Запуск для прода:
```shell
gunicorn --bind 0.0.0.0:9000 main:app
```
[+]
Nginx config in `sites_available` folder:
```nginx
server {
    listen 80;
    server_name your_domain;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:9000;
    }
}
```

