"""
Filters for the activity app.
"""
import django_filters
from .models import ActivityLog


class ActivityLogFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='timestamp', lookup_expr='date__gte')
    date_to = django_filters.DateFilter(field_name='timestamp', lookup_expr='date__lte')

    class Meta:
        model = ActivityLog
        fields = ['user', 'action', 'entity_type', 'date_from', 'date_to']
