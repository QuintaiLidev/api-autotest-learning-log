# autofw/utils/api_client.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

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
    session: requests.Session = field(default_factory=requests.Session)

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
            session=new_session,
        )

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
        self.session.headers.setdefault("User-Agent", "APIClient/1.0")
        self.session.headers.setdefault("Accept", "application/json, */*;q=0.8")

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

    # ------------------ 对外暴露的方法 ------------------ #

    def get(
            self,
            path: str,
            params: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> requests.Response:
        """
        发送 GET 请求，并且记录基础日志 + 请求级 request_id
        """
        url = self._full_url(path)
        req_id = self._new_req_id()  # 8位短 ID， 够用又好看
        # 这里用 logging 的占位符写法，避免字符串拼接带来的格式问题
        logger.info("[REQ %s] GET %s params=%s", req_id, url, params)

        try:
            resp = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
        except Exception as e:
            # 记录错误日志，然后原样抛出（不吞异常）
            logger.exception(
                "[ERR %s] GET %s error=%s",
                req_id,
                url,
                e,
            )
            raise
        logger.info(
            "[RESP %s] GET %s status=%s",
            req_id,
            url,
            resp.status_code
        )
        return resp

    def post(
            self,
            path: str,
            json: Optional[Dict[str, Any]] = None,
            data: Any = None,
            **kwargs,
    ) -> requests.Response:
        """
        发送 POST 请求，并记录基础日志 + 请求级 request_id。
        """
        url = self._full_url(path)
        req_id = self._new_req_id()

        logger.info("[REQ %s] POST %s json=%s data=%s", req_id, url, json, data)

        try:
            resp = self.session.post(
                url,
                json=json,
                data=data,
                timeout=self.timeout,
                **kwargs,
            )
        except Exception as e:
            logger.exception("[ERR %s] POST %s error=%s", req_id, url, e)
            raise

        logger.info(
            "[RESP %s] POST %s status=%s",
            req_id,
            url,
            resp.status_code,
        )

        return resp
