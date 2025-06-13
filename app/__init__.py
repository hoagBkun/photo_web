import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
import re

def extract_iframe_src(iframe):
    if iframe and isinstance(iframe, str) and iframe.startswith('<iframe'):
        match = re.search(r'src="([^"]+)"', iframe)
        return match.group(1) if match else iframe
    return iframe

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    # Import models trước db.create_all()
    from app.models.user import User
    from app.models.banner import Banner
    from app.models.post import Post
    from app.models.contact_info import ContactInfo, Contact, Location
    from app.models.pricing import Pricing
    from app.models.pricing_page import PricingPage
    from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial
    from app.models.introduce import IntroduceSection, TeamMember, MissionSection

    # Đăng ký blueprints
    from app.blueprints.main.routes import main
    from app.blueprints.auth.routes import auth
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.blog.routes import blog_bp

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(blog_bp, url_prefix='/blog')

    # In danh sách route để debug
    print(app.url_map)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Đảm bảo csrf_token có sẵn trong template
    @app.context_processor
    def utility_processor():
        def csrf_token():
            from flask_wtf.csrf import generate_csrf
            return generate_csrf()
        return dict(csrf_token=csrf_token)

    return app