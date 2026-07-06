from pathlib import Path
from app.services.store_service import StoreConfigService

CFG = str(Path(__file__).parent.parent / "data" / "store_config.json")


def test_load_config():
    svc = StoreConfigService(CFG)
    cfg = svc.get()
    assert "store" in cfg
    assert "products" in cfg


def test_store_name_shortcut():
    svc = StoreConfigService(CFG)
    assert svc.store_name == "فروشگاه نمونه"


def test_welcome_message_interpolation():
    svc = StoreConfigService(CFG)
    msg = svc.welcome_message
    assert "فروشگاه نمونه" in msg
