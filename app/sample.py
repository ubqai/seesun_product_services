from flask import Flask, make_response, redirect, render_template, url_for, flash, request
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flaskckeditor import CKEditor
from flask_uploads import UploadSet, IMAGES, configure_uploads
from werkzeug.utils import secure_filename
from collections import OrderedDict
from os import path
import os
import datetime
import random
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fuyuan:fuyuan@127.0.0.1/seesun-product-development'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_IMAGES_DEST'] = 'static/images/products'
app.config['UPLOADED_IMAGES_URL'] = '/static/images/products'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
uploaded_images = UploadSet('images', IMAGES)
configure_uploads(app, uploaded_images)
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'png', 'gif'])
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
    return render_template('index.html', current_time=datetime.datetime.utcnow(), form=form, pcs=pcs)


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


@app.route("/product_categories", methods=['GET', 'POST'])
def product_categories():
    form = ProductCategoryForm()
    pcs = ProductCategory.query.all()
    if form.validate_on_submit():
        pc = ProductCategory(name=form.name.data)
        db.session.add(pc)
        flash('创建成功!')
        return redirect(url_for('product_categories'))
    return render_template('product_categories.html', form=form, pcs=pcs)


@app.route("/sku_features", methods=['GET', 'POST'])
def sku_features():
    form = SkuFeatureForm()
    category = ProductCategory.query.get_or_404(request.args.get('category'))
    form.product_category_id.data = category.id
    if form.validate_on_submit():
        product_category = ProductCategory.query.get_or_404(request.form.get("product_category_id"))
        sku_feature = SkuFeature(
            name=form.name.data,
            description=form.description.data,
            product_category=product_category
        )
        db.session.add(sku_feature)
        flash('创建成功!')
        return redirect(url_for('product_categories'))
    return render_template('sku_features.html', form=form, category=category)


@app.route("/sku_options", methods=['GET', 'POST'])
def sku_options():
    form = SkuOptionForm()
    sku_feature = SkuFeature.query.get_or_404(request.args.get('sku_feature_id'))
    form.sku_feature_id.data = sku_feature.id
    if form.validate_on_submit():
        sku_feature = SkuFeature.query.get_or_404(request.form.get("sku_feature_id"))
        sku_option = SkuOption(
            name=form.name.data,
            sku_feature=sku_feature
        )
        db.session.add(sku_option)
        flash('创建成功!')
        return redirect(url_for('product_categories'))
    return render_template('sku_options.html', form=form, sku_feature=sku_feature)


@app.route("/products_manage", methods=['GET'])
def products_manage():
    pcs = ProductCategory.query.all()
    return render_template('products_manage.html', pcs=pcs)


@app.route("/products", methods=['GET', 'POST'])
def products():
    form = ProductForm()
    category = ProductCategory.query.get_or_404(request.args.get('category'))
    if form.validate_on_submit():
        product_category = ProductCategory.query.get_or_404(request.form.get("category_id"))
        upload_files = request.files.getlist('image_links[]')
        filenames = []
        for file in upload_files:
            if file and allowed_file(file.filename):
                try:
                    new_filename = secure_filename(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S') + file.filename)
                except:
                    parts = path.splitext(file.filename)
                    new_filename = secure_filename(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S') + parts[1])
                filename = (uploaded_images.save(file, name=new_filename))
                filenames.append(filename)
        selected_options = request.form.getlist("sku_options")
        product = Product(
            name=form.name.data,
            code=form.code.data,
            description=form.description.data,
            product_category=product_category,
            product_image_links=filenames
        )
        for option_id in selected_options:
            sku_option = SkuOption.query.get_or_404(option_id)
            product.sku_options.append(sku_option)
        db.session.add(product)
        db.session.commit()
        flash("产品创建成功")
        return redirect(url_for("product_skus", product_id=product.id))
    return render_template("products.html", form=form, category=category)


@app.route("/product_skus", methods=['GET', 'POST'])
def product_skus():
    form = ProductSkuForm()

    if form.validate_on_submit():
        nums = int(request.form.get('sku_nums'))
        product = Product.query.get_or_404(request.form.get('product_id'))
        for i in range(1, nums+1):
            option_ids = request.form.getlist("%dsku_option_ids[]" % i)
            upload_thumbnail = request.files.get('%dthumbnail' % i)
            filename = ""
            if upload_thumbnail is not None and allowed_file(upload_thumbnail.filename):
                try:
                    new_filename = secure_filename(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S') + upload_thumbnail.filename)
                except:
                    parts = path.splitext(upload_thumbnail.filename)
                    new_filename = secure_filename(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S') + parts[1])
                filename = (uploaded_images.save(upload_thumbnail, name=new_filename))
            code = request.form.get("%dcode" % i)
            price = request.form.get("%dprice" % i)
            stock = request.form.get("%dstock" % i)
            barcode = request.form.get("%dbarcode" % i)
            hscode = request.form.get("%dhscode" % i)
            weight = request.form.get("%dweight" % i)
            if price is not None and price != '':
                product_sku = ProductSku(
                    product=product,
                    code=code,
                    price=price,
                    stocks=stock,
                    barcode=barcode,
                    hscode=hscode,
                    weight=weight,
                    thumbnail=filename
                )
                db.session.add(product_sku)
                for option_id in option_ids:
                    sku_option = SkuOption.query.get_or_404(option_id)
                    product_sku.sku_options.append(sku_option)
        db.session.commit()
        flash("属性管理成功")
        return redirect(url_for("product_skus", product_id=product.id))
    else:
        product = Product.query.get_or_404(request.args.get('product_id'))
        sku_options = product.sku_options
        sku_features = {x.sku_feature for x in sku_options}
        sku_ft_dict = OrderedDict()
        sku_ft_num = 1
        for sku_ft in sorted(sku_features, key=lambda x: x.id):
            sku_ft_dict[sku_ft_num] = [sku_ft,
                                       sorted(set(sku_ft.sku_options) & set(product.sku_options.all()),
                                              key=lambda x: x.id)]
            sku_ft_num += 1
        return render_template("product_skus.html", form=form, product=product, sku_ft_dict=sku_ft_dict,
                               sku_ft_num=sku_ft_num-1)


# --- CKEditor file upload ---
def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/ckupload/', methods=['POST'])
def ckupload():
    error = ''
    url = ''
    callback = request.args.get('CKEditorFuncNum')
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload/ckupload', rnd_name)
        # check file path exists or not
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload/ckupload', rnd_name))
    else:
        error = 'post error'
    res = """
    <script type="text/javascript">
        window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>
    """ % (callback, url, error)
    response = make_response(res)
    response.headers['Content-Type'] = 'text/html'
    return response


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
    name = StringField('属性名称 ', validators=[DataRequired()])
    description = TextAreaField('属性描述 ')
    submit = SubmitField('创建属性名称')


class SkuOptionForm(FlaskForm):
    sku_feature_id = HiddenField(validators=[DataRequired()])
    name = StringField('属性值 ', validators=[DataRequired()])
    submit = SubmitField('创建属性值')


class ProductForm(FlaskForm, CKEditor):
    name = StringField('产品名称', validators=[DataRequired()])
    code = StringField('产品代码')
    description = TextAreaField('产品描述')
    submit = SubmitField('创建产品')


class ProductSkuForm(FlaskForm):
    submit = SubmitField('提交')


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    manager.run()
