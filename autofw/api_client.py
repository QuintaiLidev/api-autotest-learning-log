# autofw/api_client.py
"""
兼容旧代码用的“转发层”：
conftest 里还在从 autofw/api_client.py 加载 APIClient，
这里把真正实现从 autofw.utils.api_client 里 re-export 出来。

建议以后新代码都用：
    from autofw.utils.api_client import APIClient
"""

from autofw.utils.api_client import APIClient

__all__ = ["APIClient"]