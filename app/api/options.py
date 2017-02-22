from flask import jsonify, request
from .. import db
from ..models import SkuFeature, SkuOption
from . import api
from .errors import bad_request


# 创建产品属性值
@api.route("/sku_options", methods=['POST'])
def create_option():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('sku_feature_id'), str):
        return bad_request("sku_feature_id params is necessary")
    if not isinstance(request.json.get('names'), list):
        return bad_request("name params must be a list")
    feature = SkuFeature.query.get_or_404(request.json.get('sku_feature_id'))
    for name in request.json.get('names'):
        option = SkuOption(
            name=name,
            sku_feature=feature
        )
        db.session.add(option)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 修改产品属性值
@api.route("/sku_options/<int:id>/edit", methods=['PUT'])
def update_option(id):
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('name'), str):
        return bad_request("name params must be a str")
    option = SkuOption.query.get_or_404(id)
    option.name = request.json.get('name')
    db.session.add(option)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response
