from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from .models import Proyecto, Fase, FaseUser, Rol, TipodeItem


class TestViews(TestCase):

    longMessage = True
    def setUp(self):

        client = Client()
    def test_proyectoCancelar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')

        response = self.client.get(
            reverse('proyectoCancelarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "cancelado", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'home.html',
                                "El template renderizado debe ser home.html.")

    def test_remover_tipo_de_item_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)

        tipo1 = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo2 = TipodeItem.objects.create(nombreTipo="Tipo2", descripcion="DTipo2")
        proyecto1.tipoItem.add(tipo1)
        proyecto1.save()

        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('removertipo', kwargs={'proyectoid': proyecto1.id, 'tipoid': tipo1.id,
                                           }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(list(proyecto1.tipoItem.all()), [tipo1], "Se ha eliminado erroneamenete a ltipo de item.")

    def test_remover_tipo_de_item_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo2 = TipodeItem.objects.create(nombreTipo="Tipo2", descripcion="DTipo2")
        proyecto1.tipoItem.add(tipo1)

        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('removertipo', kwargs={'proyectoid': proyecto1.id, 'tipoid': tipo1.id,
                                       }))

        self.assertEquals(response.status_code, 200, "No se renderiza ningun html")
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html', "No se renderiza el html esperado.")

        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(list(proyecto1.tipoItem.all()), [], "No ha removido el tipo de item.")



    def test_proyectoUserRemove_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        proyecto.usuarios.add(prueba)
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoUserRemove', kwargs={'proyectoid': proyecto.id, 'userid': prueba.id,
                                                  }))


        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(response.status_code, 200, "No se ha renderizado a ningun html.")
        self.assertTemplateUsed(response, 'proyecto/proyectoUser.html', "No se renderiza a lhtml esperado")
        self.assertEquals(list(proyecto.usuarios.all()), [], "No remueve al usuario")
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), False, "Cuenta erroneamente con permisos.")

    def test_proyectoUserRemove_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoUserRemove', kwargs={'proyectoid': proyecto.id, 'userid': user.id,
                                       }))

        self.assertEquals(response.status_code, 200, "No se renderiza a ningun html.")
        self.assertTemplateUsed(response, 'proyecto/proyectoUser.html', "No se enderiza al html esperado.")

    def test_proyectoUserRemove_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoUserRemove', kwargs={'proyectoid': proyecto.id, 'userid': user.id,
                                                  }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

        

    def test_proyectoCrear_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        assign_perm("proyecto.add_proyecto", user)

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoCrear/')

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/proyectoCrear.html',
                                "El template renderizado debe ser proyecto/proyectoCrear.html.")


    def test_proyectoCrear_GET_FAIL(self):

        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()

        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoCrear/')

        self.assertEquals(response.status_code, 302, "El usuario cuenta con los permisos necesarios, no deberia.")


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
        self.assertEquals(proyecto.nombre, "Proyecto1", "No asigna correctamente el nombre de proeycto.")
        self.assertEquals(proyecto.descripcion, "Descripcion", "No asigna correctamente la descripcion.")
        self.assertEquals(proyecto.fecha_inicio, "10/10/2010", "No asigna correctamente la fecha.")
        self.assertEquals(proyecto.fecha_fin, "10/12/2010", "No asigna correctamente la efcha.")
        self.assertEquals(proyecto.estado, "pendiente", "No asigna correctamente ele estado.")
        self.assertEquals(proyecto.gerente, prueba, "No asigna correctamente el gerente.")
        self.assertEquals(proyecto.creador, user,"No asigna correctamente el creador.")
        self.assertEquals(list(proyecto.usuarios.all()), [prueba, user], "No asigna correctamente a usuarios.")
        self.assertEquals(prueba.has_perm("is_gerente", proyecto), True, "El gerente no cuenta con permisos.")
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), True, "No cuenta con permisos para ver el proyecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")


    def test_proyectoView_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("view_proyecto", user, proyecto)

        string = "/proyecto/proyectoVer/proyectoid="+str(proyecto.id)+"/"
        self.client.login(username='user', password='user')
        response = self.client.get(string)

        self.assertEquals(response.status_code, 200, "No se renderiza a ningun html.")
        self.assertTemplateUsed(response, 'proyecto/proyectoIniciado.html', "No se renderiza al html correcto.")


    def test_proyectoView_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)

        string = "/proyecto/proyectoVer/proyectoid=" + str(proyecto.id) + "/"
        self.client.login(username='user', password='user')
        response = self.client.get(string)

        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")


    def test_gestionProyecto_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("view_proyecto", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/gestionProyecto/', {'proyectoid': proyecto.id})

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/ProyectoInicializadoConfig.html')


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
        self.assertEquals(proyecto.nombre, "Proyecto2", "No se modifica el nombre de proyecto.")
        self.assertEquals(proyecto.descripcion, "Descripcion2", "No se modifica descripcion de proyecto.")
        self.assertEquals(proyecto.fecha_inicio, "10/10/2012", "No se modifica la fecha.")
        self.assertEquals(proyecto.fecha_fin, "10/12/2012", "No se modifica la fecha.")
        self.assertEquals(response.status_code, 200, "No se renderiza el html.")
        self.assertTemplateUsed(response, 'proyecto/ProyectoInicializadoConfig.html', "No se renderiza el html esperado.")

    def test_proyectoDeshabilitar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoDeshabilitar', kwargs={'proyectoid': proyecto.id,
                                                    }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "deshabilitado")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/home/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
                             
    def test_proyectoDeshabilitar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user, estado="pendiente")

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoDeshabilitar', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    

    def test_proyectoDeshabilitar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoDeshabilitar', kwargs={'proyectoid': proyecto.id,
                                                    }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "deshabilitado")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/home/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_proyectoDeshabilitar_GET_FAIL(self):

        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoDeshabilitar', kwargs={'proyectoid': proyecto.id,
                                      }))

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
        self.assertTemplateUsed(response, 'proyecto/proyectoUserAdd.html', "No se renderiza el html esperado.")

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
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        prueba = User.objects.create(username="prueba", email="bla@bla.com", password="prueba")
        prueba2 = User.objects.create(username="prueba2", email="bla2@bla.com", password="prueba")

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoUser/add/',
                                    {'proyectoid': proyecto.id, 'users': [prueba.id, prueba2.id], })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(list(proyecto.usuarios.all()), [prueba, prueba2], "No agrega usuario a proyecto")
        self.assertEquals(prueba.has_perm("view_proyecto", proyecto), True,"Usuario no cuenta con permisos para ver proyecto.")
        self.assertEquals(prueba2.has_perm("view_proyecto", proyecto), True, "Usuari ono cuenta con permisos para ver proyecto.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/proyectoUser.html',
                                "El template renderizado debe ser proyecto/proyectoUser.html." )

    
    def test_proyectoRol_GET_OK(self):
        user = User.objects.create(username="user", password="user")

        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoRol', kwargs={'proyectoid': proyecto.id, 'mensaje': " ",
                                           }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRol.html', "No se renderiza el html esperado.")
    

    def test_proyectoRol_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoRol', kwargs={'proyectoid': proyecto.id, 'mensaje': " ",
                                           }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")
        
    def test_proyectoRolCrear_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/create/',
                                    {'proyectoid': proyecto.id, 'nombre': "Rol_prueba", })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(Rol.objects.filter(nombre="Rol_prueba").exists(), True)
        self.assertEquals(proyecto.roles.filter(nombre="Rol_prueba").exists(), True)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoRol/proyectoid=' + str(proyecto.id) + '/'
                             'mensaje=' + 'Rol%20creado%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    

    def test_proyectoRolCrear_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol = Rol.objects.create(nombre="Rol_prueba")
        proyecto.roles.add(rol)
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/proyecto/proyectoRol/create/',
                                    {'proyectoid': proyecto.id, 'nombre': "Rol_prueba", })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.roles.filter(nombre="Rol_prueba").exclude(id=rol.id).exists(), False)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoRol/proyectoid=' + str(proyecto.id) + '/'
                                                                                                'mensaje=' + 'Error!%20No%20se%20pudo%20crear%20el%20rol%20porque%20dentro%20del%20proyecto%20ya%20se%20cuenta%20con%20otro%20rol%20con%20el%20mismo%20nombre./'
,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

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
        self.assertTemplateUsed(response, 'proyecto/proyectoRolCrear.html', "No se renderiza el html esperado.")

    def test_proyectoRolCrear_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoRol/create/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302)

    
        
        
    def test_proyectoRolModificar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        rol = Rol.objects.create(nombre="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_menu")
        perms = Group.objects.create(name="rol")
        perms.permissions.add(permiso)
        perms.save()
        rol.perms = perms
        rol.save()

        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoRolModify', kwargs={'proyectoid': proyecto.id, 'rolid': rol.id,
                                       }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html', "No se renderiza el html esperado.")

    def test_proyectoRolModificar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        rol = Rol.objects.create(nombre="Rol_prueba2")
        permiso = Permission.objects.get(codename="view_menu")
        perms = Group.objects.create(name="rol")
        perms.permissions.add(permiso)
        perms.save()
        rol.perms = perms
        rol.save()
        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoRolModify', kwargs={'proyectoid': proyecto.id, 'rolid': rol.id,
                                                 }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")
                             
    def test_proyectoRolModificar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol2 = Rol.objects.create(nombre="Rol_prueba2")
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol1.perms = grupo
        rol1.save()

        self.client.login(username='user', password='user')
        path="/proyecto/proyectoRol/modify/proyectoid="+str(proyecto.id)+"/rolid="+str(rol1.id)+"/"
        response = self.client.post(path, {'nombreanterior': rol1.nombre, 'nombre': "Rol_prueba"})



        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso])
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoRol/proyectoid=' + str(proyecto.id) + '/'
                             'mensaje=' + 'Rol%20modificado%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_proyectoRolModificar_POST_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        rol2 = Rol.objects.create(nombre="Rol_prueba2")
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        proyecto.roles.add(rol1)
        proyecto.roles.add(rol2)
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol1.perms = grupo
        rol1.save()

        self.client.login(username='user', password='user')
        path = "/proyecto/proyectoRol/modify/proyectoid=" + str(proyecto.id) + "/rolid=" + str(rol1.id) + "/"
        response = self.client.post(path, {'nombreanterior': rol1.nombre, 'nombre': "Rol_prueba2"})


        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba1")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html', "No se renderiza el html esperado.")

    def test_proyectoRolModificar_POST_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol1 = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso1 = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso1)
        rol1.perms = grupo
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        faseuser = FaseUser.objects.create(user=user, fase=fase)
        rol1.faseUser.add(faseuser)
        rol1.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoRolModify', kwargs={'proyectoid': proyecto.id, 'rolid': rol1.id,
                                                 }))

        rol1 = Rol.objects.get(id=rol1.id)
        self.assertEquals(rol1.nombre, "Rol_prueba1")
        self.assertEquals(list(rol1.perms.permissions.all()), [permiso1])
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoRolModificar.html', "No se renderiza el html esperado.")

    

    def test_proyectoRolEliminar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        rol.save()

        self.client.login(username='user', password='user')
        path='/proyecto/proyectoRol/delete/proyectoid=' + str(proyecto.id) + '/rolid=' + str(rol.id) + '/'
        response = self.client.get(path)


        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoRol/proyectoid=' + str(proyecto.id) + '/'
                             'mensaje=' + 'Rol%20removido%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
        self.assertEquals(list(proyecto.roles.all()), [])
    

    

    def test_proyectoRolEliminar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)
        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        rol.save()

        self.client.login(username='user', password='user')
        path='/proyecto/proyectoRol/delete/proyectoid=' + str(proyecto.id) + '/rolid=' + str(rol.id) + '/'
        response = self.client.get(path)


        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoRol/proyectoid=' + str(proyecto.id) + '/'
                             'mensaje=' + 'Rol%20removido%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
        self.assertEquals(list(proyecto.roles.all()), [], "No elimina el rol")

    
    def test_proyectoRolEliminar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        rol.save()

        self.client.login(username='user', password='user')
        path = '/proyecto/proyectoRol/delete/proyectoid=' + str(proyecto.id) + '/rolid=' + str(rol.id) + '/'
        response = self.client.get(path)

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")
        self.assertEquals(rol in proyecto.roles.all(), True , "Se elimino erroneamente el rol")
        
        
    def test_proyectoRolEliminar_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        rol = Rol.objects.create(nombre="Rol_prueba1")
        grupo = Group.objects.create(name="Rol_prueba1")
        permiso = Permission.objects.get(codename="view_fase")
        grupo.permissions.add(permiso)
        rol.perms = grupo
        proyecto.roles.add(rol)
        rol.save()

        self.client.login(username='user', password='user')
        path = '/proyecto/proyectoRol/delete/proyectoid=' + str(proyecto.id) + '/rolid=' + str(rol.id) + '/'
        response = self.client.get(path)

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")
        self.assertEquals(rol in proyecto.roles.all(), True, "Se elimina el rol incorrectamente." )



    def test_gestionar_tipo_de_item(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/proyectoTipodeItem/', {'proyectoid': proyecto1.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html', "No se renderiza el html esperado.")


    def test_crear_tipo_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get('/proyecto/creartipo/', {'proyectoid': proyecto1.id, })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/creartipo.html', "No se renderiza el html esperado.")

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
            'camposadd': '[fecha]'
        })

        proyecto1 = Proyecto.objects.get(nombre="Proyecto1")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html',
                                "El template renderizado debe ser proyecto/gestionartipodeitem.html.")
        self.assertEquals(TipodeItem.objects.first().nombreTipo, 'RF1', "No se asigna correctamente el nombre")
        self.assertEquals(list(proyecto1.tipoItem.all()), [TipodeItem.objects.first()], "Tipo de item no existe en proyecto.")


    


    def test_modificar_tipo_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        tipo1 = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        proyecto1 = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('modificartipo', kwargs={'proyectoid': proyecto1.id, 'tipoid': tipo1.id,
                                       }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/modifTipodeItem.html', "No se renderiza el html esperado.")

    def test_modificar_tipo_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        proyecto1.tipoItem.add(tipo1)
        proyecto1.save()

        path = "/proyecto/modifdeItem/proyectoid=" + str(proyecto1.id) + "/tipoid=" + str(tipo1.id) + "/"
        self.client.login(username="user", password="user")
        response = self.client.post(path, {'cambio': 1, 'proyectoid': proyecto1.id, 'tipodeitem_id': tipo1.id,
                                           'nombretipo': "tipo1", 'descripciontipo': "dtipo1",
                                           'campos': [], 'camposadd': ""})

        tipo1 = TipodeItem.objects.get(id=tipo1.id)
        self.assertEquals(tipo1.nombreTipo, "tipo1", "No se modifica el nombre")
        self.assertEquals(tipo1.descripcion, "dtipo1", "No se modifica descripcion")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html',
                                "El template renderizado debe ser proyecto/gestionartipodeitem.html.")


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
        self.assertTemplateUsed(response, 'proyecto/importartipo.html', "No se renderiza el html esperado.")
        
    


    def test_importar_tipo_de_item_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        tipo1 = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo2 = TipodeItem.objects.create(nombreTipo="Tipo2", descripcion="DTipo2")

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/importTdeItem/', {'proyectoid': proyecto1.id, 'importados': [tipo1.id, tipo2.id], })

        proyecto1 = Proyecto.objects.get(nombre="Proyecto1")
        self.assertEquals(list(proyecto1.tipoItem.all()), [tipo1, tipo2])
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/gestionartipodeitem.html',
                                "El template renderizado debe ser proyecto/gestionartipodeitem.html.")

    



    def test_proyectoComite(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('Comite', kwargs={'proyectoid': proyecto1.id, 'mensaje': " ",
                                             }))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyectoComite.html', "No se renderiza el html esperado.")

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
        self.assertTemplateUsed(response, 'proyecto/proyectoComiteAdd.html', "No se renderiza el html esperado.")

    def test_proyectoComiteAdd_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        proyecto1.estado = "inicializado"
        proyecto1.save()
        assign_perm("is_gerente", user, proyecto1)

        self.client.login(username="user", password="user")
        response = self.client.post('/proyecto/proyectoComite/add/',
                                    {'proyectoid': proyecto1.id, 'miembros': [user.id], })

        user = User.objects.get(id=user.id)
        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(proyecto1.comite.filter(id=user.id).exists(), True)
        self.assertEquals(user.has_perm("break_lineaBase", proyecto1), True)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoComite/proyectoid=' + str(proyecto1.id) + '/'
                             'mensaje=' + 'Se%20agreg%C3%B3%20correctamente%20al%20usuario%20dentro%20del%20Comit%C3%A9/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_proyectoComiteRemove_GET(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        proyecto1.comite.add(user)

        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('ComiteRemove', kwargs={'proyectoid': proyecto1.id, 'userid': user.id,
                                      }))

        user = User.objects.get(id=user.id)
        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(proyecto1.comite.filter(id=user.id).exists(), False)
        self.assertEquals(user.has_perm("aprobar_rotura_lineaBase", proyecto1), False)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoComite/proyectoid=' + str(proyecto1.id) + '/'
                             + 'mensaje=' + 'Se%20removi%C3%B3%20correctamente%20al%20usuario%20del%20Comit%C3%A9/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_proyectoComiteRemove_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto1 = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                            fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto1)
        proyecto1.comite.add(user)

        self.client.login(username="user", password="user")
        response = self.client.get(
            reverse('ComiteRemove', kwargs={'proyectoid': proyecto1.id, 'userid': user.id,
                                      }))

        user = User.objects.get(id=user.id)
        proyecto1 = Proyecto.objects.get(id=proyecto1.id)
        self.assertEquals(proyecto1.comite.filter(id=user.id).exists(), False)
        self.assertEquals(user.has_perm("aprobar_rotura_lineaBase", proyecto1), False)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoComite/proyectoid=' + str(proyecto1.id) + '/'
                             + 'mensaje=' + 'Se%20removi%C3%B3%20correctamente%20al%20usuario%20del%20Comit%C3%A9/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
    def test_proyectoInicializar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        user2 = User.objects.create(username="user2", password="user")
        user.set_password("user")
        user.save()
        user3 = User.objects.create(username="user3", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        proyecto.tipoItem.add(tipo)
        proyecto.fases.add(fase)
        proyecto.comite.add(user)
        proyecto.comite.add(user2)
        proyecto.comite.add(user3)
        proyecto.estado = "pendiente"
        proyecto.save()
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('proyectoInicializarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "inicializado", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'proyecto/proyectoIniciado.html',
                                "El template renderizado debe ser proyecto/proyectoIniciado.html")

    def test_proyectoInicializar_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.estado = "pendiente"
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('proyectoInicializarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_proyectoInicializar_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.estado = "cancelado"
        proyecto.save()
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('proyectoInicializarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "cancelado", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_proyectoInicializar_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "pendiente"
        proyecto.save()
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('proyectoInicializarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")



    def test_proyectoCancelar_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "pendiente"
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('proyectoCancelarView', kwargs={'proyectoid': proyecto.id, }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
