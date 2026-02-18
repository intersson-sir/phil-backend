"""
Django signals for automatic activity logging.
Logs only non-sensitive fields (e.g. status, manager_id); no url/notes.
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from .context import get_current_request
from .models import ActivityLog
from links.models import NegativeLink

logger = logging.getLogger(__name__)

# Thread-local cache of previous instance state (set in pre_save, read in post_save)
_prev_link_state = {}


def _safe_link_snapshot(link):
    """Minimal snapshot for log (no sensitive data)."""
    if link is None:
        return None
    return {
        'status': link.status,
        'manager_id': str(link.manager_id) if link.manager_id else None,
    }


def _log_activity(action, entity_type, entity_id, old_value=None, new_value=None):
    request = get_current_request()
    user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    ip = None
    if request and getattr(request, 'META', None):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            ip = xff.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip,
        )
    except Exception as e:
        logger.warning("Activity log create failed: %s", e)


@receiver(pre_save, sender=NegativeLink)
def negative_link_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = NegativeLink.objects.get(pk=instance.pk)
            _prev_link_state[id(instance)] = _safe_link_snapshot(old)
        except NegativeLink.DoesNotExist:
            _prev_link_state[id(instance)] = None
    else:
        _prev_link_state[id(instance)] = None


@receiver(post_save, sender=NegativeLink)
def negative_link_post_save(sender, instance, created, **kwargs):
    entity_id = instance.pk
    new_snap = _safe_link_snapshot(instance)
    try:
        if created:
            _log_activity('created', 'link', entity_id, old_value=None, new_value=new_snap)
            return
        old_snap = _prev_link_state.pop(id(instance), None)
        if old_snap is None:
            _log_activity('updated', 'link', entity_id, old_value=None, new_value=new_snap)
            return
        if old_snap.get('status') != new_snap.get('status'):
            _log_activity(
                'status_changed', 'link', entity_id,
                old_value={'status': old_snap.get('status')},
                new_value={'status': new_snap.get('status')},
            )
        elif old_snap.get('manager_id') != new_snap.get('manager_id'):
            _log_activity(
                'assigned', 'link', entity_id,
                old_value={'manager_id': old_snap.get('manager_id')},
                new_value={'manager_id': new_snap.get('manager_id')},
            )
        else:
            _log_activity('updated', 'link', entity_id, old_value=old_snap, new_value=new_snap)
    finally:
        _prev_link_state.pop(id(instance), None)


@receiver(post_delete, sender=NegativeLink)
def negative_link_post_delete(sender, instance, **kwargs):
    _log_activity(
        'deleted', 'link', instance.pk,
        old_value=_safe_link_snapshot(instance),
        new_value=None,
    )
