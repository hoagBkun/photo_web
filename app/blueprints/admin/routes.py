from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.post import Post
from app.models.banner import Banner
from app.models.contact_info import ContactInfo
from app.blueprints.admin.forms import BannerForm, PostForm, ContactInfoForm, UserForm
from functools import wraps
from werkzeug.utils import secure_filename
import os

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    banner_count = Banner.query.count()
    post_count = Post.query.count()
    user_count = User.query.count()
    return render_template('admin/dashboard.html', 
                          banner_count=banner_count, 
                          post_count=post_count, 
                          user_count=user_count)

@admin.route('/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_banners():
    form = BannerForm()
    if form.validate_on_submit():
        try:
            file = form.image.data
            if not file:
                flash('Vui lòng chọn hình ảnh banner.', 'error')
                return redirect(url_for('admin.manage_banners'))
            filename = secure_filename(file.filename)
            file_path = os.path.join('app/static/uploads', filename)
            os.makedirs('app/static/uploads', exist_ok=True)
            file.save(file_path)
            banner = Banner(
                image_url=f'/static/uploads/{filename}', 
                title=form.title.data, 
                description=form.description.data
            )
            db.session.add(banner)
            db.session.commit()
            flash('Banner đã được thêm thành công!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            flash(f'Có lỗi khi thêm banner: {str(e)}', 'error')
    banners = Banner.query.all()
    return render_template('admin/banners.html', form=form, banners=banners)

@admin.route('/banners/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_banner(id):
    banner = Banner.query.get_or_404(id)
    form = BannerForm(obj=banner)
    if form.validate_on_submit():
        try:
            if form.image.data:
                file = form.image.data
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads', filename)
                os.makedirs('app/static/uploads', exist_ok=True)
                file.save(file_path)
                if banner.image_url and banner.image_url != '/static/uploads/default.jpg':
                    old_file = os.path.join('app/static/uploads', banner.image_url.lstrip('/static/uploads/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                banner.image_url = f'/static/uploads/{filename}'
            banner.title = form.title.data
            banner.description = form.description.data
            db.session.commit()
            flash('Banner đã được cập nhật!', 'success')
            return redirect(url_for('admin.manage_banners'))
        except Exception as e:
            flash(f'Có lỗi khi cập nhật banner: {str(e)}', 'error')
    return render_template('admin/edit_banner.html', form=form, banner=banner)

@admin.route('/banners/delete/<int:id>')
@login_required
@admin_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    try:
        if banner.image_url and banner.image_url != '/static/uploads/default.jpg':
            file_path = os.path.join('app/static/uploads', banner.image_url.lstrip('/static/uploads/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(banner)
        db.session.commit()
        flash('Banner đã được xóa!', 'success')
    except Exception as e:
        flash(f'Có lỗi khi xóa banner: {str(e)}', 'error')
    return redirect(url_for('admin.manage_banners'))

@admin.route('/posts', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_posts():
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
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads', filename)
                os.makedirs('app/static/uploads', exist_ok=True)
                file.save(file_path)
                post.image_url = f'/static/uploads/{filename}'
            db.session.add(post)
            db.session.commit()
            flash('Bài viết đã được thêm thành công!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            flash(f'Có lỗi khi thêm bài viết: {str(e)}', 'error')
    posts = Post.query.all()
    return render_template('admin/posts.html', form=form, posts=posts)

@admin.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
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
                filename = secure_filename(file.filename)
                file_path = os.path.join('app/static/uploads', filename)
                os.makedirs('app/static/uploads', exist_ok=True)
                file.save(file_path)
                if post.image_url and post.image_url != '/static/uploads/default.jpg':
                    old_file = os.path.join('app/static/uploads', post.image_url.lstrip('/static/uploads/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                post.image_url = f'/static/uploads/{filename}'
            db.session.commit()
            flash('Bài viết đã được cập nhật!', 'success')
            return redirect(url_for('admin.manage_posts'))
        except Exception as e:
            flash(f'Có lỗi khi cập nhật bài viết: {str(e)}', 'error')
    return render_template('admin/edit_post.html', form=form, post=post)

@admin.route('/posts/delete/<int:id>')
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    try:
        if post.image_url and post.image_url != '/static/uploads/default.jpg':
            file_path = os.path.join('app/static/uploads', post.image_url.lstrip('/static/uploads/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.delete(post)
        db.session.commit()
        flash('Bài viết đã được xóa!', 'success')
    except Exception as e:
        flash(f'Có lỗi khi xóa bài viết: {str(e)}', 'error')
    return redirect(url_for('admin.manage_posts'))

@admin.route('/contact', methods=['GET', 'POST'])
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
            db.session.commit()
            flash('Thông tin liên hệ đã được cập nhật!', 'success')
            return redirect(url_for('admin.manage_contact'))
        except Exception as e:
            flash(f'Có lỗi khi cập nhật thông tin liên hệ: {str(e)}', 'error')
    if contact_info:
        form.address.data = contact_info.address
        form.phone.data = contact_info.phone
        form.email.data = contact_info.email
    return render_template('admin/contact.html', form=form)

@admin.route('/users', methods=['GET'])
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        try:
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user and existing_user.id != user.id:
                flash('Tên người dùng đã tồn tại.', 'error')
                return redirect(url_for('admin.edit_user', id=user.id))
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email and existing_email.id != user.id:
                flash('Email đã tồn tại.', 'error')
                return redirect(url_for('admin.edit_user', id=user.id))
            user.username = form.username.data
            user.email = form.email.data
            user.is_admin = form.is_admin.data
            db.session.commit()
            flash('Người dùng đã được cập nhật!', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            flash(f'Có lỗi khi cập nhật người dùng: {str(e)}', 'error')
    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/users/delete/<int:id>')
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
        flash('Người dùng đã được xóa!', 'success')
    except Exception as e:
        flash(f'Có lỗi khi xóa người dùng: {str(e)}', 'error')
    return redirect(url_for('admin.manage_users'))