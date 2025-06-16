from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FloatField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, Length, URL
from app.models.post import Post

class BannerForm(FlaskForm):
    image = FileField('Hình ảnh Banner', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=1000)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Lưu')

class EditBannerForm(FlaskForm):
    image = FileField('Hình ảnh Banner', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=1000)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=5000)])
    submit = SubmitField('Lưu')

class PostForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Nội dung', validators=[DataRequired(), Length(max=100000)])
    image = FileField('Ảnh bìa', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class UserForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Mật khẩu', validators=[Optional(), Length(min=6, max=128)])
    is_admin = BooleanField('Quyền quản trị', default=False)
    submit = SubmitField('Lưu')

class PricingForm(FlaskForm):
    name = StringField('Tên gói dịch vụ', validators=[DataRequired(), Length(max=1000)])
    price = FloatField('Giá tiền (VNĐ)', validators=[DataRequired()])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=5000)])
    features = TextAreaField('Tính năng (mỗi dòng một tính năng)', validators=[Optional(), Length(max=10000)])
    featured = BooleanField('Gói nổi bật', default=False)
    submit = SubmitField('Lưu')

class PricingPageForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=500)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=10000)])
    show_banner = BooleanField('Hiển thị banner', default=False)
    submit = SubmitField('Lưu')

class IntroSectionForm(FlaskForm):
    text = TextAreaField('Văn bản', validators=[DataRequired(), Length(max=5000)])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=500)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL(), Length(max=255)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class PortfolioItemForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=1000)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class ServiceCardForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=1000)])
    description = TextAreaField('Mô tả', validators=[DataRequired(), Length(max=5000)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=500)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL(), Length(max=255)])
    submit = SubmitField('Lưu')

class TestimonialForm(FlaskForm):
    content = TextAreaField('Nội dung', validators=[DataRequired(), Length(max=5000)])
    author = StringField('Tác giả', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Lưu')

class FeaturedPostForm(FlaskForm):
    post_id = SelectField('Chọn bài viết', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Thêm vào Bài viết nổi bật')

    def __init__(self, *args, **kwargs):
        super(FeaturedPostForm, self).__init__(*args, **kwargs)
        self.post_id.choices = [(post.id, post.title) for post in Post.query.order_by(Post.created_at.desc()).all()]

class IntroduceSectionForm(FlaskForm):
    text = TextAreaField('Văn bản', validators=[DataRequired(), Length(max=10000)])
    cta_text = StringField('Nút CTA', validators=[DataRequired(), Length(max=500)])
    cta_url = StringField('Link CTA', validators=[DataRequired(), URL(), Length(max=255)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class TeamMemberForm(FlaskForm):
    name = StringField('Tên', validators=[DataRequired(), Length(max=1000)])
    role = StringField('Vai trò', validators=[DataRequired(), Length(max=1000)])
    description = TextAreaField('Mô tả', validators=[Optional(), Length(max=5000)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class MissionSectionForm(FlaskForm):
    text = TextAreaField('Văn bản', validators=[DataRequired(), Length(max=10000)])
    image = FileField('Hình ảnh', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Chỉ cho phép ảnh!')])
    submit = SubmitField('Lưu')

class ContactInfoForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Email(), Length(max=255)])
    hotline = StringField('Hotline', validators=[Optional(), Length(max=20)])
    fanpage = StringField('Fanpage URL', validators=[Optional(), URL(), Length(max=255)])
    submit = SubmitField('Lưu')

class LocationForm(FlaskForm):
    name = StringField('Tên cơ sở', validators=[DataRequired(), Length(max=1000)])
    address = TextAreaField('Địa chỉ', validators=[DataRequired(), Length(max=255)])
    google_maps_link = StringField('Google Maps Link', validators=[Optional(), URL(), Length(max=10000)])
    submit = SubmitField('Lưu')

class ContactForm(FlaskForm):
    name = StringField('Họ và Tên', validators=[DataRequired(), Length(max=1000)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField('Số Điện Thoại', validators=[DataRequired(), Length(max=20)])
    message = TextAreaField('Tin Nhắn', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField('Gửi')