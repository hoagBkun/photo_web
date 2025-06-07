from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.banner import Banner
from app.models.contact_info import ContactInfo
from app.models.pricing import Pricing
from app.models.pricing_page import PricingPage
from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial, BlogCard
from app.blueprints.admin.forms import BannerForm, PostForm, ContactInfoForm, UserForm, PricingForm, PricingPageForm, IntroSectionForm, PortfolioItemForm, ServiceCardForm, TestimonialForm, BlogCardForm
from functools import wraps
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__)

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
                return redirect(url_for('admin.redirect_banners'))
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
            return redirect(url_for('admin.redirect_banners'))
        except Exception as e:
            flash(f'LFLỗi khi thêm banner: {str(e)}', 'error')
    banners = Banner.query.all()
    return render_template('admin/banners/home.html', form=form, banners=banners)

@admin_bp.route('/banners/edit/<int:id>/edit', methods=['GET', 'POST'])
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
                if banner.image_url and banner.image_url != '/static/uploads/default.jpg':
                    old_file = os.path.join('app', banner.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                banner.image_url = f'/static/uploads/banners/{filename}'
            banner.title = form.title.data
            banner.description = form.description.data
            db.session.commit()
            flash('Cập nhật banner thành công!', 'success')
            return redirect(url_for('admin.redirect_banners'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật banner: {str(e)}', 'error')
    return render_template('admin/banners.html', form=form, banner=banner)

@admin_bp.route('/banners/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    try:
        if banner.image_url and banner.image_url != '/static/uploads/default.jpg':
            file_path = os.path.join('app', banner.image_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(banner)
        db.session.commit()
        flash('Xóa banner thành công!', 'success')
    except Exception as e:
        flash(f'LFLỗi khi xóa banner: {str(e)}', 'error')
    return redirect(url_for('admin.redirect_banners'))

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
            return redirect(url_for('admin.redirect_posts'))
        except Exception as e:
            flash(f'LFLỗi khi thêm bài viết: {str(e)}', 'error')
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
                if post.image_url and post.image_url != '/static/uploads/default.jpg':
                    old_file = os.path.join('app', post.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                post.image_url = f'/static/uploads/posts/{filename}'
            db.session.commit()
            flash('Cập nhật bài viết thành công!', 'success')
            return redirect(url_for('admin.redirect_posts'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật bài viết: {str(e)}', 'error')
    return render_template('admin/post_form.html', form=form, title='Sửa bài viết', post=post)

@admin_bp.route('/posts/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    try:
        if post.image_url and post.image_url != '/static/uploads/default.jpg':
            file_path = os.path.join('app', post.image_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(post)
        db.session.commit()
        flash('Xóa bài viết thành công!', 'success')
    except Exception as e:
        flash(f'LFLỗi khi xóa bài viết: {str(e)}', 'error')
    return redirect(url_for('admin.redirect_posts'))

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
            return redirect(url_for('admin.redirect_pricing'))
        except Exception as e:
            flash(f'LFLỗi khi thêm gói dịch vụ: {str(e)}', 'error')
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
            return redirect(url_for('admin.redirect_pricing'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật gói dịch vụ: {str(e)}', 'error')
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
        flash(f'LFLỗi khi xóa gói dịch vụ: {str(e)}', 'error')
    return redirect(url_for('admin.redirect_pricing'))

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
            return redirect(url_for('admin.redirect_pricing_page'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật nội dung: {str(e)}', 'error')
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
            return redirect(url_for('admin.redirect_contact'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật thông tin liên hệ: {str(e)}', 'error')
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
            return redirect(url_for('admin.redirect_users'))
        except Exception as e:
            flash(f'LFLỗi khi cập nhật người dùng: {str(e)}', 'error')
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        if user.id == current_user.id:
            flash('Bạn không thể xóa chính mình!', 'error')
            return redirect(url_for('admin.redirect_users'))
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    except Exception as e:
        flash(f'LFLỗi khi xóa người dùng: {str(e)}', 'error')
    return redirect(url_for('admin.redirect_users'))

@admin_bp.route('/home', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_home():
    intro_form = IntroSectionForm()
    portfolio_form = PortfolioItemForm()
    service_form = ServiceCardForm()
    testimonial_form = TestimonialForm()
    blog_form = BlogCardForm()

    if intro_form.validate_on_submit():
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
                    if intro.image_url and intro.image_url != 'default_intro.jpg':
                        old_file = os.path.join('app', intro.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            try:
                                os.remove(old_file)
                            except Exception as e:
                                pass
                    intro.image_url = f'/static/uploads/home/{filename}'
                else:
                    flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif)', 'error')
                    return redirect(url_for('admin.manage_home'))
            db.session.commit()
            flash('Cập nhật phần giới thiệu thành công!', 'success')
            return redirect(url_for('admin.manage_home'))
        except Exception as e:
            flash(f'Lỗi khi cập nhật phần giới thiệu: {str(e)}', 'error')
            return redirect(url_for('admin.manage_home'))

    if portfolio_form.validate_on_submit():
        try:
            file = portfolio_form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/home', filename)
                os.makedirs('app/static/uploads/home', exist_ok=True)
                file.save(file_path)
                portfolio = PortfolioItem(
                    title=portfolio_form.title.data,
                    image_url=f'/static/uploads/home/{filename}'
                )
                db.session.add(portfolio)
                db.session.commit()
                flash('Thêm portfolio thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
        except Exception as e:
            flash(f'Lỗi khi thêm portfolio: {str(e)}', 'error')
        return redirect(url_for('admin.manage_home'))

    if service_form.validate_on_submit():
        try:
            file = service_form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/home', filename)
                os.makedirs('app/static/uploads/home', exist_ok=True)
                file.save(file_path)
                service = ServiceCard(
                    title=service_form.title.data,
                    description=service_form.description.data,
                    image_url=f'/static/uploads/home/{filename}',
                    cta_text=service_form.cta_text.data,
                    cta_url=service_form.cta_url.data
                )
                db.session.add(service)
                db.session.commit()
                flash('Thêm dịch vụ thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
        except Exception as e:
            flash(f'Lỗi khi thêm dịch vụ: {str(e)}', 'error')
        return redirect(url_for('admin.manage_home'))

    if testimonial_form.validate_on_submit():
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
        return redirect(url_for('admin.manage_home'))

    if blog_form.validate_on_submit():
        try:
            file = blog_form.image.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads/home', filename)
                os.makedirs('app/static/uploads/home', exist_ok=True)
                file.save(file_path)
                blog = BlogCard(
                    title=blog_form.title.data,
                    description=blog_form.description.data,
                    image_url=f'/static/uploads/home/{filename}',
                    cta_text=blog_form.cta_text.data,
                    cta_url=blog_form.cta_url.data
                )
                db.session.add(blog)
                db.session.commit()
                flash('Thêm bài viết nổi bật thành công!', 'success')
                return redirect(url_for('admin.manage_home'))
            else:
                flash('Vui lòng chọn file hợp lệ (jpg, jpeg, png, gif).', 'error')
        except Exception as e:
            flash(f'Lỗi khi thêm bài viết: {str(e)}', 'error')
        return redirect(url_for('admin.manage_home'))

    intro = IntroSection.query.first()
    portfolios = PortfolioItem.query.all()
    services = ServiceCard.query.all()
    testimonials = Testimonial.query.all()
    blogs = BlogCard.query.all()

    if intro:
        intro_form.text.data = intro.text
        intro_form.cta_text.data = intro.cta_text
        intro_form.cta_url.data = intro.cta_url

    return render_template('admin/home.html', 
                          intro_form=intro_form,
                          portfolio_form=portfolio_form,
                          service_form=service_form,
                          testimonial_form=testimonial_form,
                          blog_form=blog_form,
                          intro=intro,
                          portfolios=portfolios,
                          services=services,
                          testimonials=testimonials,
                          blogs=blogs)

@admin_bp.route('/home/delete/<string:model>/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_home_item(model, id):
    try:
        if model == 'portfolio':
            item = PortfolioItem.query.get_or_404(id)
            if item.image_url and item.image_url != 'default_intro.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
        elif model == 'service':
            item = ServiceCard.query.get_or_404(id)
            if item.image_url and item.image_url != 'default_intro.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
        elif model == 'testimonial':
            item = Testimonial.query.get_or_404(id)
        elif model == 'blog':
            item = BlogCard.query.get_or_404(id)
            if item.image_url and item.image_url != 'default_intro.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash('Mục không hợp lệ.', 'error')
            return redirect(url_for('admin.manage_home'))

        db.session.delete(item)
        db.session.commit()
        flash('Xóa mục thành công!', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa mục: {str(e)}', 'error')
    return redirect(url_for('admin.manage_home'))