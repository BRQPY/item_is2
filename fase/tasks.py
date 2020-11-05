from item_is2.celery import app
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template


@app.task
def sendEmailViewFase(mail, name, item, fase):
    context = {'name': name, 'item': item, 'fase': fase}
    template = get_template('fase/correoSolicitudAprobacion.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Solicitud de aprobacion de Item',
        'item',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    email.attach_alternative(content, 'text/html')
    email.send()

@app.task
def sendEmailViewFaseSolicitud(mail, name, item, fase):
    context = {'name': name, 'item': item, 'fase': fase}

    template = get_template('fase/correoSolicitudCambioEstado.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Solicitud de Cambio de estado de Item',
        'item',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    email.attach_alternative(content, 'text/html')
    email.send()



@app.task
def sendEmailHaySolicitudPendiente(mail, name, lineaBase, fase, proyecto):
    context = {'name': name, 'lineaBase': lineaBase, 'fase': fase, 'proyecto': proyecto}
    template = get_template('fase/correocomitevotaahora.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Solicitud de Rotura de Linea Base Pendiente',
        'item',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    email.attach_alternative(content, 'text/html')
    email.send()