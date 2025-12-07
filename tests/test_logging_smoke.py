from autofw.utils.logger_helper import get_logger
from autofw.utils.api_client import APIClient


def test_logging_smoke():
    logger = get_logger("debug.smoke")
    logger.info("hello from smoke test")

    client = APIClient(base_url="https://postman-echo.com", timeout=3)
    resp = client.get("/get", params={"ping": "pong"})
    assert resp.status_code == 200
