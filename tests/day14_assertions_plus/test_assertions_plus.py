# tests/day14_assertions_plus/test_assertions_plus.py
from __future__ import annotations

import pytest

from autofw.utils.assertions import (
    assert_status_code,
    assert_dict_contains,
    assert_json_value,
    assert_list_length,
)
from autofw.services.demo_echo_service import EchoService


@pytest.mark.assertions
def test_assert_json_value_success():
    """
    纯本地数据，验证 assert_json_value 在嵌套 dict / list 上的行为。
    """
    body = {
        "json": {
            "user": {
                "id": 10086,
                "name": "Quintai-Li",
            },
            "tags": ["api", "test"],
        },
        "items": [
            {"id": 1},
            {"id": 2},
        ],
    }

    # dict 链路
    assert_json_value(body, "json.user.id", 10086)
    assert_json_value(body, "json.user.name", "Quintai-Li")

    # list 下标（items.1.id -> 第二个元素的 id）
    assert_json_value(body, "items.1.id", 2)


@pytest.mark.assertions
def test_assert_json_value_failure_message():
    """
    故意让断言失败，看看错误信息是否包含路径，便于排查。
    """
    body = {
        "json": {
            "user": {"id": 10086},
        }
    }

    with pytest.raises(AssertionError) as excinfo:
        assert_json_value(body, "json.user.id", 10010)  # 故意写错

    msg = str(excinfo.value)
    assert "json.user.id" in msg
    assert "expected=10010" in msg
    assert "actual=10086" in msg


@pytest.mark.assertions
def test_assert_list_length_success_and_failure():
    """
    演示 assert_list_length 的成功 / 失败场景。
    """
    data = [1, 2, 3]

    # 成功
    assert_list_length(data, 3)

    # 失败示例
    with pytest.raises(AssertionError) as excinfo:
        assert_list_length(data, 2)

    msg = str(excinfo.value)
    assert "expected=2" in msg
    assert "actual=3" in msg


@pytest.mark.service
@pytest.mark.assertions
def test_echo_post_json_with_path_assertions(echo_service: EchoService):
    """
    Day14 实战版：

    - 通过 Service 层调用 POST /post
    - 用 assert_json_value 做“路径断言”，让用例更贴近业务含义
    """
    payload = {
        "user": {
            "id": 10086,
            "name": "Quintai-Li",
        },
        "meta": {
            "env": "dev",
            "page": 1,
        },
    }

    # 通过 Service 层发送请求
    resp = echo_service.post_json(payload)

    # 统一状态码断言
    assert_status_code(resp, 200)

    body = resp.json()

    # postman-echo 的 /post 会在 json 字段里回显原始 JSON 请求体
    assert_json_value(body, "json.user.id", 10086)
    assert_json_value(body, "json.user.name", "Quintai-Li")
    assert_json_value(body, "json.meta.env", "dev")
    assert_json_value(body, "json.meta.page", 1)

    # 顺便再用一次字典子集断言，验证兼容性
    expected_subset = {
        "json": {
            "user": {
                "id": 10086,
            }
        }
    }
    assert_dict_contains(body, expected_subset)
