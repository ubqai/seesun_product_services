from flask import jsonify, request
from .. import db
from ..models import ProductCategory, SkuFeature
from . import api
from .errors import bad_request


# 创建产品属性
@api.route("/sku_features", methods=['POST'])
def create_feature():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('product_category_id'), str):
        return bad_request("product_category_id params is necessary")
    if not isinstance(request.json.get('feature_infos'), list):
        return bad_request("feature_infos params must be a list")
    category = ProductCategory.query.get_or_404(request.json.get('product_category_id'))
    for feature_info in request.json.get('feature_infos'):
        feature = SkuFeature(
            name=feature_info.get('name'),
            description=feature_info.get('description'),
            product_category=category
        )
        db.session.add(feature)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 获取产品属性信息
@api.route("/sku_feature/<int:id>", methods=['GET'])
def get_feature(id):
    feature = SkuFeature.query.get_or_404(id)
    response = jsonify(feature.to_json())
    response.status_code = 200
    return response


# 创建产品属性
@api.route("/sku_features/<int:id>/edit", methods=['PUT'])
def update_feature(id):
    if request.json is None:
        return bad_request("not json request")
    feature = SkuFeature.query.get_or_404(id)
    if isinstance(request.json.get('name'), str):
        feature.name = request.json.get('name')
    if isinstance(request.json.get('description'), str):
        feature.description = request.json.get('description')
    db.session.add(feature)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response
