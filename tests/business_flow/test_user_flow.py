import pytest

pytestmark = [pytest.mark.db, pytest.mark.network]


def test_create_and_query_user_flow(user_service, pg_clean_users):
    username = "flow_user_01"
    email = "flow_user_01@example.com"

    # step1: login
    token = user_service.login("tester", "123456")
    assert token.startswith("demo-token-")

    # step2: create
    create_resp, create_row = user_service.create_user(
        token,
        username=username,
        email=email,
        status="active",
    )
    assert create_resp.status_code == 200
    assert create_row is not None
    assert create_row["username"] == username
    assert create_row["email"] == email
    assert create_row["status"] == "active"

    # step3: query
    query_resp, query_row = user_service.get_user(
        token,
        username=username,
    )
    assert query_resp.status_code == 200
    assert query_row is not None
    assert query_row["username"] == username
    assert query_row["email"] == email
    assert query_row["status"] == "active"


def test_update_user_status_flow(user_service, pg_clean_users):
    username = "flow_user_02"
    email = "flow_user_02@example.com"

    # step1: login
    token = user_service.login("tester", "123456")

    # step2: create
    _, create_row = user_service.create_user(
        token,
        username=username,
        email=email,
        status="active",
    )
    assert create_row is not None
    assert create_row["status"] == "active"

    # step3: update
    update_resp, update_row = user_service.update_user_status(
        token,
        username=username,
        new_status="disabled",
    )
    assert update_resp.status_code == 200
    assert update_row is not None
    assert update_row["username"] == username
    assert update_row["status"] == "disabled"
