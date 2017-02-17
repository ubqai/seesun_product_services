from . import db


class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sku_features = db.relationship('SkuFeature', backref='product_category')
    products = db.relationship('Product', backref='product_category')

    def __repr__(self):
        return '<ProductCategory %r>' % self.name

    def to_json(self):
        json_category = {
            "id": self.id,
            "name": self.name,
            "features": [feature.to_json() for feature in self.sku_features]
        }
        return json_category


class SkuFeature(db.Model):
    __tablename__ = 'sku_features'
    id = db.Column(db.Integer, primary_key=True)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    sku_feature_type = db.Column(db.String)
    sku_options = db.relationship('SkuOption', backref='sku_feature')

    def __repr__(self):
        return '<SkuFeature %r>' % self.name

    def to_json(self):
        json_feature = {
            "id": self.id,
            "name": self.name,
            "options": [option.to_json() for option in self.sku_options]
        }
        return json_feature


class SkuOption(db.Model):
    __tablename__ = 'sku_options'
    id = db.Column(db.Integer, primary_key=True)
    sku_feature_id = db.Column(db.Integer, db.ForeignKey('sku_features.id'))
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<SkuOption %r>' % self.name

    def to_json(self):
        json_option = {
            "id": self.id,
            "name": self.name
        }
        return json_option

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
    product_image_links = db.Column(db.JSON)
    rating = db.Column(db.Float)

    product_skus = db.relationship('ProductSku', backref='product')
    sku_options = db.relationship('SkuOption', secondary=products_and_skuoptions,
                                  backref=db.backref('products', lazy='dynamic'), lazy='dynamic')


class ProductSku(db.Model):
    __tablename__ = 'product_skus'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    code = db.Column(db.String(32), unique=True)
    price = db.Column(db.Float)
    stocks = db.Column(db.Integer)
    barcode = db.Column(db.String)
    hscode = db.Column(db.String)
    weight = db.Column(db.Float)
    thumbnail = db.Column(db.Text)
    sku_options = db.relationship('SkuOption', secondary=products_sku_options,
                                  backref=db.backref('product_skus', lazy='dynamic'), lazy='dynamic')