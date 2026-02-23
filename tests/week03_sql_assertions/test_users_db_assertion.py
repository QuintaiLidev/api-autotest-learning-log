# tests/week03_sql_assertions/test_users_db_assertion.py

import pytest

pytestmark = pytest.mark.db  # ✅ 单独标记 db 层（不会被 network job 误跑）


def test_create_user_persisted(pg, pg_clean_users):
    username = "u_week03"
    email = "u_week03@example.com"

    # “模拟接口写入后的落库结果”: 这里先用 INSERT　表示接口 side-effect
    pg.execute(
        "INSERT INTO users(username, email, status) VALUES (%s, %s, %s);",
        (username, email, "active"),
    )

    row = pg.fetchone("SELECT username, email, status FROM users WHERE username=%s;", (username,))
    assert row is not None
    assert row["username"] == username
    assert row["email"] == email
    assert row["status"] == "active"


def test_update_user_persisted(pg, pg_clean_users):
    username = "u_week03_2"
    pg.execute(
        "INSERT INTO users(username, email, status) VALUES (%s, %s, %s);",
        (username, "u2@example.com", "active")
    )

    # "模拟接口更新后的落库结果"
    pg.execute(
        "update users SET status=%s, update_at=NOW() WHERE username=%s;",
        ("disabled", username),
    )

    row = pg.fetchone("SELECT status FROM users WHERE username=%s;", (username,))
    assert row is not None
    assert row["status"] == "disabled"
