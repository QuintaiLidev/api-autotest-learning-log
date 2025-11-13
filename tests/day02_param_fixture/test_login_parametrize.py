import pytest
import requests

# ①定义公共接口
Base_URL = "https://httpbin.org"


# ②参数化测试
@pytest.mark.parametrize("endpoint, expected_status", [
    ("/get", 200),
    ("/status/200", 200),
    ("/status/404", 404)
])
def test_api_status(endpoint, expected_status,setup_env):
    """测试不同接口的返回状态码"""
    url = Base_URL + endpoint
    response = requests.get(url)
    print(f"Testing endpoint:{url}, got status:{response.status_code}")
    assert response.status_code == expected_status
