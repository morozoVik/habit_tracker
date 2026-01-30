from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "time", "place", "is_pleasant", "is_public")
    list_filter = ("is_pleasant", "is_public", "frequency")
    search_fields = ("action", "place", "user__username")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основная информация", {"fields": ("user", "action", "place", "time")}),
        (
            "Характеристики привычки",
            {
                "fields": (
                    "is_pleasant",
                    "related_habit",
                    "reward",
                    "frequency",
                    "duration",
                )
            },
        ),
        ("Дополнительно", {"fields": ("is_public", "created_at", "updated_at")}),
    )
