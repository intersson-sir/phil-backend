"""
Views for the managers app.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Manager
from .serializers import ManagerSerializer


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        return Manager.objects.all()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
