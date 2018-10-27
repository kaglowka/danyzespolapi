import base64

from celery import shared_task
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage

from mcod import settings
from mcod.datasets.models import Dataset


@shared_task
def send_application_proposal(app_proposal):
    conn = get_connection(settings.EMAIL_BACKEND)
    emails = [settings.CONTACT_MAIL, ]

    title = app_proposal["title"]
    applicant_email = app_proposal['applicant_email']
    template_suffix = '-test' if settings.DEBUG else ''

    img_data = app_proposal['image']
    data = img_data.split(';base64,')[-1].encode('utf-8')
    decoded_img = base64.b64decode(data)

    image = MIMEImage(decoded_img)
    image.add_header('content-disposition', 'attachment',
                     filename=f"app_image.{image.get_content_subtype()}")

    app_proposal['datasets'] = '\n'.join(
        ("%d. %s (%s)" % (ds.id, ds.title, ds.organization.title))
        for ds in Dataset.objects.filter(id__in=app_proposal['datasets'])
    )

    msg_plain = render_to_string(f'mails/propose-application{template_suffix}.txt', app_proposal)
    msg_html = render_to_string(f'mails/propose-application{template_suffix}.html', app_proposal)

    if settings.DEBUG and getattr(settings, 'TESTER_EMAILS', False):
        emails = settings.TESTER_EMAILS

    mail = EmailMultiAlternatives(
        f'Zgłoszono propozycję aplikacji {title}',
        msg_plain,
        from_email=applicant_email,
        to=emails,
        attachments=[image, ],
        connection=conn
    )
    mail.attach_alternative(msg_html, 'text/html')
    mail.send()

    if settings.DEBUG:
        debug_conn = get_connection(settings.DEBUG_EMAIL_BACKEND)
        mail = EmailMultiAlternatives(
            f'Zgłoszono propozycję aplikacji {title}',
            msg_plain,
            from_email=applicant_email,
            to=emails,
            attachments=[image, ],
            connection=debug_conn
        )
        mail.attach_alternative(msg_html, 'text/html')
        mail.send()

    return {'application_proposed': f'{title} - {applicant_email}'}
