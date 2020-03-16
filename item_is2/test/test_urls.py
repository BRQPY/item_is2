from django.test import SimpleTestCase
from django.urls import reverse, resolve
from item_is2.views import login_prueba, bienvenido

class TestUrls(SimpleTestCase):

    def test_login_url_is_resolved(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, login_prueba)

    def test_bienvenida_url_is_resolved(self):
        url = reverse('bienvenido')
        self.assertEquals(resolve(url).func, bienvenido)
