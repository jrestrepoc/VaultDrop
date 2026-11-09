from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_alter_transaccion_tipo_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaccion',
            options={'ordering': ['id']},
        ),
    ]
