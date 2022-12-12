# TechSupport backend v1.0

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

