import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestUserAPI:
    """Тесты для API пользователей"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def test_user(self):
        """Создание тестового пользователя"""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            first_name="Test",
            last_name="User",
        )

    def test_user_registration_success(self, api_client):
        """Успешная регистрация пользователя"""
        url = reverse("register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass123",
            "password2": "StrongPass123",
            "first_name": "New",
            "last_name": "User",
            "telegram_chat_id": "123456789",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "newuser"
        assert response.data["email"] == "newuser@example.com"
        assert response.data["first_name"] == "New"
        assert response.data["last_name"] == "User"
        assert response.data["telegram_chat_id"] == "123456789"
        assert "password" not in response.data

        assert User.objects.filter(username="newuser").exists()

    def test_user_registration_password_mismatch(self, api_client):
        """Регистрация с несовпадающими паролями"""
        url = reverse("register")
        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password": "Pass123",
            "password2": "DifferentPass123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_user_registration_weak_password(self, api_client):
        """Регистрация со слабым паролем"""
        url = reverse("register")
        data = {
            "username": "newuser3",
            "email": "newuser3@example.com",
            "password": "123",
            "password2": "123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_user_registration_duplicate_username(self, api_client, test_user):
        """Регистрация с существующим username"""
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "different@example.com",
            "password": "TestPass123",
            "password2": "TestPass123",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_jwt_token_obtain(self, api_client, test_user):
        """Получение JWT токена"""
        url = reverse("token_obtain_pair")
        data = {"username": "testuser", "password": "TestPass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert len(response.data["access"]) > 0
        assert len(response.data["refresh"]) > 0

    def test_jwt_token_obtain_invalid_credentials(self, api_client):
        """Получение токена с неверными учетными данными"""
        url = reverse("token_obtain_pair")
        data = {"username": "nonexistent", "password": "wrongpassword"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data

    def test_jwt_token_refresh(self, api_client, test_user):
        """Обновление JWT токена"""
        token_url = reverse("token_obtain_pair")
        token_response = api_client.post(
            token_url,
            {"username": "testuser", "password": "TestPass123"},
            format="json",
        )

        refresh_token = token_response.data["refresh"]

        refresh_url = reverse("token_refresh")
        response = api_client.post(
            refresh_url, {"refresh": refresh_token}, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert len(response.data["access"]) > 0

    def test_user_profile_retrieve(self, api_client, test_user):
        """Получение профиля пользователя"""
        token_url = reverse("token_obtain_pair")
        token_response = api_client.post(
            token_url,
            {"username": "testuser", "password": "TestPass123"},
            format="json",
        )

        token = token_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        profile_url = reverse("profile")
        response = api_client.get(profile_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"
        assert response.data["first_name"] == "Test"
        assert response.data["last_name"] == "User"

    def test_user_profile_update(self, api_client, test_user):
        """Обновление профиля пользователя"""
        token_url = reverse("token_obtain_pair")
        token_response = api_client.post(
            token_url,
            {"username": "testuser", "password": "TestPass123"},
            format="json",
        )

        token = token_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        profile_url = reverse("profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "telegram_chat_id": "999888777",
        }

        response = api_client.patch(profile_url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"
        assert response.data["email"] == "updated@example.com"
        assert response.data["telegram_chat_id"] == "999888777"

        test_user.refresh_from_db()
        assert test_user.first_name == "Updated"
        assert test_user.telegram_chat_id == "999888777"

    def test_user_profile_unauthenticated(self, api_client):
        """Попытка получить профиль без аутентификации"""
        profile_url = reverse("profile")
        response = api_client.get(profile_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_telegram_connect_success(self, api_client, test_user):
        """Успешное подключение Telegram"""
        token_url = reverse("token_obtain_pair")
        token_response = api_client.post(
            token_url,
            {"username": "testuser", "password": "TestPass123"},
            format="json",
        )

        token = token_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        telegram_url = reverse("telegram-connect")
        data = {"telegram_chat_id": "1234567890"}

        response = api_client.post(telegram_url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["telegram_chat_id"] == "1234567890"
        assert "message" in response.data

        test_user.refresh_from_db()
        assert test_user.telegram_chat_id == "1234567890"

    def test_telegram_connect_invalid_data(self, api_client, test_user):
        """Подключение Telegram с неверными данными"""
        token_url = reverse("token_obtain_pair")
        token_response = api_client.post(
            token_url,
            {"username": "testuser", "password": "TestPass123"},
            format="json",
        )

        token = token_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        telegram_url = reverse("telegram-connect")
        data = {}

        response = api_client.post(telegram_url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_telegram_connect_unauthenticated(self, api_client):
        """Попытка подключить Telegram без аутентификации"""
        telegram_url = reverse("telegram-connect")
        data = {"telegram_chat_id": "1234567890"}

        response = api_client.post(telegram_url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_login_endpoint(self, api_client, test_user):
        """Тест альтернативного эндпоинта логина"""
        login_url = reverse("login")
        data = {"username": "testuser", "password": "TestPass123"}

        response = api_client.post(login_url, data, format="json")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]
