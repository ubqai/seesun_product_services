from flask import jsonify, request
from .. import db
from ..models import ProductComments
from . import api
from .errors import bad_request

# 根据产品获取sku
@api.route("/products/<int:id>/comments", methods=["GET"])
def get_comments(id):
    response = jsonify(
        ProductComments.query.filter_by(product_id=id).to_json()
    )
    response.status_code = 200
    return response