import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "update_user_info": {
        "task": "core.tasks.update_user_info",
        "schedule": 60*60*12, ## Once every 12 hours: 60*60*12
    },
    "sample_task": {
        "task": "core.tasks.sample_task",
        "schedule": 60,
    },
}
