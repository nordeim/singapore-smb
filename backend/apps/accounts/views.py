"""
DRF Views for accounts app.

Provides ViewSets and APIViews for:
- Company management
- User management
- Role management
- Authentication (login, logout, token refresh)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.permissions import IsCompanyMember, IsAdminUser, HasAnyRole
from .models import Company, User, Role, UserRole
from .serializers import (
    CompanySerializer, CompanyCreateSerializer,
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer,
    RoleSerializer, UserRoleSerializer,
    LoginSerializer, TokenSerializer, TokenRefreshSerializer,
)
from .services import AuthService, UserService, CompanyService


# =============================================================================
# COMPANY VIEWSET
# =============================================================================

class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Company CRUD operations.
    
    list: List companies (admin only)
    create: Create new company with owner
    retrieve: Get company details
    update: Update company
    """
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return companies based on user access."""
        user = self.request.user
        
        if user.is_superuser:
            return Company.objects.all()
        
        # Regular users can only see their own company
        if user.company:
            return Company.objects.filter(id=user.company.id)
        
        return Company.objects.none()
    
    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer
    
    def get_permissions(self):
        """Allow unauthenticated company creation (registration)."""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users in the company."""
        company = self.get_object()
        users = company.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Get all roles in the company."""
        company = self.get_object()
        roles = company.roles.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


# =============================================================================
# USER VIEWSET
# =============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    
    Filtered by company for multi-tenant isolation.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Return users in the current company."""
        user = self.request.user
        
        if user.is_superuser:
            return User.objects.all()
        
        if user.company:
            return User.objects.filter(company=user.company, is_active=True)
        
        return User.objects.none()
    
    def get_serializer_class(self):
        """Use different serializers based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_serializer_context(self):
        """Add company to serializer context."""
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['company'] = self.request.user.company
        return context
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user's profile."""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        UserService.change_password(
            request.user,
            serializer.validated_data['new_password']
        )
        
        return Response({'message': 'Password changed successfully.'})
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assign a role to a user."""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        try:
            role = Role.objects.get(id=role_id, company=request.user.company)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        UserService.assign_role(user, role, request.user)
        return Response({'message': f'Role {role.name} assigned.'})
    
    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Remove a role from a user."""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        try:
            role = Role.objects.get(id=role_id, company=request.user.company)
        except Role.DoesNotExist:
            return Response(
                {'error': 'Role not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        UserService.remove_role(user, role)
        return Response({'message': f'Role {role.name} removed.'})


# =============================================================================
# ROLE VIEWSET
# =============================================================================

class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Role CRUD operations.
    
    Only admins can manage roles.
    """
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    
    def get_queryset(self):
        """Return roles for the current company."""
        user = self.request.user
        
        if user.is_superuser:
            return Role.objects.all()
        
        if user.company:
            return Role.objects.filter(company=user.company)
        
        return Role.objects.none()
    
    def perform_create(self, serializer):
        """Set company when creating role."""
        serializer.save(company=self.request.user.company)
    
    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of system roles."""
        role = self.get_object()
        if role.is_system:
            return Response(
                {'error': 'Cannot delete system roles.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/v1/accounts/auth/login/
    
    Request Body:
        email: User's email
        password: User's password
    
    Response:
        access: JWT access token
        refresh: JWT refresh token
        user: User details
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Get client IP
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Record login and generate tokens
        user.record_successful_login(ip_address)
        tokens = AuthService.generate_tokens(user)
        
        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/v1/accounts/auth/logout/
    
    Request Body:
        refresh: JWT refresh token to blacklist
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            AuthService.blacklist_token(refresh_token)
        
        return Response({'message': 'Logged out successfully.'})


class TokenRefreshView(APIView):
    """
    Token refresh endpoint.
    
    POST /api/v1/accounts/auth/refresh/
    
    Request Body:
        refresh: JWT refresh token
    
    Response:
        access: New JWT access token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tokens = AuthService.refresh_token(refresh_token)
            return Response(tokens)
        except (InvalidToken, TokenError) as e:
            return Response(
                {'error': 'Invalid or expired token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class CurrentUserView(APIView):
    """
    Get current authenticated user.
    
    GET /api/v1/accounts/auth/me/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)
