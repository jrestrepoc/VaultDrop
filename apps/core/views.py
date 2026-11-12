from django.conf import settings
from django.core import signing
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from apps.core.domain import ExternalServiceError
from apps.core.hanzi import reto_pinyin


@ensure_csrf_cookie
def home_view(request):
    """Muestra la plataforma; las acciones que requieren cuenta se protegen en ella."""
    return render(request, 'core/home.html', {'catalog_url': settings.CATALOG_URL or reverse('cases:list')})


@require_http_methods(['GET', 'POST'])
def reto_pinyin_view(request):
    context = {}
    if request.method == 'POST':
        try:
            challenge = signing.loads(request.POST.get('reto', ''), salt='vaultdrop.pinyin', max_age=600)
            choice = int(request.POST.get('opcion', ''))
            if choice not in range(len(challenge['opciones'])):
                raise ValueError('opción inválida')
            context['acerto'] = choice == challenge['respuesta']
            context['pinyin_correcto'] = challenge['opciones'][challenge['respuesta']]
        except (signing.BadSignature, ValueError):
            context['reto_vencido'] = True
    else:
        try:
            challenge = reto_pinyin(settings.HANZI_CATALOGO_URL)
        except ExternalServiceError:
            context['no_disponible'] = True
        else:
            context['caracter'] = challenge['hanzi']
            context['opciones'] = challenge['opciones']
            context['reto'] = signing.dumps(challenge, salt='vaultdrop.pinyin')
    return render(request, 'core/reto_pinyin.html', context)
