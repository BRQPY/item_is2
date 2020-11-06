from django.shortcuts import render, redirect
from .models import Proyecto, Fase, Rol, FaseUser, TipodeItem, RoturaLineaBase, ActaInforme
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.decorators import permission_required
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
from django.contrib import messages
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from proyecto.tasks import sendEmailViewProyecto
from django.http import HttpResponse
from .reportes import ReporteProyecto


@permission_required('proyecto.add_proyecto', login_url='/permissionError/')
def proyectoCrear(request):
    """
       **proyectoCrear:**
        Vista utilizada para crear proyectos.
        Solicita que el usuario que realiza el
        request cuente con el permiso para crear
        proyectos y que (indirectamente) haya iniciado sesion
    """
    """POST request, captura los datos ingresados por el usuario para crear el proyecto."""
    if request.method == 'POST':
        """Nombre del Proyecto"""
        nombre = request.POST.get('nombre')
        """Descripcion del Proyecto"""
        descripcion = request.POST.get('descripcion')
        """Fecha de Inicio del Proyecto"""
        fechaini = request.POST.get('fechaini')
        """Fecha de finalizacion del Proyecto"""
        fechafin = request.POST.get('fechafin')
        """Id Gerente del Proyecto"""
        gerente = request.POST.get('gerente')
        """Gerente del proyecto"""
        gerente = User.objects.get(id=gerente)

        """Creador del Proyecto"""
        creador = User.objects.get(id=request.user.id)
        """Creacion del Proyecto"""
        proyecto = Proyecto.objects.create(nombre=nombre, descripcion=descripcion, fecha_inicio=fechaini,
                                           fecha_fin=fechafin, gerente=gerente, )
        """Asignar el creador"""
        proyecto.creador = creador
        """Agregar creador a lista de usuarios"""
        proyecto.usuarios.add(creador)
        """Agregar permisos de gerente y permiso para Ver Proyecto al gerente"""
        assign_perm("is_gerente", gerente, proyecto)
        assign_perm("view_proyecto", gerente, proyecto)
        assign_perm("view_proyecto", creador, proyecto)
        """Agregar gerente a lista de usuarios"""
        proyecto.usuarios.add(gerente)
        """Estado de proyecto creado: pendiente"""
        proyecto.estado = "pendiente"
        """Guardar"""
        proyecto.save()
        # Envio de Correo al gerente del proyecto
        mail = gerente.email
        name = gerente.username
        messages.success(request, "Permisos asignados exitosamente!")
        sendEmailViewProyecto.delay(mail, name, proyecto.nombre, 0)
        """
        #Vista a redirigir: homeView"""
        return redirect("/home/")

    else:
        """GET request, envia lista de usuarios para elegir el gerente y muestra el template para la creacion de proyecto."""
        users = User.objects.all()
        usuarios = []
        for user in users:
            """Filtra que el usuario no este deshabilitado."""
            if user.is_active and user.has_perm("perms.view_menu") == True and user.username != "AnonymousUser":
                usuarios.append(user)
        """Template a renderizar: proyectoCrear.html"""
        return render(request, 'proyecto/proyectoCrear.html', {'usuarios': usuarios, })


def proyectoInicializar(request, proyectoid):
    """
           **proyectoInicializar:**
            Vista utilizada para inicializar proyectos.
            Solicita que el usuario que realiza el request
            cuente con los permisos de gerente de
             proyecto y que(indirectamente) haya iniciado
              sesion.
    """

    """Proyecto a inicializar."""
    proyecto = Proyecto.objects.get(id=proyectoid)

    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Verificar que el estado del proyecto sea pendiente."""
    if proyecto.estado != "pendiente":
        mensaje = "No se puede inicializar proyecto. El estado del mismo no lo permite."
        """En caso contrario, no permite inicializar el proyecto y redirige a la vista de proyecto."""
        return redirect('proyectoView', id=proyectoid)

    """Verifica que el proyecto cuente con fases."""
    if list(proyecto.fases.all()) == []:
        mensaje = "No se puede inicializar proyecto. Aun no cuenta con fases."
        """En caso contrario, no permite inicializar el proyecto y redirige a la vista del proyecto."""
        return redirect('proyectoView', id=proyectoid)

    if int(proyecto.comite.count()) != 3:
        mensaje = "No se puede inicializar proyecto. No cuenta con el comite de 3 miembros."
        """En caso contrario, no permite inicializar el proyecto y redirige a la vista del proyecto."""
        return redirect('proyectoView', id=proyectoid)

    if int(proyecto.tipoItem.count()) == 0:
        mensaje = "No se puede inicializar proyecto. No cuenta con tipos de item."
        """En caso contrario, no permite inicializar el proyecto y redirige a la vista del proyecto."""
        return redirect('proyectoView', id=proyectoid)

    """Establecer el estado de proyecto como inicializado."""
    proyecto.estado = "inicializado"
    """Guardar."""
    """Asignando permisos al miembro del comite"""
    for user in proyecto.comite.all():
        assign_perm("break_lineaBase", user, proyecto)
        for f in proyecto.fases.all().exclude(estado="deshabilitado"):
            assign_perm("ver_lineaBase", user, f)
            assign_perm("view_fase", user, f)

    proyecto.save()
    """Redirigir a la vista del proyecto correspondiente."""
    return redirect('proyectoView', id=proyectoid)


def proyectoCancelar(request, proyectoid):
    """
               **proyectoCancelar:**
                Vista utilizada para cancelar proyectos.
                Solicita que el usuario que realiza el request
                cuente con los permisos de gerente de
                 proyecto y que(indirectamente) haya iniciado
                  sesion.
    """
    """Proyecto a cancelar."""
    proyecto = Proyecto.objects.get(id=proyectoid)

    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Establecer estado del poryecto como cancelado."""
    proyecto.estado = "cancelado"
    # proyecto._history_date = datetime.now()
    """Guardar."""
    proyecto.save()
    """Redirigir al menu principal del sistema."""
    return redirect("/home/")


'''
def proyectoView(request, id):
    """
       **proyectoView:**
        Vista utilizada para visualizar proyectos.
        Solicita que el usuario que realiza el request
        cuente con el permiso para ver el proyecto
        correspondiente,recibiendo el id del mismo y que
        (indirectamente) haya iniciado sesion
     """
    """Proyecto a visualizar"""
    proyecto = Proyecto.objects.get(id=id)
    """Solicitar permiso asociado al proyecto correspondiente"""
    if not(request.user.has_perm("view_proyecto", proyecto)):
        return redirect('/permissionError/')

    """Fases del proyecto para enviar al template que muestra la informacion"""
    fases = proyecto.fases.all()
    fasesUser = []
    for f in fases:
        if request.user.has_perm("view_fase", f) and f.estado != "deshabilitada":
            fasesUser.append(f)
    """Template a renderizar: proyectoListarFases.html con parametros -> proyectoid y fases del proyecto"""
    return render(request, 'proyecto/proyectoListarFases.html', {'proyecto': proyecto, 'fases':fases, 'fasesUser': sorted(fasesUser, key=lambda x: x.id, reverse=False)})

'''


def proyectoFase(request, id):
    if request.method == 'GET':
        """
           **proyectoView:**
            Vista utilizada para visualizar proyectos.
            Solicita que el usuario que realiza el request
            cuente con el permiso para ver el proyecto
            correspondiente,recibiendo el id del mismo y que
            (indirectamente) haya iniciado sesion
         """
        """Proyecto a visualizar"""
        proyecto = Proyecto.objects.get(id=id)
        """Solicitar permiso asociado al proyecto correspondiente"""
        if not (request.user.has_perm("view_proyecto", proyecto)):
            return redirect('/permissionError/')

        """Fases del proyecto para enviar al template que muestra la informacion"""
        fases = proyecto.fases.all()
        fasesUser = []
        for f in fases:
            if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente", proyecto)):
                fasesUser.append(f)

        """Se verifica el estado del proyecto, para destinarlo al html correcto"""
        if (proyecto.estado == 'pendiente'):
            """Template a renderizar: proyectoListarFases.html con parametros -> proyectoid y fases del proyecto"""
            return render(request, 'proyecto/proyectoListarFases.html', {'proyecto': proyecto, 'fases': fases,
                                                                         'fasesUser': sorted(fasesUser,
                                                                                             key=lambda x: x.id,
                                                                                             reverse=False), })


def proyectoView(request, id):
    seleccion = None
    if request.method == 'GET':
        """
           **proyectoView:**
            Vista utilizada para visualizar proyectos.
            Solicita que el usuario que realiza el request
            cuente con el permiso para ver el proyecto
            correspondiente,recibiendo el id del mismo y que
            (indirectamente) haya iniciado sesion
         """
        """Proyecto a visualizar"""
        proyecto = Proyecto.objects.get(id=id)
        """Solicitar permiso asociado al proyecto correspondiente"""
        if not (request.user.has_perm("view_proyecto", proyecto)):
            return redirect('/permissionError/')

        """Fases del proyecto para enviar al template que muestra la informacion"""
        fases = proyecto.fases.all()
        fasesUser = []
        for f in fases:
            if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente",
                                                                               proyecto)) and f.estado != "deshabilitada":
                fasesUser.append(f)

        usuarios = proyecto.usuarios.all()
        roles = proyecto.roles.all()
        tipoItem = proyecto.tipoItem.all()
        comite = proyecto.comite.all()
        """Se verifica el estado del proyecto, para destinarlo al html correcto"""
        if (proyecto.estado == 'pendiente'):
            """Template a renderizar: proyectoListarFases.html con parametros -> proyectoid y fases del proyecto"""
            hay_miembros = False
            if len(proyecto.usuarios.all()) > 2:
                hay_miembros = True
            hay_roles = False
            if len(proyecto.roles.all()) > 0:
                hay_roles = True
            hay_tipos = False
            if len(proyecto.tipoItem.all()) > 0:
                hay_tipos = True
            hay_comite = False
            if len(proyecto.comite.all()) == 3:
                hay_comite = True
            hay_fases = False
            if len(proyecto.fases.all()) > 0:
                hay_fases = True
            return render(request, 'proyecto/proyectoPendiente.html', {'proyecto': proyecto, 'fases': fases,
                                                                       'fasesUser': sorted(fasesUser,
                                                                                           key=lambda x: x.id,
                                                                                           reverse=False),
                                                                       'usuarios': usuarios,
                                                                       'roles': roles,
                                                                       'tipoItem': tipoItem,
                                                                       'comite': comite, 'hay_miembros': hay_miembros,
                                                                       'hay_roles': hay_roles,
                                                                       'hay_tipos': hay_tipos, 'hay_comite': hay_comite,
                                                                       'hay_fases': hay_fases})
        else:
            hay_acta = False
            acta = list(proyecto.acta.all())
            if len(acta) > 0:
                acta = acta.pop()
            if acta:
                hay_acta = True
            """Template a renderizar: proyectoIniciado.html con parametros -> proyectoid y fases del proyecto"""
            return render(request, 'proyecto/proyectoIniciado.html', {'proyecto': proyecto, 'fases': fases,
                                                                      'fasesUser': sorted(fasesUser,
                                                                                          key=lambda x: x.id,
                                                                                          reverse=False),
                                                                      'usuarios': usuarios,
                                                                      'roles': roles,
                                                                      'tipoItem': tipoItem,
                                                                      'comite': comite, 'hay_acta': hay_acta,
                                                                      'acta': acta})
    if request.method == "POST":
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Solicitar permiso asociado al proyecto correspondiente"""
        if not (request.user.has_perm("view_proyecto", proyecto)):
            return redirect('/permissionError/')

        """Fases del proyecto para enviar al template que muestra la informacion"""
        fases_item = Fase.objects.get(id=request.POST['fase'])
        fases = proyecto.fases.all()
        items = fases_item.items.exclude(estado="deshabilitado").order_by('id')
        fasesUser = []
        for f in fases:
            if request.user.has_perm("view_fase", f) and f.estado != "deshabilitada":
                fasesUser.append(f)
        seleccion = proyecto.fases.get(id=request.POST['fase'])
        usuarios = proyecto.usuarios.all()
        roles = proyecto.roles.all()
        tipoItem = proyecto.tipoItem.all()
        comite = proyecto.comite.all()

        return render(request, 'proyecto/proyectoIniciado.html', {'proyecto': proyecto, 'fases': fases,
                                                                  'fasesUser': sorted(fasesUser,
                                                                                      key=lambda x: x.id,
                                                                                      reverse=False),
                                                                  'usuarios': usuarios,
                                                                  'roles': roles,
                                                                  'tipoItem': tipoItem,
                                                                  'comite': comite,
                                                                  'select': seleccion,
                                                                  'items': items,
                                                                  })


def gestionProyecto(request):
    """
      **gestionProyecto:**
        Vista utilizada para visualizar Gestion del Proyecto.
        Solicita que el usuario que realiza el request cuente
        con el permiso para ver el proyecto correspondiente
        y que (indirectamente) haya iniciado sesion
    """

    """ID del Proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto para el acceso a Gestion de Proyecto"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Solicitar permiso asociado al proyecto correspondiente"""
    if not (request.user.has_perm("view_proyecto", proyecto)):
        return redirect('/permissionError/')
    fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
    finalizar = True
    for f in fasesProyecto:
        if not f.estado == "cerrada":
            finalizar = False
            break
    """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
    return render(request, 'proyecto/ProyectoInicializadoConfig.html',
                  {'proyecto': proyecto, 'fases': proyecto.fases.all(), 'finalizar': finalizar})


def proyectoModificar(request):
    """
       **proyectoModificar:**
        Vista utilizada para visualizar Modificar Proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para modificar el proyecto"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')

        """Proyecto a modificar"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""

        """Template a renderizar: proyectoModificar con parametro -> proyecto"""
        return render(request, 'proyecto/proyectoModificar.html', {'proyecto': proyecto, })

    """POST request, captura la informacion para actualizar los datos del proyecto"""

    """Nuevo nombre del proyecto"""
    nombre = request.POST.get('nombre')
    """Nueva descripcion del proyecto"""
    descripcion = request.POST.get('descripcion')
    """Nueva fecha de inicio del proyecto"""
    fechaini = request.POST.get('fechaini')
    """Nueva fecha de finalizacion del proyecto"""
    fechafin = request.POST.get('fechafin')
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto a modificar"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Actualizar informacion"""
    proyecto.nombre = nombre
    proyecto.descripcion = descripcion
    if proyecto.estado != "inicializado":
        proyecto.fecha_inicio = fechaini
    proyecto.fecha_fin = fechafin
    """Guardar"""
    proyecto.save()

    """Template a renderizar: gestionProyecto con parametro -> proyectoid"""
    return render(request, 'proyecto/ProyectoInicializadoConfig.html', {'proyecto': proyecto, })


def proyectoDeshabilitar(request, proyectoid):
    """
       **proyectoDeshabilitar:**
        Vista utilizada para visualizar Deshabilitar Proyecto.
        Solicita que el usuario que realiza el request cuente
        con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para deshabilitar el proyecto"""
    if request.method == 'GET':
        """Proyecto a deshabilitar"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        """Deshabilitar proyecto, cambio de estado"""
        proyecto.estado = "deshabilitado"
        proyecto.save()
        return redirect("/home/")


def faseView(request, faseid, proyectoid):
    """
       **faseView:**
        Vista utilizada para visualizar fases.
        Solicita que el usuario que realiza el request
        cuente con el permiso para ver la fase
        correspondiente, o bien, sea el gerente del
        proyecto. Recibe el id de la fase y del proyecto
         en el que se encuentra.
        Tambien solicita que (indirectamente) el usuario
        haya iniciado sesion.
     """
    """Fase a visualizar."""
    fase = Fase.objects.get(id=faseid)
    """Proyecto en el cual se encuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("view_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        """Al no contar con los permisos, niega el acceso, redirigiendo."""
        return redirect('/permissionError/')

    """Obtiene todos los items de la fase, exclyendo a los deshabilitados, ordenados por id."""
    items = fase.items.exclude(estado="deshabilitado").order_by('id')

    roles = proyecto.roles.all()
    usuarios = []
    rolesUser = []
    for r in roles:
        fasesUser = r.faseUser.all()

        for f in fasesUser:
            if f.fase == fase:
                usuarios.append(f.user)
                rolesUser.append(r)
    user_sin_repetidos = []
    roles_por_user = []
    for u, r in zip(usuarios, rolesUser):
        if not u in user_sin_repetidos:
            user_sin_repetidos.append(u)
            cadena = ""
            for uu, rr in zip(usuarios, rolesUser):
                if u == uu:
                    cadena = cadena + rr.nombre + ', '
            cadena = cadena[:-2]
            roles_por_user.append(cadena)

    cant_user = len(user_sin_repetidos)
    hay_roles = proyecto.roles.exists()
    hay_tipos_item = proyecto.tipoItem.exists()
    """Template a renderizar: fase.html con parametros -> fase, proyecto, items de fase."""
    return render(request, 'fase/fase.html', {'fase': fase, 'proyecto': proyecto, 'items': items,
                                              'userRol': zip(user_sin_repetidos, roles_por_user),
                                              'cant_user': cant_user, 'hay_roles': hay_roles,
                                              'hay_tipos_item': hay_tipos_item,
                                              })


def proyectoUser(request):
    """
       **proyectoUser:**
        Vista utilizada para mostrar Gestion de Miembros
        dentro del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """ID del Proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')


    """Lista de miembros del proyecto para mostrar en el template."""
    usuarios = proyecto.usuarios.all()
    user_sistema = User.objects.all()
    usuarios_add = []
    for u in user_sistema:
        if u.is_active and u.username != "AnonymousUser":
            if not u in proyecto.usuarios.all():
                usuarios_add.append(u)
    comite = proyecto.comite.all()
    cant_user = len(usuarios)
    add_user = len(usuarios_add)
    """Template a renderizar; proyectoUser.html con parametros -> proyectoid y usuarios del proyecto"""
    return render(request, 'proyecto/proyectoUser.html', {'proyecto': proyecto, 'usuarios': usuarios,
                                                          'cant_user': cant_user, 'comite': comite, 'add_user':add_user})


def proyectoUserAdd(request):
    """
       **proyectoUserAdd:**
        Vista utilizada para agregar miembros al proyecto.
        Solicita que el usuario que realiza el request cuente
        con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para agregar miembros al proyecto"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')

        """Proyecto al cual agregar miembros"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""
        if proyecto.estado == "cancelado":
            return redirect('proyectoView', id=proyectoid)

        """Gerente del proyecto"""
        gerente = Proyecto.objects.get(id=proyectoid).gerente
        usuarios = []
        """Lista de usuarios posibles a ser agregados"""
        users = User.objects.all()
        for u in users:
            """
            Filtrar que no se pueda agregar un usuario staff, 
            gerente. Tampoco puede ser el usuario que realiza
            el request, los usuarios ya agregados al proyecto
            y los usuarios deshabilitados.
            """
            if u.is_staff == False and u != request.user and u != gerente and not (u in proyecto.usuarios.all()) \
                    and u.is_active and u.has_perm("perms.view_menu") == True and u.username != "AnonymousUser":
                usuarios.append(u)
        """
        Template a renderizar: proyectoUserAdd.html con parametros
         -> usuarios posibles para agregar y proyectoid
        """
        return render(request, "proyecto/proyectoUserAdd.html", {'usuarios': usuarios, 'proyecto': proyecto, })

    """POST request, captura una lista de usuarios a agregar al proyecto"""
    """Lista de usuarios a agregar"""
    users = request.POST.getlist('users')
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto en el cual agregar miembros"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    for u in users:
        """Usuario a ser agregado"""
        user = User.objects.get(id=u)
        """Agregar usuario"""
        proyecto.usuarios.add(user)
        """Agregar permiso para Verl el Proyecto al usuario"""
        assign_perm("view_proyecto", user, proyecto)

    usuarios = proyecto.usuarios.all()
    user_sistema = User.objects.all()
    usuarios_add = []
    for u in user_sistema:
        if u.is_active and u.username != "AnonymousUser":
            if not u in proyecto.usuarios.all():
                usuarios_add.append(u)

    comite = proyecto.comite.all()
    cant_user = len(usuarios)
    add_user = len(usuarios_add)
    """Template a renderizar; proyectoUser.html con parametros -> proyectoid y usuarios del proyecto"""
    return render(request, 'proyecto/proyectoUser.html', {'proyecto': proyecto, 'usuarios': usuarios,
                                                          'cant_user': cant_user, 'comite': comite,
                                                          'add_user': add_user})


def proyectoUserRemove(request, proyectoid, userid):
    """
       **proyectoUserRemove:**
        Vista utilizada para remover miembros del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """


    if request.method == 'GET':
        """POST request, captura la lista de usuarios para remover del proyecto"""
        """Lista de usuarios a remover"""
        # users = request.POST.getlist('users')
        """ID del proyecto"""
        # proyectoid = request.POST.get('proyectoid')
        """Proyecto del cual remover"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        """Usuario a remover"""
        user = User.objects.get(id=userid)
        """Remover usuario"""
        proyecto.usuarios.remove(user)
        proyecto.save()
        """Remover permiso para ver el proyecto"""
        remove_perm("view_proyecto", user, proyecto)
        if user in proyecto.comite.all():
            """Si el usuario era miembro del Comite de Control de Cambio. removerlo."""
            proyecto.comite.remove(user)
            """Remover permiso para aprobar la rotura de linea base."""
            remove_perm("break_lineaBase", user, proyecto)
        usuarios = proyecto.usuarios.all()
        cant_user = len(usuarios)
        return render(request, 'proyecto/proyectoUser.html', {'proyecto': proyecto, 'usuarios': usuarios,
                                                              'cant_user': cant_user, })


def proyectoComite(request, proyectoid, mensaje):
    """
       **proyectoComite:**
        Vista utilizada para mostrar Gestion de Comite
        de Control de Cambios del Proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """ID del proyecto"""
    # proyectoid = request.GET.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')



    """Lista de miembros del comite para mostrar en el template"""
    comite = proyecto.comite.all()
    agregar_mas_users = False
    miembros_no_comite = proyecto.usuarios.exclude(is_active=False)
    if int(len(comite)) < 3:
        for m in miembros_no_comite:
            if not m in comite:
                """Setea en TRUE la bandera y corta el ciclo cuando encuentra hay al menos algun miembro del proyecto 
                    que se pueda agregar al comite
                """
                agregar_mas_users = True
                break;

    """Template a renderizar: proyectoComite.html con parametros -> proyectoid y comite de control de cambios"""
    return render(request, 'proyecto/proyectoComite.html', {'proyecto': proyecto, 'comite': comite,
                                                            'agregar_mas_users': agregar_mas_users, 'mensaje': mensaje})


def proyectoComiteAdd(request):
    """
       **proyectoComiteAdd:**
        Vista utilizada para agregar miembros
        al Comite de Control de Cambios del Proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para agregar miembros al comite."""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')

        """Proyecto al cual agregar"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""
        if proyecto.estado == "cancelado":
            return redirect('proyectoView', id=proyectoid)

        miembros = []
        """Lista de usuarios del proyecto"""
        users = proyecto.usuarios.all()
        for u in users:
            """Filtrar que no sean usuarios que ya pertenecen al comite y que no esten deshabilitados."""
            if not (u in proyecto.comite.all()) and u.is_active:
                """Agregar usuarios al comite"""
                miembros.append(u)

        """
        Template a renderizar: proyectoComiteAdd.html con parametros -> 
        miembros posibles a agregar y proyectoid
        """
        return render(request, "proyecto/proyectoComiteAdd.html", {'miembros': miembros, 'proyectoid': proyectoid, })

    """POST request, captura lista de miembros para agregar al comite."""

    """Lista de miembros a agregar"""
    users = request.POST.getlist('miembros')
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto al cual agregar"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar que los miembros del comite no pueden ser mas de 3"""
    if (len(users) + len(list(proyecto.comite.all()))) > 3:
        miembros = []
        """Lista de usuarios del proyecto"""
        users = proyecto.usuarios.all()
        for u in users:
            """Filtrar que los usuarios no pertenezcan al comite"""
            if not (u in proyecto.comite.all()):
                miembros.append(u)

        """
        Template a renderizar: proyectoComiteAdd.html con parametros ->
        miembros posibles a agregar, proyectoid
        y mensaje de error
        """
        return render(request, "proyecto/proyectoComiteAdd.html", {'miembros': miembros, 'proyectoid': proyectoid,
                                                                   'mensaje': "El Comite Solo puede contar con 3 miembros."})

    for u in users:
        """Miembro a agregar al Comite"""
        user = User.objects.get(id=u)
        """Agregar miembro al Comite"""
        proyecto.comite.add(user)
        """envio de notificacion"""
        mail = user.email
        name = user.username
        sendEmailViewProyecto.delay(mail, name, proyecto.nombre, 1)
        """Agregar el permiso para aprobar rotura de linea base"""
        if proyecto.estado == "inicializado":
            assign_perm("break_lineaBase", user, proyecto)
            for f in proyecto.fases.all().exclude(estado="deshabilitado"):
                assign_perm("ver_lineaBase", user, f)
                assign_perm("view_fase", user, f)

    if len(users) == 0:
        mensaje = "Error, no se añadio a ningún miembro al Comité."
    else:
        """Notificar a los miembros del comite"""
        mensaje = "Se agregó correctamente al usuario dentro del Comité"
    """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
    return redirect('Comite', proyectoid=proyectoid, mensaje=mensaje)


def proyectoComiteRemove(request, proyectoid, userid):
    """
       **proyectoComiteRemove:**
        Vista utilizada para remover miembros
        del Comite de Control de Cambios del Proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para remover miembros del comite."""
    if request.method == 'GET':
        """Proyecto en el cual remover miembros del comite"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        """POST request, captura una lista de miembros para remover del comite"""
        """Lista de miembros"""
        user = User.objects.get(id=userid)
        fases = proyecto.fases.all().exclude(estado="deshabilitada")
        linea_base_norota = []
        for f in fases:
            for l in f.lineasBase.all().exclude(estado="rota"):
                linea_base_norota.append(l)
        solicitudes = []

        proyecto.comite.remove(user)
        proyecto.save()
        """Remover permisos para aprobar rotura de linea base"""
        if proyecto.estado == "inicializado":
            remove_perm("break_lineaBase", user, proyecto)
            for f in proyecto.fases.all().exclude(estado="deshabilitado"):
                remove_perm("ver_lineaBase", user, f)
                remove_perm("view_fase", user, f)

            usuarios_votantes = []
            for lb in linea_base_norota:
                for s in lb.roturaslineasBase.all().filter(estado="pendiente"):
                    for v in s.votos_registrados.all():
                        usuarios_votantes.append(int(v.id))
                    if int(user.id) in usuarios_votantes:
                        posicion_user = usuarios_votantes.index(int(user.id))
                        """Solo se puede remover los primeros dos votos, porque si hay 3 votos ya se cerró la votación"""
                        if posicion_user == 0:
                            s.voto_uno = s.voto_dos
                            s.voto_dos = -1
                            s.votos_registrados.remove(user)
                            s.save()
                        if posicion_user == 1:
                            s.voto_dos = -1
                            s.votos_registrados.remove(user)
                            s.save()
                usuarios_votantes_comprometida = []
                for s in lb.roturaLineaBaseComprometida.all().filter(comprometida_estado="pendiente"):
                    for v in s.registrados_votos_comprometida.all():
                        usuarios_votantes_comprometida.append(int(v.id))
                    if int(user.id) in usuarios_votantes_comprometida:
                        posicion_user = usuarios_votantes_comprometida.index(int(user.id))
                        """Solo se puede remover los primeros dos votos, porque si hay 3 votos ya se cerró la votación"""
                        if posicion_user == 0:
                            s.uno_voto_comprometida = s.dos_voto_comprometida
                            s.dos_voto_comprometida = -1
                            s.registrados_votos_comprometida.remove(user)
                            s.save()
                        if posicion_user == 1:
                            s.dos_voto_comprometida = -1
                            s.registrados_votos_comprometida.remove(user)
                            s.save()
        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        return redirect('Comite', proyectoid=proyectoid, mensaje="Se removió correctamente al usuario del Comité")


def proyectoRol(request, proyectoid, mensaje):
    """
       **proyectoRol:**
        Vista utilizada para mostrar Gestion de Roles en el proyecto.
        Solicita que el usuario que realiza el request cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """ID del proyecto"""
    # proyectoid = request.GET.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')



    """Lista de roles del proyecto para visualizar en el template"""
    roles = proyecto.roles.all()
    """
    Template a renderizar: proyectoRol.html con parametros -> peroyectoid
    y roles del proyecto
    """
    return render(request, 'proyecto/proyectoRol.html', {'proyecto': proyecto, 'roles': roles, 'mensaje': mensaje})


def proyectoRolCrear(request):
    """
       **proyectoRolCrear**
        Vista utilizada para crear roles en el proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """POST request, captura la informacion estblecida por el usuario para crear el rol"""
    if request.method == 'POST':
        """ID proyecto"""
        proyectoid = request.POST.get('proyectoid')
        """Proyecto al cual agregar rol"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Nombre del Rol"""
        nombre = request.POST.get('nombre')
        """Verificar si ya existe un rol con el nombre especificado en el proyecto, este debe ser unico"""
        if proyecto.roles.filter(nombre=nombre).exists():
            """Template a renderizar: proyectoRolCrear.html con parametros -> mensaje de error"""
            return render(request, 'proyecto/proyectoRolCrear.html', {'proyectoid': proyectoid,
                                                                      'mensaje': "Lo sentimos, el nombre del Rol ya ha sido asignado en el proyecto.", })

        """Crear el rol con el nombre especificado"""
        rol = Rol.objects.create(nombre=nombre)
        cont = 1
        """Verificar si ya existe un grupo con ese nombre, para evitar romper la condicion de unicidad."""
        nombreGrupo = nombre
        while Group.objects.filter(name=nombreGrupo).exists():
            nombreGrupo = nombre + str(cont)
            cont = cont + 1

        grupo = Group.objects.create(name=nombreGrupo)
        """Lista de permisos de proyecto para el rol"""
        permisos = request.POST.getlist('perms')

        for p in permisos:
            if int(p) == 1:
                """Permiso Proyecto ID=4 corresponde a Ver Fase"""
                permiso = Permission.objects.get(codename="view_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 3:
                """Permiso Proyecto ID=2 corresponde a Modificar Fase"""
                permiso = Permission.objects.get(codename="change_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 4:
                """Permiso Proyecto ID=3 corresponde a Remover Fase"""
                permiso = Permission.objects.get(codename="delete_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 5:
                """Permiso Proyecto ID=19 corresponde a Cerrar Fase"""
                permiso = Permission.objects.get(codename="cerrar_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 6:
                """Permiso Proyecto ID=14 corresponde a Ver Item"""
                permiso = Permission.objects.get(codename="ver_item")
                grupo.permissions.add(permiso)
            elif int(p) == 7:
                """Permiso Proyecto ID=5 corresponde a Crear Item"""
                permiso = Permission.objects.get(codename="create_item")
                grupo.permissions.add(permiso)
            elif int(p) == 8:
                """Permiso Proyecto ID=10 corresponde a Modificar Item"""
                permiso = Permission.objects.get(codename="modify_item")
                grupo.permissions.add(permiso)
            elif int(p) == 9:
                """Permiso Proyecto ID=7 corresponde a Deshabilitar Item"""
                permiso = Permission.objects.get(codename="deshabilitar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 10:
                """Permiso Proyecto ID=8 corresponde a Reversionar Item"""
                permiso = Permission.objects.get(codename="reversionar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 11:
                """Permiso Proyecto ID=9 corresponde a Relacionar Item"""
                permiso = Permission.objects.get(codename="relacionar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 12:
                """Permiso Proyecto ID=6 corresponde a Aprobar Item"""
                permiso = Permission.objects.get(codename="aprove_item")
                grupo.permissions.add(permiso)
            elif int(p) == 13:
                """Permiso Proyecto ID=13 corresponde a Obtener Trazabilidad de Item"""
                permiso = Permission.objects.get(codename="obtener_trazabilidadItem")
                grupo.permissions.add(permiso)
            elif int(p) == 14:
                """Permiso Proyecto ID=15 corresponde a Obtener Calculo de Impacto"""
                permiso = Permission.objects.get(codename="obtener_calculoImpacto")
                grupo.permissions.add(permiso)
            elif int(p) == 15:
                """Permiso Proyecto ID=12 corresponde a Establecer Item Desarrollo"""
                permiso = Permission.objects.get(codename="establecer_itemDesarrollo")
                grupo.permissions.add(permiso)
            elif int(p) == 16:
                """Permiso Proyecto ID=11 corresponde a Establecer Item Pendiente de Aprobacion"""
                permiso = Permission.objects.get(codename="establecer_itemPendienteAprob")
                grupo.permissions.add(permiso)
            elif int(p) == 17:
                """Permiso Proyecto ID=19 corresponde a Ver Linea Base"""
                permiso = Permission.objects.get(codename="ver_lineaBase")
                grupo.permissions.add(permiso)
            elif int(p) == 18:
                """Permiso Proyecto ID=16 corresponde a Crear Linea Base"""
                permiso = Permission.objects.get(codename="create_lineaBase")
                grupo.permissions.add(permiso)
            elif int(p) == 19:
                """Permiso Proyecto ID=19 corresponde a Modificar Linea Base"""
                permiso = Permission.objects.get(codename="modify_lineaBase")
                grupo.permissions.add(permiso)
            elif int(p) == 20:
                """Permiso Proyecto ID=18 corresponde a Solicitar Rotura de Linea Base"""
                permiso = Permission.objects.get(codename="solicitar_roturaLineaBase")
                grupo.permissions.add(permiso)

            if 5 < int(p) < 17:
                """Garantizar la presencia del permiso Ver Item"""
                permiso = Permission.objects.get(codename="ver_item")
                if not grupo.permissions.filter(codename="ver_item").exists():
                    grupo.permissions.add(permiso)

            if 16 < int(p) < 21:
                """Garantizar la presencia del permiso Ver Item"""
                permiso = Permission.objects.get(codename="ver_lineaBase")
                if not grupo.permissions.filter(codename="ver_lineaBase").exists():
                    grupo.permissions.add(permiso)

        """Garantizar la presencia del permiso Ver Fase"""
        permiso = Permission.objects.get(codename="view_fase")
        if not grupo.permissions.filter(codename="view_fase").exists():
            grupo.permissions.add(permiso)
        """Establecer el grupo de permisos al rol"""
        rol.perms = grupo
        """Guardar ROl"""
        rol.save()
        """Agregar rol a proyecto"""
        proyecto.roles.add(rol)
        roles = proyecto.roles.all()
        """Template a renderizar: gestion Proyecto.html con parametro -> proyectoid"""
        mensaje = "Rol creado correctamente."
        return redirect('ProyectoRol', proyectoid=proyectoid, mensaje=mensaje)
    else:
        """GET request, muestra el template correspondiente para la creacion del rol"""
        """ID Proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""
        if proyecto.estado == "cancelado":
            return redirect('proyectoView', id=proyectoid)

        """Template a renderizar: proyectoRolCrear.html con parametro -> proyectoid"""
        return render(request, "proyecto/proyectoRolCrear.html", {'proyectoid': proyectoid, })


def proyectoRolModificar(request, proyectoid, rolid):
    """
       **proyectoRolModificar:**
        Vista utilizada para modificar roles del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    if request.method == "GET":
        """GET request, muestra el template correspondiente a la modificacion de roles"""
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID Proyecto"""
        # proyectoid = request.GET.get('proyectoid')
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""
        if proyecto.estado == "cancelado":
            return redirect('proyectoView', id=proyectoid)
        """Si el rol no ha sido asignado"""
        """Actualizar los datos para visualizar en el template"""
        rol = Rol.objects.get(id=rolid)
        permisos = []
        """Permisos del rol"""
        perms = rol.perms.permissions.all()
        for p in perms:
            permisos.append(p.codename)
        """Template a renderizar: proyectoRolModificar.html con parametros -> roles del proyecto, proyectoid"""
        return render(request, "proyecto/proyectoRolModificar.html",
                      {'rol': rol, 'proyecto': proyecto, 'permisos': permisos, })

    """POST request, captura la nueva informacion del rol para actualizarlo"""
    if request.method == "POST":
        """Boton Modificar presionado en el template"""
        """ID del rol"""
        # rolid = request.POST.get('rolid')
        """Permisos nuevos para el rol"""
        """Proyecto en el que se encuentra el rol"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        rol = Rol.objects.get(id=rolid)
        perms_antes_modificar = rol.perms.permissions.all()
        permisos = request.POST.getlist('perms')
        vector = []
        """Nuevo nombre del rol"""
        nombreanterior = request.POST.get('nombreanterior')
        nombrenuevo = request.POST.get('nombre')
        """ Verificar si hubo un cambbio de nombre"""
        if nombrenuevo != nombreanterior:
            """Verificar si el nombre asignado ya corresponde al nombre de otro rol"""
            if proyecto.roles.filter(nombre=nombrenuevo).exclude(id=rolid).exists():
                """Roles del Proyecto"""
                roles = proyecto.roles.all()
                """
                Template a renderizar: proyectoRolModificar.html con parametros -> 
                roles del proyecto, proyectoid y mensaje de error
                """
                return render(request, "proyecto/proyectoRolModificar.html",
                              {'roles': roles, 'select': None, 'proyectoid': proyectoid, 'permisos': None,
                               'mensaje': "Lo sentimos, el nombre del Rol ya ha sido asignado en el proyecto.", })
            """Rol a modificar"""

            """Grupo a poseer los nuevos permisos"""
            grupo = Group.objects.get(name=rol.perms)
            cont = 1
            """Verificar si ya existe un grupo con ese nombre, para evitar romper la condicion de unicidad."""
            nombreGrupo = nombrenuevo
            while Group.objects.filter(name=nombreGrupo).exists():
                nombreGrupo = nombrenuevo + str(cont)
                cont = cont + 1

            grupo.name = nombreGrupo
            """Asignar nuevo nombre al rol"""
            rol.nombre = nombrenuevo

        grupo = Group.objects.get(name=rol.perms)
        for p in permisos:
            if int(p) == 1:
                """Permiso Proyecto ID=4 corresponde a Ver Fase"""
                permiso = Permission.objects.get(codename="view_fase")
                vector.append(permiso)
            elif int(p) == 3:
                """Permiso Proyecto ID=2 corresponde a Modificar Fase"""
                permiso = Permission.objects.get(codename="change_fase")
                vector.append(permiso)
            elif int(p) == 4:
                """Permiso Proyecto ID=3 corresponde a Remover Fase"""
                permiso = Permission.objects.get(codename="delete_fase")
                vector.append(permiso)
            elif int(p) == 5:
                """Permiso Proyecto ID=19 corresponde a Cerrar Fase"""
                permiso = Permission.objects.get(codename="cerrar_fase")
                vector.append(permiso)
            elif int(p) == 6:
                """Permiso Proyecto ID=14 corresponde a Ver Item"""
                permiso = Permission.objects.get(codename="ver_item")
                vector.append(permiso)
            elif int(p) == 7:
                """Permiso Proyecto ID=5 corresponde a Crear Item"""
                permiso = Permission.objects.get(codename="create_item")
                vector.append(permiso)
            elif int(p) == 8:
                """Permiso Proyecto ID=10 corresponde a Modificar Item"""
                permiso = Permission.objects.get(codename="modify_item")
                vector.append(permiso)
            elif int(p) == 9:
                """Permiso Proyecto ID=7 corresponde a Deshabilitar Item"""
                permiso = Permission.objects.get(codename="deshabilitar_item")
                vector.append(permiso)
            elif int(p) == 10:
                """Permiso Proyecto ID=8 corresponde a Reversionar Item"""
                permiso = Permission.objects.get(codename="reversionar_item")
                vector.append(permiso)
            elif int(p) == 11:
                """Permiso Proyecto ID=9 corresponde a Relacionar Item"""
                permiso = Permission.objects.get(codename="relacionar_item")
                vector.append(permiso)
            elif int(p) == 12:
                """Permiso Proyecto ID=6 corresponde a Aprobar Item"""
                permiso = Permission.objects.get(codename="aprove_item")
                vector.append(permiso)
            elif int(p) == 13:
                """Permiso Proyecto ID=13 corresponde a Obtener Trazabilidad de Item"""
                permiso = Permission.objects.get(codename="obtener_trazabilidadItem")
                vector.append(permiso)
            elif int(p) == 14:
                """Permiso Proyecto ID=15 corresponde a Obtener Calculo de Impacto"""
                permiso = Permission.objects.get(codename="obtener_calculoImpacto")
                vector.append(permiso)
            elif int(p) == 15:
                """Permiso Proyecto ID=12 corresponde a Establecer Item Desarrollo"""
                permiso = Permission.objects.get(codename="establecer_itemDesarrollo")
                vector.append(permiso)
            elif int(p) == 16:
                """Permiso Proyecto ID=11 corresponde a Establecer Item Pendiente de Aprobacion"""
                permiso = Permission.objects.get(codename="establecer_itemPendienteAprob")
                vector.append(permiso)
            elif int(p) == 17:
                """Permiso Proyecto ID=19 corresponde a Ver Linea Base"""
                permiso = Permission.objects.get(codename="ver_lineaBase")
                vector.append(permiso)
            elif int(p) == 18:
                """Permiso Proyecto ID=16 corresponde a Crear Linea Base"""
                permiso = Permission.objects.get(codename="create_lineaBase")
                vector.append(permiso)
            elif int(p) == 19:
                """Permiso Proyecto ID=19 corresponde a Modificar Linea Base"""
                permiso = Permission.objects.get(codename="modify_lineaBase")
                vector.append(permiso)
            elif int(p) == 20:
                """Permiso Proyecto ID=18 corresponde a Solicitar Rotura de Linea Base"""
                permiso = Permission.objects.get(codename="solicitar_roturaLineaBase")
                vector.append(permiso)

            if 5 < int(p) < 17:
                """Garantizar la presencia del permiso Ver Item"""
                permiso = Permission.objects.get(codename="ver_item")
                if permiso not in vector:
                    vector.append(permiso)

            if 16 < int(p) < 21:
                """Garantizar la presencia del permiso Ver Item"""
                permiso = Permission.objects.get(codename="ver_lineaBase")
                if permiso not in vector:
                    vector.append(permiso)

        """Garantizar la presencia del permiso Ver Fase"""
        permiso = Permission.objects.get(codename="view_fase")
        if permiso not in vector:
            vector.append(permiso)

        for fu in rol.faseUser.all():
            for p in perms_antes_modificar:
                remove_perm(p.codename, fu.user, fu.fase)

        """Agregar permisos al grupo"""
        grupo.permissions.set(vector)
        """Guardar grupo"""
        grupo.save()
        usuarios_con_el_rol = []

        for fu in rol.faseUser.all():
            for p in grupo.permissions.all():
                assign_perm(p.codename, fu.user, fu.fase)
        """Agregar grupo de permisos al rol"""
        rol.perms = grupo
        """Guardar Rol"""
        rol.save()
        roles = proyecto.roles.all()
        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        mensaje = "Rol modificado correctamente."
        return redirect('ProyectoRol', proyectoid=proyectoid, mensaje=mensaje)


def proyectoRolEliminar(request, proyectoid, rolid):
    """
       **proyectoRolEliminar:**
        Vista utilizada para remover roles del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """

    if request.method == 'GET':
        # proyectoid = request.POST.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        """Lista de roles del proyecto"""

        rol = Rol.objects.get(id=rolid)

        """Si el rol no ha sido asignado previamente"""
        proyecto.roles.remove(rol)

        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        mensaje = "Rol removido correctamente."
        return redirect('ProyectoRol', proyectoid=proyectoid, mensaje=mensaje)


def crear_tipo_form(request):
    if request.method == "POST":
        """Recibe el POST con los datos del formulario para la creación de un Tipo de Item"""
        dato = request.POST
        """Recupera de la BD el proyecto en el que se encuentra el usuario."""
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Se asignan variables con los valores del POST para poder crear el tipo de Item"""
        nombre1 = dato['nombretipo']
        """Se verifica que el nombre del tipo de item no exista en el proyecto."""
        if proyecto.tipoItem.filter(nombreTipo=nombre1).exists():
            return render(request, "proyecto/creartipo.html", {'proyectoid': proyectoid,
                                                               'mensaje': "Lo sentimos, el nombre de tipo de item"
                                                                          " ya ha sido asignado en el proyecto.", })
        descrip = dato['descripciontipo']
        campo = dato['camposadd'].split(',')
        """Creación de un objeto Tipo de Item con los valores recibidos en el post"""
        obj = TipodeItem.objects.create(nombreTipo=nombre1, descripcion=descrip)
        """Ciclo para agregar los campos extra creados por el usuario al objeto del tipo "Tipo de Item" """
        for c in campo:
            if not c == "":
                obj.campo_extra.append(c)
        """Se guarda en la BD el objeto creado"""
        obj.save()
        """Se asigna el proyecto en el cual se encuentra proyectoidel usuario el nuevo tipo de Item creado"""
        proyecto.tipoItem.add(obj)
        tipos = proyecto.tipoItem.all()
        tipos_modificable = list(tipos)
        tipos_no_modificable = []
        fasesProyecto = proyecto.fases.all()
        for f in fasesProyecto:
            itemsFase = f.items.all()
            for i in itemsFase:
                if i.tipoItem == tipos and i.estado != "deshabilitado":
                    tipos_modificable.remove(tipos)
                    tipos_no_modificable.append(tipos)
        return render(request, "proyecto/gestionartipodeitem.html",
                      {'proyecto': proyecto, 'tipos_modificable': tipos_modificable,
                       'tipos_no_modificable': tipos_no_modificable, })

    """En caso de recibir un método GET, renderiza al html creartipo.html"""
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Verifica que el proyecto no se encuentre cancelado"""
    if proyecto.estado == "cancelado":
        return redirect('proyectoView', id=proyectoid)

    return render(request, "proyecto/creartipo.html", {'proyectoid': proyectoid})


def gestionar_tipo_de_item(request):
    """
       ** gestionar_tipo_de_item**
        View para gestionar los tipos de Item,
        en ella se encuentran las opciones de
        Creación, Modificación y
        Eliminación de Tipos de Items.
    """
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    tipos = proyecto.tipoItem.all()
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')


    tipos_modificable = list(tipos)
    tipos_no_modificable = []
    fasesProyecto = proyecto.fases.all()
    for f in fasesProyecto:
        itemsFase = f.items.all()
        for i in itemsFase:
            if i.tipoItem == tipos and i.estado != "deshabilitado":
                tipos_modificable.remove(tipos)
                tipos_no_modificable.append(tipos)

    return render(request, "proyecto/gestionartipodeitem.html",
                  {'proyecto': proyecto, 'tipos_modificable': tipos_modificable,
                   'tipos_no_modificable': tipos_no_modificable, })


def modificar_tipo_de_item(request, proyectoid, tipoid):
    """
       **modificar_tipo_de_item:**
        View para modificar los datos de un tipo
        de Item previamente creado.
    """

    """
    Se establece seleccion en None debido a que 
    se encuentra en el metodo GET, el usuario aún no
    selecciono un tipo de Item para modificar.
    """
    if request.method == "GET":
        """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
        """Recupera de la BD el proyecto en el que se encuentra el usuario."""
        # proyectoid = request.GET.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Verifica que el proyecto no se encuentre cancelado"""
        if proyecto.estado == "cancelado":
            return redirect('proyectoView', id=proyectoid)
        """
        Se asigna a la variable "tipos" todos los Tipos de Item
        con los que cuenta el proyecto en el cual se encuentra el usuario
        """
        tipo = TipodeItem.objects.get(id=tipoid)

        return render(request, "proyecto/modifTipodeItem.html", {'proyectoid': proyectoid,
                                                                 'tipo': tipo})
    if request.method == "POST":
        """
        Consulta si el post recibido es el de la selección de 
        un Tipo de Item o el post para guardar la información modificada.
        """
        if 'cambio' in request.POST:
            proyectoid = request.POST.get('proyectoid')
            proyecto = Proyecto.objects.get(id=proyectoid)
            """Recibe el POST con los datos del formulario para la modificación de un Tipo de Item"""
            dato = request.POST
            """Creación de un objeto Tipo de Item con los valores recibidos en el post"""
            obj = proyecto.tipoItem.get(id=dato['tipodeitem_id'])
            """Se verifica que el nombre nuevo no este asociado a otro tipo de item en el proyecto."""
            if proyecto.tipoItem.filter(nombreTipo=dato['nombretipo']).exclude(id=dato['tipodeitem_id']).exists():
                """
                Se asigna a la variable "tipos" todos los Tipos de Item 
                con los que cuenta el proyecto en el cual se encuentra el usuario
                """
                tipos = proyecto.tipoItem.all()
                return render(request, "proyecto/modifTipodeItem.html",
                              {'proyectoid': proyectoid, 'tipos': tipos, 'select': None,
                               'mensaje': "El nombre ya ha sido asignado a otro tipo de item en el proyecto.", })

            """Se guarda en el objeto Tipo de Item los valores de modificación establecidos por el usuario."""
            obj.nombreTipo = dato['nombretipo']
            obj.descripcion = dato['descripciontipo']
            cambios = request.POST.getlist('campos')
            campos_add = dato['camposadd'].split(",")
            """Se crea un vector para guardar los cambios en los campos extras"""
            cambios_campos = []
            for c in cambios:
                if not c == "":
                    """
                    Agrega campos que no sean igual a un espacio en blanco,
                    pues estos fueron eliminados por el usuario.
                    """
                    cambios_campos.append(c)
            for cc in campos_add:
                if not cc == "":
                    """Guarda los campos extra filtrados, es decir, sin espacios en blanco."""
                    cambios_campos.append(cc)
            obj.campo_extra = cambios_campos
            """Guarda las modificaciones en la BD"""
            obj.save()
            tipos = proyecto.tipoItem.all()
            tipos_modificable = list(tipos)
            tipos_no_modificable = []
            fasesProyecto = proyecto.fases.all()
            for f in fasesProyecto:
                itemsFase = f.items.all()
                for i in itemsFase:
                    if i.tipoItem == tipos and i.estado != "deshabilitado":
                        tipos_modificable.remove(tipos)
                        tipos_no_modificable.append(tipos)
            return render(request, "proyecto/gestionartipodeitem.html",
                          {'proyecto': proyecto, 'tipos_modificable': tipos_modificable,
                           'tipos_no_modificable': tipos_no_modificable, })


def importar_tipo_de_item(request):
    """
       **importar_tipo_de_item:**
        View para la importación de
        Tipos de Item al proyecto.
    """
    if request.method == "POST":
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Recibe los tipos de Item que el usuario desea importar al proyecto actual."""
        elegidos = request.POST.getlist('importados')
        """Ciclo para recorrer los tipos de Item seleccionados por el usuario."""
        tipos = TipodeItem.objects.all()
        for e in elegidos:
            tipo = tipos.get(id=e)
            if proyecto.tipoItem.filter(nombreTipo=tipo.nombreTipo).exists():
                """
                Se crea un vector para guardar los Tipos de Item 
                existentes que no pertenezcan ya al proyecto actual.
                """
                tipos_de_item = []
                """Ciclo que recorre todos los tipos de item en la BD."""
                for t in tipos:
                    if not t in proyecto.tipoItem.all():
                        """Agrega al vector solo si el Tipo de Item no coincide con alguno perteneciente al proyecto."""
                        tipos_de_item.append(t)
                return render(request, "proyecto/importartipo.html", {'tipos': tipos_de_item, 'proyectoid': proyectoid,
                                                                      'mensaje': "Ya existe un tipo de item con ese"
                                                                                 " nombre en el proyecto."})

            """Agrega al proyecto actual los tipos de Item seleccionados."""
            proyecto.tipoItem.add(tipo)
        tipos = proyecto.tipoItem.all()
        tipos_modificable = list(tipos)
        tipos_no_modificable = []
        fasesProyecto = proyecto.fases.all()
        for f in fasesProyecto:
            itemsFase = f.items.all()
            for i in itemsFase:
                if i.tipoItem == tipos and i.estado != "deshabilitado":
                    tipos_modificable.remove(tipos)
                    tipos_no_modificable.append(tipos)
        return render(request, "proyecto/gestionartipodeitem.html",
                      {'proyecto': proyecto, 'tipos_modificable': tipos_modificable,
                       'tipos_no_modificable': tipos_no_modificable, })

    """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
    """Recupera de la BD el proyecto en el que se encuentra el usuario."""
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Verifica que el proyecto no se encuentre cancelado"""
    if proyecto.estado == "cancelado":
        return redirect('proyectoView', id=proyectoid)
    """
    Recupera de la BD todos los Tipos de Item con
    los que cuenta el proyecto en el cual se encuentra el usuario.
     """
    tipos_enel_Proyecto = proyecto.tipoItem.all()
    """Recupera de la BD todos los Tipos de Item creados."""
    tipos = TipodeItem.objects.all()
    """
    Se crea un vector para guardar los Tipos de Item 
    existentes que no pertenezcan ya al proyecto actual.
    """
    tipos_de_item = []
    """Ciclo que recorre todos los tipos de item en la BD."""
    for t in tipos:
        if not t in proyecto.tipoItem.all():
            """Agrega al vector solo si el Tipo de Item no coincide con alguno perteneciente al proyecto."""
            tipos_de_item.append(t)
    """Renderiza la pagina cargandola con los Tipos de Item disponibles para importar."""
    proyectoid = request.GET.get('proyectoid')
    return render(request, "proyecto/importartipo.html", {'tipos': tipos_de_item, 'proyectoid': proyectoid})


def remover_tipo_de_item(request, proyectoid, tipoid):
    """
       **remover_tipo_de_item:**
        View para remover un tipo de Item
    """
    if request.method == "GET":
        """
        Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario
        Recupera de la BD el proyecto en el que se encuentra el usuario.
        """
        # proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            """Redireccionar al no contar con los permisos"""
            return redirect('/permissionError/')
        tipo = TipodeItem.objects.get(id=tipoid)

        """Remueve del proyecto actual los tipos de Item seleccionados."""
        proyecto.tipoItem.remove(tipo)
        proyecto.save()
        tipos = proyecto.tipoItem.all()
        tipos_modificable = list(tipos)
        tipos_no_modificable = []
        fasesProyecto = proyecto.fases.all()
        for f in fasesProyecto:
            itemsFase = f.items.all()
            for i in itemsFase:
                if i.tipoItem == tipos and i.estado != "deshabilitado":
                    tipos_modificable.remove(tipos)
                    tipos_no_modificable.append(tipos)
        return render(request, "proyecto/gestionartipodeitem.html",
                      {'proyecto': proyecto, 'tipos_modificable': tipos_modificable,
                       'tipos_no_modificable': tipos_no_modificable, })


def ProyectoFinalizar(request, proyectoid):
    """
         **ProyectoFinalizar:**
         View para finalizar el proyecto. Es necesario que el usuario
         sea gerente del proyecto y que (indirectamente) haya iniciado
         sesion.
    """
    if request.method == "GET":
        """Obtener proyecto"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            """Redireccionar al no contar con los permisos"""
            return redirect('/permissionError/')
        """Obtener fases del proyecto"""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        """Verificar que el proyecto pueda ser finalizado"""
        finalizar = True
        """Recorrer fases del proyecto"""
        for f in fasesProyecto:
            """Si la fase no esta cerrada"""
            if not f.estado == "cerrada":
                """No es posible finalizar el proyecto"""
                finalizar = False
                """Romper ciclo"""
                break

        """Si es posible finalizar el proyecto"""
        if finalizar:
            """Actualizar estado"""
            proyecto.estado = "finalizado"
            """Guardar"""
            proyecto.save()

        """Redireccionar a vista de proyecto"""
        return redirect('proyectoView', id=proyectoid)


def formActaProyecto(request, proyectoid):
    """
    **formRoturaLineaBase:**
    Vista utilizada para garantizar un formulario para solicitar
    la rotura de linea base.
    Solicita que el usuario que realiza el request cuente
    con el permiso para solicitar rotura de lineas base en la fase
    correspondiente y que (indirectamente) haya
    iniciado sesion.
    """

    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Renderizar html"""
        return render(request, "proyecto/FormularioFinalProyecto.html", {'proyecto': proyecto})
    if request.method == "POST":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        descripcion = request.POST.get('descripcion')
        fecha_fin = request.POST.get('fechafin')
        """Se crea un objeto de tipo acta"""
        acta = ActaInforme.objects.create(justificacion=descripcion, fechafin=fecha_fin)
        """Se guarda el objeto"""
        acta.save()
        """Se agrega el al proyecto"""
        proyecto.acta.add(acta)
        """Guardar cambios"""
        proyecto.save()

        return redirect('proyectoView', id=proyectoid)


def reporte(request, proyectoid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Renderizar html"""
        return render(request, "proyecto/Reporte.html", {'proyecto': proyecto})
    if request.method == "POST":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        fecha_ini = request.POST.get('fechainicio')
        fecha_fin = request.POST.get('fechafin')
        fases = proyecto.fases.all()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
        r = ReporteProyecto()
        response.write(r.run(proyectoid, fases, fecha_ini, fecha_fin))
        return response
