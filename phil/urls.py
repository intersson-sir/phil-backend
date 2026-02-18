"""
URL configuration for phil project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('managers.urls')),
    path('api/', include('links.urls')),
    path('api/', include('stats.urls')),
    path('api/', include('activity.urls')),
]
