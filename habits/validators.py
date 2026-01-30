from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RelatedHabitRewardValidator:
    """Валидатор: нельзя одновременно выбирать связанную привычку и вознаграждение"""

    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")
        reward = attrs.get("reward")

        if related_habit and reward:
            raise ValidationError(
                _("Нельзя одновременно выбирать связанную привычку и вознаграждение.")
            )


class DurationValidator:
    """Валидатор: время выполнения не должно превышать 120 секунд"""

    def __call__(self, attrs):
        duration = attrs.get("duration")

        if duration and duration > 120:
            raise ValidationError(_("Время выполнения не должно превышать 120 секунд."))


class RelatedHabitIsPleasantValidator:
    """Валидатор: в связанные привычки могут попадать только приятные привычки"""

    def __call__(self, attrs):
        related_habit = attrs.get("related_habit")

        if related_habit and not related_habit.is_pleasant:
            raise ValidationError(
                _("В связанные привычки могут попадать только приятные привычки.")
            )


class PleasantHabitValidator:
    """Валидатор: у приятной привычки не может быть вознаграждения или связанной привычки"""

    def __call__(self, attrs):
        is_pleasant = attrs.get("is_pleasant")
        reward = attrs.get("reward")
        related_habit = attrs.get("related_habit")

        if is_pleasant and (reward or related_habit):
            raise ValidationError(
                _(
                    "У приятной привычки не может быть вознаграждения или связанной привычки."
                )
            )


class FrequencyValidator:
    """Валидатор: периодичность не может быть больше 7 дней"""

    def __call__(self, attrs):
        frequency = attrs.get("frequency")

        if frequency and frequency > 7:
            raise ValidationError(_("Периодичность не может быть больше 7 дней."))
