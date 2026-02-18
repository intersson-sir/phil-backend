"""
Views for the activity app.
"""
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import ActivityLog
from .serializers import ActivityLogSerializer
from .filters import ActivityLogFilter


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related('user').all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ActivityLogFilter
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'], url_path='link/(?P<link_id>[^/.]+)')
    def by_link(self, request, link_id=None):
        """GET /api/activity/link/:link_id/ — logs for a specific link."""
        qs = self.get_queryset().filter(entity_type='link', entity_id=link_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
