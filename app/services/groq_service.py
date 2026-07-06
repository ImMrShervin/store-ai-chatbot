import logging
import time
from typing import Iterable, Optional

from groq import Groq, APIError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)


class GroqService:

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("GROQ_API_KEY is required")
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"🤖 Groq service initialized with model={model}")

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.4,
        max_tokens: int = 1024,
        retries: int = 3,
    ) -> dict:

        last_err: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=0.9,
                    stream=False,
                )
                choice = resp.choices[0]
                usage = resp.usage
                return {
                    "content": choice.message.content or "",
                    "tokens_used": getattr(usage, "total_tokens", 0) if usage else 0,
                    "model": resp.model,
                    "finish_reason": choice.finish_reason,
                }
            except RateLimitError as e:
                last_err = e
                wait = 2 ** attempt
                logger.warning(f"⚠️  Rate limited (attempt {attempt}/{retries}). Sleeping {wait}s")
                time.sleep(wait)
            except APIConnectionError as e:
                last_err = e
                logger.warning(f"⚠️  Connection error (attempt {attempt}/{retries}): {e}")
                time.sleep(1.5 * attempt)
            except APIError as e:
                last_err = e
                logger.error(f"❌ Groq API error: {e}")
                break
            except Exception as e:
                last_err = e
                logger.exception("❌ Unexpected error calling Groq")
                break

        raise RuntimeError(f"Groq call failed after {retries} attempts: {last_err}")

    def stream_chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.4,
        max_tokens: int = 1024,
    ) -> Iterable[str]:
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            logger.exception("Streaming error")
            yield f"\n\n⚠️ Error: {e}"
