# autofw/utils/response_builder.py
from __future__ import annotations

import json
from typing import Any

import requests


def build_response(
        status_code: int,
        json_body: dict[str, Any] | None = None,
        url: str = "http://mock.local",
        headers: dict[str, str] | None = None,
) -> requests.Response:
    """
    构造一个假的 requests.Response，用于 Mock 测试。
    """
    resp = requests.Response()
    resp.status_code = status_code
    resp.url = url

    h = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        h.update(headers)
    resp.headers.update(h)

    if json_body is None:
        resp._content = b""
    else:
        resp._content = json.dumps(json_body, ensure_ascii=False).encode("utf-8")

    return resp
