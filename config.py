import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOADED_IMAGES_DEST = 'app/static/images/products'
    UPLOADED_IMAGES_URL = '/app/static/images/products'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = set(['jpg', 'png', 'gif'])

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://fuyuan:fuyuan@127.0.0.1/seesun-product-development'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://fuyuan:fuyuan@127.0.0.1/seesun-product-development'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://fuyuan:fuyuan@127.0.0.1/seesun-product-development'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}