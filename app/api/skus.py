from flask import jsonify, request, current_app
from .. import db
from ..models import Product, SkuOption, ProductSku, Inventory
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
            barcode=sku_info.get("barcode"),
            hscode=sku_info.get("hscode"),
            weight=sku_info.get("weight"),
            thumbnail=sku_info.get("thumbnail"),
            name=sku_info.get("name"),
            memo=sku_info.get("memo"),
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


# 修改产品sku
@api.route("/product_skus/<int:id>/edit", methods=["PUT"])
def update_sku(id):
    current_app.logger.info(request.json)
    if request.json is None:
        return bad_request("not json request")
    current_app.logger.info(request.json)
    sku = ProductSku.query.get_or_404(id)
    if isinstance(request.json.get('code'), str):
        if ProductSku.query.filter_by(code=request.json.get('code')).first() is not None:
            db.session.rollback()
            raise ValidationError("%s sku code has existed" % request.json.get('code'), 400)
        else:
            sku.code = request.json.get('code')
    if isinstance(request.json.get('barcode'), str):
        sku.barcode = request.json.get('barcode')
    if isinstance(request.json.get('hscode'), str):
        sku.hscode = request.json.get('hscode')
    if request.json.get('weight') is not None:
        sku.weight = request.json.get('weight')
    if isinstance(request.json.get('thumbnail'), str):
        sku.thumbnail = request.json.get('thumbnail')
    if isinstance(request.json.get('name'), str):
        sku.name = request.json.get('name')
    if isinstance(request.json.get('memo'), str):
        sku.memo = request.json.get('memo')
    if isinstance(request.json.get('isvalid'), str):
        if request.json.get('isvalid') != "YES" and request.json.get('isvalid') != "NO":
            db.session.rollback()
            raise ValidationError("%s isvalid enum must be YES or NO" % request.json.get('isvalid'), 400)
        sku.isvalid = request.json.get('isvalid')
    if request.json.get('stocks_for_order') is not None:
        sku.stocks_for_order += int(request.json.get('stocks_for_order'))
    if isinstance(request.json.get('options_id'), list):
        for sku_option in sku.sku_options.all():
            sku.sku_options.remove(sku_option)
        for option_id in request.json.get('options_id'):
            sku_option = SkuOption.query.get_or_404(option_id)
            sku.sku_options.append(sku_option)
    db.session.add(sku)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 生成合同时修改产品sku的stocks_for_order及批次中的库存
@api.route("/product_skus/edit_by_code", methods=["PUT"])
def update_sku_by_code():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('sku_infos'), list):
        return bad_request("sku_infos params must be a list")
    current_app.logger.info(request.json)

    for sku_info in request.json.get('sku_infos'):
        code = sku_info.get("code")
        sku = ProductSku.query.filter_by(code=code).first()
        if sku_info.get('stocks_for_order') is not None:
            sku.stocks_for_order += int(sku_info.get('stocks_for_order'))

        if isinstance(sku_info.get('batches'), list):
            for batch in sku_info.get('batches'):
                inv = Inventory.query.get_or_404(batch['inv_id'])
                inv.stocks -= int(batch['sub_stocks'])
                db.session.add(inv)
        db.session.add(sku)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 删除产品sku
@api.route("/product_skus/<int:id>", methods=["DELETE"])
def delete_sku(id):
    sku = ProductSku.query.get_or_404(id)
    db.session.delete(sku)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 根据sku_id获取sku
@api.route("/product_skus/<int:id>", methods=["GET"])
def get_sku(id):
    response = jsonify(
        ProductSku.query.get_or_404(id).to_json()
    )
    response.status_code = 200
    return response


@api.route("/product_skus/search", methods=["POST"])
def search_skus():
    if request.json is None:
        return bad_request("not json request")
    if request.json.get('option_ids') is None:
        return bad_request("option_ids params is necessary")
    if not isinstance(request.json.get('option_ids'), list):
        return bad_request("option_ids params must be a list")

    bq = db.session.query(ProductSku)
    for option_id in request.json.get('option_ids'):
        bq = bq.from_self().join(ProductSku.sku_options).filter(SkuOption.id == option_id)
    total_count = bq.count()
    page_size = int(request.json.get('page_size', 20))
    page_index = int(request.json.get('page', 1))
    has_prev = False
    has_next = False
    if page_index > 1:
        has_prev = True
    if page_size*page_index < total_count:
        has_next = True

    response = jsonify({
        "skus": [sku.to_search_json() for sku in bq.offset(page_size*(page_index-1)).limit(page_size)],
        "has_prev": has_prev,
        "has_next": has_next,
        "page_size": page_size,
        "page": page_index
        }
    )
    response.status_code = 200
    return response
