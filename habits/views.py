from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Habit
from .permissions import IsOwner
from .serializers import HabitCreateUpdateSerializer, HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для привычек пользователя"""

    permission_classes = [IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action in ["create", "update", "partial_update"]:
            return HabitCreateUpdateSerializer
        return HabitSerializer

    def get_queryset(self):
        """Возвращаем только привычки текущего пользователя"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически назначаем пользователя при создании"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def make_public(self, request, pk=None):
        """Сделать привычку публичной"""
        habit = self.get_object()
        habit.is_public = True
        habit.save()
        return Response({"status": "habit made public"})

    @action(detail=True, methods=["post"])
    def make_private(self, request, pk=None):
        """Сделать привычку приватной"""
        habit = self.get_object()
        habit.is_public = False
        habit.save()
        return Response({"status": "habit made private"})


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек (только для чтения)"""

    permission_classes = [IsAuthenticated]
    serializer_class = HabitSerializer

    def get_queryset(self):
        """Возвращаем только публичные привычки других пользователей"""
        return (
            Habit.objects.filter(is_public=True)
            .exclude(user=self.request.user)
            .select_related("user")
        )
