# Generated manually for the academic delivery baseline.

from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Caja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, unique=True)),
                ('descripcion', models.TextField(blank=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=12)),
                ('activa', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, unique=True)),
                ('rareza', models.CharField(choices=[('COMUN', 'Comun'), ('RARO', 'Raro'), ('EPICO', 'Epico'), ('LEGENDARIO', 'Legendario')], default='COMUN', max_length=20)),
                ('valor_estimado', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
            ],
            options={'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='CajaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('probabilidad', models.DecimalField(decimal_places=2, max_digits=5)),
                ('caja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caja_items', to='cases.caja')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='caja_items', to='cases.item')),
            ],
            options={'ordering': ['caja_id', 'item_id'], 'unique_together': {('caja', 'item')}},
        ),
    ]
