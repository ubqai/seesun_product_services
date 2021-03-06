from flask import jsonify, request
from .. import db, cache
from ..models import SkuFeature
from . import api
from .errors import bad_request
from app.exceptions import ValidationError


# 创建产品属性
@api.route("/sku_features", methods=['POST'])
def create_feature():
    if request.json is None:
        return bad_request("not json request")
    # if not isinstance(request.json.get('product_category_id'), str):
    #    return bad_request("product_category_id params is necessary")
    if not isinstance(request.json.get('feature_infos'), list):
        return bad_request("feature_infos params must be a list")
    # category = ProductCategory.query.get_or_404(request.json.get('product_category_id'))
    for feature_info in request.json.get('feature_infos'):
        feature = SkuFeature(
            name=feature_info.get('name'),
            description=feature_info.get('description')
            # product_category=category
        )
        db.session.add(feature)
    db.session.commit()
    cache.delete_memoized(get_features)
    # cache.delete_memoized(get_feature)
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 获取产品属性信息
@api.route("/sku_feature/<int:id>", methods=['GET'])
@cache.memoize(720000)
def get_feature(id):
    feature = SkuFeature.query.get_or_404(id)
    response = jsonify(feature.to_json())
    response.status_code = 200
    return response


# 删除产品属性
@api.route("/sku_feature/<int:id>", methods=['DELETE'])
def delete_feature(id):
    feature = SkuFeature.query.get_or_404(id)
    if feature.is_used():
        raise ValidationError("sku feature has been used", 400)
    for option in feature.sku_options:
        db.session.delete(option)
    db.session.delete(feature)
    db.session.commit()
    cache.delete_memoized(get_features)
    cache.delete_memoized(get_feature, id)
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 修改产品属性
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
    cache.delete_memoized(get_features)
    cache.delete_memoized(get_feature, id)
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 获取产品属性信息
@api.route("/sku_features", methods=['GET'])
@cache.memoize(720000)
def get_features():
    response = jsonify([feature.to_json() for feature in SkuFeature.query.all()])
    response.status_code = 200
    return response
