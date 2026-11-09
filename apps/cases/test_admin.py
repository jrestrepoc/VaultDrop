from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import TokenProxy

from apps.cases.models import Caja, CajaItem, Item
from apps.openings.models import AperturaCaja
from apps.users.services import UserService
from apps.wallet.models import Billetera, Transaccion

User = get_user_model()


class PanelTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('jefe', 'jefe@example.test', 'vault-Admin-4821')
        self.client.force_login(self.admin)
        self.item = Item.objects.create(nombre='Skin A', valor_estimado=Decimal('30'))
        self.otro = Item.objects.create(nombre='Skin B', valor_estimado=Decimal('10'))

    def crear_caja(self, *probabilidades):
        datos = {
            'nombre': 'Caja nueva', 'imagen_url': '', 'descripcion': '', 'precio': '20', 'activa': 'on',
            'caja_items-TOTAL_FORMS': str(len(probabilidades)), 'caja_items-INITIAL_FORMS': '0',
            'caja_items-MIN_NUM_FORMS': '0', 'caja_items-MAX_NUM_FORMS': '1000',
        }
        for i, (item, probabilidad) in enumerate(probabilidades):
            datos[f'caja_items-{i}-item'] = item.pk
            datos[f'caja_items-{i}-probabilidad'] = probabilidad
        return self.client.post(reverse('admin:cases_caja_add'), datos)

    def caja_con_aperturas(self):
        caja = Caja.objects.create(nombre='Con datos', precio=Decimal('20'))
        CajaItem.objects.create(caja=caja, item=self.item, probabilidad=Decimal('25'))
        CajaItem.objects.create(caja=caja, item=self.otro, probabilidad=Decimal('75'))
        for item in (self.item, self.otro, self.otro, self.otro):
            AperturaCaja.objects.create(user=self.admin, caja=caja, item=item, costo=Decimal('20'))
        return caja


class CajasEnPanelTest(PanelTestCase):
    def test_rechaza_probabilidades_que_no_suman_100(self):
        resp = self.crear_caja((self.item, '50'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'deben sumar 100%')
        self.assertFalse(Caja.objects.filter(nombre='Caja nueva').exists())

    def test_crea_caja_con_probabilidades_validas(self):
        resp = self.crear_caja((self.item, '40'), (self.otro, '60'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Caja.objects.get(nombre='Caja nueva').caja_items.count(), 2)

    def test_precio_debe_ser_positivo(self):
        datos = {'nombre': 'Gratis', 'precio': '0', 'caja_items-TOTAL_FORMS': '0', 'caja_items-INITIAL_FORMS': '0'}
        self.assertEqual(self.client.post(reverse('admin:cases_caja_add'), datos).status_code, 200)
        self.assertFalse(Caja.objects.filter(nombre='Gratis').exists())

    def test_lista_muestra_estadisticas_de_la_caja(self):
        self.caja_con_aperturas()
        fila = self.client.get(reverse('admin:cases_caja_changelist')).context['cl'].result_list[0]
        self.assertEqual((fila._aperturas, fila._ingresos, fila._valor), (4, Decimal('80'), Decimal('60')))
        self.assertContains(self.client.get(reverse('admin:cases_caja_changelist')), '75,0%')

    def test_aperturas_gratis_no_inflan_el_retorno(self):
        caja = self.caja_con_aperturas()
        AperturaCaja.objects.create(user=self.admin, caja=caja, item=self.item, costo=Decimal('0'))
        fila = self.client.get(reverse('admin:cases_caja_changelist')).context['cl'].result_list[0]
        self.assertEqual((fila._aperturas, fila._ingresos, fila._valor), (5, Decimal('80'), Decimal('60')))

    def test_detalle_compara_probabilidad_configurada_y_real(self):
        caja = self.caja_con_aperturas()
        resp = self.client.get(reverse('admin:cases_caja_change', args=[caja.pk]))
        self.assertContains(resp, '<td>Skin B</td><td>75,00%</td><td>3</td><td>75,00%</td>', html=True)

    def test_caja_abierta_no_se_puede_borrar(self):
        caja = self.caja_con_aperturas()
        self.client.post(reverse('admin:cases_caja_delete', args=[caja.pk]), {'post': 'yes'})
        self.assertTrue(Caja.objects.filter(pk=caja.pk).exists())

    def test_accion_desactiva_cajas(self):
        caja = self.caja_con_aperturas()
        self.client.post(reverse('admin:cases_caja_changelist'), {'action': 'desactivar', '_selected_action': [caja.pk]})
        caja.refresh_from_db()
        self.assertFalse(caja.activa)

    def test_listas_con_estadisticas_conservan_el_orden(self):
        for modelo in (Caja, Item):
            self.assertTrue(admin.site._registry[modelo].get_queryset(None).ordered)

    def test_caja_borrada_no_reaparece_al_arrancar(self):
        call_command('seed_catalog', verbosity=0)
        total = Caja.objects.count()
        Caja.objects.order_by('pk').first().delete()
        call_command('seed_catalog', '--if-empty', verbosity=0)
        self.assertEqual(Caja.objects.count(), total - 1)


class AccesoAlPanelTest(PanelTestCase):
    def test_usuario_normal_no_entra(self):
        normal = UserService().register('normal', 'normal@example.test', 'vault-Test-4821')
        self.client.force_login(normal)
        resp = self.client.get(reverse('admin:index'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('admin:login'), resp.url)

    def test_saldos_e_historial_son_solo_lectura(self):
        usuario = UserService().register('cuenta', 'cuenta@example.test', 'vault-Test-4821')
        billetera = Billetera.objects.get(user=usuario)
        movimiento = Transaccion.objects.get(billetera=billetera)
        self.assertEqual(self.client.get(reverse('admin:wallet_transaccion_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('admin:wallet_billetera_change', args=[billetera.pk]), {'saldo': '999999'}).status_code, 403)
        self.assertEqual(self.client.post(reverse('admin:wallet_transaccion_delete', args=[movimiento.pk]), {'post': 'yes'}).status_code, 403)
        billetera.refresh_from_db()
        self.assertEqual(billetera.saldo, Decimal('1000.00'))

    def test_cuentas_no_se_crean_ni_borran_desde_el_panel(self):
        self.assertEqual(self.client.get(reverse('admin:users_user_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('admin:users_user_delete', args=[self.admin.pk]), {'post': 'yes'}).status_code, 403)

    def test_accion_desactiva_cuentas_menos_la_propia(self):
        usuario = UserService().register('baja', 'baja@example.test', 'vault-Test-4821')
        self.client.post(reverse('admin:users_user_changelist'), {'action': 'desactivar', '_selected_action': [usuario.pk, self.admin.pk]})
        usuario.refresh_from_db()
        self.admin.refresh_from_db()
        self.assertFalse(usuario.is_active)
        self.assertTrue(self.admin.is_active)

    def test_historial_identifica_al_dueno_de_la_billetera(self):
        usuario = UserService().register('dueno', 'dueno@example.test', 'vault-Test-4821')
        self.assertContains(self.client.get(reverse('admin:wallet_transaccion_changelist')), usuario.username)

    def test_tokens_no_aparecen_en_el_panel(self):
        self.assertFalse(admin.site.is_registered(TokenProxy))

    def test_superusuario_puede_usar_la_aplicacion(self):
        resp = self.client.get(reverse('core:account'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['wallet']['saldo'], '0.00')

    def test_panel_carga_en_ingles(self):
        resp = self.client.get(reverse('admin:cases_caja_changelist'), HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(resp, 'VaultDrop administration')
        self.assertContains(resp, 'Openings')
