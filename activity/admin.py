from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'entity_type', 'entity_id', 'user', 'timestamp', 'ip_address']
    list_filter = ['action', 'entity_type']
    search_fields = ['entity_id', 'user__username']
    readonly_fields = ['id', 'user', 'action', 'entity_type', 'entity_id', 'old_value', 'new_value', 'timestamp', 'ip_address']
    date_hierarchy = 'timestamp'
