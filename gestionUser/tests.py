from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from guardian.shortcuts import assign_perm

class TestViews(TestCase):

    longMessage = True
    def setUp(self):

        client = Client()

    def test_gestionUserView_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        assign_perm("perms.view_menu", user)
        response = self.client.get(reverse('gestionUserView', kwargs={'mensaje':" " }))

        self.assertEquals(response.status_code, 200, "No se renderiza un html.")
        self.assertTemplateUsed(response, 'gestionUser/gestionUser.html', "Html renderizado erroneo.")

    def test_gestionUserView_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        path='/gestionUser/mensaje='+' '+'/'
        response = self.client.get(path)

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/?next=%2FgestionUser%2Fmensaje%253D%2520%2F',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_confUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get(reverse('confUserView', kwargs={'userid':user.id }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/mensaje=' +
                             'Usuario%20agregado%20correctamente%20al%20sistema./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_confUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get(reverse('confUserView', kwargs={'userid':user.id }))

        self.assertEquals(response.status_code, 302, "No sw ha redirigido a la vista de error.")

    def test_confUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get(reverse('confUserView', kwargs={'userid': user.id}))

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/mensaje=' +
                             'Usuario%20agregado%20correctamente%20al%20sistema./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_gestionPermsView_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/')

        self.assertEquals(response.status_code, 200, "No se renderizo ningun html")
        self.assertTemplateUsed(response, 'gestionUser/permisos.html', "No se renderizo el html esperado")

    def test_gestionPermsView_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/')

        self.assertEquals(response.status_code, 302, "No se redirige a la vista de error.")

    def test_addPerms_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/agregar/', {'userid': user.id })

        self.assertEquals(response.status_code, 200, "No se renderizo a ningun html.")
        self.assertTemplateUsed(response, 'gestionUser/addPerms.html', "No se renderizo al html esperado.")

    def test_addPerms_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/agregar/')

        self.assertEquals(response.status_code, 302, "No se redirige a la vista de error.")

    def test_addPerms_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)
        permiso = Permission.objects.get(codename="view_menu")
        permiso2 = Permission.objects.get(codename="assign_perms")
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        assign_perm("perms.assign_perms", user)
        response = self.client.post('/gestionUser/permisos/agregar/', {'usuario': user.id, 'addperm': 1, 'perms': ["1", "2", ], })

        self.assertEquals(user.has_perm("perms.view_menu"), True)
        self.assertEquals(user.has_perm("perms.assign_perms"), True)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/Usuario/userid=' + str(user.id) +
                             '/mensaje=' + 'Permisos%20actualizados%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_removePerms_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/remover/')

        self.assertEquals(response.status_code, 200, "No se renderiza ningun html.")
        self.assertTemplateUsed(response, 'gestionUser/removePerms.html', "No se renderiza al html esperado.")

    def test_removePerms_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/remover/')

        self.assertEquals(response.status_code, 302, "No se redirige a la vista de error")

    def test_removePerms_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)
        permiso = Permission.objects.get(codename="view_menu")
        permiso2 = Permission.objects.get(codename="assign_perms")
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        assign_perm("perms.view_menu", prueba)
        assign_perm("perms.assign_perms", prueba)

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/permisos/remover/', {'usuario': prueba.id, 'removeperm': 1, 'perms': [permiso.codename, permiso2.codename, ], })

        permisos = list(prueba.user_permissions.all())
        self.assertEquals(permisos, [])
        self.assertEquals(response.status_code, 200, "No se renderizo ningun html.")
        self.assertTemplateUsed(response, 'gestionUser/permisos.html', "No se renderizo al html esperado.")

    def test_verUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.view_user", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/ver/', {'userid': user.id })

        self.assertEquals(response.status_code, 200, "No se rendrizo a ningun html.")
        self.assertTemplateUsed(response, 'gestionUser/verUser.html', "No se renderiza a html esperado.")

    def test_verUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/ver/')

        self.assertEquals(response.status_code, 302, "No se redirigea la vista de error.")

    def test_changeUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.change_user", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/modify/', {'userid': user.id })

        self.assertEquals(response.status_code, 200, "No se ha renderizado a ningun html")
        self.assertTemplateUsed(response, 'gestionUser/changeUser.html', "No se renderiza al html esperado.")

    def test_changeUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/modify/')

        self.assertEquals(response.status_code, 302, "No se redirige a la vista de error.")

    def test_changeUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.change_user", user)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba", first_name="prueba", last_name="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/modify/', {'usuario': user.id, 'changeuser': 1, 'nombre': "pruebaCambio",
                                                             'firstname': "pruebaCambio", 'lastname': "pruebaCambio", })

        prueba = User.objects.get(id=user.id)
        self.assertEquals(prueba.username, "pruebaCambio")
        self.assertEquals(prueba.first_name, "pruebaCambio")
        self.assertEquals(prueba.last_name, "pruebaCambio")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/Usuario/userid=' + str(user.id) +
                             '/mensaje=' + 'Los%20datos%20del%20usuario%20fueron%20actualizados%20correctamente/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_unableUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()


        self.client.login(username="user", password="user")
        assign_perm("perms.unable_user", user)
        response = self.client.get(reverse('unableUser', kwargs={'userid':user.id }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/mensaje=' +
                             'Se%20removi%C3%B3%20correctamente%20al%20usuario./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_unableUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get(reverse('unableUser', kwargs={'userid':user.id }))

        self.assertEquals(response.status_code, 302, "No se redirige a la vista de error")

    def test_unableUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()


        self.client.login(username='user', password='user')
        assign_perm("perms.unable_user", user)
        response = self.client.get(reverse('unableUser', kwargs={'userid':user.id }))

        user = User.objects.get(id=user.id)
        self.assertEquals(user.is_active, False)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/gestionUser/mensaje=' +
                             'Se%20removi%C3%B3%20correctamente%20al%20usuario./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")







