"""
Compliance URL routing.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.compliance.views import (
    GSTReturnViewSet,
    DataAccessRequestViewSet,
    AuditLogViewSet,
    ConsentView,
)


router = DefaultRouter()
router.register('gst-returns', GSTReturnViewSet, basename='gst-returns')
router.register('data-requests', DataAccessRequestViewSet, basename='data-requests')
router.register('audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    path('', include(router.urls)),
    path('consent/', ConsentView.as_view(), name='consent'),
]
