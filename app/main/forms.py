from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from flaskckeditor import CKEditor


class ProductCategoryForm(FlaskForm):
    name = StringField('产品目录名称 ', validators=[DataRequired()])
    submit = SubmitField('提交')


class SkuFeatureForm(FlaskForm):
    product_category_id = HiddenField(validators=[DataRequired()])
    name = StringField('属性名称 ', validators=[DataRequired()])
    description = TextAreaField('属性描述 ')
    submit = SubmitField('提交')


class SkuOptionForm(FlaskForm):
    sku_feature_id = HiddenField(validators=[DataRequired()])
    name = StringField('属性值 ', validators=[DataRequired()])
    submit = SubmitField('提交')


class ProductForm(FlaskForm, CKEditor):
    name = StringField('产品名称', validators=[DataRequired()])
    code = StringField('产品代码')
    description = TextAreaField('产品描述')
    submit = SubmitField('提交')


class ProductSkuForm(FlaskForm):
    submit = SubmitField('提交')