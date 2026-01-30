import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Тесты для модели пользователя"""

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            telegram_chat_id="123456789",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.telegram_chat_id == "123456789"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password("TestPass123")

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="AdminPass123"
        )

        assert superuser.username == "admin"
        assert superuser.email == "admin@example.com"
        assert superuser.is_active is True
        assert superuser.is_staff is True
        assert superuser.is_superuser is True

    def test_user_str_method(self):
        """Тест строкового представления"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPass123"
        )

        assert str(user) == "testuser"

    def test_user_without_username(self):
        """Тест: пользователь без username должен вызывать ошибку"""
        with pytest.raises(ValueError):
            User.objects.create_user(
                username="", email="test@example.com", password="TestPass123"
            )

    def test_update_telegram_chat_id(self):
        """Тест обновления Telegram chat_id"""
        user = User.objects.create_user(
            username="telegramuser",
            email="telegram@example.com",
            password="TestPass123",
        )

        user.telegram_chat_id = "987654321"
        user.save()

        user.refresh_from_db()
        assert user.telegram_chat_id == "987654321"

    def test_user_email_normalization(self):
        """Тест нормализации email"""
        email = "Test@EXAMPLE.com"
        user = User.objects.create_user(
            username="emailuser", email=email, password="TestPass123"
        )

        assert user.email == "Test@example.com"
