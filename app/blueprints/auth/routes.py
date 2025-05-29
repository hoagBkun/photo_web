from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.password_reset import PasswordReset
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.login'))
        user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.home'))
        flash('Đăng nhập thất bại. Vui lòng kiểm tra lại tên người dùng hoặc mật khẩu.', 'error')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.register'))
        if db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none():
            flash('Tên người dùng đã tồn tại.', 'error')
            return redirect(url_for('auth.register'))
        if db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none():
            flash('Email đã được sử dụng.', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('main.home'))

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Vui lòng nhập email.', 'error')
            return redirect(url_for('auth.forgot_password'))
        user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
        if user:
            token = secrets.token_urlsafe(32)
            reset = PasswordReset(
                email=email,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(reset)
            db.session.commit()

            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Link đặt lại mật khẩu: {reset_url}', 'success')  # Hiển thị link thay vì gửi email
        else:
            flash('Email không tồn tại.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = db.session.execute(
        db.select(PasswordReset).where(PasswordReset.token == token, PasswordReset.expires_at > datetime.utcnow())
    ).scalar_one_or_none()
    if not reset:
        flash('Token không hợp lệ hoặc đã hết hạn.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        if not new_password:
            flash('Vui lòng nhập mật khẩu mới.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        user = db.session.execute(db.select(User).where(User.email == reset.email)).scalar_one_or_none()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.delete(reset)
            db.session.commit()
            flash('Mật khẩu đã được đặt lại thành công!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)