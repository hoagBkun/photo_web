# Phần 2.1: Import các module và package
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.banner import Banner
from app.models.contact_info import ContactInfo, Location, Contact
from app.models.pricing import Pricing
from app.models.pricing_page import PricingPage
from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial
from app.models.introduce import IntroduceSection, TeamMember, MissionSection
from app.blueprints.admin.forms import (
    BannerForm, PostForm, ContactInfoForm, UserForm, PricingForm, PricingPageForm,
    IntroSectionForm, PortfolioItemForm, ServiceCardForm, TestimonialForm,
    FeaturedPostForm, IntroduceSectionForm, TeamMemberForm, MissionSectionForm,
    LocationForm, ContactForm, EditBannerForm
)
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import logging
from PIL import Image
import re

# Phần 2.2: Định nghĩa blueprint và decorator
admin_bp = Blueprint('admin', __name__)

# Setup logging
logging.basicConfig(
    filename='flask.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

# Phần 2.3: Hàm tiện ích
def allowed_file(filename):
    """Check if file has allowed extension."""
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, output_path, max_size):
    """Resize image to fit within max_size while maintaining aspect ratio."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(output_path, quality=85)
    except Exception as e:
        logging.error(f"Image resize error: {str(e)}")
        raise

def extract_iframe_src(iframe):
    """Extract src URL from iframe tag or return input if not iframe."""
    if iframe and iframe.startswith('<iframe'):
        match = re.search(r'src="([^"]+)"', iframe)
        if match:
            return match.group(1)
    return iframe

# Phần 2.4: Route quản lý dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    banner_count = Banner.query.count()
    post_count = Post.query.count()
    user_count = User.query.count()
    pricing_count = Pricing.query.count()
    team_member_count = TeamMember.query.count()
    location_count = Location.query.count()
    return render_template('admin/dashboard.html',
                           banner_count=banner_count,
                           post_count=post_count,
                           user_count=user_count,
                           pricing_count=pricing_count,
                           team_member_count=team_member_count,
                           location_count=location_count)

# Phần 2.5: Route quản lý banner
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
            upload_folder = 'app/static/uploads/banners'
            os.makedirs(upload_folder, exist_ok=True)
            original_path = os.path.join(upload_folder, filename)
            file.save(original_path)
            resized_filename = f"resized_{filename}"
            resized_path = os.path.join(upload_folder, resized_filename)
            resize_image(original_path, resized_path, max_size=(1200, 600))
            os.remove(original_path)
            banner = Banner(
                image_url=f'/static/uploads/banners/{resized_filename}',
                title=form.title.data,
                description=form.description.data
            )
            db.session.add(banner)
            db.session.commit()
            flash('Thêm banner thành công!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm banner: {str(e)}', 'error')
            logging.error(f"Error adding banner: {str(e)}")
    banners = Banner.query.all()
    return render_template('admin/banners.html', form=form, banners=banners)

@admin_bp.route('/banners/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_banner(id):
    banner = Banner.query.get_or_404(id)
    form = EditBannerForm(obj=banner)
    if form.validate_on_submit():
        try:
            if form.image.data:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Hình ảnh không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.edit_banner', id=id))
                filename = secure_filename(file.filename)
                upload_folder = 'app/static/uploads/banners'
                os.makedirs(upload_folder, exist_ok=True)
                original_path = os.path.join(upload_folder, filename)
                file.save(original_path)
                resized_filename = f"resized_{filename}"
                resized_path = os.path.join(upload_folder, resized_filename)
                resize_image(original_path, resized_path, max_size=(1200, 600))
                os.remove(original_path)
                if banner.image_url and banner.image_url != '/static/images/default.jpg':
                    old_file = os.path.join('app', banner.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                banner.image_url = f'/static/uploads/banners/{resized_filename}'
            banner.title = form.title.data
            banner.description = form.description.data
            db.session.commit()
            flash('Cập nhật banner thành công!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật banner: {str(e)}', 'error')
            logging.error(f"Error editing banner ID {id}: {str(e)}")
    return render_template('admin/edit_banner.html', form=form, banner=banner)

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
        return jsonify({'success': True, 'message': 'Xóa banner thành công!'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting banner ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xóa banner: {str(e)}'}), 500
    
# Phần 2.6: Route quản lý bài viết
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
            if form.image.data and form.image.data.filename:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Ảnh bìa không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.add_post'))
                filename = secure_filename(file.filename)
                upload_folder = 'app/static/uploads/posts'
                os.makedirs(upload_folder, exist_ok=True)
                original_path = os.path.join(upload_folder, filename)
                file.save(original_path)
                resized_filename = f"resized_{filename}"
                resized_path = os.path.join(upload_folder, resized_filename)
                resize_image(original_path, resized_path, max_size=(800, 400))
                os.remove(original_path)
                post.image_url = f'/static/uploads/posts/{resized_filename}'
            db.session.add(post)
            db.session.commit()
            flash('Thêm bài viết thành công!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi thêm bài viết: {str(e)}', 'error')
            logging.error(f"Error adding post: {str(e)}")
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
            if form.image.data and form.image.data.filename:
                file = form.image.data
                if not allowed_file(file.filename):
                    flash('Ảnh bìa không hợp lệ (jpg, jpeg, png, gif).', 'error')
                    return redirect(url_for('admin.edit_post', id=id))
                filename = secure_filename(file.filename)
                upload_folder = 'app/static/uploads/posts'
                os.makedirs(upload_folder, exist_ok=True)
                original_path = os.path.join(upload_folder, filename)
                file.save(original_path)
                resized_filename = f"resized_{filename}"
                resized_path = os.path.join(upload_folder, resized_filename)
                resize_image(original_path, resized_path, max_size=(800, 400))
                os.remove(original_path)
                if post.image_url and post.image_url != '/static/images/default.jpg':
                    old_file = os.path.join('app', post.image_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                post.image_url = f'/static/uploads/posts/{resized_filename}'
            db.session.commit()
            flash('Cập nhật bài viết thành công!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật bài viết: {str(e)}', 'error')
            logging.error(f"Error editing post ID {id}: {str(e)}")
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
        db.session.rollback()
        flash(f'Lỗi khi xóa bài viết: {str(e)}', 'error')
        logging.error(f"Error deleting post ID {id}: {str(e)}")
    return redirect(url_for('admin.manage_posts'))

@admin_bp.route('/upload_image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded.'}), 400
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = 'app/static/uploads/posts'
            os.makedirs(upload_folder, exist_ok=True)
            original_path = os.path.join(upload_folder, filename)
            file.save(original_path)
            resized_filename = f"resized_{filename}"
            resized_path = os.path.join(upload_folder, resized_filename)
            resize_image(original_path, resized_path, max_size=(800, 400))
            os.remove(original_path)
            url = f'/static/uploads/posts/{resized_filename}'
            return jsonify({'image': url})
        return jsonify({'error': 'Invalid file type.'}), 400
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

# Phần 2.7: Route quản lý bảng giá
@admin_bp.route('/pricing', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_pricing():
    logging.debug(f"Request: {request.method} {request.url} Form: {request.form}")
    pricing_page_form = PricingPageForm()
    pricing_form = PricingForm()
    form_name = request.form.get('form_name')
    logging.debug(f"Form submitted: {form_name}")

    if request.method == 'POST':
        try:
            if form_name == 'pricing_page' and pricing_page_form.validate_on_submit():
                logging.debug("Processing pricing page form")
                pricing_page = PricingPage.query.first()
                if not pricing_page:
                    pricing_page = PricingPage()
                    db.session.add(pricing_page)
                pricing_page.title = pricing_page_form.title.data
                pricing_page.description = pricing_page_form.description.data
                pricing_page.show_banner = pricing_page_form.show_banner.data
                db.session.commit()
                return jsonify({'success': True, 'message': 'Cập nhật thông tin trang bảng giá thành công!'})

            elif form_name == 'pricing' and pricing_form.validate_on_submit():
                logging.debug("Processing pricing form")
                pricing = Pricing(
                    name=pricing_form.name.data,
                    price=pricing_form.price.data,
                    description=pricing_form.description.data,
                    features=pricing_form.features.data,
                    featured=pricing_form.featured.data
                )
                db.session.add(pricing)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Thêm gói dịch vụ thành công!'})

            else:
                errors = {}
                for form in [pricing_page_form, pricing_form]:
                    if form.errors:
                        for field, errs in form.errors.items():
                            errors[field] = errs
                logging.error(f"Form validation errors: {errors}")
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        except Exception as e:
            db.session.rollback()
            logging.error(f"Form {form_name} error: {str(e)}")
            return jsonify({'success': False, 'error': f'Lỗi khi xử lý: {str(e)}'}), 500

    pricing_page = PricingPage.query.first()
    pricings = Pricing.query.all()

    if pricing_page:
        pricing_page_form.title.data = pricing_page.title
        pricing_page_form.description.data = pricing_page.description
        pricing_page_form.show_banner.data = pricing_page.show_banner

    return render_template('admin/pricing.html',
                           pricing_page_form=pricing_page_form,
                           pricing_form=pricing_form,
                           pricing_page=pricing_page,
                           pricings=pricings)

@admin_bp.route('/pricing/<model>/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_pricing(model, id):
    if model != 'pricing':
        return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400
    try:
        pricing = Pricing.query.get_or_404(id)
        form = PricingForm()
        if form.validate_on_submit():
            pricing.name = form.name.data
            pricing.price = form.price.data
            pricing.description = form.description.data
            pricing.features = form.features.data
            pricing.featured = form.featured.data
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Cập nhật gói dịch vụ thành công!',
                'data': {
                    'id': pricing.id,
                    'name': pricing.name,
                    'price': pricing.price,
                    'description': pricing.description,
                    'features': pricing.features,
                    'featured': pricing.featured
                }
            })
        else:
            errors = {field: errs for field, errs in form.errors.items()}
            logging.error(f"Form validation errors: {errors}")
            return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error editing pricing ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi cập nhật gói dịch vụ: {str(e)}'}), 500

@admin_bp.route('/pricing/<model>/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_pricing(model, id):
    if model != 'pricing':
        return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400
    try:
        pricing = Pricing.query.get_or_404(id)
        db.session.delete(pricing)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa gói dịch vụ thành công!'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting pricing ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xóa gói dịch vụ: {str(e)}'}), 500

# Phần 2.8: Route quản lý liên hệ
@admin_bp.route('/contact', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_contact():
    logging.debug(f"Request: {request.method} {request.url} Form: {request.form}")
    contact_info_form = ContactInfoForm()
    location_form = LocationForm()
    form_name = request.form.get('form_name')
    logging.debug(f"Form submitted: {form_name}")

    if request.method == 'POST':
        try:
            if form_name == 'contact_info' and contact_info_form.validate_on_submit():
                logging.debug("Processing contact info form")
                contact_info = ContactInfo.query.first()
                if not contact_info:
                    contact_info = ContactInfo()
                    db.session.add(contact_info)
                contact_info.email = contact_info_form.email.data
                contact_info.hotline = contact_info_form.hotline.data
                contact_info.fanpage = contact_info_form.fanpage.data
                db.session.commit()
                return jsonify({'success': True, 'message': 'Cập nhật thông tin liên hệ thành công!'})

            elif form_name == 'location' and location_form.validate_on_submit():
                logging.debug("Processing location form")
                google_maps_link = location_form.google_maps_link.data
                if google_maps_link:
                    google_maps_link = extract_iframe_src(google_maps_link)
                    if not google_maps_link.startswith('https://www.google.com/maps/embed'):
                        return jsonify({'success': False, 'error': 'URL Google Maps không hợp lệ.'}), 400
                location = Location(
                    name=location_form.name.data,
                    address=location_form.address.data,
                    google_maps_link=google_maps_link
                )
                db.session.add(location)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Thêm cơ sở thành công!'})

            else:
                errors = {}
                for form in [contact_info_form, location_form]:
                    if form.errors:
                        for field, errs in form.errors.items():
                            errors[field] = errs
                logging.error(f"Form validation errors: {errors}")
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        except Exception as e:
            db.session.rollback()
            logging.error(f"Form {form_name} error: {str(e)}")
            return jsonify({'success': False, 'error': f'Lỗi khi xử lý: {str(e)}'}), 500

    contact_info = ContactInfo.query.first()
    locations = Location.query.order_by(Location.created_at.asc()).all()

    if contact_info:
        contact_info_form.email.data = contact_info.email
        contact_info_form.hotline.data = contact_info.hotline
        contact_info_form.fanpage.data = contact_info.fanpage

    return render_template('admin/contact.html',
                           contact_info_form=contact_info_form,
                           location_form=location_form,
                           contact_info=contact_info,
                           locations=locations)

@admin_bp.route('/contact/location/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_location(id):
    try:
        location = Location.query.get_or_404(id)
        form = LocationForm()
        if form.validate_on_submit():
            google_maps_link = form.google_maps_link.data
            if google_maps_link:
                google_maps_link = extract_iframe_src(google_maps_link)
                if not google_maps_link.startswith('https://www.google.com/maps/embed'):
                    return jsonify({'success': False, 'error': 'URL Google Maps không hợp lệ.'}), 400
            location.name = form.name.data
            location.address = form.address.data
            location.google_maps_link = google_maps_link
            db.session.commit()
            return jsonify({
                'success': True,
                'data': {
                    'id': location.id,
                    'name': location.name,
                    'address': location.address,
                    'google_maps_link': location.google_maps_link
                }
            })
        else:
            errors = {field: errs for field, errs in form.errors.items()}
            logging.error(f"Form validation errors: {errors}")
            return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error editing location: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi cập nhật cơ sở: {str(e)}'}), 500


@admin_bp.route('/contact/location/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_location(id):
    logging.debug(f"CSRF token received: {request.form.get('csrf_token')}")
    try:
        location = Location.query.get_or_404(id)
        db.session.delete(location)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Xóa cơ sở thành công!'})
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting location ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xóa cơ sở: {str(e)}'}), 500


@admin_bp.route('/contact/submissions', methods=['GET'])
@login_required
@admin_required
def manage_contact_submissions():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/contact_submissions.html', contacts=contacts)

@admin_bp.route('/contact/submissions/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_contact_submission(id):
    try:
        contact = Contact.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        flash('Xóa tin nhắn liên hệ thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa tin nhắn: {str(e)}', 'error')
        logging.error(f"Error deleting contact submission ID {id}: {str(e)}")
    return redirect(url_for('admin.manage_contact_submissions'))

# Phần 2.9: Route quản lý người dùng
@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(username=form.username.data).first():
                flash('Tên người dùng đã tồn tại.', 'error')
                return render_template('admin/create_user.html', form=form)
            if User.query.filter_by(email=form.email.data).first():
                flash('Email đã tồn tại.', 'error')
                return render_template('admin/create_user.html', form=form)
            if not form.password.data:
                flash('Mật khẩu là bắt buộc khi tạo người dùng mới.', 'error')
                return render_template('admin/create_user.html', form=form)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data),
                is_admin=form.is_admin.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Tạo người dùng thành công!', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi tạo người dùng: {str(e)}', 'error')
            logging.error(f"Error creating user: {str(e)}")
    return render_template('admin/create_user.html', form=form)

@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        try:
            if User.query.filter_by(username=form.username.data).filter(User.id != id).first():
                flash('Tên người dùng đã tồn tại.', 'error')
                return render_template('admin/edit_user.html', form=form, user=user)
            if User.query.filter_by(email=form.email.data).filter(User.id != id).first():
                flash('Email đã tồn tại.', 'error')
                return render_template('admin/edit_user.html', form=form, user=user)
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            if form.password.data:
                user.password = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Cập nhật người dùng thành công!', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật người dùng: {str(e)}', 'error')
            logging.error(f"Error editing user ID {id}: {str(e)}")
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    try:
        if user.id == current_user.id:
            flash('Không thể xóa tài khoản của chính bạn!', 'error')
            return redirect(url_for('admin.manage_users'))
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Lỗi khi xóa người dùng: {str(e)}', 'error')
        logging.error(f"Error deleting user ID {id}: {str(e)}")
    return redirect(url_for('admin.manage_users'))

# Phần 2.10: Route quản lý trang chủ
@admin_bp.route('/home', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_home():
    logging.debug(f"Request: {request.method} {request.url} Form: {request.form}")
    intro_form = IntroSectionForm()
    portfolio_form = PortfolioItemForm()
    service_form = ServiceCardForm()
    testimonial_form = TestimonialForm()
    featured_post_form = FeaturedPostForm()
    form_name = request.form.get('form_name')
    logging.debug(f"Form submitted: {form_name}")

    try:
        if request.method == 'POST':
            upload_folder = 'app/static/uploads/home'
            os.makedirs(upload_folder, exist_ok=True)

            if form_name == 'intro' and intro_form.validate_on_submit():
                logging.debug("Processing intro form")
                intro = IntroSection.query.first()
                if not intro:
                    intro = IntroSection()
                    db.session.add(intro)
                intro.text = intro_form.text.data
                intro.cta_text = intro_form.cta_text.data
                intro.cta_url = intro_form.cta_url.data
                if intro_form.image.data:
                    file = intro_form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ (jpg, jpeg, png, gif).'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(800, 400))
                    os.remove(original_path)
                    if intro.image_url and intro.image_url != '/static/images/default_image.jpg':
                        old_file = os.path.join('app', intro.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    intro.image_url = f'/static/uploads/home/{resized_filename}'
                db.session.commit()
                return jsonify({'success': True, 'message': 'Cập nhật phần giới thiệu thành công!'})

            elif form_name == 'portfolio' and portfolio_form.validate_on_submit():
                logging.debug("Processing portfolio form")
                image_url = '/static/images/default_image.jpg'
                if portfolio_form.image.data:
                    file = portfolio_form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(300, 300))
                    os.remove(original_path)
                    image_url = f'/static/uploads/home/{resized_filename}'
                portfolio = PortfolioItem(
                    title=portfolio_form.title.data,
                    image_url=image_url
                )
                db.session.add(portfolio)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Thêm mục portfolio thành công!'})

            elif form_name == 'service' and service_form.validate_on_submit():
                logging.debug("Processing service form")
                image_url = '/static/images/default_image.jpg'
                if service_form.image.data:
                    file = service_form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(300, 200))
                    os.remove(original_path)
                    image_url = f'/static/uploads/home/{resized_filename}'
                service = ServiceCard(
                    title=service_form.title.data,
                    description=service_form.description.data,
                    image_url=image_url,
                    cta_text=service_form.cta_text.data,
                    cta_url=service_form.cta_url.data
                )
                db.session.add(service)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Thêm dịch vụ thành công!'})

            elif form_name == 'testimonial' and testimonial_form.validate_on_submit():
                logging.debug("Processing testimonial form")
                testimonial = Testimonial(
                    content=testimonial_form.content.data,
                    author=testimonial_form.author.data
                )
                db.session.add(testimonial)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Thêm đánh giá thành công!'})

            elif form_name == 'featured_post' and featured_post_form.validate_on_submit():
                logging.debug("Processing featured post form")
                post_id = featured_post_form.post_id.data
                post = Post.query.get_or_404(post_id)
                if not post.is_featured:
                    if Post.query.filter_by(is_featured=True).count() >= 3:
                        return jsonify({'success': False, 'error': 'Đã đủ 3 bài viết nổi bật!'})
                    post.is_featured = True
                    db.session.commit()
                    return jsonify({'success': True, 'message': 'Thêm bài viết nổi bật thành công!'})
                return jsonify({'success': False, 'error': 'Bài viết này đã được chọn làm nổi bật!'})

            else:
                errors = {}
                for form in [intro_form, portfolio_form, service_form, testimonial_form, featured_post_form]:
                    if form.errors:
                        for field, errs in form.errors.items():
                            errors[field] = errs
                logging.error(f"Form validation errors: {errors}")
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

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

    except Exception as e:
        db.session.rollback()
        logging.error(f"Form {form_name} error: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xử lý: {str(e)}'}), 500

@admin_bp.route('/home/<model>/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_home_item(model, id):
    try:
        upload_folder = 'app/static/uploads/home'
        os.makedirs(upload_folder, exist_ok=True)

        if model == 'portfolio':
            item = PortfolioItem.query.get_or_404(id)
            form = PortfolioItemForm()
            if form.validate_on_submit():
                item.title = form.title.data
                if form.image.data and form.image.data.filename:
                    file = form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(300, 300))
                    os.remove(original_path)
                    if item.image_url and item.image_url != '/static/images/default_image.jpg':
                        old_file = os.path.join('app', item.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    item.image_url = f'/static/uploads/home/{resized_filename}'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': {
                        'id': item.id,
                        'title': item.title,
                        'image_url': item.image_url
                    }
                })
            else:
                errors = {field: errs for field, errs in form.errors.items()}
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        elif model == 'service':
            item = ServiceCard.query.get_or_404(id)
            form = ServiceCardForm()
            if form.validate_on_submit():
                item.title = form.title.data
                item.description = form.description.data
                item.cta_text = form.cta_text.data
                item.cta_url = form.cta_url.data
                if form.image.data and form.image.data.filename:
                    file = form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(300, 200))
                    os.remove(original_path)
                    if item.image_url and item.image_url != '/static/images/default_image.jpg':
                        old_file = os.path.join('app', item.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    item.image_url = f'/static/uploads/home/{resized_filename}'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': {
                        'id': item.id,
                        'title': item.title,
                        'description': item.description,
                        'cta_text': item.cta_text,
                        'cta_url': item.cta_url,
                        'image_url': item.image_url
                    }
                })
            else:
                errors = {field: errs for field, errs in form.errors.items()}
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        elif model == 'testimonial':
            item = Testimonial.query.get_or_404(id)
            form = TestimonialForm()
            if form.validate_on_submit():
                item.content = form.content.data
                item.author = form.author.data
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': {
                        'id': item.id,
                        'content': item.content,
                        'author': item.author
                    }
                })
            else:
                errors = {field: errs for field, errs in form.errors.items()}
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        else:
            return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error editing {model} ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi chỉnh sửa mục: {str(e)}'}), 500

@admin_bp.route('/home/<model>/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_home_item(model, id):
    try:
        if model == 'portfolio':
            item = PortfolioItem.query.get_or_404(id)
            if item.image_url and item.image_url.lstrip() != '/static/images/default_image.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Xóa mục portfolio thành công!'})

        elif model == 'service':
            item = ServiceCard.query.get_or_404(id)
            if item.image_url and item.image_url != '/static/images/default_image.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Xóa dịch vụ thành công!'})

        elif model == 'testimonial':
            item = Testimonial.query.get_or_404(id)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Xóa đánh giá thành công!'})

        elif model == 'featured_post':
            item = Post.query.get_or_404(id)
            item.is_active = False
            db.session.commit()
            return jsonify({'success': True, 'message': 'Xóa bài viết nổi bật thành công!'})

        else:
            return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting {model} ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xóa mục: {str(e)}'}), 500

# Phần 2.11: Route quản lý giới thiệu
@admin_bp.route('/introduce', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_introduce():
    logging.debug(f"Request: {request.method} {request.url} Form: {request.form}")
    introduce_form = IntroduceSectionForm()
    team_form = TeamMemberForm()
    mission_form = MissionSectionForm()
    form_name = request.form.get('form_name')
    logging.debug(f"Form submitted: {form_name}")

    try:
        if request.method == 'POST':
            upload_folder = 'app/static/uploads/introduce'
            os.makedirs(upload_folder, exist_ok=True)

            if form_name == 'introduce' and introduce_form.validate_on_submit():
                logging.debug("Processing introduce form")
                introduce = IntroduceSection.query.first()
                if not introduce:
                    introduce = IntroduceSection()
                    db.session.add(introduce)
                introduce.text = introduce_form.text.data
                introduce.cta_text = introduce_form.cta_text.data
                introduce.cta_url = introduce_form.cta_url.data
                if introduce_form.image.data:
                    file = introduce_form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(800, 400))
                    os.remove(original_path)
                    if introduce.image_url and introduce.image_url != '/static/images/default_image.jpg':
                        old_file = os.path.join('app', introduce.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    introduce.image_url = f'/static/uploads/introduce/{resized_filename}'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': 'Cập nhật phần giới thiệu thành công!',
                    'data': {
                        'text': introduce.text,
                        'cta_text': introduce.cta_text,
                        'cta_url': introduce.cta_url,
                        'image_url': introduce.image_url
                    }
                })

            # Trong route manage_introduce
            elif form_name == 'team' and team_form.validate_on_submit():
                try:
                    logging.debug("Processing team member form")
                    member_id = request.form.get('id')  # Lấy ID nếu là chỉnh sửa
                    upload_folder = 'app/static/uploads/introduce'  # Định nghĩa upload_folder
                    os.makedirs(upload_folder, exist_ok=True)  # Tạo thư mục nếu chưa có

                    if member_id:  # Chỉnh sửa thành viên
                        team_member = TeamMember.query.get_or_404(member_id)
                        team_member.name = team_form.name.data
                        team_member.role = team_form.role.data
                        team_member.description = team_form.description.data
                    else:  # Thêm thành viên mới
                        team_member = TeamMember(
                            name=team_form.name.data,
                            role=team_form.role.data,
                            description=team_form.description.data,
                            image_url=None  # Không sử dụng default_image.jpg
                        )
                        db.session.add(team_member)
                    
                    if team_form.image.data:
                        file = team_form.image.data
                        if not allowed_file(file.filename):
                            return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'}), 400
                        filename = secure_filename(file.filename)
                        original_path = os.path.join(upload_folder, filename)
                        file.save(original_path)
                        resized_filename = f"resized_{filename}"
                        resized_path = os.path.join(upload_folder, resized_filename)
                        resize_image(original_path, resized_path, max_size=(200, 200))
                        os.remove(original_path)
                        if team_member.image_url and team_member.image_url != '/static/images/default_image.jpg':
                            old_file = os.path.join('app', team_member.image_url.lstrip('/'))
                            if os.path.exists(old_file):
                                os.remove(old_file)
                        team_member.image_url = f'/static/uploads/introduce/{resized_filename}'
                    
                    db.session.commit()
                    return jsonify({
                        'success': True,
                        'message': 'Cập nhật thành viên đội ngũ thành công!' if member_id else 'Thêm thành viên đội ngũ thành công!',
                        'data': {
                            'id': team_member.id,
                            'name': team_member.name,
                            'role': team_member.role,
                            'description': team_member.description,
                            'image_url': team_member.image_url or '/static/images/placeholder.jpg'
                        }
                    })
                except Exception as e:
                    db.session.rollback()
                    logging.error(f"Error processing team form: {str(e)}")
                    return jsonify({'success': False, 'error': f'Lỗi server: {str(e)}'}), 500

            elif form_name == 'mission' and mission_form.validate_on_submit():
                logging.debug("Processing mission form")
                mission = MissionSection.query.first()
                if not mission:
                    mission = MissionSection()
                    db.session.add(mission)
                mission.text = mission_form.text.data
                if mission_form.image.data:
                    file = mission_form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(800, 400))
                    os.remove(original_path)
                    if mission.image_url and mission.image_url != '/static/images/default_image.jpg':
                        old_file = os.path.join('app', mission.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    mission.image_url = f'/static/uploads/introduce/{resized_filename}'
                db.session.commit()
                return jsonify({'success': True, 'message': 'Cập nhật mission thành công!'})

            else:
                errors = {}
                for form in [introduce_form, team_form, mission_form]:
                    if form_name == 'team' and form == team_form:
                        logging.debug(f"Team form data: {form.data}")
                        logging.debug(f"Team form validate: {form.validate()}")
                        logging.debug(f"Team form errors: {form.errors}")
                    if form.errors:
                        for field, errs in form.errors.items():
                            errors[field] = errs
                logging.error(f"Form validation errors: {errors}")
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        introduce = IntroduceSection.query.first()
        team_members = TeamMember.query.all()
        mission = MissionSection.query.first()

        if introduce:
            introduce_form.text.data = introduce.text
            introduce_form.cta_text.data = introduce.cta_text
            introduce_form.cta_url.data = introduce.cta_url
        if mission:
            mission_form.text.data = mission.text

        return render_template('admin/introduce.html',
                               introduce_form=introduce_form,
                               team_form=team_form,
                               mission_form=mission_form,
                               introduce=introduce,
                               team_members=team_members,
                               mission=mission)

    except Exception as e:
        db.session.rollback()
        logging.error(f"Form {form_name} error: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xử lý: {str(e)}'}), 500

@admin_bp.route('/introduce/<model>/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_introduce_item(model, id):
    try:
        upload_folder = 'app/static/uploads/introduce'
        os.makedirs(upload_folder, exist_ok=True)

        if model == 'team_member':
            item = TeamMember.query.get_or_404(id)
            form = TeamMemberForm()
            if form.validate_on_submit():
                item.name = form.name.data
                item.role = form.role.data
                item.description = form.description.data
                if form.image.data and form.image.data.filename:
                    file = form.image.data
                    if not allowed_file(file.filename):
                        return jsonify({'success': False, 'error': 'Vui lòng chọn file ảnh hợp lệ!'})
                    filename = secure_filename(file.filename)
                    original_path = os.path.join(upload_folder, filename)
                    file.save(original_path)
                    resized_filename = f"resized_{filename}"
                    resized_path = os.path.join(upload_folder, resized_filename)
                    resize_image(original_path, resized_path, max_size=(200, 200))
                    os.remove(original_path)
                    if item.image_url and item.image_url != '/static/images/':
                        old_file = os.path.join('app', item.image_url.lstrip('/'))
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    item.image_url = f'/static/uploads/introduce/{resized_filename}'
                db.session.commit()
                return jsonify({
                    'success': True,
                    'data': {
                        'id': item.id,
                        'name': item.name,
                        'role': item.role,
                        'description': item.description,
                        'image_url': item.image_url
                    }
                })
            else:
                errors = {field: errs for field, errs in form.errors.items()}
                return jsonify({'success': False, 'error': 'Dữ liệu không hợp lệ', 'details': errors}), 400

        else:
            return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error editing {model} ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi chỉnh sửa mục: {str(e)}'}), 500

@admin_bp.route('/introduce/<model>/<int:id>', methods=['POST', 'DELETE'])
@login_required
@admin_required
def delete_introduce_item(model, id):
    logging.debug(f"CSRF token received: {request.form.get('csrf_token')}")
    try:
        if model == 'team_member':
            item = TeamMember.query.get_or_404(id)
            if item.image_url and item.image_url != '/static/images/default_image.jpg':
                file_path = os.path.join('app', item.image_url.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Xóa thành viên đội ngũ thành công!'})
        else:
            return jsonify({'success': False, 'error': 'Mục không hợp lệ!'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting {model} ID {id}: {str(e)}")
        return jsonify({'success': False, 'error': f'Lỗi khi xóa mục: {str(e)}'}), 500