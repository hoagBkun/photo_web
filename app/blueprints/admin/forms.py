from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class BannerForm(FlaskForm):
    image = FileField('Hình ảnh Banner', validators=[DataRequired()])
    title = StringField('Tiêu đề', validators=[DataRequired()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    submit = SubmitField('Lưu')

class PostForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired()])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    image = FileField('Hình ảnh bài viết', validators=[Optional()])
    submit = SubmitField('Lưu')

class ContactInfoForm(FlaskForm):
    address = StringField('Địa chỉ', validators=[Optional()])
    phone = StringField('Số điện thoại', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    submit = SubmitField('Lưu')

class UserForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Quyền quản trị')
    submit = SubmitField('Lưu')