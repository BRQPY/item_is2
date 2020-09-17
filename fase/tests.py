from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from proyecto.models import Proyecto, Fase, FaseUser, Rol, TipodeItem, Item, LineaBase


class TestViews(TestCase):

    longMessage = True
    def setUp(self):

        client = Client()

    def test_itemRelacionar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/addRelacion/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'item/itemAddRelacion.html',
                                "El template renderizado debe ser item/itemAddRelacion.html")

    def test_itemRelacionar_GET_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/addRelacion/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRelacionar_GET_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/addRelacion/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")


    def test_itemRelacionar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item2.estado = "aprobado"
        item2.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.post('/item/addRelacion/', {'itemIdActual': item.id, 'itemIdRelacion': item2.id,
                                                      'siguiente': 'no',
                                                      'proyectoid': proyecto.id,
                                                      'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item2 in item.relaciones.all(), True, "No se ha establecido la relacion en item origen.")
        self.assertEquals(item in item2.relaciones.all(), True, "No se ha establecido la relacion en item destino.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_gestionLineaBase_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("ver_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/gestionLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_gestionLineaBase_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/gestionLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_configLineaBase_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        assign_perm("ver_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('faseConfigLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                               'lineaBaseid': lineaBase.id, }))
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")

    def test_configLineaBase_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('faseConfigLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                               'lineaBaseid': lineaBase.id, }))
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_addLineaBase_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("create_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/addLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseAddLineaBase.html',
                                "El template renderizado debe ser fase/faseAddLineaBase.html")

    def test_addLineaBase_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/addLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_addLineaBase_GET_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("create_lineaBase", user, fase)


        self.client.login(username='user', password='user')
        response = self.client.get('/fase/addLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/faseVer/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
            proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_addLineaBase_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item2.estado = "aprobado"
        item2.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/addLineaBase/', {'nombre': "LineaBase1", 'items': [item.id, item2.id],
                                                      'proyectoid': proyecto.id,
                                                      'faseid': fase.id, 'itemid': item.id, })

        fase= Fase.objects.get(id=fase.id)
        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(LineaBase.objects.count(), 1, "No se ha creado la linea base.")
        lineaBase = LineaBase.objects.get(nombre="LineaBase1")
        self.assertEquals(lineaBase in fase.lineasBase.all(), True, "No se ha guardado la linea base en la fase.")
        self.assertEquals(item in lineaBase.items.all(), True, "No se ha agregado item a linea base.")
        self.assertEquals(item2 in lineaBase.items.all(), True, "No se ha agregado item2 a linea base.")
        self.assertEquals("en linea base", item.estado, "No se cambio el estado de item.")
        self.assertEquals("en linea base", item2.estado, "No se cambio el estado de item2.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_lineaBaseAddItem_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)

        assign_perm("modify_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/lineaBaseAddItem/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/lineaBaseAddItem.html',
                                "El template renderizado debe ser fase/lineaBaseAddItem.html")

    def test_lineaBaseAddItem_GET_Fail1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/lineaBaseAddItem/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_lineaBaseAddItem_GET_Fail2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        assign_perm("modify_lineaBase", user, fase)


        self.client.login(username='user', password='user')
        response = self.client.get('/fase/lineaBaseAddItem/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id})

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")

    def test_lineaBaseAddItem_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)


        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item2.estado = "aprobado"
        item2.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/lineaBaseAddItem/', {'lineaBaseid': lineaBase.id, 'items': [item.id, item2.id],
                                                      'proyectoid': proyecto.id,
                                                      'faseid': fase.id, 'itemid': item.id, })

        lineaBase= LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in lineaBase.items.all(), True, "No se ha agregado item a linea base.")
        self.assertEquals(item2 in lineaBase.items.all(), True, "No se ha agregado item2 a linea base.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")

    def test_lineaBaseRemoveItem_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        lineaBase.items.add(item)
        lineaBase.save()

        assign_perm("modify_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('lineaBaseRemoveItem', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id, 'itemid': item.id }))

        lineaBase=LineaBase.objects.get(id=lineaBase.id)
        item=Item.objects.get(id=item.id)
        self.assertEquals(item in lineaBase.items.all(), False, "No se ha removido el item de la linea base.")
        self.assertEquals("aprobado", item.estado, "No se ha modificado el estado del item.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")

    def test_lineaBaseRemoveItem_GET_Fail1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        lineaBase.items.add(item)


        self.client.login(username='user', password='user')
        response = self.client.get(reverse('lineaBaseRemoveItem', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'itemid': item.id}))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_lineaBaseRemoveItem_GET_Fail2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        lineaBase.items.add(item)
        lineaBase.save()

        assign_perm("modify_lineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('lineaBaseRemoveItem', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'itemid': item.id}))

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")

    def test_lineaCerrar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/cerrarLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id })

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals("cerrada", lineaBase.estado, "No se ha modificado el estado de la linea base.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_lineaBaseCerrar_GET_Fail1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        user2 = User.objects.create(username="user2", password="user2")
        user.set_password("user2")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user2)
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/fase/cerrarLineaBase/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id })

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals("abierta", lineaBase.estado, "Se ha modificado el estado de la linea base.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_lineaBaseCerrar_GET_Fail2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase2", estado="abierta", creador=user)


        self.client.login(username='user', password='user')
        response = self.client.get('/fase/cerrarLineaBase/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'lineaBaseid': lineaBase.id})

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals("abierta", lineaBase.estado, "Se ha modificado el estado de la linea base.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")




'''
    def test_faseCrear_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/faseCrear/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'fase/faseCrear.html',
                                "El template renderizado debe ser fase/faseCrear.html.")

    def test_faseCrear_GET_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/faseCrear/', {'proyectoid': proyecto.id, })

        self.assertEquals(response.status_code, 302, "El usuario cuenta con los permisos necesarios, no deberia.")
        self.assertRedirects(response, '/permissionError/', status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_faseCrear_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "pendiente"
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/faseCrear/', {'nombre': "Fase1", 'descripcion': "Descripcion",
                                                         'proyectoid': proyecto.id, })

        fase = Fase.objects.get(nombre="Fase1")
        self.assertEquals(fase.nombre, "Fase1", "El nombre de la fase es incorrecto.")
        self.assertEquals(fase.descripcion, "Descripcion", "La descripcion de la fase es incorrecta.")
        self.assertEquals(fase.estado, "abierta", "El estado de la fase es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid='+str(proyecto.id)+'/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_faseCrear_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/faseCrear/', {'nombre': "Fase1", 'descripcion': "Descripcion",
                                                         'proyectoid': proyecto.id, })

        self.assertEquals(Fase.objects.all().filter(nombre="Fase1").exists(), False)
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid='+str(proyecto.id)+'/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_faseCrear_POST_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.estado = "pendiente"
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/faseCrear/', {'nombre': "Fase1", 'descripcion': "Descripcion",
                                                         'proyectoid': proyecto.id, })

        self.assertEquals(len(Fase.objects.all()), 1)
        self.assertEquals(response.status_code, 200, "El template no se ha renderizado.")
        self.assertTemplateUsed(response, 'fase/faseCrear.html',
                                "El template renderizado debe ser fase/faseCrear.html.")

    def test_faseModificar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("change_fase", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'fase/faseModificar.html',
                                "El template renderizado debe ser fase/faseModificar.html.")

    def test_faseModificar_GET_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "El usuario cuenta con los permisos necesarios, no deberia.")
        self.assertRedirects(response, '/permissionError/', status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_faseModificar_GET_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("change_fase", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'fase/gestionFase.html',
                                "El template renderizado debe ser fase/gestionFase.html.")

    def test_faseModificar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/modify/', {'nombre': "Fase2", 'descripcion': "Descripcion2",
                                                         'proyectoid': proyecto.id, 'faseid': fase.id})

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(fase.nombre, "Fase2", "El nombre de la fase es incorrecto.")
        self.assertEquals(fase.descripcion, "Descripcion2", "La descripcion de la fase es incorrecta.")
        self.assertEquals(response.status_code, 200, "El template no se ha renderizado.")
        self.assertTemplateUsed(response, 'fase/gestionFase.html',
                                "El template renderizado debe ser fase/gestionFase.html.")

    def test_faseModificar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        fase2 = Fase.objects.create(nombre="Fase2", descripcion="Descripcion2", estado="abierta")
        proyecto.fases.add(fase, fase2)

        self.client.login(username='user', password='user')
        response = self.client.post('/fase/modify/', {'nombre': "Fase2", 'descripcion': "Descripcion2",
                                                         'proyectoid': proyecto.id, 'faseid': fase.id})

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(fase.nombre, "Fase1", "El nombre de la fase es incorrecto.")
        self.assertEquals(fase.descripcion, "Descripcion", "La descripcion de la fase es incorrecta.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'fase/faseModificar.html',
                                "El template renderizado debe ser fase/faseModificar.html.")

    def test_faseDeshabilitar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("delete_fase", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/unable/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(fase.estado, "deshabilitada", "El estado de fase es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_faseModificar_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/unable/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(fase.estado, "abierta", "El estado de fase es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_faseModificar_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("delete_fase", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/fase/unable/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(fase.estado, "abierta", "El estado de fase es incorrecto.")
        self.assertEquals(response.status_code, 200, "El template no se ha renderizado.")
        self.assertTemplateUsed(response, 'fase/gestionFase.html',
                                "El template renderizado debe ser fase/gestionFase.html.")

    def test_itemCrear_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("create_item", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/item/itemCrear/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 200, "El template no se ha renderizado.")
        self.assertTemplateUsed(response, 'item/itemCrear.html',
                                "El template renderizado debe ser item/itemCrear.html.")

    def test_itemCrear_GET_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username="user", password="user")
        response = self.client.get('/item/itemCrear/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCrear_GET_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado="pendiente"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        assign_perm("create_item", user, fase)

        self.client.login(username="user", password="user")
        response = self.client.get('/item/itemCrear/', {'proyectoid': proyecto.id, 'faseid': fase.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/fase/faseVer/faseid='+str(fase.id)+'proyectoid='+str(proyecto.id)+'/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCrear_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        proyecto.tipoItem.add(tipo)
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/item/itemCrear/', {'nombre': "Item1", 'fecha': "10/10/2010",
                                                         'observacion': "Item1Obs", 'costo': 10,
                                                         'CampoExtra': "CampoExtra1", 'CampoExtra2': "CampoExtra2",
                                                         'proyectoid': proyecto.id,
                                                         'faseid': fase.id, 'tipodeitem_id': tipo.id, 'crear': 1, })

        fase = Fase.objects.get(id=fase.id)
        item = Item.objects.get(nombre="Item1")
        self.assertEquals(item.nombre, "Item1", "El nombre del item es incorrecto.")
        self.assertEquals(item.fecha, "10/10/2010", "La fecha del item es incorrecta.")
        self.assertEquals(item.observacion, "Item1Obs", "La observacion del item es incorrecta.")
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(item.costo, 10, "El costo del item es incorrecto.")
        cont = 0
        for c in item.tipoItem.campo_extra:
            self.assertEquals(item.campo_extra_valores[cont], "CampoExtra"+str(cont+1),
                              "El campo extra "+str(cont+1)+" del item es incorrecto.")
            cont = cont+1
        self.assertEquals(fase.items.all().filter(id=item.id).exists(), True, "El item no existe en la fase.")

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCrear_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        proyecto.tipoItem.add(tipo)
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        fase.items.add(item)
        fase.save()
        proyecto.fases.add(fase)
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.post('/item/itemCrear/', {'nombre': "Item1", 'fecha': "10/10/2010",
                                                         'observacion': "Item1Obs", 'costo': 10,
                                                         'CampoExtra': "CampoExtra1", 'CampoExtra2': "CampoExtra2",
                                                         'proyectoid': proyecto.id,
                                                         'faseid': fase.id, 'tipodeitem_id': tipo.id, 'crear': 1, })

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals(len(fase.items.all()), 1, "El item se agrego erroneamente en la fase.")

        self.assertEquals(response.status_code, 200, "El template no se ha renderizado.")
        self.assertTemplateUsed(response, 'item/itemCrear.html',
                                "El template renderizado debe ser item/itemCrear.html.")

    def test_itemView_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        assign_perm("ver_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemView', kwargs={'itemid': item.id, 'faseid': fase.id,
                                                               'proyectoid': proyecto.id, }))

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'item/item.html',
                                "El template renderizado debe ser item/item.html.")

    def test_itemView_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemView', kwargs={'itemid': str(item.id), 'faseid': str(fase.id),
                                                               'proyectoid': str(proyecto.id), }))

        self.assertEquals(response.status_code, 302,
                          "El usuario cuenta con los permisos necesarios, para esta prueba no deberia.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemModificar_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        assign_perm("modify_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'item/itemModificar.html',
                                "El template renderizado debe ser item/itemModificar.html.")

    def test_itemModificar_GET_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemModificar_GET_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        assign_perm("modify_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemModificar_GET_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre = "Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010", fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        assign_perm("modify_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemModificar_POST_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("change_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.post('/item/modify/', {'nombre': "Item2", 'fecha': "12/10/2010",
                                                         'observacion': "Item2Obs", 'costo': 20,
                                                         'CampoExtra': "CampoExtra2", 'CampoExtra2': "CampoExtra3",
                                                         'proyectoid': proyecto.id,
                                                         'faseid': fase.id, 'itemid': item.id, })

        fase = Fase.objects.get(id=fase.id)
        item = Item.objects.get(id=item.id)
        self.assertEquals(item.nombre, "Item2", "El nombre del item es incorrecto.")
        self.assertEquals(item.fecha, "12/10/2010", "La fecha del item es incorrecta.")
        self.assertEquals(item.observacion, "Item2Obs", "La observacion del item es incorrecta.")
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(item.costo, 20, "El costo del item es incorrecto.")
        cont = 0
        for c in item.tipoItem.campo_extra:
            self.assertEquals(item.campo_extra_valores[cont], "CampoExtra"+str(cont+2),
                              "El campo extra "+str(cont+2)+" del item es incorrecto.")
            cont = cont+1
        self.assertEquals(fase.items.all().filter(id=item.id).exists(), True, "El item no existe en la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemModificar_POST_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="12/10/2010", observacion="Item2Obs",
                                   costo=20, campo_extra_valores=["CampoExtra2", "CampoExtra3", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        assign_perm("change_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.post('/item/modify/', {'nombre': "Item2", 'fecha': "12/10/2010",
                                                         'observacion': "Item2Obs", 'costo': 20,
                                                         'CampoExtra': "CampoExtra2", 'CampoExtra2': "CampoExtra3",
                                                         'proyectoid': proyecto.id,
                                                         'faseid': fase.id, 'itemid': item.id, })

        fase = Fase.objects.get(id=fase.id)
        item = Item.objects.get(id=item.id)
        self.assertEquals(item.nombre, "Item1", "El nombre del item es incorrecto.")
        self.assertEquals(item.fecha, "10/10/2010", "La fecha del item es incorrecta.")
        self.assertEquals(item.observacion, "Item1Obs", "La observacion del item es incorrecta.")
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(item.costo, 10, "El costo del item es incorrecto.")
        cont = 0
        for c in item.tipoItem.campo_extra:
            self.assertEquals(item.campo_extra_valores[cont], "CampoExtra"+str(cont+1),
                              "El campo extra "+str(cont+1)+" del item es incorrecto.")
            cont = cont+1

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCambiarEstado_pendiente_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("establecer_itemPendienteAprob", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "pendiente de aprobacion", })

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "pendiente de aprobacion", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'item/item.html',
                                "El template renderizado debe ser item/item.html.")

    def test_itemCambiarEstado_pendiente_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "pendiente de aprobacion"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 302,
                          "El usuario cuenta con los permisos necesarios, para esta prueba no deberia.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCambiarEstado_aprobado_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("aprove_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "aprobado"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "aprobado", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'item/item.html',
                                "El template renderizado debe ser item/item.html.")

    def test_itemCambiarEstado_aprobado_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "aprobado"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 302,
                          "El usuario cuenta con los permisos necesarios, para esta prueba no deberia.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemCambiarEstado_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("aprove_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "aprobado"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/fase/faseVer/faseid=' + str(fase.id) + 'proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemDeshabilitar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("unable_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/unable/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "deshabilitado", "El estado del item es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemDeshabilitar_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/unable/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemDeshabilitar_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("unable_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/unable/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "aprobado", "El estado del item es incorrecto.")
        self.assertEquals(response.status_code, 200, "EL template no ha sido renderizado.")
        self.assertTemplateUsed(response, 'item/gestionItem.html',
                                "El template renderizado debe ser item/gestionItem.html.")


    def test_itemDeshabilitar_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "cancelado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ])
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        assign_perm("unable_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/unable/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_faseView_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        assign_perm("view_fase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('faseView', kwargs={'faseid': fase.id, 'proyectoid': proyecto.id, }))

        self.assertEquals(response.status_code, 200, "EL template no ha sido renderizado.")
        self.assertTemplateUsed(response, 'fase/fase.html',
                                "El template renderizado debe ser fase/fase.html.")

    def test_faseView_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('faseView', kwargs={'faseid': fase.id, 'proyectoid': proyecto.id, }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_proyectoInicializar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.estado = "pendiente"
        proyecto.save()
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoInicializar/', {'proyectoid': proyecto.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "inicializado", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

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
        response = self.client.get('/proyecto/proyectoInicializar/', {'proyectoid': proyecto.id, })

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
        response = self.client.get('/proyecto/proyectoInicializar/', {'proyectoid': proyecto.id, })

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
        response = self.client.get('/proyecto/proyectoInicializar/', {'proyectoid': proyecto.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_proyectoCancelar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)

        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get('/proyecto/proyectoCancelar/', {'proyectoid': proyecto.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "cancelado", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/home/',
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
        response = self.client.get('/proyecto/proyectoCancelar/', {'proyectoid': proyecto.id, })

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "pendiente", "El estado del proyecto es incorrecto.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a la vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")
'''