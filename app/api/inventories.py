from flask import jsonify, request, current_app
from .. import db
from ..models import ProductSku, Inventory
from . import api
from .errors import bad_request


# 创建库存
@api.route("/inventories", methods=["POST"])
def create_inventories():
    if request.json is None:
        return bad_request("not json request")
    if not isinstance(request.json.get('inventory_infos'), list):
        return bad_request("inventory_infos params must be a list")
    current_app.logger.info("11111111")
    current_app.logger.info(request.json.get('inventory_infos'))
    for inventory_info in request.json.get('inventory_infos'):
        sku = ProductSku.query.get_or_404(inventory_info.get('sku_id'))
        for inv in inventory_info.get('inventory'):
            inventory = Inventory(
                type=inv.get('type'),
                user_id=inv.get('user_id'),
                user_name=inv.get('user_name'),
                production_date=inv.get('production_date'),
                valid_until=inv.get('valid_until'),
                batch_no=inv.get('batch_no'),
                stocks=inv.get('stocks'),
                product_sku=sku
            )
            db.session.add(inventory)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 201
    return response


# 根据sku id 获取 库存
@api.route("/sku/<int:id>/inventories", methods=["GET"])
def get_inventories(id):
    sku = ProductSku.query.get_or_404(id)
    response = jsonify(
        [{"user_id": user[0], "user_name": user[1], "total": user[2], "batches":
            [inv.to_json() for inv in Inventory.query.filter_by(user_id=user[0], user_name=user[1],
                                                                product_sku_id=sku.id)]}
         for user in sku.inv_group_by_user()]
    )
    response.status_code = 200
    return response


# 根据sku id和user_id 获取 库存
@api.route("/sku/<int:user_id>/<int:id>/inventories", methods=["GET"])
def get_user_inventories(user_id, id):
    sku = ProductSku.query.get_or_404(id)
    response = jsonify(
        [{"user_id": user[0], "user_name": user[1], "total": user[2], "batches":
            [inv.to_json() for inv in Inventory.query.filter_by(user_id=user[0], user_name=user[1],
                                                                product_sku_id=sku.id)]}
         for user in sku.inv_group_by_user(user_id=user_id)]
    )
    response.status_code = 200
    return response


# 修改库存
@api.route("/inventories/<int:id>/edit", methods=["PUT"])
def update_inv(id):
    if request.json is None:
        return bad_request("not json request")
    inv = Inventory.query.get_or_404(id)
    if isinstance(request.json.get('production_date'), str):
        inv.production_date = request.json.get('production_date')
    if isinstance(request.json.get('valid_until'), str):
        inv.valid_until = request.json.get('valid_until')
    if isinstance(request.json.get('batch_no'), str):
        inv.batch_no = request.json.get('batch_no')
    if isinstance(request.json.get('stocks'), str):
        inv.stocks = request.json.get('stocks')
    if isinstance(request.json.get('share_stocks'), str):
        inv.share_stocks = request.json.get('share_stocks')
    db.session.add(inv)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 删除库存
@api.route("/inventories/<int:id>", methods=["DELETE"])
def delete_inv(id):
    inv = Inventory.query.get_or_404(id)
    db.session.delete(inv)
    db.session.commit()
    response = jsonify(
        {
            'status': "success"
        }
    )
    response.status_code = 200
    return response


# 根据id 获取 库存
@api.route("/inventories/<int:id>", methods=["GET"])
def get_inventory(id):
    inv = Inventory.query.get_or_404(id)
    response = jsonify(
        inv.to_json()
    )
    response.status_code = 200
    return response
