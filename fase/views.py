from django.shortcuts import render, redirect
from proyecto.models import Proyecto, Fase, TipodeItem, Item
from proyecto.views import proyectoView, faseView


def gestionFase(request):
    """
      **gestionFase:**
        Vista utilizada para visualizar Gestion de la Fase.
        Solicita que el usuario que realiza el request cuente
        con el permiso para ver la fase correspondiente
        y que (indirectamente) haya iniciado sesion
    """

    """ID del Proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto para el acceso a Gestion de Fase"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """ID de Fase"""
    faseid = request.GET.get('faseid')
    """Fase correspondiente"""
    fase = Fase.objects.get(id=faseid)
    """
    Verificar que el usuario que realiza el request cuente con el 
    permiso para ver la fase correspondiente o bien,
    sea el gerente del proyecto.
    """
    if not (request.user.has_perm("view_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verifica que el estado del proyecto sea distinto a pedniente."""
    if proyecto.estado != "pendiente":
        """Si el estado del proyecto es pendiente, no accede a gestion de fase y redirige a la vista del proyecto."""
        return redirect('proyectoView', id=proyectoid)

    """Template a renderizar: gestionFase.html con parametro -> proyectoid, faseid"""
    return render(request, 'fase/gestionFase.html', {'proyectoid': proyectoid, 'faseid': faseid, })

def faseCrear(request):
    """
       **faseCrear:**
        Vista utilizada para crear fases.
        Solicita que el usuario que realiza el
        request sea el gerente del proyecto
         y que (indirectamente) haya iniciado sesion.
    """
    """POST request, captura los datos ingresados por el usuario para crear la fase."""
    if request.method == 'POST':
        """ID del proyecto"""
        proyectoid = request.POST.get('proyectoid')
        """Proyecto en el cual crear la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar que el estado del proyecto sea distinto a pendiente."""
        if proyecto.estado != "pendiente":
            """
            Si el estado del proyecto es pendiente,
            no accede a gestion de fase y redirige
            a la vista del proyecto.
             """
            return redirect('proyectoView', id=proyectoid)

        """Nombre de la Fase"""
        nombre = request.POST.get('nombre')
        """
        Verificar que no exista otra fase en el 
        proyecto con el mismo nombre, excluyendo a
        las fases deshabilitadas.
         """
        if proyecto.fases.filter(nombre=nombre).exclude(estado="deshabilitada").exists():
            """
            Si existe otra fase con el mismo nombre en el proyecto, 
            volver a mostrar el formulario de creacion
            de fases, emitiendo un mensaje de error.
            Template a renderizar: faseCrear.html con 
            parametros -> proyectoid y mensaje de error.
            """
            return render(request, 'fase/faseCrear.html', {'proyectoid': proyectoid,
                                                           'mensaje': "Lo sentimos, el nombre ya pertenece a otra fase"
                                                                      "del proyecto", })

        """Descripcion de la Fase"""
        descripcion = request.POST.get('descripcion')
        """Creacion de la fase con los datos proveidos por el usuario."""
        fase = Fase.objects.create(nombre=nombre, descripcion=descripcion, estado="abierta")
        """Agregar la fase creada al proyecto correspondiente."""
        proyecto.fases.add(fase)
        """Guardar"""
        fase.save()
        """Redirigir a la vista del proyecto en el cual la fase fue creada."""
        return redirect('proyectoView', id=proyectoid)

    else:
        """
        GET request, muestra el template 
        correspondiente para crear la fase.
        """
        """ID del proyecto correspondiente."""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto en el cual crear la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)

        """Verificar que el usuario sea el gerente del proyecto."""
        if not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        """Template a renderizar: faseCrear.html con parametro -> proyectoid"""
        return render(request, 'fase/faseCrear.html', {'proyectoid': proyectoid, })


def faseModificar(request):
    """
       **faseModificar:**
        Vista utilizada para visualizar Modificar Fases.
        Solicita que el usuario que realiza el request
        cuente con los permisos para modificar fases o
         de gerente del proyecto y que
         (indirectamente) haya iniciado sesion.
    """
    """GET request, muestra el template correspondiente para modificar la fase."""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        print(proyectoid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de la fase correspondiente"""
        faseid = request.GET.get('faseid')

        """Fase a modificar"""
        fase = Fase.objects.get(id=faseid)
        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("change_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        """Verificar que el estado del proyecto sea distinto a pendiente."""
        if proyecto.estado != "pendiente":
            """
            Si el estado del proyecto es pendiente,
             no accede al formulario de modificacion de fase 
             y redirige a gestion de Fase.
             """
            return render(request, 'fase/gestionFase.html', {'proyectoid': proyectoid, 'faseid': faseid,
                                                             'mensaje': "No se puede modificar la fase, el proyecto"
                                                                        " no se encuentra en estado pendiente."})
        print(fase.estado)
        if fase.estado == "deshabilitada":
            return redirect('proyectoFase', id=proyectoid)
        """Template a renderizar: faseModificar con parametro -> fase, proyectoid"""
        return render(request, 'fase/faseModificar.html', {'fase': fase, 'proyecto': proyecto, })

    """POST request, captura la informacion para actualizar los datos de la fase."""

    """Nuevo nombre de fase."""
    nombre = request.POST.get('nombre')
    """Nueva descripcion de fase"""
    descripcion = request.POST.get('descripcion')
    """ID del proyecto en el que se encuentra la fase."""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto en el que se enuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """ID de la fase a modificar"""
    faseid = request.POST.get('faseid')
    """Fase a modificar"""
    fase = Fase.objects.get(id=faseid)

    """
    Verificar que no exista otra fase en el proyecto 
    con el mismo nombre, excluyendo a
    las fases deshabilitadas y a la fase correspondiente a modificar, 
    en caso de que el nombre se mantenga.
    """
    if proyecto.fases.filter(nombre=nombre).exclude(estado="deshabilitada").exclude(id=faseid).exists():
        """
        Si existe otra fase con el mismo nombre en el proyecto, 
        volver a mostrar el formulario de modificacion
        de fases, emitiendo un mensaje de error.
        Template a renderizar: faseModificar.html 
        con parametros -> proyectoid y mensaje de error.
        """
        return render(request, 'fase/faseModificar.html', {'fase': fase, 'proyectoid': proyectoid,
                                                           'mensaje': "Lo sentimos, el nombre ya pertenece a otra fase"
                                                                      "del proyecto.", })

    """Actualizar nombre de fase"""
    fase.nombre = nombre
    """Actualizar descripcion de fase"""
    fase.descripcion = descripcion
    """Guardar"""
    fase.save()

    """Template a renderizar: gestionFase con parametro -> proyectoid, faseid"""
    return render(request, 'fase/fase.html', {'proyecto': proyecto, 'fase': fase, })


def faseDeshabilitar(request):
    """
           **faseDeshabilitar:**
            Vista utilizada para Deshabilitar Fases.
            Solicita que el usuario que realiza el request
            cuente con los permisos para deshabilitar fases o
             de gerente del proyecto y que
             (indirectamente) haya iniciado sesion.
    """
    """ID del proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto en el cual se encuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """ID de fase."""
    faseid = request.GET.get('faseid')
    """Fase a deshabilitar."""
    fase = Fase.objects.get(id=faseid)

    """Verificar que el usuario cuente con los permisos necesarios."""
    if not (request.user.has_perm("delete_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verificar que el estado del proyecto sea distinto a pendiente."""
    if proyecto.estado != "pendiente":
        """
        Si el estado del proyecto es pendiente,
        no accede al formulario de modificacion de fase y 
        redirige a gestion de Fase.
        """
        return render(request, 'fase/gestionFase.html', {'proyectoid': proyectoid, 'faseid': faseid,
                                                         'mensaje': "No se puede deshabilitar la fase,"
                                                                    " el proyecto no se encuentra en estado pendiente."})

    """Establecer el estado de la fase como deshabilitada."""
    fase.estado = "deshabilitada"
    """Guardar"""
    fase.save()
    """Redirigir a la vista del proyecto correspondiente."""
    return redirect('proyectoView', id=proyectoid)


def fasesDeshabilitadas(request):
    proyectoid = request.GET.get('proyectoid')
    """Proyecto en el cual se encuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Fases del proyecto para enviar al template que muestra la informacion"""
    fases = proyecto.fases.all()
    fasesDes = []
    for f in fases:
        if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente", proyecto)) and f.estado == "deshabilitada":
            fasesDes.append(f)

    return render(request, 'fase/fasesDeshabilitadas.html', {'proyecto': proyecto, 'fasesDes': fasesDes, })

def itemCrear(request):
    """
               **itemCrear:**
                Vista utilizada para Crear Items.
                Solicita que el usuario que realiza el request
                cuente con los permisos para crear items o
                 de gerente del proyecto y que
                 (indirectamente) haya iniciado sesion.
    """
    seleccion= None
    """POST request, recibe los datos ingresados por el usuario para la creacion del item."""
    if request.method=="POST":
        """
        Consulta si el post recibido es el de la selección de 
        un Tipo de Item o el post para crear el item correspondiente.
        """
        if 'crear' in request.POST:
            """ID del proyecto en el cual crear el item."""
            proyectoid = request.POST.get('proyectoid')
            """ID de la fase en la cual crear el item."""
            faseid = request.POST.get('faseid')
            """Proyecto en el cual crear el item."""
            proyecto = Proyecto.objects.get(id=proyectoid)
            """Fase en la cual crear el item."""
            fase = Fase.objects.get(id=faseid)
            """Recibe el POST con los datos del formulario para la creacion del Item."""
            dato= request.POST
            """Tipo de item establecido para el item."""
            obj = proyecto.tipoItem.get(id=dato['tipodeitem_id'])
            """
            Verifica que no exista otro item con el mismo nombre en la fase, 
            excluyendo a los items
             deshabilitados.
             """
            if fase.items.filter(nombre=dato['nombre']).exclude(estado="deshabilitado").exists():
                """
                En el caso de que ya exista un item con el mismo nombre
                 en la fase, se vuelve a mostrar el
                formulario de creacion de item con un mensaje de error.
                """
                """Se obtiene todos los tios de item del proyecto."""
                tipos = proyecto.tipoItem.all()
                """
                Template a renderizar: itemCrear.html 
                con parametros -> proyectoid, faseid, tipos de item, 
                seleccion de tipo de item y mensaje de error.
                """
                return render(request, "item/itemCrear.html",
                              {'proyectoid': proyectoid, 'faseid': faseid, 'tipos': tipos, 'select': seleccion,
                               'mensaje': "Lo sentimos, el nombre ya pertenece a otro item en la fase."})

            """Creacion del item con los datos proveidos por el usuario."""
            item = Item.objects.create(tipoItem=obj, nombre=dato['nombre'], fecha=dato['fecha'],
                                       observacion=dato['observacion'], costo=dato['costo'])

            """Estado del item predefinido en la creacion igual a en desarrollo."""
            item.estado = "en desarrollo"
            """Almacenar la informacion de cada campo extra proveido por el usuario."""
            for c in obj.campo_extra:
                item.campo_extra_valores.append(dato[c])

            """Guardar."""
            item.save()
            """Agregar item a fase."""
            fase.items.add(item)
            """Redirigir a la vista de la fase correspondiente."""
            return redirect('proyectoView',id=proyectoid)
        else:
            """POST para seleccionar tipo de item"""
            """ID del proyecto correspondiente."""
            proyectoid = request.POST.get('proyectoid')
            """ID de fase correspondiente."""
            faseid = request.POST.get('faseid')
            """Proyeto en el cual crear el item."""
            proyecto = Proyecto.objects.get(id=proyectoid)
            """
            Se asigna a la variable "tipos" todos los Tipos de Item 
            con los que cuenta el proyecto en el cual se encuentra el usuario
            """
            tipos = proyecto.tipoItem.all()
            """Guarda en la variable seleccion el tipo de Item seleccionado por el usuario."""
            seleccion = TipodeItem.objects.get(id=request.POST['tipo'])

            """
            Template a renderizar: itemCrear.html 
            con parametros -> proyectoid, 
            faseid, tipos de item, 
            seleccion de tipo de item.
            """
            return render(request, "item/itemCrear.html",
                          {'proyectoid': proyectoid, 'faseid': faseid, 'tipos': tipos, 'select': seleccion})

    """GET request, muestra el template correspondiente para la creacion de items."""
    """ID del proyecto correspondiente."""
    proyectoid = request.GET.get('proyectoid')
    """ID de fase correspondiente."""
    faseid = request.GET.get('faseid')
    """Proyecto en el cual crear el item."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Fase en la cual crear el item."""
    fase = Fase.objects.get(id=faseid)
    """
    Verificar que el usuario cuente 
    con los permisos necesarios.
    """
    if not (request.user.has_perm("create_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verificar que el estado del proyecto sea inicializado."""
    if proyecto.estado != "inicializado":
        """En caso contrario, no permite la creacion de items y redirige a la vista de fase."""
        return redirect('faseView', faseid=faseid, proyectoid=proyectoid)

    """
    Se asigna a la variable "tipos" todos los Tipos de Item
    con los que cuenta el proyecto en el 
    cual se encuentra el usuario
    """
    tipos = proyecto.tipoItem.all()

    """
    Template a renderizar: itemCrear.html c
    on parametros -> proyectoid, faseid, tipos de item, 
    seleccion de tipo de item.
    """
    return render(request, "item/itemCrear.html", {'proyectoid': proyectoid, 'faseid': faseid,
                                                   'tipos': tipos, 'select': seleccion})


def itemView(request, itemid, faseid, proyectoid):
    """
       **itemView:**
        Vista utilizada para visualizar items.
        Solicita que el usuario que realiza el request
        cuente con el permiso para ver items en la fase
        correspondiente, o bien, sea el gerente del
        proyecto. Recibe el id de la fase y del proyecto
         en el que se encuentra ademas del id del item a ver.
        Tambien solicita que (indirectamente) el usuario
        haya iniciado sesion.
     """
    """Fase en el cual se encuentra el item."""
    fase = Fase.objects.get(id=faseid)
    """Proyecto en el cual se encuentra el item."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Item a visualizar."""
    item = Item.objects.get(id=itemid)
    """Verificar que el usuario cuente con los permisos necesarios."""
    if not (request.user.has_perm("ver_item", fase)) and not(request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """
    Template a renderizar: item.html con parametros -> faseid, 
    proyectoid, item, proyecto, campos extra de item,
    permiso para establecer item como pendiente de aprobacion, 
    permiso para establecer item como parobado y choices
    con los distintos estados del item.
    """
    return render(request, 'item/item.html',
                        {'faseid': faseid, 'proyectoid': proyectoid, 'item': item, 'proyecto': proyecto,
                                    'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),
                                    'pendientePermiso': request.user.has_perm("establecer_itemPendienteAprob",fase),
                                    'aprobadoPermiso': request.user.has_perm("aprove_item", fase),
                                    'choices': ['en desarrollo', 'pendiente de aprobacion', 'aprobado', ], })



def gestionItem(request):
    """
      **gestionItem:**
        Vista utilizada para visualizar Gestion del Item.
        Solicita que el usuario que realiza el request cuente
        con los permisos necesarios para ver el item correspondiente,
        o bien, los de gerente del proyecto y que (indirectamente)
         haya iniciado sesion.
    """

    """ID del Proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto para el acceso a Gestion de Item"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """ID de fase."""
    faseid = request.GET.get('faseid')
    """Fase correspindiente."""
    fase = Fase.objects.get(id=faseid)
    """Verificar que el usuario cuente con los permisos necesarios."""
    if not (request.user.has_perm("ver_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verificar que el estado del proyecto sea inicializado."""
    if proyecto.estado != "inicializado":
        """
        En caso contrario, no permite la acceder a 
        gestion de item y redirige a la vista de fase.
        """
        return redirect('faseView', faseid=faseid, proyectoid=proyectoid)

    """ID de item correspondiente."""
    itemid=request.GET.get('itemid')
    """
    Template a renderizar: gestionItem.html 
    con parametro -> proyectoid, faseid, itemid
    """
    return render(request, 'item/gestionItem.html', {'proyectoid': proyectoid, 'faseid': faseid, 'itemid': itemid, })


def itemModificar(request):
    """
           **itemModificar:**
            Vista utilizada para modificar Item.
            Solicita que el usuario que realiza el request
            cuente con los permisos para modificar items de
             fase, o bien, de gerente del proyecto
            y que (indirectamente) haya iniciado sesion.
        """
    """GET request, muestra el template correspondiente para modificar el item"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto en el cual se encuentra el item"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase"""
        faseid = request.GET.get('faseid')
        """ID del item"""
        itemid = request.GET.get('itemid')
        """Item a modificar."""
        item = Item.objects.get(id=itemid)
        """Fase en la cual se encuentra el iten a modificar."""
        fase = Fase.objects.get(id=faseid)
        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("modify_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        """Verificar que el estado del proyecto sea inicializado."""
        if proyecto.estado != "inicializado":
            """En caso contrario, no permite modificar el item y redirige a la vista de fase."""
            return redirect('proyectoView', id=proyectoid)

        """
        Verificar que el estado del item se 
        encuentre en desarrollo, permitiendo modificaciones.
        """
        if item.estado == "pendiente de aprobacion" or item.estado == "aprobado":
            mensaje = "El estado actual del item no permite la modificacion del mismo."
            """
            En caso contrario, no permite la modificacion del item y 
            vuelve a gestion de Item con mensaje de error.
            Template a renderizar: gestionItem.html con 
            parametros -> proyectoid, faseid, itemid y mensaje de error.
            """
            return redirect('proyectoView',id=proyectoid)


        """
        Template a renderizar: itemModificar 
        con parametros -> proyectoid, faseid, item y campos extra.
        """
        return render(request, 'item/itemModificar.html',
                      {'faseid': faseid, 'proyectoid': proyectoid, 'item': item,
                       'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores), })

    """POST request, captura la informacion para actualizar los datos del item"""
    """Captura toda la informacion proveida por el usuario."""
    dato = request.POST
    """Item a modificar."""
    item = Item.objects.get(id=dato['itemid'])
    """Fase en el que sed encuentra el item."""
    fase = Fase.objects.get(id=dato['faseid'])
    """
    Verifica que no exista otro item con el 
    mismo nombre en la fase, excluyendo a los items
    deshabilitados y al item a modificar en
    caso de que el nombre se mantenga.
    """
    if fase.items.filter(nombre=dato['nombre']).exclude(estado="deshabilitado").exclude(id=dato['itemid']).exists():
        """
        En el caso de que ya exista un item con el 
        mismo nombre en la fase, se vuelve a mostrar el
        formulario de modificacion de item con un mensaje de error.
        """
        """
        Template a renderizar: itemModificar con 
        parametros -> proyectoid, faseid, item, campos extra
        y mensaje de error.
        """
        return redirect('proyectoView', id=dato['proyectoid'])

    """Actualizar nombre del item."""
    item.nombre = dato['nombre']
    """Actualizar fecha del item."""
    item.fecha = dato['fecha']
    """Actualizar observacion del item."""
    item.observacion = dato['observacion']
    """Actualizar costo del item."""
    item.costo = dato['costo']

    cont = 0
    """Actualizar campos extra del item."""
    for c in item.tipoItem.campo_extra:
        item.campo_extra_valores[cont]=dato[c]
        cont = cont+1

    """Guardar"""
    item.save()

    """
    Template a renderizar: gestionItem con 
    parametro -> proyectoid, faseid, itemid
    """
    return redirect('proyectoView',id=dato['proyectoid'])


def itemCambiarEstado(request):
    """
               **itemCambiarEstado:**
                Vista utilizada para modificar el estado del Item.
                Solicita que el usuario que realiza el request
                cuente con los permisos para asignar el estado deseado
                a los item de fase, o bien, los de gerente del proyecto
                y que (indirectamente) haya iniciado sesion.
    """
    """Capturar datos proveidos por el usuario."""
    dato = request.GET
    """Fase en el que se encuentra el item."""
    fase = Fase.objects.get(id=dato['faseid'])
    """Proyecto en e que se encuentra el item."""
    proyecto = Proyecto.objects.get(id=dato['proyectoid'])
    """Item al cual modificar el estado."""
    item = Item.objects.get(id=dato['itemid'])

    mensaje = ""
    """Verificar que el estado no sea el mismo que ya poseia."""
    if item.estado != dato['estado']:
        """Si el nuevo estado es pendiente de aprobacion."""
        if dato['estado'] == "pendiente de aprobacion":
            """Verificar que el usuario cuente con los permisos para asignar ese estado."""
            if not (request.user.has_perm("establecer_itemPendienteAprob", fase)) and not (
                    request.user.has_perm("is_gerente", proyecto)):
                """Al no contar con los permisos, niega el acceso, redirigiendo."""
                return redirect('/permissionError/')

        """Si el nuevo estado es aprobado."""
        if dato['estado'] == "aprobado":
            """Verificar que el usuario cuente con los permisos para asignar ese estado."""
            if not (request.user.has_perm("aprove_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
                """Al no contar con los permisos, niega el acceso, redirigiendo."""
                return redirect('/permissionError/')

        """Verificar que el estado del proyecto sea inicializado."""
        if proyecto.estado != "inicializado":
            """En caso contrario, no permite cambiar el estado del item y redirige a la vista de fase."""
            return redirect('faseView', faseid=dato['faseid'], proyectoid=dato['proyectoid'])

        mensaje = "Estado actualizado correctamente."
        """Acgtualiza estado del item."""
        item.estado = dato['estado']
        """Guardar."""
        item.save()


    """
    Template a renderizar: item.html 
    con parametros -> faseid, proyectoid, item, proyecto, campos extra de item,
    permiso para establecer item como pendiente de aprobacion, 
    permiso para establecer item como parobado, choices
    con los distintos estados del item y el mensaje correspondiente.
    """
    return render(request, 'item/item.html',
                  {'faseid': dato['faseid'], 'proyectoid': dato['proyectoid'], 'item': item,
                   'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),
                   'pendientePermiso': request.user.has_perm("establecer_itemPendienteAprob", fase),
                   'aprobadoPermiso': request.user.has_perm("aprove_item", fase),
                   'choices': ['en desarrollo', 'pendiente de aprobacion', 'aprobado', ],
                   'mensaje': mensaje, })


def itemDeshabilitar(request):
    """
        **itemDeshabilitar:**
         Vista utilizada para deshabilitar Item.
          Solicita que el usuario que realiza el request
           cuente con los permisos para deshabilitar los
            items de fase, o bien, los permisos de gerente del proyecto
            y que (indirectamente) haya iniciado sesion.
    """
    """ID del proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto en el cual se encuentra el item."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """ID de fase."""
    faseid = request.GET.get('faseid')
    """Fase en la cual se encuentra el item."""
    fase = Fase.objects.get(id=faseid)
    """ID de item."""
    itemid = request.GET.get('itemid')
    """Item a deshabilitar."""
    item = Item.objects.get(id=itemid)
    """Verificar que el usuario cuente con los permisos necesarios."""
    if not (request.user.has_perm("unable_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verificar que el estado del proyecto sea inicializado."""
    if proyecto.estado != "inicializado":
        """En caso contrario, no permite deshabilitar el item y redirige a la vista de fase."""
        return redirect('proyectoView',id=proyectoid)

    """Verificar que el estado del item sea en desarrollo."""
    if item.estado == "pendiente de aprobacion" or item.estado == "aprobado":
        mensaje = "El estado actual del item no permite la deshabilitacion del mismo."
        """
        En caso contrario niega la deshabilitacion del mismo y 
        vuelve a gestion de item mostrando un mensaje de error.
        Template a renderizar gestionItem.html con parametros -> proyectoid, faseid, itemid y mensaje de error.
        """
        return render(request, 'item/gestionItem.html',
                      {'proyectoid': proyectoid, 'faseid': faseid, 'itemid': itemid, 'mensaje': mensaje, })

    """Establece estado de item como deshabilitado."""
    item.estado = "deshabilitado"
    """Guardar."""
    item.save()
    """Redirige a la vista de la fase correspondiente."""
    return redirect('proyectoView', id=proyectoid)










