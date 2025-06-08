from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.banner import Banner
from app.models.pricing import Pricing
from app.models.pricing_page import PricingPage
from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial
from app.models.post import Post  # Thêm import Post
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    intro = IntroSection.query.first()
    portfolios = PortfolioItem.query.order_by(PortfolioItem.created_at.desc()).limit(10).all()
    services = ServiceCard.query.all()
    testimonials = Testimonial.query.all()
    featured_posts = Post.query.filter_by(is_featured=True).limit(2).all()  # Thay BlogCard bằng Post
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/home.html',
                           intro=intro,
                           portfolios=portfolios,
                           services=services,
                           testimonials=testimonials,
                           featured_posts=featured_posts,  # Thay blogs bằng featured_posts
                           banners=banners)

@main.route('/introduce')
def introduce():
    banners = Banner.query.order_by(Banner.created_at.desc()).limit(3).all()
    return render_template('main/introduce.html', banners=banners)

@main.route('/pricing')
def pricing():
    pricings = Pricing.query.all()
    pricing_page = PricingPage.query.first()
    banners = Banner.query.order_by(Banner.created_at.desc()).limit(3).all() if pricing_page and pricing_page.show_banner else []
    return render_template('main/pricing.html', pricings=pricings, pricing_page=pricing_page, banners=banners)

@main.route('/contact')
def contact():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/contact.html', banners=banners)

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    try:
        new_username = request.form['username']
        new_email = request.form['email']
        new_phone = request.form['phone']
        new_address = request.form.get('address')

        if new_username != user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != user.id:
                flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'error')
                return redirect(url_for('main.profile'))

        if new_email != user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user.id:
                flash('Email đã tồn tại. Vui lòng chọn email khác.', 'error')
                return redirect(url_for('main.profile'))

        user.username = new_username
        user.email = new_email
        user.phone = new_phone
        user.address = new_address

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs('app/static/avatars', exist_ok=True)
                file_path = os.path.join('app/static/avatars', filename)
                file.save(file_path)
                if user.avatar and user.avatar != 'default_avatar.png':
                    old_file = os.path.join('app/static/avatars', user.avatar)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                user.avatar = filename

        db.session.commit()
        flash('Thông tin cá nhân đã được cập nhật thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi cập nhật hồ sơ: {str(e)}', 'error')
    return redirect(url_for('main.profile'))