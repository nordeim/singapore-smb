"""
URL routing for accounts app.

API Endpoints:
- /api/v1/accounts/companies/ - Company CRUD
- /api/v1/accounts/users/ - User CRUD
- /api/v1/accounts/roles/ - Role CRUD
- /api/v1/accounts/auth/login/ - Login
- /api/v1/accounts/auth/logout/ - Logout
- /api/v1/accounts/auth/refresh/ - Token refresh
- /api/v1/accounts/auth/me/ - Current user
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CompanyViewSet, UserViewSet, RoleViewSet,
    LoginView, LogoutView, TokenRefreshView, CurrentUserView,
)

app_name = 'accounts'

# Router for ViewSets
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')

# URL patterns
urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
]
