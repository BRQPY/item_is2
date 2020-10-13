from item_is2.celery import app
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
@app.task
def sendEmailViewProyecto(mail, name,proyecto_name,n):
    context = {'name': name, 'proyecto_name':proyecto_name}
    if(n==0):

        template = get_template('proyecto/correoGerente.html')
    else:
        template = get_template('proyecto/correoComite.html')
    content = template.render(context)

    email = EmailMultiAlternatives(
        'Noficacion de Proyectos',
        'item',
        settings.EMAIL_HOST_USER,
        [mail]
    )
    email.attach_alternative(content, 'text/html')
    email.send()