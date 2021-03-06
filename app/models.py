from . import db
import datetime
from functools import reduce


class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # sku_features = db.relationship('SkuFeature', backref='product_category') 取消属性与产品目录关系
    products = db.relationship('Product', backref='product_category', order_by='Product.created_at.desc()')

    def __repr__(self):
        return '<ProductCategory %r>' % self.to_json()

    def to_json(self):
        json_category = {
            "category_id": self.id,
            "category_name": self.name
            # "features": [feature.to_json() for feature in self.sku_features] 取消属性与产品目录关系
        }
        return json_category


class SkuFeature(db.Model):
    __tablename__ = 'sku_features'
    id = db.Column(db.Integer, primary_key=True)
    # product_category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id')) 取消属性与产品目录关系
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    sku_feature_type = db.Column(db.String)
    sku_options = db.relationship('SkuOption', backref='sku_feature')

    def __repr__(self):
        return '<SkuFeature %r>' % self.to_json()

    def to_json(self):
        json_feature = {
            "feature_id": self.id,
            "feature_name": self.name,
            "is_used": self.is_used(),
            "options": [option.to_json() for option in self.sku_options]
        }
        return json_feature

    def is_used(self):
        for option in self.sku_options:
            if option.is_used():
                return True
        return False


class SkuOption(db.Model):
    __tablename__ = 'sku_options'
    id = db.Column(db.Integer, primary_key=True)
    sku_feature_id = db.Column(db.Integer, db.ForeignKey('sku_features.id'))
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<SkuOption %r>' % self.to_json()

    def to_json(self):
        json_option = {
            "option_id": self.id,
            "option_name": self.name,
            "is_used": self.is_used(),
            "feature_name": self.sku_feature.name
        }
        return json_option

    def is_used(self):
        prt = db.session.query(Product).join(Product.sku_options).filter(SkuOption.id == self.id).first()
        sku = db.session.query(ProductSku).join(ProductSku.sku_options).filter(SkuOption.id == self.id).first()
        if prt is None and sku is None:
            return False
        else:
            return True

products_and_skuoptions = db.Table(
    'products_and_skuoptions',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('sku_option_id', db.Integer, db.ForeignKey('sku_options.id'))
)

products_sku_options = db.Table(
    'products_sku_options',
    db.Column('product_sku_id', db.Integer, db.ForeignKey('product_skus.id')),
    db.Column('sku_option_id', db.Integer, db.ForeignKey('sku_options.id'))
)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    name = db.Column(db.String(64))
    code = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)
    length = db.Column(db.String(256))
    width = db.Column(db.String(256))
    product_image_links = db.Column(db.JSON)
    rating = db.Column(db.Float)
    case_ids = db.Column(db.JSON, default=[])
    isvalid = db.Column(db.String(10), default='YES')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    product_skus = db.relationship('ProductSku', backref='product', order_by='ProductSku.created_at.desc()')
    sku_options = db.relationship('SkuOption', secondary=products_and_skuoptions,
                                  backref=db.backref('products', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Product %r>' % self.to_json()

    def to_json(self):
        json_product = {
            "product_id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "length": 1 if self.length is None or self.length == 0 else self.length,
            "width": 1 if self.width is None or self.width == 0 else self.width,
            "images": self.product_image_links,
            "case_ids": self.case_ids,
            "isvalid": self.isvalid
            # "options": [option.to_json() for option in self.sku_options]
        }
        return json_product

    def to_option_json(self):
        json_options = {
            "options": [option.to_json() for option in self.sku_options]
        }
        return json_options

    def to_sku_json(self):
        json_skus = {
            "product_id": self.id,
            "name": self.name,
            "skus": [sku.to_json() for sku in self.product_skus]
        }
        return json_skus


class ProductSku(db.Model):
    __tablename__ = 'product_skus'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    code = db.Column(db.String(32), unique=True)
    price = db.Column(db.Float)
    barcode = db.Column(db.String)
    hscode = db.Column(db.String)
    weight = db.Column(db.Float)
    stocks_for_order = db.Column(db.Float, default=0)
    thumbnail = db.Column(db.Text)
    isvalid = db.Column(db.String(10), default='YES')
    name = db.Column(db.String(256))
    memo = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    sku_options = db.relationship('SkuOption', secondary=products_sku_options,
                                  backref=db.backref('product_skus', lazy='dynamic'), lazy='dynamic')
    inventories = db.relationship('Inventory', backref='product_sku')

    def __repr__(self):
        return '<ProductSku %r>' % self.to_json()

    @property
    def stocks(self):
        return reduce(lambda x, y: x + y, [inv.stocks for inv in self.inventories], 0)

    @property
    def normal_stocks(self):
        return reduce(lambda x, y: x + y, [inv.stocks for inv in [inv for inv in self.inventories if inv.type == 1]], 0)

    @property
    def tailory_stock(self):
        return reduce(lambda x, y: x + y, [inv.stocks for inv in [inv for inv in self.inventories if inv.type == 2]], 0)

    def to_json(self):
        json_sku = {
            "sku_id": self.id,
            "code": self.code,
            "price": self.price,
            "stocks": self.stocks,
            "normal_stocks": self.normal_stocks,
            "tailory_stock": self.tailory_stock,
            "stocks_for_order": self.stocks_for_order,
            "barcode": self.barcode,
            "hscode": self.hscode,
            "weight": self.weight,
            "thumbnail": self.thumbnail,
            "isvalid": self.isvalid,
            "name": self.name,
            "memo": self.memo,
            "length": 1 if self.product.length is None or self.product.length == 0 else self.product.length,
            "width": 1 if self.product.width is None or self.product.width == 0 else self.product.width,
            "options": [{option.sku_feature.name: option.name} for option in self.sku_options]
        }
        return json_sku

    def to_search_json(self):
        json_sku = {
            "sku_id": self.id,
            "code": self.code,
            "price": self.price,
            "stocks": self.stocks,
            "normal_stocks": self.normal_stocks,
            "tailory_stock": self.tailory_stock,
            "stocks_for_order": self.stocks_for_order,
            "barcode": self.barcode,
            "hscode": self.hscode,
            "weight": self.weight,
            "thumbnail": self.thumbnail,
            "isvalid": self.isvalid,
            "name": self.name,
            "memo": self.memo,
            "length": 1 if self.product.length is None or self.product.length == 0 else self.product.length,
            "width": 1 if self.product.width is None or self.product.width == 0 else self.product.width,
            "options": [{option.sku_feature.name: option.name} for option in self.sku_options],
            "product_info": self.product.to_json(),
            "category_info": self.product.product_category.to_json()
        }
        return json_sku

    def inv_group_by_user(self, user_id='default'):
        if user_id == 'default':
            inv_users_list = db.session.query(Inventory.user_id, Inventory.user_name,
                                              db.func.sum(Inventory.stocks).label('total')).\
                filter_by(product_sku_id=self.id).group_by(Inventory.user_id, Inventory.user_name).all()
        else:
            inv_users_list = db.session.query(Inventory.user_id, Inventory.user_name,
                                              db.func.sum(Inventory.stocks).label('total')). \
                filter_by(product_sku_id=self.id, user_id=user_id).\
                group_by(Inventory.user_id, Inventory.user_name).all()
        return inv_users_list

    def inv_group_by_users(self, user_ids):
        inv_users_list = db.session.query(Inventory.user_id, Inventory.user_name,
                                          db.func.sum(Inventory.stocks).label('total')). \
            filter_by(product_sku_id=self.id).filter(Inventory.user_id.in_(user_ids)).\
            group_by(Inventory.user_id, Inventory.user_name).all()
        return inv_users_list


class Inventory(db.Model):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    product_sku_id = db.Column(db.Integer, db.ForeignKey('product_skus.id'))
    type = db.Column(db.Integer, default=1)  # 1--公司正常库存，2--公司和经销商工程剩余库存
    user_id = db.Column(db.Integer)  # 经销商id（公司id=0）
    user_name = db.Column(db.String(200))  # 经销商名称
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    production_date = db.Column(db.Date, default=datetime.datetime.today())
    valid_until = db.Column(db.Date)
    batch_no = db.Column(db.String(30))
    stocks = db.Column(db.Float, default=0)
    price = db.Column(db.Float)

    def __repr__(self):
        return '<Inventory %r>' % self.to_json()

    def to_json(self):
        json_inv = {
            "inv_id": self.id,
            "type": self.type,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "created_at": self.created_at.strftime("%Y-%m-%d"),
            "production_date": self.production_date.strftime("%Y-%m-%d") if self.production_date is not None else "",
            "valid_until": self.valid_until.strftime("%Y-%m-%d") if self.valid_until is not None else "",
            "batch_no": self.batch_no,
            "stocks": self.stocks,
            "price": self.price
        }
        return json_inv

