from flask import Blueprint, render_template, jsonify
from app.services.store_service import StoreConfigService
from app.config import Config

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    store = StoreConfigService(Config.STORE_CONFIG_PATH).get()
    return render_template("index.html", store=store)


@main_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "store-chatbot"})
