# autofw/utils/api_client.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from requests.adapters import HTTPAdapter
from requests import exceptions as req_exc
from urllib3.util.retry import Retry

import time
import uuid
import logging
import requests

from autofw.utils.logger_helper import get_logger  # ✅ 建议用绝对导入

logger = get_logger("autofw.api_client")  # ✅ 全局 logger


@dataclass
class APIClient:
    """
    统一的 HTTP 客户端封装：

    - 负责拼接 base_url + path
    - 统一设置 timeout
    - 封装 get / post
    - 支持 with_headers 克隆一个带额外 headers 的客户端
    """

    base_url: str  # 例如: "https://postman-echo.com"
    timeout: int = 20  # 默认超时（秒）

    # Day16 新增：重试次数 + 退避时间（秒）
    retries: int = 2  # 1 = 失败后再试2次（总共最多 3 次）
    backoff: float = 0.5  # 每次重试前 sleep 一下

    session: requests.Session = field(default_factory=requests.Session)

    # 默认请求头（可以按需扩展）
    default_headers: Dict[str, str] = field(
        default_factory=lambda: {
            "User-Agent": "APIClient/1.0",
            "Accept": "application/json, */*;q=0.8",
        }
    )

    def __post_init__(self) -> None:
        """
        dataclass 初始化后的钩子：
        - 规范 base_url 结尾不要带 '/'
        - 关闭 requests 的环境代理读取
        - 给 session 设置默认请求头
        """
        # 1）规范 base_url
        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

        # 2）最关键：禁止从系统环境读取代理（trust_env=False）
        #    这样就不会自动使用 HTTP_PROXY / HTTPS_PROXY 等环境变量，
        #    也就不会再走 127.0.0.1:7897 这种代理了。
        self.session.trust_env = False

        # 3）设置默认头
        self.session.headers.update(self.default_headers)

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.5,  # 0.5s, 1s, 2s...
            status_forcelist=(429, 500, 503, 503, 504),
            allowed_methods=frozenset(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # ------------------ 内部工具方法 ------------------ #

    def _full_url(self, path: str) -> str:
        """
        如果 path 是绝对 URL（以 http:// 或 https:// 开头），直接返回；
        否则拼接 base_url 和 path。
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return self.base_url.rstrip("/") + "/" + path.lstrip("/")

    def _new_req_id(self) -> str:
        return uuid.uuid4().hex[:8]

    # ✅ Day16 核心：统一请求入口
    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = self._full_url(path)
        req_id = self._new_req_id()

        max_attempts = 1 + int(self.retries)

        for attempt in range(1, max_attempts + 1):
            logger.info("[REQ %s] %s %s attempt=%s/%s kwargs=%s",
                        req_id, method, url, attempt, max_attempts,
                        {k: kwargs.get(k) for k in ("params", "json", "data")})

            try:
                resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
                logger.info("[RESP %s] %s %s status=%s", req_id, method, url, resp.status_code)
                return resp
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt >= max_attempts:
                    logger.exception("[ERR %s] %s %s final_error=%s", req_id, method, url, e)
                    raise

                sleep_s = float(self.backoff) * (2 ** (attempt - 1))
                logger.warning("[RETRY %s] %s %s error=%s sleep=%.2fs", req_id, method, url, e, sleep_s)
                time.sleep(sleep_s)

    def get(
            self,
            path: str,
            params=None,
            **kwargs
    ):
        return self._request("GET", path, params=params, **kwargs)

    def post(
            self,
            path: str,
            json=None,
            data=None,
            **kwargs
    ):
        return self._request("POST", path, json=json, data=data, **kwargs)

    def with_headers(self, headers: Dict[str, str]) -> "APIClient":
        """
        返回一个“克隆客户端”，在当前 client 的配置基础上，
        追加一些 headers，但不污染原来的 session.headers。

        用法示例：
            auth_client = client.with_headers({"Authorization": "Bearer xxx"})
            resp = auth_client.get("/get")

        这里会：
        - 新建一个 Session
        - 合并 default_headers + 原 session.headers + 新传入的 headers
        - 返回一个新的 APIClient 实例
        """
        new_session = requests.Session()
        new_session.trust_env = False  # 克隆出来的 client 也关闭代理

        # 合并头信息（后面的覆盖前面的）
        merged_headers: Dict[str, str] = {}
        merged_headers.update(self.default_headers)  # 默认头
        merged_headers.update(self.session.headers)  # 当前 client 的头
        merged_headers.update(headers)  # 新追加的头

        new_session.headers.update(merged_headers)

        return APIClient(
            base_url=self.base_url,
            timeout=self.timeout,
            retries=self.retries,
            backoff=self.backoff,
            session=new_session,
        )
