import os
from flask import Flask
from flask_mail import Mail

from src.blueprints.user import app as user_app
from src.blueprints.admin import app as admin_app
from src.blueprints.event import app as event_app
from src.blueprints.ratings import app as ratings_app
from src.blueprints.participation import app as participation_app
from src.blueprints.place import app as place_app
from src.blueprints.position import app as position_app
from src.blueprints.docs import app as docs_app
from src.blueprints.image import app as image_app
from src.blueprints.achievements import app as achievements_app
from middleware import Middleware
from src.utils.utils import read_app_config

_config = read_app_config('./configs/config.json')

app = Flask(__name__)
app.wsgi_app = Middleware(app.wsgi_app, url_prefix='/api', cors_origins=_config['cors-origins'])

app.register_blueprint(user_app,   url_prefix='/user')
app.register_blueprint(admin_app,  url_prefix='/admin')
app.register_blueprint(event_app,  url_prefix='/event')
app.register_blueprint(ratings_app, url_prefix='/ratings')
app.register_blueprint(participation_app,   url_prefix='/participation')
app.register_blueprint(place_app,   url_prefix='/place')
app.register_blueprint(position_app,   url_prefix='/position')
app.register_blueprint(docs_app,   url_prefix='/docs')
app.register_blueprint(image_app,   url_prefix='/image')
app.register_blueprint(achievements_app,   url_prefix='/achievements')

app.config['MAIL_SERVER'] = _config['SMTP_mail_server_host']
app.config['MAIL_PORT'] = _config['SMTP_mail_server_port']
app.config['MAIL_USE_TLS'] = _config['SMTP_mail_server_use_tls']
app.config['MAIL_USERNAME'] = _config['mail_address']
app.config['MAIL_DEFAULT_SENDER'] = _config['mail_sender_name']
app.config['MAIL_PASSWORD'] = _config['mail_password']

mail = Mail(app)


@app.route('/')
def home():
    return "Это начальная страница API для сайта техподдержки, а не сайт. Вiйди отсюда!"


@app.errorhandler(404)
def error404(err):
    print(err)
    return "404 страница не найдена"


@app.errorhandler(500)
def error500(err):
    print(err)
    return "500 внутренняя ошибка сервера"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', _config['api_port']))
    app.run(port=port, debug=bool(_config['debug']))
