# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0008_alter_eventoclinico_tipo_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='mascota',
            name='activa',
            field=models.BooleanField(default=True, verbose_name='Activa'),
        ),
    ]

