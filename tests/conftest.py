import pytest
import requests


@pytest.fixture(scope="function")
def setup_env():
    print("\n[Fixture]初始化测试环境")
    yield
    print("[Fixture]测试结束，清理环境")


@pytest.fixture(scope="session")
def get_token():
    """
    模拟获取登录token的前置操作
    scope=“session” 表示整个测试运行期间只执行一次
    """
    print("\n[Fixture]开始获取token...")
    url = "https://httpbin.org/post"
    payload = {
        "username": "test_user",
        "password": "123456"
    }

    # 这里用httpbin模拟登录接口
    response = requests.post(url, json=payload)

    # 模拟从响应中“提取token”
    # 实际项目中你会从response.json()里拿真实字段
    if response.status_code == 200:
        # 随便拿一个字段当作token（这里只是一个模拟）
        token = response.json().get("json", {}).get("username", "") + "fake_token"
    else:
        token = ""

    print(f"[Fixture]获取到的 token{token}")
    # yield 前 = 前置逻辑
    yield token
    # yield 后 = 后置逻辑
    print("[Fixture] 测试结束，清理token（这里暂时只是打印）")