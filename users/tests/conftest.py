import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Фикстура для аутентифицированного клиента"""
    response = api_client.post(
        "/api/token/", {"username": test_user.username, "password": "TestPass123"}
    )
    token = response.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client
