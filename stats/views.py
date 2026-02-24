"""
Views for the stats app.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from links.models import NegativeLink

logger = logging.getLogger(__name__)

# period query param: 1d, 7d, 30d (default 30d)
PERIOD_DAYS = {'1d': 1, '7d': 7, '30d': 30}
DEFAULT_PERIOD = '30d'


def parse_period(period_value):
    """Return (period_key, days). If invalid, return default."""
    if not period_value or period_value not in PERIOD_DAYS:
        return DEFAULT_PERIOD, PERIOD_DAYS[DEFAULT_PERIOD]
    return period_value, PERIOD_DAYS[period_value]


def get_period_range(period_key, days):
    """Return (start_datetime, end_datetime) for the given period.

    All periods use a rolling window: now minus N days/hours.
    '1d' = last 24 hours, '7d' = last 7 days, '30d' = last 30 days.
    """
    now = timezone.now()
    start = now - timedelta(days=days)
    return start, now


def _touched_qs(start, end):
    """Links that were created OR had their status/data changed within [start, end]."""
    return NegativeLink.objects.filter(
        Q(detected_at__gte=start, detected_at__lte=end) |
        Q(updated_at__gte=start, updated_at__lte=end)
    )


def build_dashboard_stats(period_key, days):
    """Build dashboard stats for the given period. Uses ORM aggregation where possible."""
    start, end = get_period_range(period_key, days)

    # Links active in this period = created OR updated within the window
    base_qs = _touched_qs(start, end)

    # Total and by status (aggregation)
    total = base_qs.count()
    status_breakdown = dict(
        base_qs.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )
    active = status_breakdown.get('active', 0)
    removed = status_breakdown.get('removed', 0)
    in_work = status_breakdown.get('in_work', 0)
    pending = status_breakdown.get('pending', 0)
    cancelled = status_breakdown.get('cancelled', 0)

    # By platform (aggregation)
    # For 'account': match either platform=account OR type=account so that
    # links tagged as account-type (on any social platform) appear in this bucket.
    platforms_data = []
    for platform_code, platform_name in NegativeLink.PLATFORM_CHOICES:
        if platform_code == 'account':
            platform_qs = base_qs.filter(Q(platform='account') | Q(type='account'))
        else:
            platform_qs = base_qs.filter(platform=platform_code)
        platform_stats = {
            'platform': platform_code,
            'total': platform_qs.count(),
            'active': platform_qs.filter(status='active').count(),
            'removed': platform_qs.filter(status='removed').count(),
            'in_work': platform_qs.filter(status='in_work').count(),
            'pending': platform_qs.filter(status='pending').count(),
            'cancelled': platform_qs.filter(status='cancelled').count(),
        }
        platforms_data.append(platform_stats)

    # By priority (aggregation)
    priority_breakdown = []
    for priority_code, _ in NegativeLink.PRIORITY_CHOICES:
        cnt = base_qs.filter(priority=priority_code).count()
        priority_breakdown.append({'priority': priority_code, 'count': cnt})

    # New links = only those created (detected_at) within the period
    new_in_period = NegativeLink.objects.filter(
        detected_at__gte=start,
        detected_at__lte=end,
    ).count()

    # Removed within period (removed_at in range)
    removed_in_period = NegativeLink.objects.filter(
        removed_at__gte=start,
        removed_at__lte=end,
    ).count()

    # Activity chart by day (within period)
    activity_chart = []
    current_date = start.date()
    end_date = end.date()
    while current_date <= end_date:
        # Count links touched on this calendar day (created or updated)
        active_count = NegativeLink.objects.filter(
            Q(detected_at__date=current_date) | Q(updated_at__date=current_date),
            status='active',
        ).count()
        removed_count = NegativeLink.objects.filter(removed_at__date=current_date).count()
        activity_chart.append({
            'date': current_date.isoformat(),
            'active': active_count,
            'removed': removed_count,
        })
        current_date += timedelta(days=1)

    return {
        'period': period_key,
        'total': total,
        'active': active,
        'removed': removed,
        'in_work': in_work,
        'pending': pending,
        'cancelled': cancelled,
        'new_in_period': new_in_period,
        'removed_in_period': removed_in_period,
        'by_status': {
            'active': active,
            'removed': removed,
            'in_work': in_work,
            'pending': pending,
            'cancelled': cancelled,
        },
        'platforms': platforms_data,
        'by_priority': priority_breakdown,
        'activity_chart': activity_chart,
    }


class DashboardStatsView(APIView):
    """
    API view for dashboard statistics.

    GET /api/stats/dashboard/?period=1d|7d|30d

    Query params:
      period: 1d, 7d, or 30d (default 30d). Stats are computed for links with detected_at in that range.

    Returns:
      period, total, active, removed, in_work, pending, by_status, platforms, by_priority, activity_chart.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period_key, days = parse_period(request.query_params.get('period'))
        cache_key = f'dashboard_stats_v2_{period_key}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("Returning cached dashboard stats for period=%s", period_key)
                return Response(cached_data)
        except Exception as e:
            logger.warning("Cache get failed for dashboard stats, computing: %s", e)

        logger.info("Calculating dashboard stats for period=%s", period_key)
        response_data = build_dashboard_stats(period_key, days)
        try:
            cache.set(cache_key, response_data, 300)
        except Exception as e:
            logger.warning("Cache set failed for dashboard stats: %s", e)
        logger.info("Dashboard stats calculated successfully")
        return Response(response_data)


def build_platform_stats(platform, period_key, days):
    """Build platform-specific stats for the given period."""
    start, end = get_period_range(period_key, days)
    touched = _touched_qs(start, end)
    if platform == 'account':
        base_qs = touched.filter(Q(platform='account') | Q(type='account'))
    else:
        base_qs = touched.filter(platform=platform)
    by_priority = [
        {'priority': code, 'count': base_qs.filter(priority=code).count()}
        for code, _ in NegativeLink.PRIORITY_CHOICES
    ]
    return {
        'period': period_key,
        'platform': platform,
        'total': base_qs.count(),
        'active': base_qs.filter(status='active').count(),
        'removed': base_qs.filter(status='removed').count(),
        'in_work': base_qs.filter(status='in_work').count(),
        'pending': base_qs.filter(status='pending').count(),
        'cancelled': base_qs.filter(status='cancelled').count(),
        'by_priority': by_priority,
    }


class PlatformStatsView(APIView):
    """
    API view for platform-specific statistics.

    GET /api/stats/platform/{platform}/?period=1d|7d|30d

    Query params:
      period: 1d, 7d, or 30d (default 30d).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, platform):
        valid_platforms = [code for code, _ in NegativeLink.PLATFORM_CHOICES]
        if platform not in valid_platforms:
            return Response(
                {'detail': f'Invalid platform. Must be one of: {", ".join(valid_platforms)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        period_key, days = parse_period(request.query_params.get('period'))
        cache_key = f'platform_stats_v2_{platform}_{period_key}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("Returning cached stats for platform=%s period=%s", platform, period_key)
                return Response(cached_data)
        except Exception as e:
            logger.warning("Cache get failed for platform stats, computing: %s", e)

        logger.info("Calculating stats for platform=%s period=%s", platform, period_key)
        platform_stats = build_platform_stats(platform, period_key, days)
        try:
            cache.set(cache_key, platform_stats, 300)
        except Exception as e:
            logger.warning("Cache set failed for platform stats: %s", e)
        return Response(platform_stats)
