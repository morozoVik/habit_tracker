from rest_framework import serializers

from .models import Habit
from .validators import (DurationValidator, FrequencyValidator,
                         PleasantHabitValidator,
                         RelatedHabitIsPleasantValidator,
                         RelatedHabitRewardValidator)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения привычек"""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class HabitCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления привычек с валидацией"""

    class Meta:
        model = Habit
        fields = [
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
        ]

    def validate(self, attrs):
        """Применяем кастомные валидаторы"""
        validators = [
            DurationValidator(),
            FrequencyValidator(),
            PleasantHabitValidator(),
            RelatedHabitIsPleasantValidator(),
            RelatedHabitRewardValidator(),
        ]

        for validator in validators:
            validator(attrs)

        return attrs

    def create(self, validated_data):
        """Автоматически добавляем текущего пользователя"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновление привычки"""
        validated_data["user"] = self.context["request"].user
        return super().update(instance, validated_data)
