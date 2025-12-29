import os

import requests
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer


class UserLoginView(APIView):
    """Аутентификация пользователя (альтернатива JWT)"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                }
            )

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля пользователя"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TelegramConnectView(APIView):
    """Подключение Telegram аккаунта"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        telegram_chat_id = request.data.get("telegram_chat_id")

        if not telegram_chat_id:
            return Response(
                {"error": "Telegram chat ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.telegram_chat_id = telegram_chat_id
        request.user.save()

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token:
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": telegram_chat_id,
                    "text": "Ваш аккаунт успешно подключен к Habit Tracker!",
                    "parse_mode": "HTML",
                }
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"Failed to send welcome message: {e}")

        return Response(
            {
                "success": True,
                "message": "Telegram account connected successfully",
                "telegram_chat_id": telegram_chat_id,
            }
        )
