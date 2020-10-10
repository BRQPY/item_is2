from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_is2.settings')
app = Celery('proj')
app.config_from_object('django.conf:settings', namespace='CELERY') #Nota 2
app.autodiscover_tasks()


app.conf.update(
    BROKER_URL = 'redis://localhost:6379/0',

)
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')