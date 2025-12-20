"""
Compliance API views.

Provides ViewSets for:
- GSTReturn (with validate/submit actions)
- DataAccessRequest (with complete/reject actions)
- AuditLog (read-only)
- Consent recording
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.compliance.models import GSTReturn, DataConsent, DataAccessRequest, AuditLog
from apps.compliance.serializers import (
    GSTReturnSerializer, GSTReturnListSerializer, GSTReturnCreateSerializer,
    GSTReturnValidateSerializer, DataConsentSerializer, DataConsentCreateSerializer,
    ConsentSummarySerializer, DataAccessRequestSerializer,
    DataAccessRequestCreateSerializer, DataAccessRequestActionSerializer,
    CustomerDataExportSerializer, AuditLogSerializer,
)
from apps.compliance.services import PDPAService, GSTReturnService


class GSTReturnViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GST F5 returns.
    
    Endpoints:
    - GET /gst-returns/ - List returns for company
    - POST /gst-returns/ - Prepare new return
    - GET /gst-returns/{id}/ - Get return details
    - POST /gst-returns/{id}/validate/ - Validate boxes
    - POST /gst-returns/{id}/submit/ - Submit to IRAS
    """
    
    queryset = GSTReturn.objects.all()
    serializer_class = GSTReturnSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's company."""
        return GSTReturn.objects.filter(
            company=self.request.user.company
        ).order_by('-year', '-quarter')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GSTReturnListSerializer
        if self.action == 'create':
            return GSTReturnCreateSerializer
        return GSTReturnSerializer
    
    def create(self, request, *args, **kwargs):
        """Prepare a new GST return."""
        serializer = GSTReturnCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            gst_return = GSTReturnService.prepare_return(
                company=request.user.company,
                quarter=serializer.validated_data['quarter'],
                year=serializer.validated_data['year'],
                prepared_by=request.user,
            )
            
            return Response(
                GSTReturnSerializer(gst_return).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate GST return boxes."""
        gst_return = self.get_object()
        
        is_valid, errors = GSTReturnService.validate_return(gst_return)
        
        return Response({
            'is_valid': is_valid,
            'errors': errors,
        })
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit GST return to IRAS."""
        gst_return = self.get_object()
        iras_reference = request.data.get('iras_reference', '')
        
        try:
            gst_return = GSTReturnService.submit_return(
                gst_return=gst_return,
                submitted_by=request.user,
                iras_reference=iras_reference,
            )
            
            return Response(GSTReturnSerializer(gst_return).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DataAccessRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PDPA data access requests.
    
    Endpoints:
    - GET /data-requests/ - List requests for company
    - POST /data-requests/ - Create new request
    - GET /data-requests/{id}/ - Get request details
    - POST /data-requests/{id}/complete/ - Complete request
    - POST /data-requests/{id}/reject/ - Reject request
    """
    
    queryset = DataAccessRequest.objects.all()
    serializer_class = DataAccessRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's company."""
        return DataAccessRequest.objects.filter(
            company=self.request.user.company
        ).order_by('-requested_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DataAccessRequestCreateSerializer
        return DataAccessRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a data access request."""
        serializer = DataAccessRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.commerce.models import Customer
        
        try:
            customer = Customer.objects.get(
                id=serializer.validated_data['customer_id'],
                company=request.user.company,
            )
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data_request = PDPAService.create_access_request(
            company=request.user.company,
            customer=customer,
            request_type=serializer.validated_data['request_type'],
        )
        
        return Response(
            DataAccessRequestSerializer(data_request).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a data access request."""
        data_request = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            PDPAService.process_access_request(
                request=data_request,
                action='complete',
                notes=notes,
                user=request.user,
            )
            return Response(DataAccessRequestSerializer(data_request).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a data access request."""
        data_request = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            PDPAService.process_access_request(
                request=data_request,
                action='reject',
                notes=reason,
                user=request.user,
            )
            return Response(DataAccessRequestSerializer(data_request).data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for audit logs.
    
    Endpoints:
    - GET /audit-logs/ - List audit logs for company
    - GET /audit-logs/{id}/ - Get audit log detail
    """
    
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user's company."""
        queryset = AuditLog.objects.filter(
            company=self.request.user.company
        ).order_by('-created_at')
        
        # Optional filters
        resource_type = self.request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        resource_id = self.request.query_params.get('resource_id')
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset[:500]  # Limit for performance


class ConsentView(APIView):
    """
    API for recording and viewing consent.
    
    Endpoints:
    - POST /consent/ - Record consent
    - GET /consent/status/?customer_id= - Get consent status
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Record consent for a customer."""
        serializer = DataConsentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.commerce.models import Customer
        
        try:
            customer = Customer.objects.get(
                id=customer_id,
                company=request.user.company,
            )
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get IP from request
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        consent = PDPAService.record_consent(
            customer=customer,
            consent_type=serializer.validated_data['consent_type'],
            is_granted=serializer.validated_data['is_granted'],
            source=serializer.validated_data.get('source', ''),
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        return Response(
            DataConsentSerializer(consent).data,
            status=status.HTTP_201_CREATED
        )
    
    def get(self, request):
        """Get consent status for a customer."""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {'error': 'customer_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.commerce.models import Customer
        
        try:
            customer = Customer.objects.get(
                id=customer_id,
                company=request.user.company,
            )
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summary = PDPAService.get_consent_summary(customer)
        
        return Response(summary)
