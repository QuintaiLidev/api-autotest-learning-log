from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from autofw.api_client import APIClient
from autofw.utils.db import PG


@dataclass
class UserService:
    """
    Demo business flow service:
    - login -> token
    - create user
    - query user
    - update user status

    Notes:
    - We use postman-echo to simulate API request/response.
    - We use Postgres users table to simulate backend state change.
    """

    client: APIClient
    pg: PG

    def login(self, username: str, password: str) -> str:
        resp = self.client.post(
            "/post",
            json={"username": username, "password": password},
        )
        if resp.status_code != 200:
            raise AssertionError(f"login failed, status={resp.status_code}")

        # demo token
        return f"demo-token-{username}"

    def _auth_client(self, token: str) -> APIClient:
        return self.client.with_headers({"Authorization": f"Bearer {token}"})

    def create_user(
            self,
            token: str,
            *,
            username: str,
            email: str,
            status: str = "active",
    ) -> Tuple[Any, Optional[Dict[str, Any]]]:
        auth_client = self._auth_client(token)

        resp = auth_client.post(
            "/post",
            json={
                "action": "create_user",
                "username": username,
                "email": email,
                "status": status,
            },
        )

        if resp.status_code != 200:
            raise AssertionError(f"create_user failed, status={resp.status_code}")

        # simulate persistence side effect
        self.pg.execute(
            """
            INSERT INTO users(username, email, status)
            values (%s, %s, %s)
            ON CONFLICT (username)
            DO UPDATE SET
                email = EXCLUDED.email,
                status = EXCLUDED.status,
                update_at = NOW();
            """,
            (username, email, status),
        )

        row = self.pg.fetchone(
            "SELECT username, email, status FROM users WHERE username=%s;",
            (username,),
        )
        return resp, row

    def get_user(
            self,
            token: str,
            *,
            username: str
    ) -> Tuple[Any, Optional[Dict[str, Any]]]:
        auth_client = self._auth_client(token)

        resp = auth_client.get(
            "/get",
            params={"action": "get_user", "username": username},
        )

        if resp.status_code != 200:
            raise AssertionError(f"get_user failed, status={resp.status_code}")

        row = self.pg.fetchone(
            "SELECT username,email,status from users WHERE username=%s;",
            (username,),
        )
        return resp, row

    def update_user_status(
            self,
            token: str,
            *,
            username: str,
            new_status: str,
    ) -> Tuple[Any, Optional[Dict[str, Any]]]:
        auth_client = self._auth_client(token)

        resp = auth_client.post(
            "/post",
            json={
                "action": "update_user_status",
                "username": username,
                "status": new_status,
            }
        )

        if resp.status_code != 200:
            raise AssertionError(
                f"update_user_status failed, status={resp.status_code}"
            )

        self.pg.execute(
            """
            UPDATE users
            SET status=%s, update_at=NOW()
            WHERE username=%s;
            """,
            (new_status, username),
        )

        row = self.pg.fetchone(
            "SELECT username, email, status FROM users WHERE username=%s;",
            (username,),
        )
        return resp, row
