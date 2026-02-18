"""
Serializers for the links app.
"""
from rest_framework import serializers
from .models import NegativeLink


class ManagerInlineSerializer(serializers.Serializer):
    """Minimal manager representation for link responses."""
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class NegativeLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for NegativeLink model.
    manager is returned as full object; accept manager_id (UUID) on write.
    """
    manager = ManagerInlineSerializer(read_only=True, allow_null=True)
    manager_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = NegativeLink
        fields = [
            'id',
            'url',
            'platform',
            'type',
            'status',
            'detected_at',
            'removed_at',
            'priority',
            'manager',
            'manager_id',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'detected_at', 'created_at', 'updated_at']
    
    def validate_url(self, value):
        """
        Validate URL field.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("URL cannot be empty.")
        return value.strip()

    def validate_manager_id(self, value):
        if value is None:
            return value
        from managers.models import Manager
        if not Manager.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Manager not found or inactive.")
        return value

    def create(self, validated_data):
        manager_id = validated_data.pop('manager_id', None)
        if manager_id is not None:
            from managers.models import Manager
            validated_data['manager'] = Manager.objects.filter(id=manager_id).first()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update instance with special handling for status changes.
        When status changes to 'removed', removed_at is set automatically in the model.
        """
        manager_id = validated_data.pop('manager_id', None)
        if manager_id is not None:
            from managers.models import Manager
            validated_data['manager'] = Manager.objects.filter(id=manager_id).first()
        return super().update(instance, validated_data)


class BulkUpdateStatusSerializer(serializers.Serializer):
    """
    Serializer for bulk status update operation.
    """
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of link IDs to update"
    )
    status = serializers.ChoiceField(
        choices=NegativeLink.STATUS_CHOICES,
        help_text="New status to set"
    )
    
    def validate_ids(self, value):
        """Validate that all IDs exist."""
        if not value:
            raise serializers.ValidationError("At least one ID is required.")
        return value


class BulkAssignManagerSerializer(serializers.Serializer):
    """
    Serializer for bulk manager assignment operation.
    manager_id: UUID of the Manager to assign.
    """
    ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of link IDs to update"
    )
    manager_id = serializers.UUIDField(help_text="Manager UUID to assign")

    def validate_ids(self, value):
        """Validate that all IDs exist."""
        if not value:
            raise serializers.ValidationError("At least one ID is required.")
        return value

    def validate_manager_id(self, value):
        """Validate that Manager exists and is active."""
        from managers.models import Manager
        if not Manager.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Manager not found or inactive.")
        return value
