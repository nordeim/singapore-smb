"""
URL configuration for Singapore SMB E-commerce Platform.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def health_check(request):
    """Health check endpoint for load balancers and monitoring."""
    return JsonResponse({
        'status': 'ok',
        'version': settings.PLATFORM_VERSION,
    })


urlpatterns = [
    # Health check (no auth required)
    path('health/', health_check, name='health-check'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('accounts/', include('apps.accounts.urls', namespace='accounts')),
        path('commerce/', include('apps.commerce.urls', namespace='commerce')),
        path('inventory/', include('apps.inventory.urls', namespace='inventory')),
        path('accounting/', include('apps.accounting.urls', namespace='accounting')),
        # Phase 5 apps:
        path('compliance/', include('apps.compliance.urls', namespace='compliance')),
        path('payments/', include('apps.payments.urls', namespace='payments')),
        path('integrations/', include('apps.integrations.urls', namespace='integrations')),
        path('invoicenow/', include('apps.invoicenow.urls', namespace='invoicenow')),
    ])),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
