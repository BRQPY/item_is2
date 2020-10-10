from item_is2.celery import app
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from celery import shared_task
from time import sleep


@shared_task
def sendEmailView(mail, name):
    print("jjjj")


    context = {'name': name}

    template = get_template('gestionUser/correo.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Noficacion de acceso',
        'item',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    email.attach_alternative(content, 'text/html')
    email.send()
