from flask import jsonify, request
from .. import db
from ..models import ProductCategory, Product, SkuOption
from . import api
from .errors import bad_request
import datetime
from app.exceptions import ValidationError


# 创建产品
@api.route("/products", methods=["POST"])
def create_product():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('product_category_id'), str):
        return bad_request("product_category_id params is necessary")
    if not isinstance(request.json.get('product_info'), dict):
        return bad_request("product_info params must be a dict")
    category = ProductCategory.query.get_or_404(request.json.get('product_category_id'))
    code = request.json.get('product_info').get('code')
    if code is None or code.strip() == '':
        code = "SS%s" % datetime.datetime.now().strftime('%y%m%d%H%M%S')
    else:
        if Product.query.filter_by(code=code).first() is not None:
            db.session.rollback()
            raise ValidationError("%s product code has existed" % code, 400)
    product = Product(
        name=request.json.get('product_info').get('name'),
        code=code,
        description=request.json.get('product_info').get('description'),
        product_category=category,
        product_image_links=request.json.get('product_info').get('product_image_links')
    )
    for option_id in request.json.get('product_info').get('options_id'):
        sku_option = SkuOption.query.get_or_404(option_id)
        product.sku_options.append(sku_option)
    db.session.add(product)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


@api.route("/product_category/<int:id>/products", methods=["GET"])
def get_products(id):
    response = jsonify(
        [product.to_json() for product in ProductCategory.query.get_or_404(id).products]
    )
    response.status_code = 200
    return response
