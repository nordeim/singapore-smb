"""
URL configuration for commerce API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.commerce.views import (
    CategoryViewSet,
    ProductViewSet,
    CustomerViewSet,
    CartViewSet,
    OrderViewSet,
)


app_name = 'commerce'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]
