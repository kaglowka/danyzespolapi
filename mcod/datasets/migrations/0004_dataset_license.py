# Generated by Django 2.0.4 on 2018-05-31 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0001_initial'),
        ('datasets', '0003_auto_20180525_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='license',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='licenses.License', verbose_name='License ID'),
        ),
    ]