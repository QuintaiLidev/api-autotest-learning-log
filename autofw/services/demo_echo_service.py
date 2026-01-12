# autofw/services/demo_echo_service.py
from __future__ import annotations

from typing import Any

from autofw.api_client import APIClient


class EchoService:
    """
    一个“玩具”服务层示例，基于 postman-echo：

    - get_with_params: 对 GET /get 做了一层封装
    - post_json: 对 POST /post 做了一层封装

    以后你在真实项目里，可以对应“用户模块”、“订单模块”等，
    建自己的 XxxService 类。
    """

    def __init__(self, client: APIClient) -> None:
        self.client = client

    def get_with_params(self, params: dict[str, Any]):
        """
        调用 GET /get，并把查询参数传过去。
        一定要把 client.get(...) 的结果 return 出去！
        """
        return self.client.get("/get", params=params)

    def post_json(self, json_body: dict[str, Any]):
        """
        调用 POST /post，并发送 JSON 请求体。
        同样要记得 return。
        """
        return self.client.post("/post", json=json_body)
