import logging
from typing import Optional

from app.config import Config
from app.models import database as db
from app.services.groq_service import GroqService
from app.services.prompt_builder import PromptBuilder
from app.services.store_service import StoreConfigService

logger = logging.getLogger(__name__)


class ChatService:

    def __init__(self):
        self.store = StoreConfigService(Config.STORE_CONFIG_PATH)
        self.groq = GroqService(api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL)

    def get_or_create_session(
        self,
        session_id: Optional[str],
        user_agent: str = "",
        ip: str = "",
    ) -> str:
        if session_id and db.session_exists(session_id):
            if db.is_session_expired(session_id, Config.SESSION_TIMEOUT_MINUTES):
                logger.info(f"⏰ Session {session_id} expired → creating new")
                return db.create_session(user_agent, ip)
            db.touch_session(session_id)
            return session_id
        return db.create_session(user_agent, ip)

    def chat(self, session_id: str, user_message: str) -> dict:
        user_message = (user_message or "").strip()
        if not user_message:
            raise ValueError("Empty message")

        db.add_message(session_id, "user", user_message)

        system_prompt = PromptBuilder.build(self.store.get())
        history = db.get_messages(session_id, limit=Config.MAX_HISTORY_MESSAGES)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        for m in history[-Config.MAX_HISTORY_MESSAGES:]:
            messages.append({"role": m["role"], "content": m["content"]})

        try:
            result = self.groq.chat_completion(
                messages=messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
            )
        except Exception as e:
            logger.exception("Groq call failed")
            error_reply = (
                "متأسفانه در حال حاضر مشکلی در ارتباط با سرویس هوش مصنوعی پیش آمده. "
                "لطفاً چند لحظه دیگر مجدداً تلاش کنید.\n\n"
                "Sorry, there was an issue connecting to the AI service. Please try again shortly."
            )
            db.add_message(session_id, "assistant", error_reply, model="error")
            return {
                "reply": error_reply,
                "session_id": session_id,
                "tokens_used": 0,
                "model": "error",
                "error": str(e),
            }

        db.add_message(
            session_id,
            "assistant",
            result["content"],
            tokens_used=result["tokens_used"],
            model=result["model"],
        )
        db.touch_session(session_id)

        return {
            "reply": result["content"],
            "session_id": session_id,
            "tokens_used": result["tokens_used"],
            "model": result["model"],
        }

    def welcome_message(self) -> str:
        return self.store.welcome_message
