"""
Day06：环境配置 & pytest 标记练习
"""

import pytest

from autofw.utils.config_loader import load_config


@pytest.mark.config
def test_config_default_env():
    """
    不设置 TEST_ENV 时，应该使用 config.yml 里的 default_env（dev）
    """
    cfg = load_config()
    assert cfg["env"] == "dev"
    assert cfg["base_url"].startswith("https://")
    assert cfg["timeout"] > 0


@pytest.mark.config
def test_config_switch_env_with_monkeypatch(monkeypatch):
    """
    用 monkeypatch 模拟切换 TEST_ENV，验证读取的是 staging 配置
    """
    monkeypatch.setenv("TEST_ENV", "staging")
    cfg = load_config()
    assert cfg["env"] == "staging"
    # 我们在 config.yml 里把 staging 的 timeout 设成了 5
    assert cfg["timeout"] == 5


@pytest.mark.api
@pytest.mark.external  # 标记：依赖外网
def test_client_get_works_with_config(client):
    """
    验证 client 使用配置里的 base_url，能正常访问 /get
    注意：这个用例需要访问 postman-echo，因此打 external 标记
    """
    resp = client.get("get", params={"foo": "bar"})
    assert resp.status_code == 200
    data = resp.json()
    # postman-echo 会回显 query 参数
    assert data.get("args", {}).get("foo") == "bar"
