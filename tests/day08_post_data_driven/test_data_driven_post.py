import pytest

from autofw.utils.data_loader import load_yaml

# 模块加载时，就把 YAML 读进来
cases = load_yaml("day08_post_cases.yml")


@pytest.mark.data_driven
@pytest.mark.parametrize(
    "case",  # ← 这里是 pytest 传给测试函数的参数名
    cases,  # ← 这里是上面的 Python 变量 `cases`
    ids=[c["name"] for c in cases],
)
def test_data_driven_post(client, case):
    """
    用 YAML 驱动 POST 用例：
    - 接口：POST /post  （postman-echo 的回显接口）
    - 请求体：来自 YAML 的 body
    - 行为：断言状态码，并校验回显的 json
    """
    path = case["path"]
    body = case.get("body") or {}
    expected_status = case["expected_status"]

    # 发送post请求
    resp = client.post(path, json=body)

    # 断言状态码
    assert resp.status_code == expected_status

    # ）postman-echo 会把我们发的 JSON 回显在 resp.json()["json"] 里
    resp_json = resp.json()
    # postman-echo 把我们发的 JSON 放在 "json" 字段里
    echoed_json = resp_json.get("json", {})

    # ⚠️ 特殊情况：当 body 是空 {} 时，postman-echo 会返回 json: null（Python 里的 None）
    if body == {} and echoed_json is None:
        echoed_json = {}
    # 只要保证回显的内容 == 我们发的 body 即可
    assert echoed_json == body
