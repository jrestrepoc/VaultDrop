from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def home_view(request):
    """Muestra la plataforma; las acciones que requieren cuenta se protegen en ella."""
    return render(request, 'core/home.html')
