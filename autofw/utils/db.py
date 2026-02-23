import os
import time
from typing import Any, Dict, List, Optional, Sequence

import psycopg2
from psycopg2.extras import RealDictCursor


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v else default


class PG:
    """
    Minimal Postgres helper for tests:
    - connect with retry (wait db ready)
    - execute / fetchone / fetchall
    """

    def __init__(
        self,
        host: str = _env("PGHOST", "127.0.0.1"),
        port: int = int(_env("PGPORT", "5432")),
        db: str = _env("PGDATABASE", "autofw"),
        user: str = _env("PGUSER", "autofw"),
        password: str = _env("PGPASSWORD", "autofw"),
        connect_timeout: int = int(_env("PGCONNECT_TIMEOUT", "3")),
    ) -> None:
        self.dsn = (
            f"host={host} port={port} dbname={db} user={user} "
            f"password={password} connect_timeout={connect_timeout}"
        )

    def connect(self):
        return psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)

    def wait_ready(self, retries: int = 20, sleep: float = 0.5) -> None:
        last_err: Optional[Exception] = None
        for _ in range(retries):
            try:
                with self.connect() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1;")
                        return
            except Exception as err:  # noqa: BLE001
                last_err = err
                time.sleep(sleep)

        raise RuntimeError(
            f"Postgres not ready after retries. last_err={last_err!r}"
        ) from last_err

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> int:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.rowcount

    def fetchone(
        self, sql: str, params: Optional[Sequence[Any]] = None
    ) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return dict(row) if row else None

    def fetchall(
        self, sql: str, params: Optional[Sequence[Any]] = None
    ) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                return [dict(r) for r in rows]