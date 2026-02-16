"""
Пример интеграционного теста с реальными HTTP-запросами между микросервисами
"""

import pytest
import requests
from test_tasks import APIClient


@pytest.fixture(scope="module")
def api_base_url():
    return "http://localhost:8000"


@pytest.fixture(scope="module")
def api_client(api_base_url):
    return APIClient(api_base_url)


@pytest.mark.integration
def test_api_client_get_real_request(api_client):
    result = api_client.get("users")

    assert "users" in result or "data" in result
    assert isinstance(result, dict)


@pytest.mark.integration
def test_api_client_post_real_request(api_client):
    import time
    user_data = {
        "name": "Test User",
        "email": f"test_{int(time.time())}@example.com"
    }

    result = api_client.post("users", user_data)

    assert "id" in result
    assert result["name"] == user_data["name"]
    assert result["email"] == user_data["email"]


@pytest.mark.integration
def test_api_client_error_handling(api_client):
    with pytest.raises(Exception):
        api_client.get("nonexistent-endpoint")


@pytest.fixture(scope="module")
def test_server():
    import subprocess
    import time

    process = subprocess.Popen(["python", "test_server.py"])
    time.sleep(2)

    yield

    process.terminate()
    process.wait()


@pytest.mark.integration
@pytest.mark.slow
def test_full_integration_flow(test_server, api_client):
    user_data = {"name": "Integration Test", "email": "integration@test.com"}

    created = api_client.post("users", user_data)
    user_id = created["id"]

    retrieved = api_client.get(f"users/{user_id}")
    assert retrieved["name"] == user_data["name"]

    updated_data = {"name": "Updated Name"}
    updated = api_client.post(f"users/{user_id}", updated_data)
    assert updated["name"] == "Updated Name"


@pytest.mark.integration
def test_api_with_real_database(api_client):
    user1 = api_client.post("users", {"name": "User 1", "email": "user1@test.com"})
    user2 = api_client.post("users", {"name": "User 2", "email": "user2@test.com"})

    users = api_client.get("users")

    assert len(users) >= 2
    assert any(u["id"] == user1["id"] for u in users)
    assert any(u["id"] == user2["id"] for u in users)


@pytest.mark.integration
def test_api_timeout_handling(api_client):
    client_with_short_timeout = APIClient(api_client.base_url, timeout=0.001)

    with pytest.raises(requests.exceptions.Timeout):
        client_with_short_timeout.get("slow-endpoint")


@pytest.mark.integration
def test_api_network_error_handling():
    client = APIClient("http://nonexistent-server-12345.com")

    with pytest.raises(requests.exceptions.ConnectionError):
        client.get("users")
