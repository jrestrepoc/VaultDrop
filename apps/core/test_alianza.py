import json
from io import BytesIO
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.cases.models import Caja, CajaItem, Item
from apps.openings.models import AperturaCaja, ItemInventario
from apps.wallet.models import Transaccion


class IntegracionAliadaTests(TestCase):
    def test_caja_demo_publica_y_sin_mutaciones(self):
        caja = Caja.objects.create(nombre='Caja de prueba', precio=20)
        item = Item.objects.create(nombre='AK-47 | Redline', rareza='EPICO', valor_estimado=10,
                                   imagen_url='/static/core/images/item-placeholder.svg')
        CajaItem.objects.create(caja=caja, item=item, probabilidad=100)
        url = reverse('cases:demo-open')
        response = self.client.post(url)
        self.assertEqual(response.json(), {
            'item': item.nombre,
            'rareza': 'EPICO',
            'imagen': 'http://testserver/static/core/images/item-placeholder.svg',
        })
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertFalse(AperturaCaja.objects.exists())
        self.assertFalse(ItemInventario.objects.exists())
        self.assertFalse(Transaccion.objects.exists())

    @override_settings(HANZI_CATALOGO_URL='https://hanzi.example/api/v1/caracteres/')
    def test_reto_genera_cuatro_opciones_y_califica_la_respuesta(self):
        pronunciaciones = {'人': 'rén', '水': 'shuǐ', '火': 'huǒ', '山': 'shān'}
        datos = {'caracteres': [{'hanzi': hanzi, 'pinyin': pinyin} for hanzi, pinyin in pronunciaciones.items()]}
        url = reverse('core:reto-pinyin')
        with patch('apps.core.hanzi.urlopen', return_value=BytesIO(json.dumps(datos).encode())):
            response = self.client.get(url)
        opciones = response.context['opciones']
        self.assertEqual(set(opciones), set(pronunciaciones.values()))
        correcta = opciones.index(pronunciaciones[response.context['caracter']])
        reto = response.context['reto']
        for indice, mensaje in [(correcta, '¡Correcto!'), ((correcta + 1) % 4, 'Respuesta incorrecta.')]:
            response = self.client.post(url, {'reto': reto, 'opcion': indice})
            self.assertContains(response, mensaje)

    @override_settings(HANZI_CATALOGO_URL='https://hanzi.example/api/v1/caracteres/')
    def test_hanzi_caido_muestra_el_respaldo(self):
        with patch('apps.core.hanzi.urlopen', side_effect=TimeoutError):
            response = self.client.get(reverse('core:reto-pinyin'))
        self.assertContains(response, 'HanZi Mentor no está disponible en este momento.')
        self.assertEqual(self.client.get(reverse('core:home')).status_code, 200)
