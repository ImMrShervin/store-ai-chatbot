"""
Store Chatbot Application Package
Production-ready Flask application with Groq LLM integration.
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import Config
from app.models.database import init_db
from app.routes.chat import chat_bp
from app.routes.admin import admin_bp
from app.routes.main import main_bp


def create_app(config_class: type = Config) -> Flask:
    """Application factory pattern."""
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_class)

    # Logging
    logging.basicConfig(
        level=logging.INFO if app.config["FLASK_ENV"] == "production" else logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # CORS (adjust origins in production)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Database init
    with app.app_context():
        init_db(app.config["DATABASE_PATH"])

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    app.logger.info("✅ Store Chatbot initialized successfully.")
    return app
