from flask import Flask, make_response, redirect, render_template, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fuyuan:fuyuan@127.0.0.1/seesun-product-development'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route("/", methods=['GET', 'POST'])
def index():
    form = ProductCategoryForm()
    pcs = ProductCategory.query.all()
    if form.validate_on_submit():
        pc = ProductCategory(name=form.name.data)
        db.session.add(pc)
        flash('创建成功!')
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, pcs=pcs )


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)


@app.route("/response")
def response_v():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response


@app.route("/redirect")
def redirect_v():
    return redirect('http://www.baidu.com')


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


class ProductCategoryForm(FlaskForm):
    name = StringField('产品目录名称 ', validators=[DataRequired()])
    submit = SubmitField('创建产品目录')


class SkuFeatureForm(FlaskForm):
    product_category_id = HiddenField(validators=[DataRequired()])
    name = StringField('特征名称 ', validators=[DataRequired()])
    description = TextAreaField('特征描述 ')
    sku_feature_type = StringField('特征类别')
    submit = SubmitField('创建产品特征')


class SkuOptionForm(FlaskForm):
    sku_feature_id = HiddenField(validators=[DataRequired()])
    name = StringField('特征值 ', validators=[DataRequired()])
    submit = SubmitField('创建特征值')


class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    sku_features = db.relationship('SkuFeature', backref='product_category')
    products = db.relationship('Product', backref='product_category')

    def __repr__(self):
        return '<ProductCategory %r>' % self.name


class SkuFeature(db.Model):
    __tablename__ = 'sku_features'
    id = db.Column(db.Integer, primary_key=True)
    product_category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    sku_feature_type = db.Column(db.String)
    sku_options = db.relationship('SkuOption', backref='sku_feature')

    def __repr__(self):
        return '<SkuFeature %r>' % self.name


class SkuOption(db.Model):
    __tablename__ = 'sku_options'
    id = db.Column(db.Integer, primary_key=True)
    sku_feature_id = db.Column(db.Integer, db.ForeignKey('sku_features.id'))
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<SkuOption %r>' % self.name

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
    name = db.Column(db.String(64), unique=True)
    code = db.Column(db.String(32), unique=True)
    description = db.Column(db.Text)
    product_image_links = db.Column(db.String(256))
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
    thumbnail = db.Column(db.String(256))
    sku_options = db.relationship('SkuOption', secondary=products_sku_options,
                                  backref=db.backref('product_skus', lazy='dynamic'), lazy='dynamic')


if __name__ == '__main__':
    manager.run()
