import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from config import Config
import re
from dotenv import load_dotenv

# Cấu hình logging
log_file = os.path.join(os.path.dirname(__file__), '../flask.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

logging.debug(f"Logging to file: {log_file}")
logging.debug("Starting application initialization")

# Load biến môi trường
env_file = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(env_file):
    logging.debug(f"Loading .env file: {env_file}")
    load_dotenv(dotenv_path=env_file)
else:
    logging.debug("No .env file, using hardcoded config")

def extract_iframe_src(iframe):
    if iframe and isinstance(iframe, str) and iframe.startswith('<iframe'):
        match = re.search(r'src="([^"]+)"', iframe)
        return match.group(1) if match else iframe
    return iframe

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
oauth = OAuth()

def create_app():
    logging.debug("Creating Flask app")
    app = Flask(__name__)
    try:
        app.config.from_object(Config)
        logging.debug("Config loaded successfully")
        logging.debug(f"Config loaded with GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET masked")
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        raise

    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        logging.debug(f"Created instance directory: {instance_path}")

    # Khởi tạo extensions
    logging.debug("Initializing extensions")
    try:
        db.init_app(app)
        login_manager.init_app(app)
        migrate.init_app(app, db)
        csrf.init_app(app)
        oauth.init_app(app)
        logging.debug("OAuth initialized with app")
    except Exception as e:
        logging.error(f"Error initializing extensions: {str(e)}")
        raise

    # Kiểm tra biến môi trường
    if not app.config.get('GOOGLE_CLIENT_ID') or not app.config.get('GOOGLE_CLIENT_SECRET'):
        logging.error("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
        raise ValueError("Missing Google OAuth credentials")

    # Đăng ký Google OAuth
    try:
        logging.debug("Registering Google OAuth")
        redirect_uri = app.config.get('OAUTH_REDIRECT_URI', 'http://localhost:5000/auth/authorize/google')
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        logging.debug(f"Google OAuth registered successfully with redirect URI: {redirect_uri}")
        logging.debug(f"OAuth google client exists: {hasattr(oauth, 'google')}")
    except Exception as e:
        logging.error(f"Failed to register Google OAuth: {str(e)}", exc_info=True)
        raise

    login_manager.login_view = 'auth.login'

    # Import models
    logging.debug("Importing models")
    try:
        from app.models.user import User
        from app.models.banner import Banner
        from app.models.post import Post
        from app.models.contact_info import ContactInfo, Contact, Location
        from app.models.pricing import Pricing
        from app.models.pricing_page import PricingPage
        from app.models.home import IntroSection, PortfolioItem, ServiceCard, Testimonial
        from app.models.introduce import IntroduceSection, TeamMember, MissionSection
        logging.debug("Models imported successfully")
    except Exception as e:
        logging.error(f"Error importing models: {str(e)}")
        raise

    # Đăng ký blueprints
    logging.debug("Registering blueprints")
    try:
        from app.blueprints.main.routes import main
        from app.blueprints.auth.routes import auth
        from app.blueprints.admin.routes import admin_bp
        from app.blueprints.blog.routes import blog_bp
        app.register_blueprint(main)
        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(blog_bp, url_prefix='/blog')
        logging.debug("Blueprints registered successfully")
    except Exception as e:
        logging.error(f"Error registering blueprints: {str(e)}")
        raise

    logging.debug(f"URL Map: {app.url_map}")

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def utility_processor():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    logging.debug("Flask app created successfully")
    return app