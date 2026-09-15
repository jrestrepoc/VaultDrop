from django.urls import path
from apps.openings.views import InventoryAPIView, InventoryActionAPIView, SendInventoryAPIView

app_name = 'inventory'
urlpatterns = [
    path('', InventoryAPIView.as_view(), name='list'),
    path('<int:item_id>/sell/', InventoryActionAPIView.as_view(), name='sell'),
    path('<int:item_id>/send/', SendInventoryAPIView.as_view(), name='send'),
]
