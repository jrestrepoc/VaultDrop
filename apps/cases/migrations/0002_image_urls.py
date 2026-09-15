from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('cases', '0001_initial')]
    operations = [
        migrations.AddField(model_name='caja', name='imagen_url', field=models.CharField(blank=True, default='', max_length=1000)),
        migrations.AddField(model_name='item', name='imagen_url', field=models.CharField(blank=True, default='', max_length=1000)),
    ]
