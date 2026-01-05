# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registro', '0012_eventoclinico_diagnostico_archivoadjunto'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfiltutor',
            name='calle',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Calle'),
        ),
        migrations.AddField(
            model_name='perfiltutor',
            name='numero',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Número'),
        ),
        migrations.AddField(
            model_name='perfiltutor',
            name='comuna',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Comuna'),
        ),
    ]

