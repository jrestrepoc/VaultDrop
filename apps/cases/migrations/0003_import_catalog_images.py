import json
from pathlib import Path
from django.db import migrations

def import_images(apps, schema_editor):
    # Snapshot lives with the migration, never in frontend static resources.
    catalog = json.loads(Path(__file__).with_name('catalog_images.json').read_text(encoding='utf-8'))
    for model_name in ('Item', 'Caja'):
        model = apps.get_model('cases', model_name)
        for obj in model.objects.filter(imagen_url='').iterator():
            asset = catalog.get(obj.nombre.removeprefix('★ '))
            if asset:
                obj.imagen_url = asset['image']
                obj.save(update_fields=['imagen_url'])

class Migration(migrations.Migration):
    dependencies = [('cases', '0002_image_urls')]
    operations = [migrations.RunPython(import_images, migrations.RunPython.noop)]
