"""
autofw/utils/assertions.py

这里放的是：在接口自动化里可以复用的“断言工具函数”。

目前有两个：
1. assert_status_code  —— 统一断言 HTTP 状态码
2. assert_dict_contains —— 断言“实际结果至少包含期望子集”（支持嵌套 dict）
"""

from __future__ import annotations

from collections.abc import (  # Any 表示“任意类型”，方便做通用工具
    Mapping,  # Mapping 是“映射类型”接口，dict 就实现了 Mapping
    Sequence,
    Sized,
)
from typing import Any

from requests import Response  # requests.Response，用于类型标注


def assert_status_code(resp: Response, expected_status: int) -> None:
    """
    统一断言 HTTP 状态码的工具函数。

    参数：
    - resp: requests.Response 对象（接口真实返回）
    - expected_status: 期望的 HTTP 状态码（如 200, 404 等）

    作用：
    - 如果状态码不等于 expected_status，就抛出 AssertionError，
      并带上一点调试信息（实际状态码 + 响应内容前 200 字符）。
    """
    actual_status = resp.status_code

    if actual_status != expected_status:
        # 尝试拿一小段 body，方便排查
        try:
            content = resp.text
        except Exception:
            content = "<no text>"

        snippet = (content or "")[:200]
        raise AssertionError(
            f"状态码不匹配：actual={actual_status}, expected={expected_status}, "
            f"actual={actual_status}, body_snippet={snippet!r}"
        )


def _assert_dict_contains(
        actual: Mapping[str, Any],
        expected: Mapping[str, Any],
        path: str = "") -> None:
    """
    递归判断 actual 是否“包含” expected_subset 这个子集。

    - key 必须存在
    - 如果 value 是 dict，则递归检查
    - 否则做相等判断
    断言“actual 至少包含 expected_subset 中的所有键值对”。

    👇 用白话说就是：
    - expected_subset 是我们“关心的那一部分期望数据”（子集），
      actual 是接口真实返回的完整 JSON（可能字段很多）。
    - 我们不要求 actual == expected_subset（完全相等），
      只要求：expected_subset 里的每一个 key / value，
      在 actual 里都能找到，而且 value 一样。

    支持的特性：
    - 支持嵌套 dict：
        比如：
        actual = {"json": {"username": "day10_user", "password": "123"}}
        expected_subset = {"json": {"username": "day10_user"}}
      也会通过（对 json 这个子 dict 再递归比较）

    参数：
    - actual: 实际返回体（通常是 resp.json() 得到的 dict）
    - expected_subset: 期望“子集”，只写自己关心的那部分内容
    """

    # 1. 类型检查 —— 提前发现把奇怪的类型传进来的问题
    assert isinstance(actual, Mapping), (
        f"actual 必须是 dict / Mapping，当前类型: {type(actual)}"
    )
    assert isinstance(expected, Mapping), (
        f"expected_subset 必须是 dict / Mapping，当前类型: {type(expected)}"
    )

    # 2. 遍历“期望子集”中的所有 key / value
    for key, expected_value in expected.items():
        current_path = f"{path}.{key}" if path else key

        # 2.1 先确保 key 至少在 actual 里存在
        if key not in actual:
            raise AssertionError(
                f"Key {current_path} missing in actual dict")

        # 2.2 拿到 actual 中对应 key 的真实值
        actual_value = actual[key]

        # 2.3 如果“期望值”和“实际值”都是 dict / Mapping，
        #     那么说明这是一个“嵌套结构”，递归继续往里比较
        if isinstance(expected_value, dict) and isinstance(actual_value, dict):
            # 递归：继续比较子 dict
            _assert_dict_contains(actual_value, expected_value, current_path)
        else:
            if actual_value != expected_value:
                # 2.4 否则就是普通值（字符串、数字、布尔等），直接判断相等
                raise AssertionError(
                    f"Value mismatch at {current_path}: "
                    f"actual={actual_value!r}, expected={expected_value!r}"
                )


def assert_dict_contains(
        actual: Mapping[str, Any],
        expected_subset: Mapping[str, Any]) -> None:
    """
    断言 actual 字典“包含” expected_subset 描述的子集。
    """
    _assert_dict_contains(actual, expected_subset, path="")


# ================= Day14 新增：路径断言 + 列表长度断言 ================= #

def _get_by_path(data: Any, path: str) -> Any:
    """
     从嵌套的 dict / list 结构中，通过“点号路径”取值。

     约定：
     - 用 '.' 分隔层级，比如: "json.user.id"
     - 如果某一层是 list，可以用数字做下标，比如: "items.0.id"

     示例：
         body = {
             "json": {
                 "user": {"id": 10086, "name": "Quintai-Li"},
                 "tags": ["api", "test"],
             },
             "items": [
                 {"id": 1},
                 {"id": 2},
             ],
         }

         _get_by_path(body, "json.user.id")   -> 10086
         _get_by_path(body, "items.1.id")     -> 2
     """
    current: Any = data

    for part in path.split("."):
        # dict 分支
        if isinstance(current, Mapping):
            if part not in current:
                msg = (
                    f"Path {path!r} not found: missing key {part!r}",
                    f"current={current!r}"
                )
                # ❗ 这里只传一个字符串，不要传两个参数
                raise AssertionError(msg)

            # ❗ 关键：每一层都要往下“走”一步
            current = current[part]

        # list / tuple分支（非字符串）
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
            if not part.isdigit():
                msg = (
                    f"Path {path!r} expects list index at {path!r},"
                    f"but got non-digit segment. current={current!r}"
                )
                raise AssertionError(msg)

            idx = int(part)
            try:
                current = current[idx]
            except IndexError:
                msg = (
                    f"Path {path!r}: index {idx} out of range for sequence"
                    f"of length {len(current)}; current={current!r}"
                )
                raise AssertionError(msg)
        else:
            msg = (
                f"Path {path!r}: not found: cannot descend into "
                f"{type(current).__name__!r}, value={current!r}"
            )
            raise AssertionError(msg)

    return current


def assert_json_value(
        body: Mapping[str, Any],
        path: str,
        expected: Any
) -> None:
    """
    按“点号路径”断言 JSON 值。

    示例：
        assert_json_value(body, "json.user.id", 10086)
        assert_json_value(body, "items.0.id", 1)
    """
    actual = _get_by_path(body, path)

    if actual != expected:
        msg = (
            f"Json value mismatch at path{path!r}:"
            f"expected={expected!r}, actual={actual!r}"
        )
        raise AssertionError(msg)


def assert_list_length(
        seq: Sized,
        expected_length: int,
        msg: str | None = None
) -> None:
    """
    断言一个“可取长度”的对象（list/tuple 等）的长度。

    - seq: 任意实现了 __len__ 的对象
    - expected_length: 期望长度
    - msg: 可选，自定义错误信息
    """
    actual = len(seq)
    if actual != expected_length:
        default_msg = (
            f"List length mismatch: expected={expected_length},"
            f"actual={actual}, value={seq!r}"
        )
        raise AssertionError(msg or default_msg)
