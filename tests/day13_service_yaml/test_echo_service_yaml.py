# tests/day13_service_yaml/test_echo_service_yaml.py
from pathlib import Path

import pytest
import yaml

from autofw.services.demo_echo_service import EchoService
from autofw.utils.assertions import assert_status_code,assert_dict_contains


# ---------- 加载 YAML 测试数据 ---------- #

DATA_FILE = Path(__file__).with_name("echo_get_cases.yml")


def load_cases():
    """
    从 echo_get_cases.yml 加载测试用例列表。
    每条用例是一个 dict，包含：
    - id
    - params
    - expected_status
    - expected_subset
    """
    with DATA_FILE.open(encoding="utf-8") as f:
        cases = yaml.safe_load(f) or []
    return cases


CASES = load_cases()


# ---------- 用例区域：Service + YAML 驱动 ---------- #


@pytest.mark.service
@pytest.mark.data_driven
@pytest.mark.assertions
@pytest.mark.parametrize(
    "case",
    CASES,
    ids=[c["id"] for c in CASES],
)
def test_echo_get_with_params_yaml(echo_service: EchoService,case):
    """
    Day13：YAML 数据驱动的 Service 层用例。

    - 通过 echo_service 调用 GET /get
    - 测试数据从 echo_get_cases.yml 读取（params + 预期子集）
    """
    params = case["params"]
    expected_code = case["expected_code"]
    expected_subset = case["expected_subset"]

    # 1. 调用Service层
    resp = echo_service.get_with_params(params)

    # 2. 统一状态码断言
    assert_status_code(resp, expected_code)

    # 3. 响应体断言: 只关心 expected_subsrt 这个子集
    body = resp.json()
    assert_dict_contains(body, expected_subset)
