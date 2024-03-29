# Generated by Django 2.0.4 on 2018-04-26 09:53

from django.db import migrations, models
import django.utils.timezone
import mcod.lib.storages
import model_utils.fields
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False,
                                                                verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False,
                                                                      verbose_name='modified')),
                ('status', model_utils.fields.StatusField(choices=[('published', 'Published'), ('draft', 'Draft')],
                                                          default='published', max_length=100, no_check_for_status=True,
                                                          verbose_name='status')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status',
                                                                   verbose_name='status changed')),
                ('is_removed', models.BooleanField(default=False)),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('title', models.CharField(max_length=300, verbose_name='Title')),
                ('author', models.CharField(blank=True, max_length=50, null=True, verbose_name='Author')),
                ('url', models.URLField(max_length=300, null=True, verbose_name='App URL')),
                ('notes', models.TextField(null=True, verbose_name='Notes')),
                ('image', models.ImageField(blank=True, max_length=200, null=True,
                                            storage=mcod.lib.storages.ApplicationImagesStorage(base_url=None,
                                                                                               location=None),
                                            upload_to='%Y%m%d',
                                            verbose_name='Image URL')),
                ('uuid', models.UUIDField(default=uuid.uuid4)),
                ('views_count', models.PositiveIntegerField(default=0)),

            ],
            options={
                'verbose_name': 'Application',
                'verbose_name_plural': 'Applications',
                'db_table': 'application',
            },
        ),
    ]
