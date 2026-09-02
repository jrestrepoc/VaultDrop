from django.shortcuts import render


def home_view(request):
    """Muestra la plataforma; las acciones que requieren cuenta se protegen en ella."""
    return render(request, 'core/home.html')
