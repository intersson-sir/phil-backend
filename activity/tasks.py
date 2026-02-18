"""
Celery tasks for the activity app.
"""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_activity_logs(days=90):
    """
    Delete activity logs older than `days` days.
    Call periodically (e.g. daily) via Celery Beat.
    """
    from .models import ActivityLog
    threshold = timezone.now() - timedelta(days=days)
    deleted, _ = ActivityLog.objects.filter(timestamp__lt=threshold).delete()
    logger.info("Activity log cleanup: deleted %s records older than %s days", deleted, days)
    return {'deleted': deleted}
