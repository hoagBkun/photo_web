# app/blueprints/admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.banner import Banner
from app.models.contact_info import ContactInfo
from app.models.pricing import Pricing
from app.models.pricing_page import PricingPage
from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial
from app.blueprints.admin.forms import BannerForm, PostForm, ContactInfoForm, UserForm, PricingForm, PricingPageForm, IntroSectionForm, PortfolioItemForm, ServiceCardForm, TestimonialForm, FeaturedPostForm
from functools import wraps
from werkzeug.utils import secure_filename
import os
import logging

admin_bp = Blueprint('admin', __name__)

# Setup logging
logging.basicConfig(filename='flask.log', level=logging.DEBUG)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    banner_count = Banner.query.count()
    post_count = Post.query.count()
    user_count = User.query.count()
    pricing_count = Pricing.query.count()
    return render_template('admin/dashboard.html',
                           banner_count=banner_count,
                           post_count=post_count,
                           user_count=user_count,
                           pricing_count=pricing_count)

@admin_bp.route('/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_banners():
    form = BannerForm()
    if form.validate_on_submit():
        try:
            file = form.image.data
            if not file or not allowed_file(file.filename):
                flash('Vui lòng chọn hình ảnh hợp lệ (jpg, jpeg, png, gif).', 'error')
                return redirect(url_for('admin.manage_banners'))
            filename = secure_filename(file.filename)
            file_path = os.path.join('app/static/uploads/banners', filename)
            os.makedirs('app/static/uploads/banners', exist_ok=True)
            file.save(file_path)
            banner = Banner(
                image_url=f'/static/uploads/banners/{filename}',
                title=form.title.data,
                description=form.description.data
            )
            db.session.add(banner)
            db.session.commit()
            flash('Thêm banner thành công!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            flash(f'Lỗi khi thêm banner: {str(e)}', 'error')
    banners = Banner.query.all()
    return render_template('admin/banners/home.html', form=form, banners=banners)

@admin_bp.route('/banners/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_banner(id):
    banner = Banner.query.get_or_404(id)
    form = BannerForm(obj=banner)
    if form.validate_on_submit():
        try:
            if form.image.data:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Hình ảnh không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.edit_banner', id=id))
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/banners', filename)
                os.makedirs('app/static/uploads/banners', exist_ok=True)
                file.save(file_path)
                if banner.image_url and banner.image_url != '/static/images/default.jpg':
                    old_file = os.path.join('app', banner.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                banner.image_url = f'/static/uploads/banners/{filename}'
            banner.title = form.title.data
            banner.description = form.description.data
            db.session.commit()
            flash('Cập nhật banner thành công!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật banner: {str(e)}', 'error')
    return render_template('admin/banners.html', form=form, banner=banner)

@admin_bp.route('/banners/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    try:
        if banner.image_url and banner.image_url != '/static/images/default.jpg':
            file_path = os.path.join('app', banner.image_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(banner)
        db.session.commit()
        flash('Xóa banner thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa banner: {str(e)}', 'error')
    return redirect(url_for('admin.manage_banners'))

@admin_bp.route('/posts', methods=['GET'])
@login_required
@admin_required
def manage_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin/posts.html', posts=posts)

@admin_bp.route('/posts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id
            )
            if form.image.data:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Ảnh bìa không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.add_post'))
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/posts', filename)
                os.makedirs('app/static/uploads/posts', exist_ok=True)
                file.save(file_path)
                post.image_url = f'/static/uploads/posts/{filename}'
            db.session.add(post)
            db.session.commit()
            flash('Thêm bài viết thành công!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            flash(f'Lỗi khi thêm bài viết: {str(e)}', 'error')
    return render_template('admin/post_form.html', form=form, title='Thêm bài viết')

@admin_bp.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        try:
            post.title = form.title.data
            post.content = form.content.data
            if form.image.data:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Ảnh bìa không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.edit_post', id=id))
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/posts', filename)
                os.makedirs('app/static/uploads/posts', exist_ok=True)
                file.save(file_path)
                if post.image_url and post.image_url != '/static/images/default.jpg':
                    old_file = os.path.join('app', post.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                post.image_url = f'/static/uploads/posts/{filename}'
            db.session.commit()
            flash('Cập nhật bài viết thành công!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật bài viết: {str(e)}', 'error')
    return render_template('admin/post_form.html', form=form, title='Sửa bài viết', post=post)

@admin_bp.route('/posts/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    try:
        if post.image_url and post.image_url != '/static/images/default.jpg':
            file_path = os.path.join('app', post.image_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(post)
        db.session.commit()
        flash('Xóa bài viết thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa bài viết: {str(e)}', 'error')
    return redirect(url_for('admin.manage_posts'))

@admin_bp.route('/upload_image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join('app/static/uploads/posts', filename)
            os.makedirs('app/static/uploads/posts', exist_ok=True)
            file.save(file_path)
            url = f'/static/uploads/posts/{filename}'
            return jsonify({'image': url})
        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500
    return jsonify({'error': 'Invalid file type.'}), 400

@admin_bp.route('/pricing', methods=['GET'])
@login_required
@admin_required
def manage_pricing():
    pricings = Pricing.query.all()
    return render_template('admin/pricing.html', pricings=pricings)

@admin_bp.route('/pricing/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_pricing():
    form = PricingForm()
    if form.validate_on_submit():
        try:
            pricing = Pricing(
                name=form.name.data,
                price=form.price.data,
                description=form.description.data,
                features=form.features.data,
                featured=form.featured.data
            )
            db.session.add(pricing)
            db.session.commit()
            flash('Thêm gói dịch vụ thành công!', 'success')
            return redirect(url_for('admin.manage_pricing'))
        except Exception as e:
            flash(f'Lỗi khi thêm gói dịch vụ: {str(e)}', 'error')
    return render_template('admin/pricing_form.html', form=form, title='Thêm gói dịch vụ')

@admin_bp.route('/pricing/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_pricing(id):
    pricing = Pricing.query.get_or_404(id)
    form = PricingForm(obj=pricing)
    if form.validate_on_submit():
        try:
            pricing.name = form.name.data
            pricing.price = form.price.data
            pricing.description = form.description.data
            pricing.features = form.features.data
            pricing.featured = form.featured.data
            db.session.commit()
            flash('Cập nhật gói dịch vụ thành công!', 'success')
            return redirect(url_for('admin.manage_pricing'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật gói dịch vụ: {str(e)}', 'error')
    return render_template('admin/pricing_form.html', form=form, title='Sửa gói dịch vụ', pricing=pricing)

@admin_bp.route('/pricing/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_pricing(id):
    pricing = Pricing.query.get_or_404(id)
    try:
        db.session.delete(pricing)
        db.session.commit()
        flash('Xóa gói dịch vụ thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa gói dịch vụ: {str(e)}', 'error')
    return redirect(url_for('admin.manage_pricing'))

@admin_bp.route('/pricing_page', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_pricing_page():
    form = PricingPageForm()
    pricing_page = PricingPage.query.first()
    if form.validate_on_submit():
        try:
            if not pricing_page:
                pricing_page = PricingPage()
                db.session.add(pricing_page)
            pricing_page.title = form.title.data
            pricing_page.description = form.description.data
            pricing_page.show_banner = form.show_banner.data
            db.session.commit()
            flash('Cập nhật nội dung trang bảng giá thành công!', 'success')
            return redirect(url_for('admin.manage_pricing_page'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật nội dung: {str(e)}', 'error')
    if pricing_page:
        form.title.data = pricing_page.title
        form.description.data = pricing_page.description
        form.show_banner.data = pricing_page.show_banner
    return render_template('admin/pricing_page.html', form=form, title='Quản lý Trang Bảng Giá')

@admin_bp.route('/contact', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_contact():
    form = ContactInfoForm()
    contact_info = ContactInfo.query.first()
    if form.validate_on_submit():
        try:
            if not contact_info:
                contact_info = ContactInfo()
                db.session.add(contact_info)
            contact_info.address = form.address.data
            contact_info.phone = form.phone.data
            contact_info.email = form.email.data
            contact_info.social_links = form.social_links.data
            db.session.commit()
            flash('Cập nhật thông tin liên hệ thành công!', 'success')
            return redirect(url_for('admin.manage_contact'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật thông tin liên hệ: {str(e)}', 'error')
    if contact_info:
        form.address.data = contact_info.address
        form.phone.data = contact_info.phone
        form.email.data = contact_info.email
        form.social_links.data = contact_info.social_links
    return render_template('admin/contact.html', form=form)

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        try:
            if User.query.filter_by(username=form.username.data).first() and User.query.filter_by(username=form.username.data).first().id != user.id:
                flash('Tên người dùng đã tồn tại.', 'error')
                return redirect(url_for('admin.edit_user', id=user.id))
            if User.query.filter_by(email=form.email.data).first() and User.query.filter_by(email=form.email.data).first().id != user.id:
                flash('Email đã tồn tại.', 'error')
                return redirect(url_for('admin.edit_user', id=user.id))
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            db.session.commit()
            flash('Cập nhật người dùng thành công!', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật người dùng: {str(e)}', 'error')
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        if user.id == current_user.id:
            flash('Bạn không thể xóa chính mình!', 'error')
            return redirect(url_for('admin.manage_users'))
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa người dùng: {str(e)}', 'error')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/home', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_home():
    intro_form = IntroSectionForm()
    portfolio_form = PortfolioItemForm()
    service_form = ServiceCardForm()
    testimonial_form = TestimonialForm()
    featured_post_form = FeaturedPostForm()

    form_name = request.form.get('form_name')
    logging.debug(f"Form submitted: {form_name}")

    if form_name == 'intro' and intro_form.validate_on_submit():
        logging.debug("Processing intro form")
        try:
            intro = IntroSection.query.first()
            if not intro:
                intro = IntroSection()
                db.session.add(intro)
            intro.text = intro_form.text.data
            intro.cta_text = intro_form.cta_text.data
            intro.cta_url = intro_form.cta_url.data
            if intro_form.image.data:
                file = intro_form.image.data
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('app/static/uploads/home', filename)
                    os.makedirs('app/static/uploads/home', exist_ok=True)
                    file.save(file_path)
                    if intro.image_url and intro.image_url != '/static/images/default.jpg':
                        old_file = os.path.join('app', intro.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    intro.image_url = f'/static/uploads/home/{filename}'
                else:
                    flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.manage_home'))
            db.session.commit()
            flash('Cập nhật phần giới thiệu thành công!', 'success')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật phần giới thiệu: {str(e)}', 'error')
            logging.error(f"Intro form error: {str(e)}")

    if form_name == 'portfolio' and portfolio_form.validate_on_submit() and not request.form.get('portfolio_id'):
        logging.debug("Processing portfolio form")
        try:
            image_url = '/static/images/default.jpg'
            if portfolio_form.image.data:
                file = portfolio_form.image.data
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('app/static/uploads/home', filename)
                    os.makedirs('app/static/uploads/home', exist_ok=True)
                    file.save(file_path)
                    image_url = f'/static/uploads/home/{filename}'
                else:
                    flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.manage_home'))
            portfolio = PortfolioItem(
                title=portfolio_form.title.data,
                image_url=image_url
            )
            db.session.add(portfolio)
            db.session.commit()
            flash('Thêm portfolio thành công!', 'success')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi thêm portfolio: {str(e)}', 'error')
            logging.error(f"Portfolio form error: {str(e)}")

    if form_name == 'service' and service_form.validate_on_submit() and not request.form.get('service_id'):
        logging.debug("Processing service form")
        try:
            image_url = '/static/images/default.jpg'
            if service_form.image.data:
                file = service_form.image.data
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('app/static/uploads/home', filename)
                    os.makedirs('app/static/uploads/home', exist_ok=True)
                    file.save(file_path)
                    image_url = f'/static/uploads/home/{filename}'
                else:
                    flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.manage_home'))
            service = ServiceCard(
                title=service_form.title.data,
                description=service_form.description.data,
                image_url=image_url,
                cta_text=service_form.cta_text.data,
                cta_url=service_form.cta_url.data
            )
            db.session.add(service)
            db.session.commit()
            flash('Thêm dịch vụ thành công!', 'success')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi thêm dịch vụ: {str(e)}', 'error')
            logging.error(f"Service form error: {str(e)}")

    if form_name == 'testimonial' and testimonial_form.validate_on_submit() and not request.form.get('testimonial_id'):
        logging.debug("Processing testimonial form")
        try:
            testimonial = Testimonial(
                content=testimonial_form.content.data,
                author=testimonial_form.author.data
            )
            db.session.add(testimonial)
            db.session.commit()
            flash('Thêm đánh giá thành công!', 'success')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi thêm đánh giá: {str(e)}', 'error')
            logging.error(f"Testimonial form error: {str(e)}")

    if form_name == 'featured_post' and featured_post_form.validate_on_submit():
        logging.debug("Processing featured post form")
        try:
            post_id = featured_post_form.post_id.data
            post = Post.query.get_or_404(post_id)
            if not post.is_featured:
                if Post.query.filter_by(is_featured=True).count() >= 3:  # Giới hạn 3 bài
                    flash('Đã đủ 3 bài viết nổi bật!', 'warning')
                    return redirect(url_for('admin.manage_home'))
                post.is_featured = True
                db.session.commit()
                flash('Thêm bài viết nổi bật thành công!', 'success')
            else:
                flash('Bài viết này đã được chọn!', 'warning')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi thêm bài viết nổi bật: {str(e)}', 'error')
            logging.error(f"Featured post form error: {str(e)}")

    intro = IntroSection.query.first()
    portfolios = PortfolioItem.query.all()
    services = ServiceCard.query.all()
    testimonials = Testimonial.query.all()
    featured_posts = Post.query.filter_by(is_featured=True).all()

    if intro:
        intro_form.text.data = intro.text
        intro_form.cta_text.data = intro.cta_text
        intro_form.cta_url.data = intro.cta_url

    return render_template('admin/home.html',
                          intro_form=intro_form,
                          portfolio_form=portfolio_form,
                          service_form=service_form,
                          testimonial_form=testimonial_form,
                          featured_post_form=featured_post_form,
                          intro=intro,
                          portfolios=portfolios,
                          services=services,
                          testimonials=testimonials,
                          featured_posts=featured_posts)

@admin_bp.route('/home/portfolio/edit/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_portfolio(id):
    portfolio = PortfolioItem.query.get_or_404(id)
    return jsonify({
        'id': portfolio.id,
        'title': portfolio.title,
        'image_url': portfolio.image_url
    })

@admin_bp.route('/home/service/edit/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_service(id):
    service = ServiceCard.query.get_or_404(id)
    return jsonify({
        'id': service.id,
        'title': service.title,
        'description': service.description,
        'cta_text': service.cta_text,
        'cta_url': service.cta_url,
        'image_url': service.image_url
    })

@admin_bp.route('/home/testimonial/edit/<int:id>', methods=['GET'])
@login_required
@admin_required
def get_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    return jsonify({
        'id': testimonial.id,
        'content': testimonial.content,
        'author': testimonial.author
    })

@admin_bp.route('/home/<string:model>/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_home_item(model, id):
    try:
        if model == 'portfolio':
            item = PortfolioItem.query.get_or_404(id)
            form = PortfolioItemForm()
            if form.validate_on_submit():
                item.title = form.title.data
                if form.image.data:
                    file = form.image.data
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join('app/static/uploads/home', filename)
                        os.makedirs('app/static/uploads/home', exist_ok=True)
                        file.save(file_path)
                        if item.image_url and item.image_url != '/static/images/default.jpg':
                            old_file = os.path.join('app', item.image_url.lstrip('/'))
                            if os.path.exists(old_file):
                                os.remove(old_file)
                        item.image_url = f'/static/uploads/home/{filename}'
                db.session.commit()
                flash('Cập nhật portfolio thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Lỗi {field}: {error}', 'error')
        elif model == 'service':
            item = ServiceCard.query.get_or_404(id)
            form = ServiceCardForm()
            if form.validate_on_submit():
                item.title = form.title.data
                item.description = form.description.data
                item.cta_text = form.cta_text.data
                item.cta_url = form.cta_url.data
                if form.image.data:
                    file = form.image.data
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join('app/static/uploads/home', filename)
                        os.makedirs('app/static/uploads/home', exist_ok=True)
                        file.save(file_path)
                        if item.image_url and item.image_url != '/static/images/default.jpg':
                            old_file = os.path.join('app', item.image_url.lstrip('/'))
                            if os.path.exists(old_file):
                                os.remove(old_file)
                        item.image_url = f'/static/uploads/home/{filename}'
                db.session.commit()
                flash('Cập nhật dịch vụ thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Lỗi {field}: {error}', 'error')
        elif model == 'testimonial':
            item = Testimonial.query.get_or_404(id)
            form = TestimonialForm()
            if form.validate_on_submit():
                item.content = form.content.data
                item.author = form.author.data
                db.session.commit()
                flash('Cập nhật đánh giá thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Lỗi {field}: {error}', 'error')
        else:
            flash('Mục không hợp lệ.', 'error')
            return redirect(url_for('admin.manage_home'))
    except Exception as e:
        flash(f'Lỗi khi cập nhật mục: {str(e)}', 'error')
        logging.error(f"Edit {model} error: {str(e)}")
    return redirect(url_for('admin.manage_home'))

@admin_bp.route('/home/<string:model>/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_home_item(model, id):
    try:
        if model == 'portfolio':
            item = PortfolioItem.query.get_or_404(id)
            if item.image_url and item.image_url != '/static/images/default.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(item)
            flash('Xóa portfolio thành công!', 'success')
        elif model == 'service':
            item = ServiceCard.query.get_or_404(id)
            if item.image_url and item.image_url != '/static/images/default.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(item)
            flash('Xóa dịch vụ thành công!', 'success')
        elif model == 'testimonial':
            item = Testimonial.query.get_or_404(id)
            db.session.delete(item)
            flash('Xóa đánh giá thành công!', 'success')
        elif model == 'featured_post':
            item = Post.query.get_or_404(id)
            item.is_featured = False
            db.session.commit()
            flash('Xóa bài viết nổi bật thành công!', 'success')
        else:
            flash('Mục không hợp lệ.', 'error')
            return redirect(url_for('admin.manage_home'))
        db.session.commit()
        flash('Xóa mục thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa mục: {str(e)}', 'error')
        logging.error(f"Delete {model} error: {str(e)}")
    return redirect(url_for('admin.manage_home'))