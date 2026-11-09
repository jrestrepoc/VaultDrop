from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def home_view(request):
    """Muestra la plataforma; las acciones que requieren cuenta se protegen en ella."""
    return render(request, 'core/home.html', {'catalog_url': settings.CATALOG_URL or reverse('cases:list')})
