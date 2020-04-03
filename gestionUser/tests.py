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
        response = self.client.get(reverse('gestionUserView'))

        self.assertEquals(response.status_code, 200, "Mensaje")
        self.assertTemplateUsed(response, 'gestionUser/gestionUser.html')

    def test_gestionUserView_FAIL(self):
        response = self.client.get(reverse('gestionUserView'))

        self.assertEquals(response.status_code, 302, "Mensaje")

    def test_confUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/conf/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/conf.html')

    def test_confUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/conf/')

        self.assertEquals(response.status_code, 302)

    def test_confUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)
        permiso = Permission.objects.get(codename="view_menu")
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        prueba2 = User.objects.create(username="prueba2", email="bla2@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/conf/', {'users': [prueba.id, prueba2.id], })

        self.assertEquals(prueba.user_permissions.get(codename="view_menu"), permiso)
        self.assertEquals(prueba2.user_permissions.get(codename="view_menu"), permiso)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/gestionUser.html')

    def test_gestionPermsView_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/permisos.html')

    def test_gestionPermsView_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/')

        self.assertEquals(response.status_code, 302)

    def test_addPerms_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/agregar/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/addPerms.html')

    def test_addPerms_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/agregar/')

        self.assertEquals(response.status_code, 302)

    def test_addPerms_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)
        permiso = Permission.objects.get(codename="view_menu")
        permiso2 = Permission.objects.get(codename="assign_perms")
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/permisos/agregar/', {'usuario': prueba.id, 'addperm': 1, 'perms': ["1", "2", ], })

        self.assertEquals(prueba.user_permissions.get(codename="view_menu"), permiso)
        self.assertEquals(prueba.user_permissions.get(codename="assign_perms"), permiso2)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/permisos.html')

    def test_removePerms_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.assign_perms", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/remover/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/removePerms.html')

    def test_removePerms_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/permisos/remover/')

        self.assertEquals(response.status_code, 302)

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
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/permisos.html')

    def test_verUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.view_user", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/ver/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/verUser.html')

    def test_verUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/ver/')

        self.assertEquals(response.status_code, 302)

    def test_changeUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.change_user", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/modify/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/changeUser.html')

    def test_changeUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/modify/')

        self.assertEquals(response.status_code, 302)

    def test_changeUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("auth.change_user", user)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba", first_name="prueba", last_name="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/modify/', {'usuario': prueba.id, 'changeuser': 1, 'nombre': "pruebaCambio",
                                                             'firstname': "pruebaCambio", 'lastname': "pruebaCambio", })

        prueba = User.objects.get(id=prueba.id)
        self.assertEquals(prueba.username, "pruebaCambio")
        self.assertEquals(prueba.first_name, "pruebaCambio")
        self.assertEquals(prueba.last_name, "pruebaCambio")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/gestionUser.html')

    def test_unableUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.unable_user", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/deshabilitar/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/unableUser.html')

    def test_unableUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/gestionUser/deshabilitar/')

        self.assertEquals(response.status_code, 302)

    def test_unableUser_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("perms.unable_user", user)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        prueba2 = User.objects.create(username="prueba2", email="bla2@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/gestionUser/deshabilitar/', {'users': [prueba.id, prueba2.id, ], })

        prueba = User.objects.get(id=prueba.id)
        prueba2 = User.objects.get(id=prueba2.id)
        self.assertEquals(prueba.is_active, False)
        self.assertEquals(prueba2.is_active, False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestionUser/gestionUser.html')








