from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.banner import Banner
import os
from werkzeug.utils import secure_filename

main = Blueprint('main', __name__)

@main.route('/')
def home():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()  # Lấy danh sách banner
    return render_template('main/home.html', banners=banners)

@main.route('/introduce')
def introduce():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/introduce.html', banners=banners)

@main.route('/blog')
@main.route('/blog/')
def blog():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/blog.html', banners=banners)

@main.route('/pricing')
def pricing():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/price.html', banners=banners)

@main.route('/contact')
def contact():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/contact.html', banners=banners)

@main.route('/profile')
@login_required
def profile():
    banners = Banner.query.order_by(Banner.created_at.desc()).all()
    return render_template('main/profile.html', banners=banners)

@main.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    
    # Lấy dữ liệu từ form
    new_username = request.form['username']
    new_email = request.form['email']
    new_phone = request.form['phone']
    new_address = request.form['address']

    # Kiểm tra trùng username (trừ chính người dùng hiện tại)
    if new_username != user.username:  # Chỉ kiểm tra nếu username thay đổi
        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user and existing_user.id != user.id:
            flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'error')
            return redirect(url_for('main.profile'))

    # Cập nhật thông tin
    user.username = new_username
    user.email = new_email
    user.phone = new_phone
    user.address = new_address

    # Xử lý upload avatar
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Đảm bảo thư mục avatars tồn tại
            os.makedirs('app/static/avatars', exist_ok=True)
            file.save(os.path.join('app/static/avatars', filename))
            # Xóa avatar cũ nếu không phải default
            if user.avatar != 'default_avatar.png':
                old_avatar_path = os.path.join('app/static/avatars', user.avatar)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            user.avatar = filename

    db.session.commit()
    flash('Thông tin cá nhân đã được cập nhật thành công!', 'success')
    # Thêm timestamp để tránh cache ảnh trên navbar
    return redirect(url_for('main.profile', _=int(os.path.getmtime(os.path.join('app/static/avatars', user.avatar))) if user.avatar != 'default_avatar.png' else 0))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS