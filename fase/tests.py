from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from proyecto.models import Proyecto, Fase, FaseUser, Rol, TipodeItem, Item, LineaBase, Relacion
from datetime import datetime


class TestViews(TestCase):

    longMessage = True
    def setUp(self):

        client = Client()
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
        item2.estado = "aprobado"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
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
            fase_dos.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
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
            fase_dos.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , _history_date=datetime.now(), )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
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

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , _history_date=datetime.now(), )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
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

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , _history_date=datetime.now(), )
        item2.estado = "en linea base"
        item2.save()
        item3 = Item.objects.create(tipoItem=tipo, nombre="Item3", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
        item3.estado = "en linea base"
        item3.save()
        item4 = Item.objects.create(tipoItem=tipo, nombre="Item4", fecha="10/10/2010", observacion="Item1Obs",
                                    costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    , _history_date=datetime.now(), )
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

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRelacionesRemover', kwargs={'itemid': item.id, 'item_rm': item2.id,
                                                                            'faseid': fase.id, 'proyectoid': proyecto.id, }))

        item = Item.objects.get(id=item.id)
        item2 = Item.objects.get(id=item2.id)
        self.assertEquals(item in item2.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(item2 in item.relaciones.all(), False, "No se elimino la relacion.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/relaciones/ver/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   , _history_date=datetime.now(), )
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
            proyecto.id) + '/', status_code=302, fetch_redirect_response=False,
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , _history_date=datetime.now(), )
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
            proyecto.id) + '/', status_code=302, fetch_redirect_response=False,
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
                                   , _history_date=datetime.now(), )
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
                                   , _history_date=datetime.now(), )
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
        self.assertRedirects(response, '/fase/FaseIniciada/config/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
            fase.id) + '/', status_code=302, fetch_redirect_response=False,
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
                                   , _history_date=datetime.now(), )
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
        self.assertRedirects(response, '/fase/FaseIniciada/config/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
            fase.id) + '/', status_code=302, fetch_redirect_response=False,
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
                                   , _history_date=datetime.now(), )
        item.estado = "en linea base"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                   , _history_date=datetime.now(), )
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
        self.assertRedirects(response,
                             '/fase/FaseIniciada/config/proyectoid=' + str(proyecto.id) + '/' + 'faseid=' + str(
                                 fase2.id) + '/', status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) +'/proyectoid=' + str(proyecto.id) + '/',
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
                                   , _history_date=datetime.now(), )
        item.estado = "en desarrollo"
        item.save()
        item.nombre = "Item2"
        item._history_date = datetime.now()
        item.save()
        fecha = datetime.now()
        for h in item.history.all():
            if h.nombre == "Item1" and h.estado == "en desarrollo":
                fecha = h.history_date


        assign_perm("reversionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRev', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                      'itemid': item.id, 'history_date': fecha, }))

        item = Item.objects.get(id=item.id)
        self.assertEquals("Item1", item.nombre, "No se reversiono el item.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/configurar/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/',
                             status_code=302, fetch_redirect_response=False,
                             msg_prefix="No se ha redirigido a la vista esperada.")

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
                                   , _history_date=datetime.now(), )
        item.estado = "en desarrollo"
        item.save()
        item.nombre = "Item2"
        item._history_date = datetime.now()
        item.save()
        fecha = datetime.now()
        for h in item.history.all():
            if h.nombre == "Item1" and h.estado == "en desarrollo":
                fecha = h.history_date



        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRev', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                      'itemid': item.id, 'history_date': fecha, }))

        item = Item.objects.get(id=item.id)
        self.assertEquals("Item2", item.nombre, "Se reversiono el item.")
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
                                   , _history_date=datetime.now(), )
        item.estado = "aprobado"
        item.save()
        item.nombre = "Item2"
        item._history_date = datetime.now()
        item.save()
        fecha = datetime.now()
        for h in item.history.all():
            if h.nombre == "Item1" and h.estado == "en desarrollo":
                fecha = h.history_date


        assign_perm("reversionar_item", user, fase)

        self.client.login(username='user', password='user')
        response = self.client.get(reverse('itemRev', kwargs={'proyectoid': proyecto.id, 'faseid': fase.id,
                                                                      'itemid': item.id, 'history_date': fecha, }))

        item = Item.objects.get(id=item.id)
        self.assertEquals("Item2", item.nombre, "No se reversiono el item.")
        self.assertEquals(response.status_code, 302, "No se ha redirigido a ninguna vista.")
        self.assertRedirects(response, '/item/configurar/itemid=' + str(item.id) + '/' + 'faseid=' + str(
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/',
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
                                   , _history_date=datetime.now(), )
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
            fase.id) + '/' + 'proyectoid=' + str(proyecto.id) + '/' + 'mensaje=' + '%20' + '/',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],
                                   _history_date=datetime.now(),)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ]
                                    ,_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
        item.estado = "aprobado"
        item.save()
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="10/10/2010", observacion="Item1Obs",
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ],_history_date=datetime.now(),)
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

        self.assertEquals(response.status_code, 302, "No se ha redirigido.")
        self.assertRedirects(response, '/fase/FaseProyectoInicializado/faseid=' + str(fase.id) +'/proyectoid=' + str(proyecto.id) + '/',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())

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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
        item2 = Item.objects.create(tipoItem=tipo, nombre="Item2", fecha="12/10/2010", observacion="Item2Obs",
                                   costo=20, campo_extra_valores=["CampoExtra2", "CampoExtra3", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
        self.assertTemplateUsed(response, 'item/itemModificar.html',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
        self.assertEquals(response.status_code, 200, "El usuario no cuenta con los permisos necesarios.")
        self.assertTemplateUsed(response, 'item/itemModificar.html',
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
                                   costo=10, campo_extra_valores=["CampoExtra1", "CampoExtra2", ], _history_date=datetime.now())
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
