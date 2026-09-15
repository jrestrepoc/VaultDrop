from django.urls import path
from . import views
from .api_views import AccountAPIView

app_name = 'core'

urlpatterns = [
    path('api/v1/account/', AccountAPIView.as_view(), name='account'),
    path('', views.home_view, name='home'),
]
