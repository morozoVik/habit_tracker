from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitListView

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("", include(router.urls)),
    path("public-habits/", PublicHabitListView.as_view(), name="public-habits"),
]
