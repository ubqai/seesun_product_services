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
        case_ids=request.json.get('product_info').get('case_ids'),
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
            'status': "success",
            'product_id': product.id
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


@api.route("/product/<int:id>", methods=["GET"])
def get_product(id):
    response = jsonify(
        Product.query.get_or_404(id).to_json()
    )
    response.status_code = 200
    return response


# 编辑产品
@api.route("/products/<int:id>/edit", methods=["PUT"])
def update_product(id):
    if request.json is None:
        return bad_request("not json request")
    product = Product.query.get_or_404(id)
    if isinstance(request.json.get('name'), str):
        product.name = request.json.get('name')
    if isinstance(request.json.get('code'), str):
        if Product.query.filter_by(code=request.json.get('code')).first() is not None:
            db.session.rollback()
            raise ValidationError("%s product code has existed" % request.json.get('code'), 400)
        else:
            product.code = request.json.get('code')
    if isinstance(request.json.get('description'), str):
        product.description = request.json.get('description')
    if isinstance(request.json.get('case_ids'), list):
        product.case_ids = request.json.get('case_ids')
    if isinstance(request.json.get('product_image_links'), list):
        product.product_image_links = request.json.get('product_image_links')
    if isinstance(request.json.get('options_id'), list):
        for sku_option in product.sku_options.all():
            product.sku_options.remove(sku_option)
        for option_id in request.json.get('options_id'):
            sku_option = SkuOption.query.get_or_404(option_id)
            product.sku_options.append(sku_option)
    db.session.add(product)
    db.session.commit()
    response = jsonify(
        {
            'status': "success",
            'product_id': product.id
        }
    )
    response.status_code = 200
    return response


# 删除产品
@api.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response
