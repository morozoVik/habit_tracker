from unittest.mock import MagicMock, patch

import requests

from habits.tasks import send_telegram_notification


def test_send_telegram_notification_success():
    """Тест успешной отправки Telegram уведомления (только логика)"""
    with patch("habits.tasks.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = send_telegram_notification("123456789", "Тестовое сообщение")

        assert result == {"ok": True, "result": {"message_id": 1}}
        mock_post.assert_called_once()


def test_send_telegram_notification_failure():
    """Тест неудачной отправки Telegram уведомления (только логика)"""
    with patch("habits.tasks.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        result = send_telegram_notification("123456789", "Тестовое сообщение")

        assert result is None
