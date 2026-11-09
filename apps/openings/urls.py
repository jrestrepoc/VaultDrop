from django.urls import path
from apps.openings.views import (
    AccionMasivaAPIView,
    HistorialAPIView,
    InventoryAPIView,
    InventoryActionAPIView,
    MejorarAPIView,
    SendInventoryAPIView,
)

app_name = 'inventory'
urlpatterns = [
    path('', InventoryAPIView.as_view(), name='list'),
    path('masivo/', AccionMasivaAPIView.as_view(), name='bulk'),
    path('mejorar/', MejorarAPIView.as_view(), name='upgrade'),
    path('historial/', HistorialAPIView.as_view(), name='history'),
    path('<int:item_id>/sell/', InventoryActionAPIView.as_view(), name='sell'),
    path('<int:item_id>/send/', SendInventoryAPIView.as_view(), name='send'),
]
