"""
Celery configuration for phil project.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phil.settings')

app = Celery('phil')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-urls-availability': {
        'task': 'links.tasks.check_urls_availability',
        'schedule': crontab(hour='*/24'),  # Every 24 hours by default
    },
    'activity-cleanup-old-logs': {
        'task': 'activity.tasks.cleanup_old_activity_logs',
        'schedule': crontab(hour=3, minute=0),  # Daily at 03:00
    },
}
