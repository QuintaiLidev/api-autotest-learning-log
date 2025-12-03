"""
autofw/utils/assertions.py

这里放的是：在接口自动化里可以复用的“断言工具函数”。

目前有两个：
1. assert_status_code  —— 统一断言 HTTP 状态码
2. assert_dict_contains —— 断言“实际结果至少包含期望子集”（支持嵌套 dict）
"""

from collections.abc import Mapping  # Mapping 是“映射类型”接口，dict 就实现了 Mapping
from typing import Any               # Any 表示“任意类型”，方便做通用工具
from requests import Response        # requests.Response，用于类型标注


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
    assert actual_status == expected_status, (
        f"状态码不匹配：actual={actual_status}, expected={expected_status}, "
        f"body={resp.text[:200]!r}"
    )


def assert_dict_contains(actual: Mapping[str, Any], expected_subset: Mapping[str, Any]) -> None:
    """
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
    assert isinstance(expected_subset, Mapping), (
        f"expected_subset 必须是 dict / Mapping，当前类型: {type(expected_subset)}"
    )

    # 2. 遍历“期望子集”中的所有 key / value
    for key, expected_value in expected_subset.items():
        # 2.1 先确保 key 至少在 actual 里存在
        assert key in actual, (
            f"缺少键: {key!r}，"
            f"actual.keys()={list(actual.keys())}"
        )

        # 2.2 拿到 actual 中对应 key 的真实值
        actual_value = actual[key]

        # 2.3 如果“期望值”和“实际值”都是 dict / Mapping，
        #     那么说明这是一个“嵌套结构”，递归继续往里比较
        from collections.abc import Mapping as _Mapping
        if isinstance(expected_value, _Mapping) and isinstance(actual_value, _Mapping):
            # 递归：继续比较子 dict
            assert_dict_contains(actual_value, expected_value)
        else:
            # 2.4 否则就是普通值（字符串、数字、布尔等），直接判断相等
            assert actual_value == expected_value, (
                f"键 {key!r} 的值不匹配："
                f"actual={actual_value!r}, expected={expected_value!r}"
            )
