import urllib3
from django.apps import apps
from django_tqdm import BaseCommand
from mcod.resources.tasks import get_resource_from_url, process_resource_file
from django.conf import settings

urllib3.disable_warnings()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--pks', type=str)
        parser.add_argument(
            '--async',
            action='store_const',
            dest='async',
            const=True,
            help="Validate using celery tasks"
        )

    def handle(self, *args, **options):
        asnc = options.get('async') or False
        if not asnc:
            settings.CELERY_TASK_ALWAYS_EAGER = True
        Resource = apps.get_model('resources', 'Resource')

        query = Resource.objects.all()
        if options['pks']:
            pks = (int(pk) for pk in options['pks'].split(','))
            query = query.filter(pk__in=pks)

        progress_bar = self.tqdm(desc="Validating", total=query.count())
        for resource in query:
            progress_bar.update(1)
            if resource.type == 'file':
                process_resource_file.delay(resource.id)
            else:
                get_resource_from_url.delay(resource.id)
        print('Done.')
