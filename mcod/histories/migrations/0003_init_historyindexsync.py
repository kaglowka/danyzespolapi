from django.db import migrations
import datetime


def init_histories_index_sync(apps, schema_editor):
    HistoryIndexSync = apps.get_model("histories", "HistoryIndexSync")
    HistoryIndexSync.objects.create(last_indexed=datetime.datetime.now())


class Migration(migrations.Migration):

    dependencies = [
        ('histories', '0002_historyindexsync'),
    ]

    operations = [
        migrations.RunPython(init_histories_index_sync),
    ]
