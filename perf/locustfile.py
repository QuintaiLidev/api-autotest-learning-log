# perf/locustfile.py
from __future__ import annotations

import os

from locust import HttpUser, between, task


def _env(name:str, default: str) -> str:
    v = os.getenv(name)
    return v if v else default

class EchoUser(HttpUser):
    """
    Week04: Minimal performance loop with Locust.

    Notes:
    - Default host is postman-echo.com
    - You can override with
        set BASE_URL env
        or pass --host in CLI
    """

    # Wait time between tasks (simulate real user pacing)
    wait_time = between(0.2,1)

    # if you don't pass  --host, Locust uses this host attr.
    host = _env("BASE_URL", "https://postman-echo.com")

    @task(3)
    def get_echo(self):
        # a small, stable GET scenario
        with self.client.get(
                "/get",
                params={"ping": "pong"},
                name="GET /get",
                catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"status={r.status_code}")
            else:
                r.success()

    @task(1)
    def post_echo(self):
        # a small POST scenario
        payload = {"user":  {"id": 10086, "name": "Quintai_Li"}}
        with self.client.post(
                "/post",
                json=payload,
                name="POST /post",
                catch_response=True
        ) as r:
            if r.status_code != 200:
                r.failure(f"status={r.status_code}")
            else:
                r.success()