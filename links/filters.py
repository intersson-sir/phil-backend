"""
Filters for the links app.
"""
import django_filters
from django.db.models import Q
from .models import NegativeLink


class NegativeLinkFilter(django_filters.FilterSet):
    """
    Filter class for NegativeLink model.
    Provides filtering capabilities for the API endpoints.
    """
    
    platform = django_filters.CharFilter(method='filter_platform')

    def filter_platform(self, queryset, name, value):
        """Filter by platform. For 'account', also include links with type=account."""
        if value not in [code for code, _ in NegativeLink.PLATFORM_CHOICES]:
            return queryset.none()
        if value == 'account':
            return queryset.filter(Q(platform='account') | Q(type='account'))
        return queryset.filter(platform=value)
    
    status = django_filters.ChoiceFilter(
        choices=NegativeLink.STATUS_CHOICES,
        field_name='status',
        lookup_expr='exact'
    )
    
    priority = django_filters.ChoiceFilter(
        choices=NegativeLink.PRIORITY_CHOICES,
        field_name='priority',
        lookup_expr='exact'
    )
    
    manager_id = django_filters.UUIDFilter(
        field_name='manager_id',
        lookup_expr='exact',
    )
    
    dateFrom = django_filters.DateTimeFilter(
        field_name='detected_at',
        lookup_expr='gte',
        input_formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']
    )
    
    dateTo = django_filters.DateTimeFilter(
        field_name='detected_at',
        lookup_expr='lte',
        input_formats=['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search in URL'
    )
    
    class Meta:
        model = NegativeLink
        fields = ['platform', 'status', 'priority', 'manager_id', 'dateFrom', 'dateTo', 'search']
    
    def filter_search(self, queryset, name, value):
        """
        Custom search filter for URL field.
        Performs case-insensitive search.
        """
        if value:
            return queryset.filter(url__icontains=value)
        return queryset
