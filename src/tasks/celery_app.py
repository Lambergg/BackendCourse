from celery import Celery

from src.config import settings

celery_instance = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "src.tasks.tasks",
    ],
)

celery_instance.conf.beat_schedule = {
    "refresh-db": {
        "task": "booking_today_checkin",
        "schedule": 60,
    }
}

"""
from celery.schedules import crontab

celery_instance.conf.beat_schedule = {
    "refresh-db": {
        "task": "booking_today_checkin",
        "schedule": crontab(minute=0, hour=8),  # каждый день в 8:00
    }
}
"""