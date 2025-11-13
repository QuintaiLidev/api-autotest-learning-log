import requests
import pytest

def test_get_demo():
    #①使用公共API
    url = "https://httpbin.org/get"

    #②发起请求
    response = requests.get(url)

    #③打印响应内容
    print("Status_Code:", response.status_code)
    print("Response body:", response.json())

    #④验证响应
    assert response.status_code == 200
    assert "url" in response.json()