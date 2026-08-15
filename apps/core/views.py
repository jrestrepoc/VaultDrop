from django.shortcuts import render


def home_view(request):
    """Home pública/autenticada: el contenido (bienvenida vs. saludo) se
    resuelve en el template a partir de `user.is_authenticated`."""
    return render(request, 'core/home.html')
