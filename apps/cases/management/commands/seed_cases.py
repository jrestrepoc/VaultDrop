from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cases.models import Caja, Item, CajaItem


class Command(BaseCommand):
    help = 'Puebla la base de datos con las cajas e ítems exactos del catálogo de VaultDrop.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de cajas e ítems oficiales de VaultDrop...')

        # Diccionario maestro de los 15 ítems del diseño oficial
        items_catalogo = {
            'i1': {'nombre': 'AK-47 | Redline', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('85.00')},
            'i2': {'nombre': 'AWP | Dragon Lore', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('850.00')},
            'i3': {'nombre': 'M4A4 | Howl', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('320.00')},
            'i4': {'nombre': 'Glock-18 | Fade', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('55.00')},
            'i5': {'nombre': 'Desert Eagle | Blaze', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('42.00')},
            'i6': {'nombre': 'Karambit | Doppler', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('280.00')},
            'i7': {'nombre': 'P250 | Mehndi', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('8.00')},
            'i8': {'nombre': 'USP-S | Kill Confirmed', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('22.00')},
            'i9': {'nombre': 'MP5-SD | Phosphor', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('3.00')},
            'i10': {'nombre': 'Nova | Antique', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('2.00')},
            'i11': {'nombre': 'MAC-10 | Neon Rider', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('18.00')},
            'i12': {'nombre': 'Butterfly Knife | Tiger', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('190.00')},
            'i13': {'nombre': 'SSG 08 | Blue Spruce', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('5.00')},
            'i14': {'nombre': 'FAMAS | Mecha Industries', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('12.00')},
            'i15': {'nombre': 'CZ75-Auto | Emerald Quartz', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('28.00')},
        }

        # Las 4 cajas oficiales diseñadas en el frontend con probabilidades validadas al 100.00%
        cajas_data = [
            {
                'nombre': 'Fracture Case',
                'descripcion': 'High value covert items. Good chance at classified weapons.',
                'precio': Decimal('45.00'),
                'items': [
                    {'key': 'i2', 'prob': Decimal('0.50')},   # AWP | Dragon Lore
                    {'key': 'i3', 'prob': Decimal('1.50')},   # M4A4 | Howl
                    {'key': 'i6', 'prob': Decimal('3.00')},   # Karambit | Doppler
                    {'key': 'i1', 'prob': Decimal('8.00')},   # AK-47 | Redline
                    {'key': 'i5', 'prob': Decimal('12.00')},  # Desert Eagle | Blaze
                    {'key': 'i4', 'prob': Decimal('20.00')},  # Glock-18 | Fade
                    {'key': 'i8', 'prob': Decimal('30.00')},  # USP-S | Kill Confirmed
                    {'key': 'i10', 'prob': Decimal('25.00')}, # Nova | Antique
                ]
            },
            {
                'nombre': 'Operation Riptide',
                'descripcion': 'Ocean-themed skins. Risk the waves for rare finds.',
                'precio': Decimal('25.00'),
                'items': [
                    {'key': 'i3', 'prob': Decimal('0.80')},   # M4A4 | Howl
                    {'key': 'i12', 'prob': Decimal('2.50')},  # Butterfly Knife | Tiger
                    {'key': 'i1', 'prob': Decimal('5.00')},   # AK-47 | Redline
                    {'key': 'i15', 'prob': Decimal('10.00')}, # CZ75-Auto | Emerald Quartz
                    {'key': 'i11', 'prob': Decimal('18.00')}, # MAC-10 | Neon Rider
                    {'key': 'i8', 'prob': Decimal('25.00')},  # USP-S | Kill Confirmed
                    {'key': 'i13', 'prob': Decimal('28.00')}, # SSG 08 | Blue Spruce
                    {'key': 'i10', 'prob': Decimal('10.70')}, # Nova | Antique
                ]
            },
            {
                'nombre': 'Recoil Case',
                'descripcion': 'Entry-level case with balanced rarity distribution.',
                'precio': Decimal('12.00'),
                'items': [
                    {'key': 'i2', 'prob': Decimal('0.30')},   # AWP | Dragon Lore
                    {'key': 'i5', 'prob': Decimal('3.00')},   # Desert Eagle | Blaze
                    {'key': 'i4', 'prob': Decimal('8.00')},   # Glock-18 | Fade
                    {'key': 'i15', 'prob': Decimal('15.00')}, # CZ75-Auto | Emerald Quartz
                    {'key': 'i14', 'prob': Decimal('22.00')}, # FAMAS | Mecha Industries
                    {'key': 'i7', 'prob': Decimal('25.00')},  # P250 | Mehndi
                    {'key': 'i9', 'prob': Decimal('26.70')},  # MP5-SD | Phosphor
                ]
            },
            {
                'nombre': 'Dreams & Nightmares',
                'descripcion': 'Community case with stunning artwork. Very rare drops.',
                'precio': Decimal('65.00'),
                'items': [
                    {'key': 'i2', 'prob': Decimal('0.20')},   # AWP | Dragon Lore
                    {'key': 'i6', 'prob': Decimal('1.00')},   # Karambit | Doppler
                    {'key': 'i12', 'prob': Decimal('3.00')},  # Butterfly Knife | Tiger
                    {'key': 'i1', 'prob': Decimal('6.00')},   # AK-47 | Redline
                    {'key': 'i5', 'prob': Decimal('12.00')},  # Desert Eagle | Blaze
                    {'key': 'i11', 'prob': Decimal('20.00')}, # MAC-10 | Neon Rider
                    {'key': 'i8', 'prob': Decimal('27.00')},  # USP-S | Kill Confirmed
                    {'key': 'i10', 'prob': Decimal('30.80')}, # Nova | Antique
                ]
            }
        ]

        with transaction.atomic():
            # Desactivar o limpiar cajas de prueba previas si existieran
            cajas_antiguas = ['Caja Novato', 'Caja Cyberpunk', 'Caja Élite EAFIT']
            Caja.objects.filter(nombre__in=cajas_antiguas).delete()

            # 1. Crear o actualizar los 15 ítems maestros
            items_creados = {}
            for key, data in items_catalogo.items():
                item, _ = Item.objects.get_or_create(
                    nombre=data['nombre'],
                    defaults={
                        'rareza': data['rareza'],
                        'valor_estimado': data['valor'],
                    }
                )
                item.rareza = data['rareza']
                item.valor_estimado = data['valor']
                item.save()
                items_creados[key] = item

            # 2. Crear las 4 cajas y asociar los ítems con sus probabilidades exactas
            for c_data in cajas_data:
                caja, _ = Caja.objects.get_or_create(
                    nombre=c_data['nombre'],
                    defaults={
                        'descripcion': c_data['descripcion'],
                        'precio': c_data['precio'],
                        'activa': True,
                    }
                )
                caja.descripcion = c_data['descripcion']
                caja.precio = c_data['precio']
                caja.activa = True
                caja.save()

                total_prob = Decimal('0.00')
                for item_info in c_data['items']:
                    item_obj = items_creados[item_info['key']]
                    caja_item, _ = CajaItem.objects.get_or_create(
                        caja=caja,
                        item=item_obj,
                        defaults={'probabilidad': item_info['prob']}
                    )
                    caja_item.probabilidad = item_info['prob']
                    caja_item.save()
                    total_prob += item_info['prob']

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [OK] Caja "{caja.nombre}" configurada con {len(c_data["items"])} items '
                        f'(Precio: ${caja.precio}, Probabilidad total: {total_prob}%)'
                    )
                )

        self.stdout.write(self.style.SUCCESS('\n¡Carga de cajas e ítems oficiales completada con éxito!'))
