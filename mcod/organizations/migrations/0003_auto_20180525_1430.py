# Generated by Django 2.0.4 on 2018-05-25 12:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('organizations', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationTrash',
            fields=[
            ],
            options={
                'verbose_name': 'Trash',
                'verbose_name_plural': 'Trash',
                'proxy': True,
                'indexes': [],
            },
            bases=('organizations.organization',),
        ),
        migrations.AlterModelOptions(
            name='organization',
            options={'default_manager_name': 'objects', 'verbose_name': 'Institution',
                     'verbose_name_plural': 'Institutions'},
        ),
    ]
