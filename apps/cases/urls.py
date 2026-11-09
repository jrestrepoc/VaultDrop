from django.urls import path

from apps.cases.views import CajaListAPIView, CajaDetailAPIView
from apps.openings.views import AbrirCajaAPIView, CajaGratisAPIView, RankingAPIView

app_name = 'cases'

urlpatterns = [
    path('', CajaListAPIView.as_view(), name='list'),
    path('gratis/abrir/', CajaGratisAPIView.as_view(), name='free'),
    path('ranking/', RankingAPIView.as_view(), name='ranking'),
    path('<int:caja_id>/', CajaDetailAPIView.as_view(), name='detail'),
    path('<int:caja_id>/abrir/', AbrirCajaAPIView.as_view(), name='open'),
]

