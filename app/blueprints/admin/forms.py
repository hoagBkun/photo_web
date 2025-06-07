from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired, Email, Optional, Length, URL

class BannerForm(FlaskForm):
    image = FileField('Hình ảnh Banner', validators=[DataRequired()])
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả', validators=[Optional()])
    submit = SubmitField('Lưu')

class PostForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    image = FileField('Ảnh bìa', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class ContactInfoForm(FlaskForm):
    address = StringField('Địa chỉ', validators=[Optional()])
    phone = StringField('Số điện thoại', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    social_links = TextAreaField('Liên kết mạng xã hội (mỗi dòng 1 link)', validators=[Optional()])
    submit = SubmitField('Lưu')

class UserForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Quyền quản trị')
    submit = SubmitField('Lưu')

class PricingForm(FlaskForm):
    name = StringField('Tên gói', validators=[DataRequired(), Length(max=100)])
    price = FloatField('Giá', validators=[DataRequired()])
    description = TextAreaField('Mô tả', validators=[Optional()])
    features = TextAreaField('Tính năng (mỗi dòng 1 tính năng)', validators=[Optional()])
    featured = BooleanField('Gói nổi bật', default=False)
    submit = SubmitField('Lưu')

class PricingPageForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Mô tả', validators=[DataRequired()])
    show_banner = BooleanField('Hiển thị Banner', default=True)
    submit = SubmitField('Lưu')

class IntroSectionForm(FlaskForm):
    text = TextAreaField('Văn bản', validators=[DataRequired(), Length(max=500)])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=50)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL()])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class PortfolioItemForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    image = FileField('Hình ảnh', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class ServiceCardForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Mô tả', validators=[DataRequired(), Length(max=500)])
    image = FileField('Hình ảnh', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=50)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL()])
    submit = SubmitField('Lưu')

class TestimonialForm(FlaskForm):
    content = TextAreaField('Nội dung', validators=[DataRequired(), Length(max=500)])
    author = StringField('Tác giả', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Lưu')

class BlogCardForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Mô tả', validators=[DataRequired(), Length(max=500)])
    image = FileField('Hình ảnh', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=50)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL()])
    submit = SubmitField('Lưu')