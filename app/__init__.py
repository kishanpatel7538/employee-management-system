
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():

    app = Flask(__name__)

    # Flask configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = 3600

    # Validate configuration
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY not found in .env")

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL not found in .env")

    # Initialize database
    db.init_app(app)
    csrf.init_app(app)

    # Initialize Flask Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Import User model
    from app.models import User

    # Load authenticated user
    @login_manager.user_loader
    def load_user(user_id):

        try:
            return db.session.get(User, int(user_id))

        except (ValueError, TypeError):
            return None

    # Import blueprints
    from app.routes import auth, employee_bp
    from app.hr_routes import hr_bp

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(employee_bp)
    app.register_blueprint(hr_bp)

    # Home route
    @app.route("/")
    def home():
        return "Employee Management System is running!"

    return app
