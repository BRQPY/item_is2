from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from .models import Proyecto, Fase, FaseUser, Rol, TipodeItem


class TestViews(TestCase):

    def setUp(self):

        client = Client()


    def test_proyectoCrear_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("proyecto.add_proyecto", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoCrear/')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoCrear.html')


    def test_proyectoCrear_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoCrear/')

        self.assertEquals(response.status_code, 302)


    def test_proyectoCrear_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("proyecto.add_proyecto", user)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoCrear/', {'nombre': "Proyecto1", 'descripcion': "Descripcion", 'fechaini': "10/10/2010",
                                                                 'fechafin': "10/12/2010", 'gerente': prueba.id, })

        proyecto = Proyecto.objects.get(nombre="Proyecto1")
        self.assertEquals(proyecto.nombre, "Proyecto1")
        self.assertEquals(proyecto.descripcion, "Descripcion")
        self.assertEquals(proyecto.fecha_inicio, "10/10/2010")
        self.assertEquals(proyecto.fecha_fin, "10/12/2010")
        self.assertEquals(proyecto.estado, "pendiente")
        self.assertEquals(proyecto.gerente, prueba)
        self.assertEquals(proyecto.creador, user)
        self.assertEquals(list(proyecto.usuarios.all()), [prueba, user])
        self.assertEquals(prueba.has_perm("is_gerente", proyecto), True)
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), True)
        self.assertEquals(response.status_code, 302)


    def test_proyectoView_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("view_proyecto", user, proyecto)

        string = "/proyecto/proyectoVer/"+str(proyecto.id)+"/"
        self.client.login(username='user', password='user')
        response = self.client.get(string)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto.html')


    def test_proyectoView_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)

        string = "/proyecto/proyectoVer/" + str(proyecto.id) + "/"
        self.client.login(username='user', password='user')
        response = self.client.get(string)

        self.assertEquals(response.status_code, 302)


    def test_gestionProyecto_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("view_proyecto", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/gestionProyecto/', {'proyectoid': proyecto.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')


    def test_gestionProyecto_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        self.client.login(username='user', password='user')
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)

        response = self.client.get('/proyecto/gestionProyecto/', {'proyectoid': proyecto.id})

        self.assertEquals(response.status_code, 302)


    def test_proyectoModificar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/modify/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoModificar.html')


    def test_proyectoModificar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/modify/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoModificar_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/modify/', {'nombre': "Proyecto2", 'descripcion': "Descripcion2", 'fechaini': "10/10/2012",
                                                                 'fechafin': "10/12/2012", 'proyectoid': proyecto.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.nombre, "Proyecto2")
        self.assertEquals(proyecto.descripcion, "Descripcion2")
        self.assertEquals(proyecto.fecha_inicio, "10/10/2012")
        self.assertEquals(proyecto.fecha_fin, "10/12/2012")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoDeshabilitar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/unable/', {'proyectoid': proyecto.id, 'pregunta': "si"})

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "deshabilitado")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_proyectoDeshabilitar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user, estado="pendiente")
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/unable/', {'proyectoid': proyecto.id, 'pregunta': "no"})

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoDeshabilitar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/unable/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoDeshabilitar.html')

    def test_proyectoDeshabilitar_GET_FAIL(self):

        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/unable/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoUser_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoUser.html')

    def test_proyectoUser_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoUserAdd_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/add/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoUserAdd.html')

    def test_proyectoUserAdd_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/add/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoUserAdd_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        prueba2 = User.objects.create(username="prueba2", email="bla2@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoUser/add/', {'proyectoid': proyecto.id, 'users': [prueba.id, prueba2.id], })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(list(proyecto.usuarios.all()), [prueba, prueba2])
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), True)
        self.assertEquals(prueba2.has_perm("view_proyecto", proyecto), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoUserRemove_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/remove/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoUserRemove.html')

    def test_proyectoUserRemove_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoUser/remove/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoUserRemove_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        prueba2 = User.objects.create(username="prueba2", email="bla2@bla.com", password="prueba")
        proyecto.usuarios.add(prueba)
        proyecto.usuarios.add(prueba2)
        proyecto.save()
        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoUser/remove/', {'proyectoid': proyecto.id, 'users': [prueba.id, prueba2.id], })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(list(proyecto.usuarios.all()), [])
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), False)
        self.assertEquals(prueba2.has_perm("view_proyecto", proyecto), False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRol_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRol.html')

    def test_proyectoRol_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoRolCrear_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/create/', {'proyectoid': proyecto.id, 'nombre': "Rol_prueba", })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(Rol.objects.filter(nombre="Rol_prueba").exists(), True)
        self.assertEquals(proyecto.roles.filter(nombre="Rol_prueba").exists(), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRolCrear_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        Rol.objects.create(nombre="Rol_prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/create/',
                                    {'proyectoid': proyecto.id, 'nombre': "Rol_prueba", })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.roles.filter(nombre="Rol_prueba").exists(), False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolCrear.html')

    def test_proyectoRolCrear_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/create/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolCrear.html')

    def test_proyectoRolCrear_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/create/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoRolModificar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol2 = Rol.objects.create(nombre="Rol_prueba2")
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol1.perms = grupo
        rol1.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/modify/', {'proyectoid': proyecto.id, 'nombre': "Rol_prueba",
                                                                      'rolid': rol1.id, 'perms': ["1", "2"], 'changerol':1, })

        permiso1 = Permission.objects.get(codename="add_fase")
        permiso2 = Permission.objects.get(codename="change_fase")
        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso1, permiso2])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRolModificar_POST_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol2 = Rol.objects.create(nombre="Rol_prueba2")
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso1 = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso1)
        rol1.perms = grupo
        rol1.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/modify/', {'proyectoid': proyecto.id, 'nombre': "Rol_prueba2",
                                                                      'rolid': rol1.id, 'perms': ["1", "2"], 'changerol':1, })

        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba1")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso1])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html')

    def test_proyectoRolModificar_POST_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso1 = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso1)
        rol1.perms = grupo
        fase = Fase.objects.create(nombre="Fase1")
        faseuser = FaseUser.objects.create(user=user, fase=fase)
        rol1.faseUser.add(faseuser)
        rol1.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/modify/', {'proyectoid': proyecto.id, 'roles': rol1.id, })

        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba1")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso1])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html')

    def test_proyectoRolModificar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/modify/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html')

    def test_proyectoRolModificar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/modify/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoRolEliminar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        rol.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/delete/', {'proyectoid': proyecto.id, 'roles': rol.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(list(proyecto.roles.all()), [])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRolEliminar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        fase = Fase.objects.create(nombre="Fase1")
        faseuser = FaseUser.objects.create(user=user, fase=fase)
        rol.faseUser.add(faseuser)
        rol.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/delete/', {'proyectoid': proyecto.id, 'roles': rol.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(list(proyecto.roles.all()), [rol])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolEliminar.html')

    def test_proyectoRolEliminar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/delete/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolEliminar.html')

    def test_proyectoRolEliminar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/delete/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoRolAsignar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        rol.save()
        fase = Fase.objects.create(nombre="Fase1")
        fase2 = Fase.objects.create(nombre="Fase2")

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/asignar/', {'proyectoid': proyecto.id, 'roles': rol.id,
                                                                       'users': prueba.id, 'fases': [fase.id, fase2.id], })

        prueba = User.objects.get(id=prueba.id)
        rol = Rol.objects.get(id=rol.id)
        self.assertEquals(prueba.groups.filter(id=grupo.id).exists(), True)
        self.assertEquals(prueba.has_perm("view_fase", fase), True)
        self.assertEquals(prueba.has_perm("view_fase", fase2), True)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase).exists(), True)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase2).exists(), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRolAsignar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        fase = Fase.objects.create(nombre="Fase1")
        fase2 = Fase.objects.create(nombre="Fase2")
        faseUser = FaseUser.objects.create(user=prueba, fase=fase2)
        rol.faseUser.add(faseUser)
        rol.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/asignar/', {'proyectoid': proyecto.id, 'roles': rol.id,
                                                                       'users': prueba.id, 'fases': [fase.id, fase2.id], })

        prueba = User.objects.get(id=prueba.id)
        rol = Rol.objects.get(id=rol.id)
        self.assertEquals(prueba.groups.filter(id=grupo.id).exists(), False)
        self.assertEquals(prueba.has_perm("view_fase", fase), False)
        self.assertEquals(prueba.has_perm("view_fase", fase2), False)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase).exists(), False)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase2).exists(), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolAsignar.html')

    def test_proyectoRolAsinar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/asignar/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolAsignar.html')

    def test_proyectoRolAsignar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/asignar/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    def test_proyectoRolRemover_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        fase = Fase.objects.create(nombre="Fase1")
        fase2 = Fase.objects.create(nombre="Fase2")
        faseUser = FaseUser.objects.create(user=prueba, fase=fase)
        faseUser2 = FaseUser.objects.create(user=prueba, fase=fase2)
        assign_perm("view_fase", grupo, fase)
        assign_perm("view_fase", grupo, fase2)
        rol.faseUser.add(faseUser)
        rol.faseUser.add(faseUser2)
        prueba.groups.add(grupo)
        rol.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/remove/', {'proyectoid': proyecto.id, 'roles': rol.id,
                                                                       'users': prueba.id, 'fases': [fase.id, fase2.id], })

        prueba = User.objects.get(id=prueba.id)
        rol = Rol.objects.get(id=rol.id)
        self.assertEquals(prueba.has_perm("view_fase", fase), False)
        self.assertEquals(prueba.has_perm("view_fase", fase2), False)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase).exists(), False)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase2).exists(), False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_proyectoRolRemover_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        fase = Fase.objects.create(nombre="Fase1")
        fase2 = Fase.objects.create(nombre="Fase2")
        faseUser = FaseUser.objects.create(user=prueba, fase=fase)
        assign_perm("view_fase", grupo, fase)
        rol.faseUser.add(faseUser)
        prueba.groups.add(grupo)
        rol.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/remove/', {'proyectoid': proyecto.id, 'roles': rol.id,
                                                                       'users': prueba.id, 'fases': [fase.id, fase2.id], })

        prueba = User.objects.get(id=prueba.id)
        rol = Rol.objects.get(id=rol.id)
        self.assertEquals(prueba.has_perm("view_fase", fase), True)
        self.assertEquals(rol.faseUser.filter(user=prueba, fase=fase).exists(), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolRemover.html')

    def test_proyectoRolRemover_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/remove/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolRemover.html')

    def test_proyectoRolRemover_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/remove/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)


    def test_gestionar_tipo_de_item(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoTipodeItem/', {'proyectoid': proyecto1.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html')


    def test_crear_tipo_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/creartipo/', {'proyectoid': proyecto1.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/creartipo.html')


    def test_crear_tipo_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/creartipo/', {
            'proyectoid': proyecto1.id,
            'nombretipo': 'RF1',
            'descripciontipo': 'esta es una descripcion',
            'Campos': '[fecha]'
        })

        proyecto1 = Proyecto.objects.get(nombre="Proyecto1")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')
        self.assertEquals(TipodeItem.objects.first().nombre, 'RF1')
        self.assertEquals(list(proyecto1.tipoItem.all()), [TipodeItem.objects.first()])


    def test_modificar_tipo_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/modifdeItem/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/modifTipodeItem.html')

    def test_modificar_tipo_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombre="Tipo1", descripcion="DTipo1")
        proyecto1.tipoItem.add(tipo1)

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/modifdeItem/', {'proyectoid': proyecto1.id, 'cambio': 1, 'tipodeitem_id': tipo1.id,
                                                               'nombretipo': "tipo1", 'descripciontipo': "dtipo1",
                                                               'campos': [], 'camposadd': ""})

        tipo1 = TipodeItem.objects.get(id=tipo1.id)
        self.assertEquals(tipo1.nombre, "tipo1")
        self.assertEquals(tipo1.descripcion, "dtipo1")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')


    def test_importar_tipo_de_item_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/importTdeItem/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/importartipo.html')


    def test_importar_tipo_de_item_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombre="Tipo1", descripcion="DTipo1")
        tipo2 = TipodeItem.objects.create(nombre="Tipo2", descripcion="DTipo2")

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/importTdeItem/', {'proyectoid': proyecto1.id, 'importados': [tipo1.id, tipo2.id], })

        proyecto1 = Proyecto.objects.get(nombre="Proyecto1")
        self.assertEquals(list(proyecto1.tipoItem.all()), [tipo1, tipo2])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')

    def test_remover_tipo_de_item_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/removerTdeItem/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/removertipo.html')


    def test_remover_tipo_de_item_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombre="Tipo1", descripcion="DTipo1")
        tipo2 = TipodeItem.objects.create(nombre="Tipo2", descripcion="DTipo2")
        proyecto1.tipoItem.add(tipo1)
        proyecto1.tipoItem.add(tipo2)

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/removerTdeItem/', {'proyectoid': proyecto1.id, 'eliminados': [tipo1.id, tipo2.id]})

        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(list(proyecto1.tipoItem.all()), [])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')



    def test_proyectoComite(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoComite/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoComite.html')

    def test_proyectoComiteAdd_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoComite/add/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoComiteAdd.html')

    def test_proyectoComiteAdd_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/proyectoComite/add/', {'proyectoid': proyecto1.id, 'miembros': [user.id], })

        user = User.objects.get(id=user.id)
        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(proyecto1.comite.filter(id=user.id).exists(), True)
        self.assertEquals(user.has_perm("aprobar_rotura_lineaBase", proyecto1), True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')


    def test_proyectoComiteRemove_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoComite/remove/', {'proyectoid': proyecto1.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoComiteRemove.html')



    def test_proyectoComiteRemove_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        proyecto1.comite.add(user)

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/proyectoComite/remove/', {'proyectoid': proyecto1.id, 'miembros': [user.id], })

        user = User.objects.get(id=user.id)
        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(proyecto1.comite.filter(id=user.id).exists(), False)
        self.assertEquals(user.has_perm("aprobar_rotura_lineaBase", proyecto1), False)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionProyecto.html')
