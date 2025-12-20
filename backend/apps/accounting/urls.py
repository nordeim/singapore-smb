"""
URL configuration for accounting app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounting.views import (
    AccountViewSet,
    JournalEntryViewSet,
    InvoiceViewSet,
    PaymentViewSet,
    GSTF5ViewSet,
    ReportViewSet,
)


app_name = 'accounting'

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'journals', JournalEntryViewSet, basename='journal')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'gst/f5', GSTF5ViewSet, basename='gst-f5')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
