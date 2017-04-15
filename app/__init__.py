from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, IMAGES, configure_uploads
from config import config
from flask_cache import Cache

uploaded_images = UploadSet('images', IMAGES)
db = SQLAlchemy()
bootstrap = Bootstrap()
cache = Cache(config={'CACHE_TYPE': 'simple'})


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    configure_uploads(app, uploaded_images)

#   注册蓝本
    from .main import main as main_blueprint
    from .api import api as api_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api_v0.1')

    return app
