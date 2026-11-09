from datetime import date
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.cases.models import Caja, CajaItem, Item
from apps.core.domain import BusinessError
from apps.openings.models import ItemInventario, Mejora
from apps.openings.upgrades import MejoraService, probabilidad_de_mejora
from apps.users.services import UserService
from apps.wallet.models import Transaccion
from apps.wallet.services import WalletService


class Azar:
    def __init__(self, valor):
        self.valor = valor

    def uniform(self, a, b):
        return self.valor


class BaseInventario(APITestCase):
    def setUp(self):
        self.user = UserService().register('dueno', 'dueno@example.test', 'vault-Test-4821')
        self.otro = UserService().register('otro', 'otro@example.test', 'vault-Test-4821')
        self.client.force_authenticate(self.user)
        self.barato = Item.objects.create(nombre='Barato', valor_estimado=Decimal('25'))
        self.objetivo = Item.objects.create(nombre='Objetivo', valor_estimado=Decimal('100'))

    def objeto(self, user=None, item=None):
        return ItemInventario.objects.create(user=user or self.user, item=item or self.barato)

    def post(self, nombre, cuerpo, clave=None):
        return self.client.post(reverse(nombre), cuerpo, format='json', HTTP_IDEMPOTENCY_KEY=str(clave or uuid4()))

    def saldo(self):
        return WalletService().get_billetera(self.user).saldo


class AccionMasivaTest(BaseInventario):
    def test_vende_varios_con_un_solo_movimiento(self):
        ids = [self.objeto().pk, self.objeto().pk]
        resp = self.post('inventory:bulk', {'ids': ids, 'accion': 'VENDIDO'})
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(self.saldo(), Decimal('1050.00'))
        self.assertEqual(Transaccion.objects.filter(billetera__user=self.user, tipo='VENTA').count(), 1)
        self.assertEqual(ItemInventario.objects.filter(pk__in=ids, estado='VENDIDO').count(), 2)

    def test_si_uno_no_esta_disponible_no_se_vende_ninguno(self):
        libre, vendido = self.objeto(), self.objeto()
        ItemInventario.objects.filter(pk=vendido.pk).update(estado='VENDIDO')
        resp = self.post('inventory:bulk', {'ids': [libre.pk, vendido.pk], 'accion': 'VENDIDO'})
        self.assertEqual(resp.status_code, 409)
        libre.refresh_from_db()
        self.assertEqual(libre.estado, 'DISPONIBLE')
        self.assertEqual(self.saldo(), Decimal('1000.00'))

    def test_objeto_ajeno_da_404_y_no_cambia_nada(self):
        mio, ajeno = self.objeto(), self.objeto(self.otro)
        self.assertEqual(self.post('inventory:bulk', {'ids': [mio.pk, ajeno.pk], 'accion': 'ENVIADO'}).status_code, 404)
        mio.refresh_from_db()
        self.assertEqual(mio.estado, 'DISPONIBLE')

    def test_repetir_la_clave_no_acredita_dos_veces(self):
        ids, clave = [self.objeto().pk], uuid4()
        for _ in range(2):
            self.assertEqual(self.post('inventory:bulk', {'ids': ids, 'accion': 'VENDIDO'}, clave).status_code, 200)
        self.assertEqual(self.saldo(), Decimal('1025.00'))

    def test_envio_masivo_notifica_una_vez_tras_confirmar(self):
        ids = [self.objeto().pk, self.objeto().pk]
        with patch('apps.openings.inventory.NotificadorEnCola') as cola, self.captureOnCommitCallbacks(execute=True):
            self.post('inventory:bulk', {'ids': ids, 'accion': 'ENVIADO'})
        cola.return_value.enviar_envio_simulado.assert_called_once()

    def test_rechaza_accion_desconocida_y_lista_vacia(self):
        self.assertEqual(self.post('inventory:bulk', {'ids': [self.objeto().pk], 'accion': 'CONSUMIDO'}).status_code, 400)
        self.assertEqual(self.post('inventory:bulk', {'ids': [], 'accion': 'VENDIDO'}).status_code, 400)


class MejoraTest(BaseInventario):
    def mejorar(self, azar, *items):
        return MejoraService(randomizer=Azar(azar)).mejorar(self.user, [i.pk for i in items], self.objetivo.pk)

    def test_probabilidad_es_proporcional_con_tope(self):
        self.assertEqual(probabilidad_de_mejora(Decimal('50'), Decimal('100')), Decimal('50.00'))
        self.assertEqual(probabilidad_de_mejora(Decimal('99'), Decimal('100')), Decimal('80.00'))

    def test_objetivo_debe_valer_mas(self):
        for valor in ('100', '150'):
            with self.assertRaises(BusinessError):
                probabilidad_de_mejora(Decimal(valor), Decimal('100'))

    def test_probabilidad_demasiado_baja_se_rechaza(self):
        with self.assertRaises(BusinessError):
            probabilidad_de_mejora(Decimal('0.5'), Decimal('100'))

    def test_exito_consume_lo_entregado_y_entrega_el_objetivo(self):
        a, b = self.objeto(), self.objeto()
        mejora = self.mejorar(49.99, a, b)
        self.assertTrue(mejora.exito)
        self.assertEqual(mejora.probabilidad, Decimal('50.00'))
        self.assertEqual(ItemInventario.objects.filter(pk__in=[a.pk, b.pk], estado='CONSUMIDO').count(), 2)
        self.assertEqual(mejora.premio.item, self.objetivo)
        self.assertEqual(mejora.premio.estado, 'DISPONIBLE')
        self.assertEqual(set(mejora.entregados.all()), {a, b})

    def test_fallo_consume_lo_entregado_sin_premio(self):
        a, b = self.objeto(), self.objeto()
        mejora = self.mejorar(50, a, b)
        self.assertFalse(mejora.exito)
        self.assertIsNone(mejora.premio)
        self.assertFalse(ItemInventario.objects.filter(user=self.user, estado='DISPONIBLE').exists())

    def test_no_cobra_ni_mueve_saldo(self):
        self.mejorar(1, self.objeto())
        self.assertEqual(self.saldo(), Decimal('1000.00'))

    def test_objeto_ya_usado_da_conflicto_y_no_consume_el_resto(self):
        usado, libre = self.objeto(), self.objeto()
        ItemInventario.objects.filter(pk=usado.pk).update(estado='CONSUMIDO')
        resp = self.post('inventory:upgrade', {'ids': [usado.pk, libre.pk], 'objetivo': self.objetivo.pk})
        self.assertEqual(resp.status_code, 409)
        libre.refresh_from_db()
        self.assertEqual(libre.estado, 'DISPONIBLE')
        self.assertFalse(Mejora.objects.exists())

    def test_objetivo_invalido_no_consume_objetos(self):
        caro = self.objeto(item=self.objetivo)
        resp = self.post('inventory:upgrade', {'ids': [caro.pk], 'objetivo': self.barato.pk})
        self.assertEqual(resp.status_code, 400)
        caro.refresh_from_db()
        self.assertEqual(caro.estado, 'DISPONIBLE')

    def test_objeto_ajeno_da_404(self):
        self.assertEqual(self.post('inventory:upgrade', {'ids': [self.objeto(self.otro).pk], 'objetivo': self.objetivo.pk}).status_code, 404)

    def test_maximo_seis_objetos(self):
        ids = [self.objeto().pk for _ in range(7)]
        self.assertEqual(self.post('inventory:upgrade', {'ids': ids, 'objetivo': self.objetivo.pk}).status_code, 400)

    def test_repetir_la_clave_devuelve_el_mismo_resultado(self):
        cuerpo, clave = {'ids': [self.objeto().pk], 'objetivo': self.objetivo.pk}, uuid4()
        primero, segundo = self.post('inventory:upgrade', cuerpo, clave), self.post('inventory:upgrade', cuerpo, clave)
        self.assertEqual(primero.data['id'], segundo.data['id'])
        self.assertEqual(Mejora.objects.count(), 1)

    def test_inventario_muestra_objetos_sin_caja_de_origen(self):
        self.mejorar(1, self.objeto())
        resp = self.client.get(reverse('core:account'))
        self.assertEqual(resp.status_code, 200)
        premio = next(row for row in resp.data['inventory'] if row['estado'] == 'DISPONIBLE')
        self.assertEqual(premio['caja_nombre'], '')
        self.assertEqual(resp.data['aperturas'], 0)


class CajaGratisTest(BaseInventario):
    def setUp(self):
        super().setUp()
        self.gratis = Caja.objects.create(nombre='Economica', precio=Decimal('5'))
        CajaItem.objects.create(caja=self.gratis, item=self.barato, probabilidad=Decimal('100'))
        cara = Caja.objects.create(nombre='Cara', precio=Decimal('50'))
        CajaItem.objects.create(caja=cara, item=self.barato, probabilidad=Decimal('100'))
        self.url = reverse('cases:free')

    def abrir(self):
        return self.client.post(self.url, {}, format='json', HTTP_IDEMPOTENCY_KEY=str(uuid4()))

    def test_abre_la_caja_mas_barata_sin_cobrar(self):
        resp = self.abrir()
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['caja']['id'], self.gratis.pk)
        self.assertEqual(self.saldo(), Decimal('1000.00'))
        self.assertEqual(resp.data['account']['caja_gratis'], {'id': self.gratis.pk, 'disponible': False})

    def test_solo_una_por_dia(self):
        self.abrir()
        self.assertEqual(self.abrir().status_code, 409)
        self.assertEqual(ItemInventario.objects.filter(user=self.user).count(), 1)

    def test_al_dia_siguiente_vuelve_a_estar_disponible(self):
        with patch('apps.openings.services.timezone.localdate', return_value=date(2026, 1, 1)):
            self.assertEqual(self.abrir().status_code, 201)
        with patch('apps.openings.services.timezone.localdate', return_value=date(2026, 1, 2)):
            self.assertEqual(self.abrir().status_code, 201)

    def test_cada_usuario_tiene_la_suya(self):
        self.abrir()
        self.client.force_authenticate(self.otro)
        self.assertEqual(self.abrir().status_code, 201)

    def test_sin_cajas_activas_no_hay_oferta(self):
        Caja.objects.update(activa=False)
        self.assertIsNone(self.client.get(reverse('core:account')).data['caja_gratis'])
        self.assertEqual(self.abrir().status_code, 409)


class HistorialYRankingTest(BaseInventario):
    def test_ranking_es_publico_y_ordenado_por_valor(self):
        self.objeto()
        self.objeto(self.otro, self.objetivo)
        self.client.force_authenticate(None)
        resp = self.client.get(reverse('cases:ranking'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual([row['usuario'] for row in resp.data], ['otro', 'dueno'])
        self.assertNotIn('email', resp.data[0])

    def test_historial_solo_muestra_lo_propio(self):
        MejoraService(randomizer=Azar(1)).mejorar(self.otro, [self.objeto(self.otro).pk], self.objetivo.pk)
        MejoraService(randomizer=Azar(1)).mejorar(self.user, [self.objeto().pk], self.objetivo.pk)
        resp = self.client.get(reverse('inventory:history'))
        self.assertEqual(len(resp.data['mejoras']), 1)
        self.assertEqual(resp.data['aperturas'], [])

    def test_historial_requiere_sesion(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(reverse('inventory:history')).status_code, 401)
