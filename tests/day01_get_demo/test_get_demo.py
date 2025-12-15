import pytest


@pytest.mark.smoke  # ✅ 给这个用例打一个 “smoke” 标签
@pytest.mark.api  # ✅ 再打一个 “api” 标签
@pytest.mark.network
def test_get_demo(client):
    # 发起请求
    response = client.get("/get")

    # 打印响应内容
    print("Status_Code:", response.status_code)
    print("Response body:", response.json())

    # ④验证响应
    assert response.status_code == 200
    data = response.json()
    assert "headers" in data
