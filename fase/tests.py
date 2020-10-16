from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from proyecto.models import Proyecto, Fase, FaseUser, Rol, TipodeItem, Item, LineaBase, Relacion, RoturaLineaBase, RoturaLineaBaseComprometida
from datetime import datetime
from django.db import transaction
import reversion
from reversion.models import Revision, Version


class TestViews(TestCase):

    longMessage = True
    def setUp(self):

        client = Client()

    def test_proyectoFinalizar_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="cerrada")
        proyecto.fases.add(fase)
        proyecto.save()
        assign_perm("is_gerente", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoFinalizar', kwargs={'proyectoid': proyecto.id,  }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "finalizado", """No se actualizo el estado del proyecto""")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                         '/proyecto/proyectoVer/proyectoid=' + str(proyecto.id) + '/',
                         status_code=302, fetch_redirect_response=False,
                         msg_prefix="No se ha redirigido a la vista esperada.")


    def test_proyectoFinalizar_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="cerrada")
        proyecto.fases.add(fase)
        proyecto.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('ProyectoFinalizar', kwargs={'proyectoid': proyecto.id,  }))

        proyecto = Proyecto.objects.get(id=proyecto.id)
        self.assertEquals(proyecto.estado, "inicializado", """Se actualizo el estado del proyecto""")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemTrazabilidad_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)
        assign_perm("obtener_trazabilidadItem", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/trazabilidad/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemIdTrazabilidad': item.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'item/TrazabilidadItem.html',
                                "El template renderizado debe ser item/TrazabilidadItem.html")

    def test_itemTrazabilidad_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/trazabilidad/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemIdCalculo': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_RechazarRoturaLineaBaseComprometida_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1, dos_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('RechazarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "rota", "No se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "en revision", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.comprometida_estado, "aprobado", "No se ha modificado el estado de la solicitud.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_RechazarRoturaLineaBaseComprometida_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1, dos_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_RechazarRoturaLineaBaseComprometida_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.comprometida_estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")


    def test_RechazarRoturaLineaBaseComprometida_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1, dos_voto_comprometida=1)

        solicitud.registrados_votos_comprometida.add(user)
        solicitud.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.comprometida_estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_AprobarRoturaLineaBaseComprometida_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1, dos_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('AprobarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "rota", "No se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "en revision", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.comprometida_estado, "aprobado", "No se ha modificado el estado de la solicitud.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")

    def test_AprobarRoturaLineaBaseComprometida_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1, dos_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_AprobarRoturaLineaBaseComprometida_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create(uno_voto_comprometida=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.comprometida_estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionLineaBase.html")


    def test_AprobarRoturaLineaBaseComprometida_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1)

        solicitud.votos_registrados.add(user)
        solicitud.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")

    def test_votacionRoturaLineaBaseComprometida_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create()
        lineaBase.roturaLineaBaseComprometida.add(solicitud)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('votacionRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          }))
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseRoturaLineaBaseVotarComprometida.html',
                                "El template renderizado debe ser fase/faseRoturaLineaBaseVotarComprometida.html")

    def test_votacionRoturaLineaBaseComprometida_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        solicitud = RoturaLineaBaseComprometida.objects.create()

        lineaBase.roturaLineaBaseComprometida.add(solicitud)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('votacionRoturaLineaBaseComprometida', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                       'lineaBaseid': lineaBase.id,
                                                        }))
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_RechazarRoturaLineaBase_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1, voto_dos=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('RechazarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "rota", "No se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "en revision", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "aprobado", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")

    def test_RechazarRoturaLineaBase_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1, voto_dos=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_RechazarRoturaLineaBase_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")


    def test_RechazarRoturaLineaBase_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1)

        solicitud.votos_registrados.add(user)
        solicitud.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('RechazarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")

    def test_AprobarRoturaLineaBase_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1, voto_dos=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('AprobarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "rota", "No se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "en revision", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "aprobado", "No se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")

    def test_AprobarRoturaLineaBase_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1, voto_dos=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_AprobarRoturaLineaBase_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1)

        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")


    def test_AprobarRoturaLineaBase_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now(), voto_uno=1)

        solicitud.votos_registrados.add(user)
        solicitud.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        lineaBase.items.add(item)
        lineaBase.save()
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('AprobarRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id,
                                                      'solicituid': solicitud.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        item = Item.objects.get(id=item.id)
        solicitud = RoturaLineaBase.objects.get(id=solicitud.id)
        self.assertEquals(lineaBase.estado, "cerrada", "Se ha modificado el estado de la linea base.")
        self.assertEquals(item.estado, "aprobado", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(solicitud.estado, "pendiente", "Se ha modificado el estado del item de prueba.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")


    def test_votacionRoturaLineaBase_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now())
        assign_perm("break_lineaBase", user, proyecto)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('votacionRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'solicituid': solicitud.id, }))
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseRoturaLineaBaseVotar.html',
                                "El template renderizado debe ser fase/faseRoturaLineaBaseVotar.html")

    def test_votacionRoturaLineaBase_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        solicitud = RoturaLineaBase.objects.create(solicitante=user, descripcion_solicitud="Descripcion",
                                                   fecha=datetime.now())

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('votacionRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                       'lineaBaseid': lineaBase.id,
                                                       'solicituid': solicitud.id, }))
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_formRoturaLineaBase_GET_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        assign_perm("solicitar_roturaLineaBase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('formRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id, }))
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/FormularioRoturaLineaBase.html',
                                "El template renderizado debe ser fase/FormularioRoturaLineaBase.html")

    def test_formRoturaLineaBase_GET_FAIL(self):
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
        response = self.client.get(
            reverse('formRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                      'lineaBaseid': lineaBase.id, }))
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_formRoturaLineaBase_POST(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()

        self.client.login(username='user', password='user')

        path = '/fase/roturaLineaBase/form/proyectoid=' + str(proyecto.id) + '/faseid=' + str(fase.id) + '/lineaBaseid=' + str(lineaBase.id) + '/'
        response = self.client.post(path, {'descripcion': "Descripcion", 'items': [item.id], })

        self.assertEquals(True,
        RoturaLineaBase.objects.filter(solicitante=user).exists(),
                          "No se ha creado la solicitud.")
        solicitud = RoturaLineaBase.objects.get(solicitante=user)
        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals(True, solicitud in lineaBase.roturaslineasBase.all(), "No se ha agregado la solicitud a la linea base.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/roturaLineaBase/listado/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
                                 fase.id) + '/' + 'lineaBaseid=' + str(lineaBase.id) + '/' + 'mensaje=' + 'Su%20solicitud%20se%20envi%C3%B3%20correctamente.%20El%20Comit%C3%A9%20de%20Control%20de%20Cambios%20decidir%C3%A1%20romper%20o%20no%20la%20L%C3%ADnea%20Base./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_gestionRoturaLineaBase_OK(self):
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
        response = self.client.get(reverse('gestionRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                            'mensaje': " "}))
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseGestionRoturaLineaBase.html',
                                "El template renderizado debe ser fase/faseGestionRoturaLineaBase.html")

    def test_gestionRoturaLineaBase_FAIL(self):
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
        response = self.client.get(reverse('gestionRoturaLineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id,
                                                                          'mensaje': " "}))
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemCalculoImpacto_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)
        assign_perm("obtener_calculoImpacto", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/calculoImpacto/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemIdCalculo': item.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'item/itemCalculoImpacto.html',
                                "El template renderizado debe ser item/itemCalculoImpacto.html")

    def test_itemCalculoImpacto_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.save()
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/calculoImpacto/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemIdCalculo': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")



    def test_itemRelacionar_POST_FAIL(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item2.estado = "aprobado"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item2.estado = "aprobado"
        item2.save()
        fase.items.add(item)
        fase.items.add(item2)
        fase.items.add(item3)
        fase.save()
        assign_perm("relacionar_item", user, fase)

        Relacion.objects.create(tipo="padre", item_from=item, item_to=item2,
                                fase_item_to=fase)
        Relacion.objects.create(tipo="padre", item_from=item2, item_to=item3,
                                fase_item_to=fase)

        self.client.login(username='user', password='user')
        response = self.client.post('/item/addRelacion/', {'itemIdActual': item.id, 'itemIdRelacion': item3.id,
                                                           'siguiente': 'no',
                                                           'proyectoid': proyecto.id,
                                                           'faseid': fase.id, 'itemid': item.id, })

        item = Item.objects.get(id=item.id)
        item3 = Item.objects.get(id=item3.id)
        self.assertEquals(item3 in item.relaciones.all(), False, "Se ha establecido la relacion en item origen.")
        self.assertEquals(item in item3.relaciones.all(), False, "Se ha establecido la relacion en item destino.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'Error!%20No%20se%20puede%20relacionar%20porque%20genera%20un%20ciclo.' + '/',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "en desarrollo"
        item.save()
        assign_perm("relacionar_item", user, fase)
        vacio = ' '
        self.client.login(username='user', password='user')
        response = self.client.get('/item/addRelacion/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRemoveRelaciones_FAIL1(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        fase_dos = Fase.objects.create(nombre="Fase2", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        proyecto.fases.add(fase_dos)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase_dos.lineasBase.add(lineaBase)
        fase_dos.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item4.estado = "en linea base"
        item4.save()
        fase_dos.items.add(item)
        fase_dos.save()
        fase_dos.items.add(item2)
        fase_dos.save()
        fase_dos.items.add(item3)
        fase_dos.save()
        fase_dos.items.add(item4)
        fase_dos.save()

        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item4, item_to=item2, tipo="padre", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item2, item_to=item4, tipo="hijo", fase_item_to=fase_dos)
        assign_perm("relacionar_item", user, fase_dos)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase_dos.id,
                                                                            'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), True, "Se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), True, "Se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase_dos.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'Error.%20No%20se%20pudo%20remover%20la%20relaci%C3%B3n.' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRemoveRelaciones_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        fase_dos = Fase.objects.create(nombre="Fase2", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        proyecto.fases.add(fase_dos)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase_dos.lineasBase.add(lineaBase)
        fase_dos.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item4.estado = "en linea base"
        item4.save()
        fase_dos.items.add(item)
        fase_dos.save()
        fase_dos.items.add(item2)
        fase_dos.save()
        fase_dos.items.add(item3)
        fase_dos.save()
        fase_dos.items.add(item4)
        fase_dos.save()

        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item3, item_to=item, tipo="padre", fase_item_to=fase_dos)
        Relacion.objects.create(item_from=item, item_to=item3, tipo="hijo", fase_item_to=fase_dos)
        assign_perm("relacionar_item", user, fase_dos)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase_dos.id,
                                                                            'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), True, "Se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), True, "Se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase_dos.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'Error.%20No%20se%20pudo%20remover%20la%20relaci%C3%B3n.' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRemoveRelaciones_OK3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item4.estado = "en linea base"
        item4.save()
        fase.items.add(item)
        fase.save()
        fase.items.add(item2)
        fase.save()
        fase.items.add(item3)
        fase.save()
        fase.items.add(item4)
        fase.save()
        lineaBase.items.add(item3)
        lineaBase.save()

        
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)
        Relacion.objects.create(item_from=item3, item_to=item, tipo="antecesor", fase_item_to=fase)
        Relacion.objects.create(item_from=item, item_to=item3, tipo="sucesor", fase_item_to=fase)
        Relacion.objects.create(item_from=item4, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item4, tipo="hijo", fase_item_to=fase)
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'La%20relaci%C3%B3n%20se%20removi%C3%B3%20correctamente.' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRemoveRelaciones_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item4.estado = "en linea base"
        item4.save()
        fase.items.add(item)
        fase.save()
        fase.items.add(item2)
        fase.save()
        fase.items.add(item3)
        fase.save()
        fase.items.add(item4)
        fase.save()

        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)
        Relacion.objects.create(item_from=item3, item_to=item, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item, item_to=item3, tipo="hijo", fase_item_to=fase)
        Relacion.objects.create(item_from=item4, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item4, tipo="hijo", fase_item_to=fase)
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'La%20relaci%C3%B3n%20se%20removi%C3%B3%20correctamente.' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemRemoveRelaciones_OK2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , )
        item4.estado = "en linea base"
        item4.save()
        fase.items.add(item)
        fase.save()
        fase.items.add(item2)
        fase.save()
        fase.items.add(item3)
        fase.save()
        fase.items.add(item4)
        fase.save()
        lineaBase.items.add(item4)
        lineaBase.save()

        
        Relacion.objects.create(item_from=item, item_to=item2, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item, tipo="hijo", fase_item_to=fase)
        Relacion.objects.create(item_from=item3, item_to=item, tipo="padre", fase_item_to=fase)
        Relacion.objects.create(item_from=item, item_to=item3, tipo="hijo", fase_item_to=fase)
        Relacion.objects.create(item_from=item4, item_to=item2, tipo="antecesor", fase_item_to=fase)
        Relacion.objects.create(item_from=item2, item_to=item4, tipo="sucesor", fase_item_to=fase)
        assign_perm("relacionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'La%20relaci%C3%B3n%20se%20removi%C3%B3%20correctamente.' + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    

  

    def test_cerrarFase_OK(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        fase.items.add(item)
        fase.save()
        lineaBase.items.add(item)
        lineaBase.save()

        assign_perm("cerrar_fase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id, }))

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals("cerrada", fase.estado, "No se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
            proyecto.id) + '/' + 'mensaje=' + 'La%20Fase%20se%20cerro%20correctamente.', status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_cerrarFase_OK2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        fase2 = Fase.objects.create(nombre="Fase2", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        proyecto.fases.add(fase2)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        lineaBase2 = LineaBase.objects.create(nombre="LineaBase2", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        fase2.lineasBase.add(lineaBase2)
        fase2.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item2.estado = "en linea base"
        item2.save()
        fase.items.add(item)
        fase.save()
        fase2.items.add(item2)
        fase2.save()
        lineaBase.items.add(item)
        lineaBase.save()
        lineaBase2.items.add(item2)

        Relacion.objects.create(item_from=item2, item_to=item, tipo="sucesor", fase_item_to=fase)

        assign_perm("cerrar_fase", user, fase2)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase2.id, }))

        fase2 = Fase.objects.get(id=fase2.id)
        self.assertEquals("cerrada", fase2.estado, "No se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase2.id) + '/' + 'proyectoid=' + str(
            proyecto.id) + '/' + 'mensaje=' + 'La%20Fase%20se%20cerro%20correctamente.', status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_cerrarFase_FAIL(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        fase.items.add(item)
        fase.save()
        lineaBase.items.add(item)
        lineaBase.save()


        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id, }))

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals("abierta", fase.estado, "Se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_cerrarFase_FAIL2(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        fase.items.add(item)
        fase.save()
        lineaBase.items.add(item)
        lineaBase.save()

        assign_perm("cerrar_fase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id, }))

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals("abierta", fase.estado, "Se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
            proyecto.id) + '/' + 'mensaje=' + 'Error!%20La%20Fase%20no%20se%20pudo%20cerrar.%20La%20fase%20debe%20poseer%20al%20menos%20un%20item%20relacionado%20con%20la%20fase%20siguiente%20y%20todos%20sus%20%C3%ADtems%20deben%20pertenecer%20a%20una%20L%C3%ADnea%20Base%20Cerrada.' , status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_cerrarFase_FAIL3(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="Proyecto1", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()
        fase.items.add(item)
        fase.save()
        lineaBase.items.add(item)
        lineaBase.save()

        assign_perm("cerrar_fase", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id, }))

        fase = Fase.objects.get(id=fase.id)
        self.assertEquals("abierta", fase.estado, "Se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'Error!%20La%20Fase%20no%20se%20pudo%20cerrar.%20La%20fase%20debe%20poseer%20al%20menos%20un%20item%20relacionado%20con%20la%20fase%20siguiente%20y%20todos%20sus%20%C3%ADtems%20deben%20pertenecer%20a%20una%20L%C3%ADnea%20Base%20Cerrada.' ,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_cerrarFase_FAIL4(self):
        user = User.objects.create(username="user", password="user")
        user.set_password("user")
        user.save()
        proyecto = Proyecto.objects.create(nombre="ProyectoX", descripcion="descripcion", fecha_inicio="10/10/2010",
                                           fecha_fin="10/12/2010", gerente=user)
        proyecto.estado = "inicializado"
        proyecto.save()
        fase = Fase.objects.create(nombre="Fase1", descripcion="Descripcion", estado="abierta")
        fase2 = Fase.objects.create(nombre="Fase2", descripcion="Descripcion", estado="abierta")
        proyecto.fases.add(fase)
        proyecto.save()
        proyecto.fases.add(fase2)
        proyecto.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="cerrada", creador=user)
        lineaBase2 = LineaBase.objects.create(nombre="LineaBase2", estado="cerrada", creador=user)
        fase.lineasBase.add(lineaBase)
        fase.save()
        fase2.lineasBase.add(lineaBase2)
        fase2.save()
        tipo = TipodeItem.objects.create(nombreTipo="Tipo1", descripcion="DTipo1")
        tipo.campo_extra.append("CampoExtra")
        tipo.campo_extra.append("CampoExtra2")
        tipo.save()
        item = Item.objects.create(tipoItem=tipo, nombre="Item1", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item2.estado = "en linea base"
        item2.save()
        fase.items.add(item)
        fase.save()
        fase2.items.add(item2)
        fase2.save()
        lineaBase.items.add(item)
        lineaBase.save()
        lineaBase2.items.add(item2)

        assign_perm("cerrar_fase", user, fase2)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('cerrarFaseView', kwargs={'proyectoid': proyecto.id, 'faseid': fase2.id, }))

        fase2 = Fase.objects.get(id=fase2.id)
        self.assertEquals("abierta", fase2.estado, "Se cerro la fase.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")


    def test_adjuntarArchivo(self):
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
        proyecto.tipoItem.add(tipo)
        proyecto.save()

        self.client.login(username='user', password='user')
        doc = ['BFS.py', 'DFS.py']
        response = self.client.post('/item/itemCrear/', {'nombre': "Item1", 'fecha': "10/10/2010",
                                                         'observacion': "Item1Obs", 'costo': 10,
                                                         'CampoExtra': "CampoExtra1", 'CampoExtra2': "CampoExtra2",
                                                         'proyectoid': proyecto.id,
                                                         'faseid': fase.id, 'tipodeitem_id': tipo.id, 'crear': 1,
                                                         'doc': doc})

        item = Item.objects.get(nombre="Item1")
        cont = 0
        for a in item.archivos:
            self.assertEquals(a[cont], doc[cont],
                              "El archivo " + str(cont + 1) + " del item es incorrecto.")
            cont = cont + 1
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) +'/proyectoid=' + str(proyecto.id) + '/'
                             + 'mensaje=' + 'Item%20creado%20correctamente.' ,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")

    def test_itemReversionar_GET_OK(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()

        assign_perm("ver_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/history/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'item/historialitem.html',
                                "El template renderizado debe ser item/historialitem.html")


    def test_itemReversionar_GET_FAIL1(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()


        self.client.login(username='user', password='user')
        response = self.client.get('/item/history/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    def test_itemReversionar_GET_FAIL2(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/history/',
                                   {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

    @transaction.atomic()
    @reversion.create_revision()
    def test_itemReversionar_POST_OK(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()

        item.refresh_from_db()

        assign_perm("reversionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('itemRev', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                       'itemid': item.id,
                                       'history_date': " "}))

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.nombre, "Item1", "No se reversiono el item")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/item/configurar/itemid=' + str(item.id) + '/faseid=' + str(
            fase.id) + '/proyectoid=' + str(proyecto.id) + '/' ,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido al url esperado.")


    def test_itemReversionar_POST_FAIL(self):
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
        item.estado = "aprobado"
        item.save()


        self.client.login(username='user', password='user')
        response = self.client.get(
            reverse('itemRev', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                       'itemid': item.id,
                                       'history_date': " "}))


        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "aprobado"
        item.save()

        self.client.login(username='user', password='user')
        response = self.client.get('/item/addRelacion/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/permissionError/',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + 'La%20relaci%C3%B3n%20se%20a%C3%B1adio%20correctamente.' + '/',
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
        response = self.client.get(
            reverse('LineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                         'mensaje': " ", }))

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
        response = self.client.get(
            reverse('LineaBase', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                   'mensaje': " ", }))

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],
                                   )
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    )
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
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/gestionLineaBase/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'mensaje=' + 'La%20L%C3%ADnea%20Base%20se%20creo%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user)
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('lineaBaseCerrar', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                      'lineaBaseid': lineaBase.id, }))
        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals("cerrada", lineaBase.estado, "No se ha modificado el estado de la linea base.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/fase/gestionLineaBase/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'mensaje=' + 'La%20L%C3%ADnea%20Base%20se%20cerro%20correctamente./',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "en linea base"
        item.save()
        lineaBase = LineaBase.objects.create(nombre="LineaBase1", estado="abierta", creador=user2)
        lineaBase.items.add(item)
        lineaBase.save()

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('lineaBaseCerrar', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                          'lineaBaseid': lineaBase.id, }))
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
        response = self.client.get(reverse('lineaBaseCerrar', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                      'lineaBaseid': lineaBase.id, }))

        lineaBase = LineaBase.objects.get(id=lineaBase.id)
        self.assertEquals("abierta", lineaBase.estado, "Se ha modificado el estado de la linea base.")
        self.assertEquals(response.status_code, 200, "No se ha renderizado el html.")
        self.assertTemplateUsed(response, 'fase/faseConfigLineaBase.html',
                                "El template renderizado debe ser fase/faseConfigLineaBase.html")





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
        self.assertEquals(response.status_code, 200, "No renderizo html.")
        self.assertTemplateUsed(response, 'proyecto/proyectoListarFases.html',
                                "El template renderizado debe ser proyecto/proyectoListarFases.html.")

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
        self.assertTemplateUsed(response, 'home.html',
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
        self.assertTemplateUsed(response, 'fase/fase.html',
                                "El template renderizado debe ser fase/fase.html.")

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
        self.assertEquals(response.status_code, 200, "No renderizo html.")
        self.assertTemplateUsed(response, 'proyecto/proyectoListarFases.html',
                                "El template renderizado debe ser proyecto/proyectoListarFases.html.")

    def test_faseDeshabilitar_FAIL1(self):
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


    def test_faseDeshabilitar_FAIL2(self):
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
        self.assertTemplateUsed(response, 'home.html',
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
        self.assertRedirects(response, '/fase/faseVer/faseid='+str(fase.id)+'/'+'proyectoid='+str(proyecto.id)+'/',
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

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'Item%20creado%20correctamente.',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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

        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'Error,%20ya%20existe%20un%20%C3%ADtem%20con%20ese%20nombre.' ,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
        item.estado = "aprobado"
        item.save()
        assign_perm("modify_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/modify/', {'proyectoid': proyecto.id, 'faseid': fase.id, 'itemid': item.id, })

        self.assertEquals(response.status_code, 200, "No renderizo el html esperado.")
        self.assertTemplateUsed(response, 'item/itemModificar.html',
                                "El template renderizado debe ser item/item.html.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'El%20%C3%ADtem%20fue%20modificado%20correctamente.' ,
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="12/10/2010", observacion="Item2Obs",
                                   costo=20, campo_extra_valores=["CampoExtra2", "CampoExtra3", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'El%20estado%20del%20%C3%8Dtem%20fue%20actualizado%20correctamente.',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        proyecto.fases.add(fase)
        proyecto.save()
        assign_perm("aprove_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "aprobado"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "aprobado", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response,
                             '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) + '/' + 'proyectoid=' + str(
                                 proyecto.id) + '/' + 'mensaje=' + 'El%20estado%20del%20%C3%8Dtem%20fue%20actualizado%20correctamente.',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
        item.estado = "en desarrollo"
        item.save()
        fase.items.add(item)
        fase.save()
        proyecto.fases.add(fase)
        proyecto.save()
        assign_perm("aprove_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get('/item/itemCambiarEstado/', {'proyectoid': proyecto.id,
                                                                 'faseid': fase.id, 'itemid': item.id,
                                                                 'estado': "aprobado"})

        item = Item.objects.get(id=item.id)
        self.assertEquals(item.estado, "en desarrollo", "El estado del item es incorrecta.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/fase/faseVer/faseid=' + str(fase.id) +'/'+ 'proyectoid=' + str(proyecto.id) + '/',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
        self.assertTemplateUsed(response, 'home.html',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], )
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
