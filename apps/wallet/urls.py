from django.urls import path
from . import api_views

app_name = 'wallet'

urlpatterns = [
    # Endpoints REST (DRF v1)
    path('api/v1/wallet/me/', api_views.BilleteraAPIView.as_view(), name='api_billetera_me'),
]

