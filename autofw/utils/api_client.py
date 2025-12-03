# autofw/api_client.py
from typing import Any, Dict, Optional
import requests


class APIClient:
    def __init__(
            self,
            base_url: str = "https://postman-echo.com",
            default_headers: Optional[Dict[str, str]] = None,
            timeout: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)
        self.session.trust_env = False  # ← 关键：忽略环境变量里的 HTTP(S)_PROXY,即系统代理

    def with_headers(self, headers: Dict[str, str]) -> "APIClient":
        clone = APIClient(self.base_url, self.default_headers.copy(), self.timeout)
        clone.session.headers.update(headers)
        clone.session.trust_env = False  # 保险起见，clone 也关掉代理
        return clone

    def build_url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{path}"

    def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        url = self.build_url(path)
        return self.session.get(url, params=params, timeout=self.timeout)

    def post(
            self,
            path: str,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
    ):
        url = self.build_url(path)
        return self.session.post(url, json=json, data=data, timeout=self.timeout)
