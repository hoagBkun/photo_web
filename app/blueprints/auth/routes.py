from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.password_reset import PasswordReset
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import logging
from wtforms.validators import Email

# Cấu hình logging chi tiết
logging.basicConfig(
    filename='flask.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

auth = Blueprint('auth', __name__)

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
        if not Email()(None, email):
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
            flash('Email không tồn tại.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

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
        flash('Token không hợp lệ hoặc đã hết hạn.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        logging.debug(f"Password reset attempt for token: {token}")
        if not new_password or not confirm_password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        if new_password != confirm_password:
            flash('Mật khẩu và xác nhận mật khẩu không khớp.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        user = db.session.execute(db.select(User).where(User.email == reset.email)).scalar_one_or_none()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.delete(reset)
            db.session.commit()
            flash('Mật khẩu đã được đặt lại thành công!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)

@auth.route('/login/google')
def login_google():
    if not hasattr(current_app, 'oauth') or not current_app.oauth.google:
        logging.error("Google OAuth not registered")
        current_app.logger.error("Google OAuth not registered")
        flash('Cấu hình Google OAuth không hợp lệ.', 'error')
        return redirect(url_for('auth.login'))
    redirect_uri = url_for('auth.authorize_google', _external=True)
    logging.debug(f"Google OAuth redirect URI: {redirect_uri}")
    try:
        return current_app.oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        logging.error(f"Google OAuth redirect error: {str(e)}")
        current_app.logger.error(f"Google OAuth redirect error: {str(e)}")
        flash('Lỗi khi đăng nhập bằng Google. Vui lòng thử lại.', 'error')
        return redirect(url_for('auth.login'))

@auth.route('/authorize/google')
def authorize_google():
    if not hasattr(current_app, 'oauth') or not current_app.oauth.google:
        logging.error("Google OAuth not registered")
        current_app.logger.error("Google OAuth not registered")
        flash('Cấu hình Google OAuth không hợp lệ.', 'error')
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
            flash('Không thể lấy thông tin email từ Google.', 'error')
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
        flash('Đăng nhập bằng Google thành công!', 'success')
        return redirect(url_for('main.home'))
    except Exception as e:
        logging.error(f"Google OAuth authorize error: {str(e)}")
        current_app.logger.error(f"Google OAuth authorize error: {str(e)}")
        flash('Lỗi khi đăng nhập bằng Google. Vui lòng thử lại.', 'error')
        return redirect(url_for('auth.login'))