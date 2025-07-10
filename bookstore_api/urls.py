"""
URL configuration for bookstore_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'success': True,
        'message': 'Bookstore API is running successfully',
        'version': '1.0.0',
        'status': 'healthy'
    })


urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check
    path('', health_check, name='health-check'),
    path('health/', health_check, name='health-check-alt'),

    # API endpoints
    path('', include('books.urls')),    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Alternative paths for v1 API docs
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-v1'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-v1'),
]
