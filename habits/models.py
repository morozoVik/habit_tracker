from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Habit(models.Model):
    """Модель привычки"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
    )
    frequency = models.PositiveIntegerField(
        default=1, verbose_name="Периодичность (в днях)", help_text="Дни (максимум 7)"
    )
    reward = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Вознаграждение"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (в секундах)",
        help_text="Секунды (максимум 120)",
    )
    is_public = models.BooleanField(default=False, verbose_name="Признак публичности")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} в {self.time} ({self.user.username})"

    def clean(self):
        """Валидация данных модели"""
        from .validators import (
            DurationValidator,
            FrequencyValidator,
            PleasantHabitValidator,
            RelatedHabitIsPleasantValidator,
            RelatedHabitRewardValidator,
        )

        attrs = {
            "duration": self.duration,
            "frequency": self.frequency,
            "is_pleasant": self.is_pleasant,
            "reward": self.reward,
            "related_habit": self.related_habit,
        }

        validators = [
            DurationValidator(),
            FrequencyValidator(),
            PleasantHabitValidator(),
            RelatedHabitIsPleasantValidator(),
            RelatedHabitRewardValidator(),
        ]

        for validator in validators:
            validator(attrs)

        if self.related_habit and self.related_habit.pk == self.pk:
            raise ValidationError(
                {"related_habit": _("Привычка не может быть связана сама с собой.")}
            )

    def save(self, *args, **kwargs):
        """Переопределяем save для вызова clean()"""
        self.full_clean()
        super().save(*args, **kwargs)
