from datetime import time

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from habits.models import Habit

User = get_user_model()


@pytest.mark.django_db
class TestHabitAPI:
    """Тесты для API привычек"""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def test_user(self):
        return User.objects.create_user(
            username="apitestuser", password="testpass123", email="test@example.com"
        )

    @pytest.fixture
    def auth_client(self, api_client, test_user):
        response = api_client.post(
            "/api/token/", {"username": "apitestuser", "password": "testpass123"}
        )
        token = response.data["access"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api_client

    def test_get_habits_unauthorized(self, api_client):
        """Тест: неавторизованный доступ должен возвращать 401"""
        response = api_client.get("/api/habits/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_habit(self, auth_client, test_user):
        """Тест создания привычки через API"""
        data = {
            "place": "Дом",
            "time": "08:00:00",
            "action": "API тест",
            "duration": 30,
            "frequency": 1,
            "is_public": True,
        }

        response = auth_client.post("/api/habits/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["action"] == "API тест"
        assert Habit.objects.filter(user=test_user, action="API тест").exists()

    def test_list_habits(self, auth_client, test_user):
        """Тест получения списка привычек"""
        Habit.objects.create(
            user=test_user,
            place="Дом",
            time=time(8, 0),
            action="Тестовая привычка",
            duration=30,
            frequency=1,
        )

        response = auth_client.get("/api/habits/")

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 1

    def test_validation_error(self, auth_client):
        """Тест валидации через API"""
        data = {
            "place": "Дом",
            "time": "08:00:00",
            "action": "Тест",
            "duration": 150,
            "frequency": 1,
            "is_public": True,
        }

        response = auth_client.post("/api/habits/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

        error_message = str(response.data["non_field_errors"][0])
        assert "120 секунд" in str(response.data["non_field_errors"])

    def test_public_habits_endpoint(self, auth_client, test_user):
        """Тест эндпоинта публичных привычек"""
        Habit.objects.create(
            user=test_user,
            place="Парк",
            time=time(9, 0),
            action="Публичная привычка",
            duration=60,
            frequency=1,
            is_public=True,
        )

        response = auth_client.get("/api/public-habits/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_get_single_habit(self, auth_client, test_user):
        """Тест получения одной привычки по ID"""
        habit = Habit.objects.create(
            user=test_user,
            place="Дом",
            time=time(8, 0),
            action="Привычка для детального просмотра",
            duration=30,
            frequency=1,
        )

        response = auth_client.get(f"/api/habits/{habit.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["action"] == "Привычка для детального просмотра"
        assert response.data["duration"] == 30

    def test_update_partial_habit(self, auth_client, test_user):
        """Тест частичного обновления привычки (PATCH)"""
        habit = Habit.objects.create(
            user=test_user,
            place="Старое место",
            time=time(8, 0),
            action="Привычка для частичного обновления",
            duration=30,
            frequency=1,
        )

        data = {"action": "Обновленное действие", "place": "Новое место"}

        response = auth_client.patch(f"/api/habits/{habit.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["action"] == "Обновленное действие"
        assert response.data["place"] == "Новое место"

        habit.refresh_from_db()
        assert habit.time.hour == 8
        assert habit.duration == 30

    def test_cannot_access_other_user_habit(self, auth_client, test_user):
        """Тест: нельзя получить доступ к привычке другого пользователя"""
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )

        other_habit = Habit.objects.create(
            user=other_user,
            place="Дом",
            time=time(8, 0),
            action="Привычка другого пользователя",
            duration=30,
            frequency=1,
        )

        response = auth_client.get(f"/api/habits/{other_habit.id}/")

        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_403_FORBIDDEN,
        ]
