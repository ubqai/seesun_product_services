from flask import jsonify, request, current_app
from .. import db
from ..models import ProductSku, Inventory
from . import api
from .errors import bad_request
import datetime
from app.exceptions import ValidationError


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
