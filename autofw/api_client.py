# autofw/api_client.py
"""
兼容旧代码用的“转发层”：
conftest 里还在从 autofw/api_client.py 加载 APIClient，
这里把真正实现从 autofw.utils.api_client 里 re-export 出来。
"""

from autofw.utils.api_client import APIClient
import requests


class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}{path}"

    def get(self, path: str, params=None, **kwargs):
        url = self._build_url(path)
        return self.session.get(url, params=params, timeout=self.timeout, **kwargs)

    def post(self, path: str, json=None, data=None, **kwargs):
        """
        发送 POST 请求：
        - json: 以 JSON 形式发送（常用）
        - data: 表单 x-www-form-urlencoded
        """
        url = self._build_url(path)
        return self.session.post(
            url,
            json=json,
            data=data,
            timeout=self.timeout,
            **kwargs,
        )

    def with_headers(self, headers: dict) -> "APIClient":
        """
        克隆一个带额外 headers 的 client，不污染原来的 session。
        """
        new_client = APIClient(self.base_url, self.timeout)
        new_client.session.headers.update(self.session.headers)
        new_client.session.headers.update(headers)
        return new_client
