# Generated by Django 2.0.4 on 2018-04-26 09:53

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mcod.users.models
import model_utils.fields
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('applications', '0001_initial'),
        ('datasets', '0001_initial'),
        ('organizations', '0001_initial'),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False,
                                                                verbose_name='created')),
                ('modified', mcod.lib.model_utils.AutoLastModifiedField(default=django.utils.timezone.now, editable=False,
                                                                      verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('password', models.CharField(max_length=130, verbose_name='Password')),
                ('customfields',
                 django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='About')),
                ('fullname', models.CharField(blank=True, max_length=100, null=True, verbose_name='Full name')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Editor')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions'
                                                               ' without explicitly assigning them.',
                                                     verbose_name='Admin status')
                 ),
                ('state', models.CharField(
                    choices=[('active', 'Active'), ('pending', 'Pending'),
                             ('blocked', 'Blocked')], default='pending', max_length=20, verbose_name='State')),
                (
                    'email_confirmed',
                    models.DateTimeField(blank=True, null=True, verbose_name='Email confirmation date')),

            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'user',
            },
            managers=[
                ('objects', mcod.users.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False,
                                                                verbose_name='created')),
                ('modified', mcod.lib.model_utils.AutoLastModifiedField(default=django.utils.timezone.now, editable=False,
                                                                      verbose_name='modified')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Token')),
                ('token_type',
                 models.IntegerField(choices=[(0, 'Email validation token'), (1, 'Password reset token')], default=0,
                                     verbose_name='Token type')),
                ('expiration_date',
                 models.DateTimeField(default=mcod.users.models.get_token_expiration_date, editable=False,
                                      verbose_name='Expiration date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens',
                                           to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'db_table': 'token',
            },
        ),
        migrations.CreateModel(
            name='UserFollowingApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='applications.Application')),
                ('follower',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_following_application',
            },
        ),
        migrations.CreateModel(
            name='UserFollowingArticle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article')),
                ('follower',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_following_article',
            },
        ),
        migrations.CreateModel(
            name='UserFollowingDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.Dataset')),
                ('follower',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_following_dataset',
            },
        ),
        migrations.CreateModel(
            name='UserFollowingUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed',
                                               to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower',
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_following_user',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='followed_applications',
            field=models.ManyToManyField(blank=True, related_name='users_following', related_query_name='user',
                                         through='users.UserFollowingApplication', to='applications.Application',
                                         verbose_name='Followed applications'),
        ),
        migrations.AddField(
            model_name='user',
            name='followed_articles',
            field=models.ManyToManyField(blank=True, related_name='users_following', related_query_name='user',
                                         through='users.UserFollowingArticle', to='articles.Article',
                                         verbose_name='Followed articles'),
        ),
        migrations.AddField(
            model_name='user',
            name='followed_datasets',
            field=models.ManyToManyField(blank=True, related_name='users_following', related_query_name='user',
                                         through='users.UserFollowingDataset', to='datasets.Dataset',
                                         verbose_name='Followed datasets'),
        ),
        migrations.AddField(
            model_name='user',
            name='followed_users',
            field=models.ManyToManyField(blank=True, through='users.UserFollowingUser', to=settings.AUTH_USER_MODEL,
                                         verbose_name='Followed users'),
        ),
        migrations.AddField(
            model_name='user',
            name='organizations',
            field=models.ManyToManyField(blank=True, db_table='user_organization', related_name='users',
                                         related_query_name='user', to='organizations.Organization',
                                         verbose_name='Organizations'),
        )
    ]
