import json
from pathlib import Path

from app.services.prompt_builder import PromptBuilder


def _sample_config():
    return json.loads(
        (Path(__file__).parent.parent / "data" / "store_config.json").read_text(encoding="utf-8")
    )


def test_prompt_contains_store_name():
    prompt = PromptBuilder.build(_sample_config())
    assert "فروشگاه نمونه" in prompt


def test_prompt_contains_products():
    prompt = PromptBuilder.build(_sample_config())
    assert "prod_1" in prompt
    assert "محصول نمونه ۱" in prompt


def test_prompt_contains_off_topic_rule():
    prompt = PromptBuilder.build(_sample_config())
    assert "STRICT SCOPE RULES" in prompt
    assert "STORE DATA" in prompt


def test_prompt_is_non_empty():
    prompt = PromptBuilder.build(_sample_config())
    assert len(prompt) > 500
