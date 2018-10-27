from celery import shared_task
# from celery.utils.log import get_task_logger
from django.apps import apps
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string

from mcod import settings

# logger = get_task_logger('resource_tasks')


@shared_task
def send_dataset_comment(dataset_id, comment):
    if len(comment) < 3:
        raise Exception('Too short comment')

    model = apps.get_model('datasets', 'Dataset')
    dataset = model.objects.get(pk=dataset_id)

    conn = get_connection(settings.EMAIL_BACKEND)
    template_suffix = ''

    emails = [settings.CONTACT_MAIL, ]
    if dataset.modified_by:
        emails.append(dataset.modified_by.email)
    else:
        emails.extend(user.email for user in dataset.organization.users.all())

    template_params = {
        'host': settings.BASE_URL,
        'title': dataset.title,
        'version': dataset.version,
        'url': dataset.url,
        'comment': comment,
    }

    if settings.DEBUG and getattr(settings, 'TESTER_EMAILS', False):
        template_params['emails'] = ', '.join(emails)
        emails = settings.TESTER_EMAILS
        template_suffix = '-test'

    msg_plain = render_to_string(f'mails/report-comment{template_suffix}.txt', template_params)
    msg_html = render_to_string(f'mails/report-comment{template_suffix}.html', template_params)

    send_mail(
        f'Zgłoszono uwagę do zbioru {dataset.title} ({dataset.version})',
        msg_plain,
        settings.NO_REPLY_EMAIL,
        emails,
        connection=conn,
        html_message=msg_html,
    )
    if settings.DEBUG:
        debug_conn = get_connection(settings.DEBUG_EMAIL_BACKEND)
        send_mail(
            f'Zgłoszono uwagę do zbioru {dataset.title} ({dataset.version})',
            msg_plain,
            settings.NO_REPLY_EMAIL,
            emails,
            connection=debug_conn,
            html_message=msg_html,
        )

    return {
        'dataset': dataset_id
    }
