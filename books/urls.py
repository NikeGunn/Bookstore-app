from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, health_check

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/health/', health_check, name='health_check'),
]
