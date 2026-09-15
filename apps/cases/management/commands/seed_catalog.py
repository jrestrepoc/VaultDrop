"""Non-destructive initial catalog; existing cases and prices are preserved."""
import json
from decimal import Decimal
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.cases.models import Caja, CajaItem, Item

class Command(BaseCommand):
    help = 'Crea solo las cajas y objetos faltantes del simulador; conserva datos existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        data = json.loads((Path(__file__).resolve().parents[2] / 'data/initial_catalog.json').read_text(encoding='utf-8'))
        rarity = {'consumer':'COMUN','industrial':'COMUN','milspec':'RARO','restricted':'RARO','classified':'EPICO','covert':'LEGENDARIO','contraband':'LEGENDARIO'}
        objects = {}
        for row in data['items']:
            name = row['nombre']
            # Preserve legacy object identity and existing inventory relations.
            obj = Item.objects.filter(nombre='Butterfly Knife | Tiger').first() if name == 'Butterfly Knife | Tiger Tooth' else None
            if obj is None:
                obj, _ = Item.objects.get_or_create(nombre=name, defaults={'rareza':rarity[row['rareza']], 'valor_estimado':Decimal(str(row['valor'])), 'imagen_url':row['image']})
            if not obj.imagen_url:
                obj.imagen_url = row['image']
                obj.save(update_fields=['imagen_url'])
            objects[row['id']] = obj
        created_count = 0
        for row in data['cases']:
            case, created = Caja.objects.get_or_create(nombre=row['nombre'], defaults={'descripcion':row['descripcion'], 'precio':Decimal(str(row['precio'])), 'imagen_url':row['image']})
            if not case.imagen_url:
                case.imagen_url = row['image']
                case.save(update_fields=['imagen_url'])
            if created:
                for entry in row['items']:
                    CajaItem.objects.create(caja=case, item=objects[entry['item']['id']], probabilidad=Decimal(str(entry['probabilidad'])))
                CajaItem.validar_probabilidades(case)
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'Catálogo listo: {created_count} cajas nuevas. Datos existentes conservados.'))
