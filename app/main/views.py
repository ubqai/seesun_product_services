from . import main
from flask import make_response, redirect, render_template, url_for, flash, request, current_app
from .. import db, uploaded_images
from ..models import ProductCategory, SkuFeature, SkuOption, Product, ProductSku
from .forms import ProductCategoryForm, SkuFeatureForm, SkuOptionForm, ProductForm, ProductSkuForm
from werkzeug.utils import secure_filename
from collections import OrderedDict
from os import path
import os
import datetime
import random


@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route("/product_categories", methods=['GET', 'POST'])
def product_categories():
    form = ProductCategoryForm()
    pcs = ProductCategory.query.all()
    if form.validate_on_submit():
        pc = ProductCategory(name=form.name.data)
        db.session.add(pc)
        flash('创建成功!')
        return redirect(url_for('main.product_categories'))
    return render_template('product_categories.html', form=form, pcs=pcs)


@main.route("/sku_features", methods=['GET', 'POST'])
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
        return redirect(url_for('main.product_categories'))
    return render_template('sku_features.html', form=form, category=category)


@main.route("/sku_feature_edit/<int:id>", methods=['GET', 'POST'])
def sku_feature_edit(id):
    sku_feature = SkuFeature.query.get_or_404(id)
    category = sku_feature.product_category
    form = SkuFeatureForm(name=sku_feature.name, description=sku_feature.description, product_category_id=category.id)
    if form.validate_on_submit():
        sku_feature.name = form.name.data,
        sku_feature.description = form.description.data
        db.session.add(sku_feature)
        flash('修改成功!')
        return redirect(url_for('main.product_categories'))
    return render_template('sku_feature_edit.html', form=form, category=category)


@main.route("/sku_options", methods=['GET', 'POST'])
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
        return redirect(url_for('main.product_categories'))
    return render_template('sku_options.html', form=form, sku_feature=sku_feature)


@main.route("/sku_option_edit/<int:id>", methods=['GET', 'POST'])
def sku_option_edit(id):
    sku_option = SkuOption.query.get_or_404(id)
    sku_feature = sku_option.sku_feature
    form = SkuOptionForm(name=sku_option.name, sku_feature_id=sku_feature.id)
    if form.validate_on_submit():
        sku_option.name = form.name.data
        db.session.add(sku_option)
        flash('修改成功!')
        return redirect(url_for('main.product_categories'))
    return render_template('sku_option_edit.html', form=form, sku_feature=sku_feature)


@main.route("/products_manage", methods=['GET'])
def products_manage():
    pcs = ProductCategory.query.all()
    return render_template('products_manage.html', pcs=pcs)


@main.route("/products_show/<int:id>", methods=['GET'])
def products_show(id):
    product = Product.query.get_or_404(id)
    return render_template("products_show.html", product=product)


@main.route("/products", methods=['GET', 'POST'])
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
        return redirect(url_for("main.product_skus", product_id=product.id))
    return render_template("products.html", form=form, category=category)


@main.route("/products/<int:id>", methods=['GET', 'POST'])
def product_edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(name=product.name, code=product.code, description=product.description)
    category = product.product_category
    if form.validate_on_submit():
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
        product.name = form.name.data
        product.code = form.code.data
        product.description = form.description.data
        product.product_image_links = filenames
        db.session.add(product)
        db.session.commit()
        flash("修改成功")
        return redirect(url_for("main.products_show", id=product.id))
    return render_template("product_edit.html", form=form, category=category)


@main.route("/product_skus", methods=['GET', 'POST'])
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
        return redirect(url_for("main.products_show", id=product.id))
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


@main.route('/ckupload/', methods=['POST'])
def ckupload():
    error = ''
    url = ''
    callback = request.args.get('CKEditorFuncNum')
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(main.static_folder, 'upload/ckupload', rnd_name)
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
            url = url_for('.static', filename='%s/%s' % ('upload/ckupload', rnd_name))
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']