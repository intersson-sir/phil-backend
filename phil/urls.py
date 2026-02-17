"""
URL configuration for phil project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    """Root API endpoint with information about available endpoints."""
    return JsonResponse({
        'message': 'Phil CRM API',
        'version': '1.0',
        'endpoints': {
            'api': '/api/',
            'links': '/api/links/',
            'stats_dashboard': '/api/stats/dashboard/',
            'admin': '/admin/',
        },
        'documentation': 'https://github.com/intersson-sir/phil-backend'
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('links.urls')),
    path('api/', include('stats.urls')),
]
