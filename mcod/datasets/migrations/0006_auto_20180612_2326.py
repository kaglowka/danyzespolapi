# Generated by Django 2.0.4 on 2018-06-12 21:26

from django.db import migrations
import django.utils.timezone
import mcod.lib.model_utils


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0004_dataset_license'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='modified',
            field=mcod.lib.model_utils.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]
