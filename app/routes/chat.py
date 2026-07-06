import logging
from flask import Blueprint, request, jsonify, current_app

from app.services.chat_service import ChatService
from app.services.rate_limiter import RateLimiter
from app.config import Config
from app.models import database as db

logger = logging.getLogger(__name__)

chat_bp = Blueprint("chat", __name__)

_chat_service: ChatService | None = None
_rate_limiter = RateLimiter(Config.RATE_LIMIT_PER_MINUTE)


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


def _client_ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()


@chat_bp.route("/message", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    if not user_message:
        return jsonify({"error": "message is required"}), 400
    if len(user_message) > 4000:
        return jsonify({"error": "message too long (max 4000 chars)"}), 400

    ip = _client_ip()
    allowed, retry_after = _rate_limiter.allow(ip)
    if not allowed:
        return jsonify({
            "error": "rate_limit_exceeded",
            "message": f"Too many requests. Retry after {retry_after}s.",
            "retry_after": retry_after,
        }), 429

    svc = get_chat_service()
    user_agent = request.headers.get("User-Agent", "")

    try:
        session_id = svc.get_or_create_session(session_id, user_agent, ip)
        result = svc.chat(session_id, user_message)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Chat endpoint error")
        return jsonify({"error": "internal_error", "detail": str(e)}), 500


@chat_bp.route("/session/new", methods=["POST"])
def new_session():
    svc = get_chat_service()
    ip = _client_ip()
    ua = request.headers.get("User-Agent", "")
    session_id = svc.get_or_create_session(None, ua, ip)
    return jsonify({
        "session_id": session_id,
        "welcome_message": svc.welcome_message(),
        "bot_name": svc.store.bot_name,
    })


@chat_bp.route("/session/<session_id>/history", methods=["GET"])
def history(session_id: str):
    if not db.session_exists(session_id):
        return jsonify({"error": "session not found"}), 404
    msgs = db.get_messages(session_id, limit=200)
    return jsonify({"session_id": session_id, "messages": msgs})


@chat_bp.route("/session/<session_id>/clear", methods=["POST"])
def clear(session_id: str):
    if not db.session_exists(session_id):
        return jsonify({"error": "session not found"}), 404
    deleted = db.clear_session_messages(session_id)
    return jsonify({"cleared": deleted})
