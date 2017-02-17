from flask import Blueprint

api = Blueprint('api', __name__, template_folder='templates', static_folder='/app/static')

from . import errors, categories, features, options

