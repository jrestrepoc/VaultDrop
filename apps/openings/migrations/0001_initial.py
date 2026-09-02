# Generated manually for the academic delivery baseline.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AperturaCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('costo', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('caja', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aperturas', to='cases.caja')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aperturas', to='cases.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aperturas', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ItemInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(choices=[('DISPONIBLE', 'Disponible')], default='DISPONIBLE', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('apertura', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inventario_item', to='openings.aperturacaja')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inventarios', to='cases.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventario', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
