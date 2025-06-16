from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.password_reset import PasswordReset
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import logging
import re

# Cấu hình logging chi tiết
logging.basicConfig(
    filename='flask.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

auth = Blueprint('auth', __name__)

# Hàm kiểm tra email đơn giản
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_pattern, email) is not None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Bạn đã đăng nhập.', 'info')
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logging.debug(f"Login attempt with username: {username}")
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.login'))
        user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.home'))
        logging.error(f"Login failed for username: {username}")
        current_app.logger.error(f"Login failed for username: {username}")
        flash('Đăng nhập thất bại. Vui lòng kiểm tra lại tên người dùng hoặc mật khẩu.', 'error')
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Bạn đã đăng nhập.', 'info')
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        logging.debug(f"Register attempt with username: {username}, email: {email}")
        if not username or not email or not password or not confirm_password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.register'))
        if password != confirm_password:
            flash('Mật khẩu và xác nhận mật khẩu không khớp.', 'error')
            return redirect(url_for('auth.register'))
        if not is_valid_email(email):
            flash('Email không hợp lệ.', 'error')
            return redirect(url_for('auth.register'))
        if db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none():
            logging.error(f"Registration failed: Username {username} already exists")
            current_app.logger.error(f"Registration failed: Username {username} already exists")
            flash('Tên người dùng đã tồn tại.', 'error')
            return redirect(url_for('auth.register'))
        if db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none():
            logging.error(f"Registration failed: Email {email} already exists")
            current_app.logger.error(f"Registration failed: Email {email} already exists")
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
    if current_user.is_authenticated:
        flash('Bạn đã đăng nhập.', 'info')
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        logging.debug(f"Password reset attempt for email: {email}")
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
            flash(f'Link đặt lại mật khẩu (chỉ dùng trong phát triển): {reset_url}', 'success')
        else:
            logging.error(f"Password reset failed: Email {email} not found")
            current_app.logger.error(f"Password reset failed: Email {email} not found")
            flash('Email không được tìm thấy.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')  # Sửa từ login.html thành auth/forgot_password.html
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash('Bạn đã đăng nhập.', 'info')
        return redirect(url_for('main.home'))
    reset = db.session.execute(
        db.select(PasswordReset).where(PasswordReset.token == token, PasswordReset.expires_at > datetime.utcnow())
    ).scalar_one_or_none()
    if not reset:
        logging.error(f"Password reset failed: Invalid or expired token {token}")
        current_app.logger.error(f"Password reset failed: Invalid or expired token {token}")
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        logging.debug(f"Attempting password reset for token: {token}")
        if not new_password or not confirm_password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        user = db.session.execute(db.select(User).where(User.email == reset.email)).scalar_one_or_none()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.delete(reset)
            db.session.commit()
            flash('Password reset successfully!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)  # Sửa từ reset_password.html thành auth/reset_password.html
@auth.route('/login/google')
def login_google():
    if not hasattr(current_app, 'oauth') or not current_app.oauth.google:
        logging.error("Google OAuth not registered")
        current_app.logger.error("Google OAuth not registered")
        flash('Invalid Google OAuth configuration.', 'error')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.authorize_google', _external=True)
    logging.debug(f"Google OAuth redirect URI: {redirect_uri}")
    try:
        return current_app.oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Google OAuth redirect error: {str(e)}", exc_info=True)
        current_app.logger.error(f"Google OAuth redirect error: {str(e)}")
        flash('Error during Google login. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/authorize/google')
def authorize_google():
    if not hasattr(current_app, 'oauth') or not current_app.oauth.google:
        logging.error("Google OAuth not registered")
        current_app.logger.error("Google OAuth not registered")
        flash('Invalid Google OAuth configuration.', 'error')
        return redirect(url_for('auth.login'))
    try:
        logging.debug("Attempting to get Google OAuth access token")
        token = current_app.oauth.google.authorize_access_token()
        logging.debug(f"Google OAuth token: {token}")
        resp = current_app.oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
        logging.debug(f"Google userinfo response: {resp.json()}")
        user_info = resp.json()
        if 'email' not in user_info:
            logging.error(f"Google OAuth error: No email in user_info: {user_info}")
            current_app.logger.error(f"Google OAuth error: No email in user_info: {user_info}")
            flash('Could not retrieve email from Google.', 'error')
            return redirect(url_for('auth.login'))
        user = db.session.execute(db.select(User).where(User.email == user_info['email'])).scalar_one_or_none()
        if not user:
            logging.debug(f"Creating new user with email: {user_info['email']}")
            user = User(
                username=user_info.get('name', user_info['email'].split('@')[0]),
                email=user_info['email'],
                password=generate_password_hash(secrets.token_urlsafe(32)),
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('Google login successful!', 'success')
        return redirect(url_for('main.home'))
    except Exception as e:
        logging.error(f"Google OAuth authorize error: {str(e)}", exc_info=True)
        current_app.logger.error(f"Google OAuth authorize error: {str(e)}")
        flash('Error during Google login. Please try again.', 'error')
        return redirect(url_for('auth.login'))
    
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        logging.debug(f"Password change attempt for user: {current_user.username}")

        if not current_password or not new_password or not confirm_password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.change_password'))

        if not check_password_hash(current_user.password, current_password):
            logging.error(f"Password change failed: Incorrect current password for user {current_user.username}")
            flash('Mật khẩu hiện tại không đúng.', 'error')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_password:
            flash('Mật khẩu mới và xác nhận mật khẩu không khớp.', 'error')
            return redirect(url_for('auth.change_password'))

        # Kiểm tra độ mạnh mật khẩu (tùy chọn)
        if len(new_password) < 8 or not any(c.isupper() for c in new_password) or not any(c.isdigit() for c in new_password):
            flash('Mật khẩu mới phải có ít nhất 8 ký tự, bao gồm chữ hoa và số.', 'error')
            return redirect(url_for('auth.change_password'))

        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        return redirect(url_for('main.profile'))

    return render_template('auth/change_password.html')   