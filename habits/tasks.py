import os

import requests
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Habit

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


@shared_task
def send_telegram_notification(chat_id, message):
    """Отправка уведомления в Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        print("Telegram bot token not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Notification sent to {chat_id}: {message}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification to {chat_id}: {e}")
        return None


@shared_task
def check_and_send_habit_notifications():
    """Проверка привычек и отправка уведомлений"""
    print("=" * 60)
    print(" НАЧИНАЕМ ПРОВЕРКУ ПРИВЫЧЕК - НОВАЯ ВЕРСИЯ")
    print("=" * 60)

    User = get_user_model()
    now = timezone.now()
    current_time = now.time()

    print(f" Дата проверки: {now.date()}")
    print(f" Текущее время: {current_time}")

    habits = Habit.objects.all().select_related("user")
    total_habits = habits.count()

    print(f" Всего привычек в базе: {total_habits}")

    if total_habits == 0:
        print(" Нет привычек для проверки")
        return "No habits found"

    notifications_sent = 0

    for i, habit in enumerate(habits, 1):
        print(f"\n[{i}/{total_habits}] Проверяем: '{habit.action}'")
        print(f" Пользователь: {habit.user.username}")
        print(f" Telegram ID: {habit.user.telegram_chat_id}")
        print(f" Время привычки: {habit.time}")

        if not habit.user.telegram_chat_id:
            print(f"️ Пропускаем: нет Telegram chat_id")
            continue

        print(f" ОТПРАВЛЯЕМ ТЕСТОВОЕ УВЕДОМЛЕНИЕ")

        message = (
            f" <b>ТЕСТ СИСТЕМЫ</b>\n\n"
            f" Привычка: {habit.action}\n"
            f" Пользователь: {habit.user.username}\n"
            f" Время привычки: {habit.time}\n"
            f" Место: {habit.place}\n"
            f" Длительность: {habit.duration} сек\n"
            f" Дата проверки: {now.strftime('%d.%m.%Y %H:%M')}"
        )

        result = send_telegram_notification.delay(habit.user.telegram_chat_id, message)

        print(f" Задача отправки: {result.id}")
        notifications_sent += 1

    print(f" \n" + "=" * 60)
    print(f" ИТОГИ ПРОВЕРКИ:")
    print(f" Проверено привычек: {total_habits}")
    print(f" Отправлено уведомлений: {notifications_sent}")
    print("=" * 60)

    return f"Проверено {total_habits} привычек, отправлено {notifications_sent} уведомлений"


@shared_task
def debug_task():
    """Отладочная задача для проверки Celery"""
    print("Celery is working!")
    return "Celery task executed successfully"
