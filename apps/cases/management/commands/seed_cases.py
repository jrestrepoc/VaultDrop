from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.cases.models import Caja, Item, CajaItem


class Command(BaseCommand):
    help = 'Puebla la base de datos con cajas e ítems iniciales para la simulación y sustentación.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos iniciales (Seed)...')

        cajas_data = [
            {
                'nombre': 'Caja Novato',
                'descripcion': 'Ideal para dar los primeros pasos. Armas confiables y costo accesible.',
                'precio': Decimal('50.00'),
                'items': [
                    {'nombre': 'Glock-18 | Arena Verde', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('15.00'), 'prob': Decimal('50.00')},
                    {'nombre': 'P250 | Ola Marina', 'rareza': Item.RAREZA_COMUN, 'valor': Decimal('25.00'), 'prob': Decimal('30.00')},
                    {'nombre': 'M4A1-S | Humo Gris', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('80.00'), 'prob': Decimal('15.00')},
                    {'nombre': 'AK-47 | Fénix Radiante', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('250.00'), 'prob': Decimal('5.00')},
                ]
            },
            {
                'nombre': 'Caja Cyberpunk',
                'descripcion': 'Skins electrizantes con estética retro-futurista y acabados neón.',
                'precio': Decimal('150.00'),
                'items': [
                    {'nombre': 'Desert Eagle | Neón Retro', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('70.00'), 'prob': Decimal('45.00')},
                    {'nombre': 'AWP | Resplandor Cósmico', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('220.00'), 'prob': Decimal('35.00')},
                    {'nombre': 'Cuchillo Karambit | Rayo Ultravioleta', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('850.00'), 'prob': Decimal('15.00')},
                    {'nombre': 'Guantes Especialistas | Dragón Carmesí', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('1500.00'), 'prob': Decimal('5.00')},
                ]
            },
            {
                'nombre': 'Caja Élite EAFIT',
                'descripcion': 'La colección más codiciada. Ítems legendarios y alta volatilidad.',
                'precio': Decimal('300.00'),
                'items': [
                    {'nombre': 'USP-S | Oro Mate', 'rareza': Item.RAREZA_RARO, 'valor': Decimal('120.00'), 'prob': Decimal('40.00')},
                    {'nombre': 'AK-47 | Emperador Imperial', 'rareza': Item.RAREZA_EPICO, 'valor': Decimal('450.00'), 'prob': Decimal('35.00')},
                    {'nombre': 'M4A4 | Aullido Estelar', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('1200.00'), 'prob': Decimal('20.00')},
                    {'nombre': 'Cuchillo Mariposa | Zafiro Líquido', 'rareza': Item.RAREZA_LEGENDARIO, 'valor': Decimal('3500.00'), 'prob': Decimal('5.00')},
                ]
            }
        ]

        with transaction.atomic():
            for c_data in cajas_data:
                caja, creada = Caja.objects.get_or_create(
                    nombre=c_data['nombre'],
                    defaults={
                        'descripcion': c_data['descripcion'],
                        'precio': c_data['precio'],
                        'activa': True
                    }
                )
                if not creada:
                    caja.descripcion = c_data['descripcion']
                    caja.precio = c_data['precio']
                    caja.activa = True
                    caja.save()

                total_prob = Decimal('0.00')
                for i_data in c_data['items']:
                    item, _ = Item.objects.get_or_create(
                        nombre=i_data['nombre'],
                        defaults={
                            'rareza': i_data['rareza'],
                            'valor_estimado': i_data['valor'],
                        }
                    )
                    caja_item, _ = CajaItem.objects.get_or_create(
                        caja=caja,
                        item=item,
                        defaults={'probabilidad': i_data['prob']}
                    )
                    caja_item.probabilidad = i_data['prob']
                    caja_item.save()
                    total_prob += i_data['prob']

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [OK] Caja "{caja.nombre}" configurada con {len(c_data["items"])} items '
                        f'(Precio: ${caja.precio}, Probabilidades: {total_prob}%)'
                    )
                )

        self.stdout.write(self.style.SUCCESS('¡Carga de datos iniciales completada exitosamente!'))

