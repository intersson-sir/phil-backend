"""
Serializers for the activity app.
"""
from rest_framework import serializers
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username if obj.user_id else None

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'user',
            'username',
            'action',
            'entity_type',
            'entity_id',
            'old_value',
            'new_value',
            'timestamp',
            'ip_address',
        ]
        read_only_fields = fields
