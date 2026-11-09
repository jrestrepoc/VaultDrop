from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('', include('apps.core.urls')),
    path('api/v1/inventory/', include('apps.openings.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.wallet.urls')),
    path('api/v1/cajas/', include('apps.cases.urls')),
]
