from datetime import time

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from habits.models import Habit

User = get_user_model()


@pytest.mark.django_db
class TestHabitModel:
    """Тесты для модели Habit"""

    def test_create_habit(self):
        """Тест создания привычки"""
        user = User.objects.create_user(username="testuser", password="testpass123")

        habit = Habit.objects.create(
            user=user,
            place="Дом",
            time=time(8, 0),
            action="Пить воду",
            duration=30,
            frequency=1,
            is_public=True,
        )

        assert habit.user == user
        assert habit.action == "Пить воду"
        assert habit.duration == 30
        assert habit.frequency == 1
        assert habit.is_public is True

    def test_duration_validation(self):
        """Тест валидации времени выполнения"""
        user = User.objects.create_user(username="testuser2", password="testpass123")

        habit = Habit(
            user=user, place="Дом", time=time(8, 0), action="Тест", duration=150
        )

        with pytest.raises(ValidationError) as exc:
            habit.full_clean()

        assert "не должно превышать 120 секунд" in str(exc.value)

    def test_frequency_validation(self):
        """Тест валидации периодичности"""
        user = User.objects.create_user(username="testuser3", password="testpass123")

        habit = Habit(
            user=user,
            place="Дом",
            time=time(8, 0),
            action="Тест",
            duration=60,
            frequency=10,
        )

        with pytest.raises(ValidationError) as exc:
            habit.full_clean()

        assert "не может быть больше 7 дней" in str(exc.value)

    def test_pleasant_habit_validation(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        user = User.objects.create_user(username="testuser4", password="testpass123")

        habit = Habit(
            user=user,
            place="Дом",
            time=time(8, 0),
            action="Приятная привычка",
            duration=60,
            is_pleasant=True,
            reward="Вознаграждение",
        )

        with pytest.raises(ValidationError) as exc:
            habit.full_clean()

        assert "не может быть вознаграждения" in str(exc.value)
