from flask import jsonify, request
from .. import db
from ..models import ProductCategory
from . import api
from .errors import bad_request


# 创建产品目录
@api.route("/product_categories", methods=['POST'])
def create_category():
    if request.json is None:
        return bad_request("not json request")
    if request.json.get('category_names') is None:
        return bad_request("category_names params is necessary")
    if not isinstance(request.json.get('category_names'), list):
        return bad_request("category_name params must be a list")
    for name in request.json.get('category_names'):
        category = ProductCategory(name=name)
        db.session.add(category)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 获取产品目录，及其下属的属性、属性值
@api.route("/product_categories/<int:id>", methods=['GET'])
def get_category(id):
    response = jsonify(
        [ProductCategory.query.get_or_404(id).to_json()]
    )
    response.status_code = 200
    return response


# 获取所有产品目录，及其下属的属性、属性值
@api.route("/product_categories", methods=['GET'])
def get_categories():
    response = jsonify(
        [category.to_json() for category in ProductCategory.query.all()]
    )
    response.status_code = 200
    return response

