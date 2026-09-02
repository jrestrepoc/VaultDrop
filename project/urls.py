from django.urls import path, include

urlpatterns = [
    path('', include('apps.core.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.wallet.urls')),
    path('api/v1/cajas/', include('apps.cases.urls')),
]
