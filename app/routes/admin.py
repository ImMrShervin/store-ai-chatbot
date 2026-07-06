import os
from functools import wraps
from flask import Blueprint, request, jsonify

from app.models import database as db
from app.services.store_service import StoreConfigService
from app.config import Config

admin_bp = Blueprint("admin", __name__)


def _require_admin_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        admin_key = os.getenv("ADMIN_API_KEY", "")
        if admin_key:
            provided = request.headers.get("X-Admin-Key", "")
            if provided != admin_key:
                return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/stats", methods=["GET"])
@_require_admin_key
def stats():
    return jsonify(db.get_stats())


@admin_bp.route("/config", methods=["GET"])
@_require_admin_key
def get_config():
    svc = StoreConfigService(Config.STORE_CONFIG_PATH)
    return jsonify(svc.get())


@admin_bp.route("/config", methods=["PUT"])
@_require_admin_key
def update_config():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid json"}), 400
    svc = StoreConfigService(Config.STORE_CONFIG_PATH)
    svc.save(data)
    return jsonify({"status": "ok", "message": "config updated & reloaded"})


@admin_bp.route("/config/reload", methods=["POST"])
@_require_admin_key
def reload_config():
    svc = StoreConfigService(Config.STORE_CONFIG_PATH)
    svc.reload()
    return jsonify({"status": "ok", "message": "config reloaded from disk"})
