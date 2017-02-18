from flask import jsonify, request
from .. import db
from ..models import Product, SkuOption, ProductSku
from . import api
from .errors import bad_request
import datetime
from app.exceptions import ValidationError


# 创建产品sku
@api.route("/product_skus", methods=["POST"])
def create_skus():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('product_id'), str):
        return bad_request("product_id params is necessary")
    if not isinstance(request.json.get('sku_infos'), list):
        return bad_request("sku_info params must be a list")
    product = Product.query.get_or_404(request.json.get('product_id'))
    seq = 1
    for sku_info in request.json.get('sku_infos'):
        code = sku_info.get("code")
        if code is None or code.strip() == '':
            code = "SKU%s%s" % (datetime.datetime.now().strftime('%y%m%d%H%M%S'), seq)
            seq += 1
        else:
            if ProductSku.query.filter_by(code=code).first() is not None:
                db.session.rollback()
                raise ValidationError("%s sku code has existed" % code, 400)
        sku = ProductSku(
            product=product,
            code=code,
            price=sku_info.get("price"),
            stocks=sku_info.get("stocks"),
            barcode=sku_info.get("barcode"),
            hscode=sku_info.get("hscode"),
            weight=sku_info.get("weight"),
            thumbnail=sku_info.get("thumbnail"),
            stocks_for_order=0
        )
        for option_id in sku_info.get('options_id'):
            sku_option = SkuOption.query.get_or_404(option_id)
            sku.sku_options.append(sku_option)
        db.session.add(sku)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 根据产品获取sku
@api.route("/products/<int:id>/skus", methods=["GET"])
def get_skus(id):
    response = jsonify(
        Product.query.get_or_404(id).to_sku_json()
    )
    response.status_code = 200
    return response
