"""
Views for the links app.
"""
import logging
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import NegativeLink
from .serializers import (
    NegativeLinkSerializer,
    NegativeLinkListSerializer,
    BulkUpdateStatusSerializer,
    BulkAssignManagerSerializer
)
from .filters import NegativeLinkFilter

logger = logging.getLogger(__name__)


class NegativeLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Negative Links.
    
    Provides CRUD operations and bulk actions for negative links.
    
    list: GET /api/links/ - Get all links with optional filtering
    retrieve: GET /api/links/{id}/ - Get a specific link
    create: POST /api/links/ - Create a new link
    update: PUT /api/links/{id}/ - Full update of a link
    partial_update: PATCH /api/links/{id}/ - Partial update of a link
    destroy: DELETE /api/links/{id}/ - Delete a link
    
    Custom actions:
    - bulk_update_status: POST /api/links/bulk-update-status/
    - bulk_assign_manager: POST /api/links/bulk-assign-manager/
    """
    
    queryset = NegativeLink.objects.select_related('manager')
    serializer_class = NegativeLinkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = NegativeLinkFilter
    search_fields = ['url']
    ordering_fields = ['detected_at', 'updated_at', 'priority', 'status']
    ordering = ['-detected_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return NegativeLinkListSerializer
        return NegativeLinkSerializer

    def get_queryset(self):
        return NegativeLink.objects.select_related('manager')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new negative link.
        """
        logger.info(f"Creating new negative link with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info(f"Created negative link with ID: {serializer.data['id']}")
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Update a negative link.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        logger.info(f"Updating negative link {instance.id} with data: {request.data}")
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        logger.info(f"Updated negative link {instance.id}")
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a negative link.
        """
        instance = self.get_object()
        logger.info(f"Deleting negative link {instance.id}")
        self.perform_destroy(instance)
        logger.info(f"Deleted negative link")
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'], url_path='bulk-update-status')
    def bulk_update_status(self, request):
        """
        Bulk update status for multiple links.
        
        POST /api/links/bulk-update-status/
        Body: {
            "ids": ["uuid1", "uuid2", ...],
            "status": "removed"
        }
        """
        serializer = BulkUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data['ids']
        new_status = serializer.validated_data['status']
        
        logger.info(f"Bulk updating status to '{new_status}' for {len(ids)} links")
        
        # Get links to update
        links = NegativeLink.objects.filter(id__in=ids)
        
        if not links.exists():
            return Response(
                {'detail': 'No links found with provided IDs.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update status
        update_data = {'status': new_status}
        if new_status == 'removed':
            update_data['removed_at'] = timezone.now()
        
        updated_count = links.update(**update_data)
        
        logger.info(f"Updated {updated_count} links to status '{new_status}'")
        
        return Response({
            'detail': f'Successfully updated {updated_count} links.',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='bulk-assign-manager')
    def bulk_assign_manager(self, request):
        """
        Bulk assign manager to multiple links.
        
        POST /api/links/bulk-assign-manager/
        Body: {
            "ids": ["link-uuid1", "link-uuid2", ...],
            "manager_id": "manager-uuid"
        }
        """
        serializer = BulkAssignManagerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data['ids']
        manager_id = serializer.validated_data['manager_id']
        
        logger.info(f"Bulk assigning manager {manager_id} to {len(ids)} links")
        
        links = NegativeLink.objects.filter(id__in=ids)
        
        if not links.exists():
            return Response(
                {'detail': 'No links found with provided IDs.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_count = links.update(manager_id=manager_id)
        
        logger.info(f"Assigned manager {manager_id} to {updated_count} links")
        
        return Response({
            'detail': f'Successfully assigned manager to {updated_count} links.',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
