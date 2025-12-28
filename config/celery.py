import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-habits-every-15-minutes": {
        "task": "habits.tasks.check_and_send_habit_notifications",
        "schedule": crontab(minute="*/15"),
    },
    "debug-task-every-hour": {
        "task": "habits.tasks.debug_task",
        "schedule": crontab(minute=0, hour="*"),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
