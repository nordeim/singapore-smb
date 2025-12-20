"""InvoiceNow URL routing."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.invoicenow.views import (
    PEPPOLInvoiceViewSet,
    PrepareInvoiceView,
    SubmissionStatusView,
    FullWorkflowView,
)


router = DefaultRouter()
router.register('peppol-invoices', PEPPOLInvoiceViewSet, basename='peppol-invoices')

app_name = 'invoicenow'

urlpatterns = [
    path('', include(router.urls)),
    path('prepare/', PrepareInvoiceView.as_view(), name='prepare-invoice'),
    path('status/<uuid:invoice_id>/', SubmissionStatusView.as_view(), name='submission-status'),
    path('submit/', FullWorkflowView.as_view(), name='full-workflow'),
]
