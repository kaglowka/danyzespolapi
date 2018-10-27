# Generated by Django 2.0.4 on 2018-05-25 12:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_auto_20180420_1245'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleTrash',
            fields=[
            ],
            options={
                'verbose_name': 'Trash',
                'verbose_name_plural': 'Trash',
                'proxy': True,
                'indexes': [],
            },
            bases=('articles.article',),
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'default_manager_name': 'objects', 'verbose_name': 'Article', 'verbose_name_plural': 'Articles'},
        ),
    ]
