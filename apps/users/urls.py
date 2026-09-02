from django.urls import path
from . import views, api_views

app_name = 'users'

urlpatterns = [
    # Vistas Web (HTML)
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Endpoints REST (DRF v1)
    path('api/v1/auth/register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('api/v1/auth/login/', api_views.LoginAPIView.as_view(), name='api_login'),
]

