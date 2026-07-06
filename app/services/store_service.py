import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StoreConfigService:

    _instance: "StoreConfigService | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = ""):
        if getattr(self, "_initialized", False) and not config_path:
            return
        if config_path:
            self._config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self._mtime: float = 0.0
        self._initialized = True
        self.reload()

    def reload(self) -> dict[str, Any]:
        if not self._config_path.exists():
            raise FileNotFoundError(
                f"❌ store_config.json not found at {self._config_path}"
            )
        with self._config_path.open("r", encoding="utf-8") as f:
            self._config = json.load(f)
        self._mtime = self._config_path.stat().st_mtime
        logger.info(f"🔄 Store config loaded from {self._config_path}")
        return self._config

    def get(self) -> dict[str, Any]:
        try:
            current_mtime = self._config_path.stat().st_mtime
            if current_mtime > self._mtime:
                logger.info("🔁 store_config.json changed on disk → hot-reload")
                self.reload()
        except FileNotFoundError:
            logger.error("store_config.json missing on disk")
        return self._config

    def save(self, new_config: dict[str, Any]) -> None:
        with self._config_path.open("w", encoding="utf-8") as f:
            json.dump(new_config, f, ensure_ascii=False, indent=2)
        self.reload()

    @property
    def store_name(self) -> str:
        return self.get().get("store", {}).get("name", "Store")

    @property
    def bot_name(self) -> str:
        return self.get().get("chatbot_settings", {}).get("bot_name", "Assistant")

    @property
    def welcome_message(self) -> str:
        msg = self.get().get("chatbot_settings", {}).get("welcome_message", "Hello!")
        return msg.replace("{store_name}", self.store_name)

    @property
    def off_topic_response(self) -> str:
        msg = self.get().get("chatbot_settings", {}).get("off_topic_response", "")
        return msg.replace("{store_name}", self.store_name)
