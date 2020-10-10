from django.shortcuts import render, redirect

from proyecto.models import Proyecto, Fase, TipodeItem, Item, FaseUser, User, Rol, Relacion, LineaBase, Files, RoturaLineaBase, RoturaLineaBaseComprometida
from guardian.shortcuts import assign_perm, remove_perm
from proyecto.views import proyectoView, faseView
import boto3
import reversion
from datetime import datetime
from reversion.models import Revision, Version

from django.db.models import Q
from collections import deque
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
import reversion
from django.db import transaction
import threading
from fase.tasks import sendEmailViewFase


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
        fases = proyecto.fases.all()
        fasesUser = []
        for f in fases:
            if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente", proyecto)):
                fasesUser.append(f)
        """Redirigir a la vista del proyecto correspondiente."""
        return render(request, 'proyecto/proyectoListarFases.html', {'proyecto': proyecto, 'fases': fases,
                                                                     'fasesUser': sorted(fasesUser, key=lambda x: x.id,
                                                                                         reverse=False), })
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


def faseVerProyectoInicializado(request, faseid, proyectoid):
    if request.method == 'GET':
        """Proyecto en el cual crear la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        items = fase.items.exclude(estado="deshabilitado").order_by('id')
        tipos = fase.tipoItem.all()
        return render(request, 'fase/FaseProyectoInicializado.html', {'proyecto': proyecto, 'fase': fase,
                                                                      'items': items, 'tipos': tipos,
                                                                      })


def faseUsers(request, faseid, proyectoid):
    if request.method == 'GET':
        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("view_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        roles = proyecto.roles.all()
        usuarios = []
        rolesUser = []
        for r in roles:
            fasesUser = r.faseUser.all()
            for f in fasesUser:
                if f.fase == fase:
                    usuarios.append(f.user)
                    rolesUser.append(r)

        cant_roles_proyecto = roles.count()
        user_sin_repetidos = []
        roles_por_user = []
        cant_roles_por_user = []
        contador_roles_por_user = 0
        for u, r in zip(usuarios, rolesUser):
            if not u in user_sin_repetidos:
                user_sin_repetidos.append(u)
                cadena = ""
                for uu, rr in zip(usuarios, rolesUser):
                    if u == uu:
                        cadena = cadena + rr.nombre + ', '
                        contador_roles_por_user = contador_roles_por_user + 1
                cadena = cadena[:-2]
                roles_por_user.append(cadena)
                cant_roles_por_user.append(contador_roles_por_user)
                contador_roles_por_user = 0
        cant_user = len(user_sin_repetidos)
        cant_usuarios_proyecto = len(proyecto.usuarios.all())
        """Verificar si se puede ser agregando usuarios a la fase. Debe tomar en cuenta la cantidad de usuarios en el proyecto"""
        if cant_user == cant_usuarios_proyecto:
            agregar_mas_users = False
        else:
            agregar_mas_users = True
        """Template a renderizar: fase.html con parametros -> fase, proyecto, items de fase."""
        return render(request, 'fase/faseUsers.html', {'fase': fase, 'proyecto': proyecto,
                                                       'userRol': zip(user_sin_repetidos, roles_por_user,
                                                                      cant_roles_por_user),
                                                       'cant_user': cant_user,
                                                       'cant_roles_proyecto': cant_roles_proyecto,
                                                       'agregar_mas_users': agregar_mas_users})
    return render(request, "fase/faseUsers.html")


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
            return render(request, 'home.html', {'proyectoid': proyectoid, 'faseid': faseid,
                                                 'mensaje': "No se puede modificar la fase, el proyecto"
                                                            " no se encuentra en estado pendiente."})
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
    #fase._history_date = datetime.now()
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
        return render(request, 'home.html', {'proyectoid': proyectoid, 'faseid': faseid,
                                             'mensaje': "No se puede deshabilitar la fase,"
                                                        " el proyecto no se encuentra en estado pendiente."})

    """Establecer el estado de la fase como deshabilitada."""
    fase.estado = "deshabilitada"
    #fase._history_date = datetime.now()
    """Guardar"""
    fase.save()
    fases = proyecto.fases.all()
    fasesUser = []
    for f in fases:
        if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente", proyecto)):
            fasesUser.append(f)
    """Redirigir a la vista del proyecto correspondiente."""
    return render(request, 'proyecto/proyectoListarFases.html', {'proyecto': proyecto, 'fases': fases,
                                                                 'fasesUser': sorted(fasesUser, key=lambda x: x.id,
                                                                                     reverse=False), })


def FaseConfigInicializada(request, proyectoid, faseid):
    """Fase a visualizar."""

    """Proyecto en el cual crear la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)

    fase = Fase.objects.get(id=faseid)
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
    """Template a renderizar: fase.html con parametros -> fase, proyecto, items de fase."""
    return render(request, 'fase/faseConfiguracionInicializada.html',
                  {'fase': fase, 'proyecto': proyecto, 'items': items,
                   'userRol': zip(user_sin_repetidos, roles_por_user),
                   'cant_user': cant_user,
                   })


def FaseAddUser(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        usuarios = proyecto.usuarios.all()
        usuarios = list(usuarios)
        fasesUsers = FaseUser.objects.all()
        for fu in fasesUsers:
            if fu.fase == fase:
                if fu.user in usuarios:
                    # Removemos los usuarios que ya forman parte de la fase
                    usuarios.remove(fu.user)
        roles = proyecto.roles.all()

        return render(request, 'fase/faseAddUser.html',
                      {'usuarios': usuarios, 'roles': roles, 'fase': fase, 'proyecto': proyecto})
    else:
        proyectoid = request.POST.get('proyectoid')
        faseid = request.POST.get('faseid')
        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """POST request, captura el usuario, el rol y las fases para asignar el mismo"""
        """ID User"""
        userid = request.POST.get('users')
        """ID rol"""
        rolid = request.POST.get('roles')

        """Usuario a ser asignado el rol"""
        user = User.objects.get(id=userid)
        """Rol a ser asignado"""
        rol = Rol.objects.get(id=rolid)
        """Permisos del rol"""
        grupo = rol.perms
        permisos = grupo.permissions.all()
        codenames = []
        for p in permisos:
            codenames.append(p.codename)

        """Crear asociacion entre fase y usuario"""
        faseUser = FaseUser.objects.create(user=user, fase=fase)

        for c in codenames:
            """Asignar los permisos del rol al grupo, en la fase correspondiente"""
            assign_perm(c, grupo, fase)
            """Asignar el grupo al usuario"""
            user.groups.add(grupo)
            user.save()
        """Agregar asociacion al rol"""
        rol.faseUser.add(faseUser)
        rol.save()
        if proyecto.estado == "pendiente":
            """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
            return redirect('faseUsers', faseid=faseid, proyectoid=proyectoid)
        elif proyecto.estado == "inicializado":
            return redirect('faseUsers', faseid=faseid, proyectoid=proyectoid)


def FaseRemoveUser(request, proyectoid, faseid, userid):
    if request.method == 'GET':

        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        usuario = User.objects.get(id=userid)
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        roles = proyecto.roles.all()
        roles_del_user = []
        for r in roles:
            fasesUser_rol = r.faseUser.all()
            for fu in fasesUser_rol:
                if fu.fase == fase and fu.user == usuario:
                    roles_del_user.append(r)

        for ru in roles_del_user:
            """Eliminar asociacion entre fase y usuario"""
            ru.faseUser.filter(user=usuario, fase=fase).delete()
            """Permisos del rol"""
            grupo = ru.perms
            permisos = grupo.permissions.all()
            codenames = []
            for p in permisos:
                codenames.append(p.codename)
            for c in codenames:
                """Asignar los permisos del rol al grupo, en la fase correspondiente"""
                remove_perm(c, usuario, fase)

        usuario.save()

        if proyecto.estado == "pendiente":
            """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
            return redirect('faseUsers', faseid=faseid, proyectoid=proyectoid)
        elif proyecto.estado == "inicializado":
            return redirect('faseUsers', faseid=faseid, proyectoid=proyectoid)


def faseRolAsignar(request, proyectoid, faseid, userid):
    """
       **faseRolAsignar:**
        Vista utilizada para asignar roles del proyecto a usuarios.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para asignar roles del proyecto dento de la fase"""
    if request.method == 'GET':
        """Proyecto ID"""
        # proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        usuario = User.objects.get(id=userid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Lista de roles del proyecto"""
        roles = proyecto.roles.all()
        roles_disponibles = list(roles)
        for r in roles:
            fasesUser_rol = r.faseUser.all()
            for fu in fasesUser_rol:
                if fu.fase == fase and fu.user == usuario:
                    roles_disponibles.remove(r)

        """
        Template a renderizar: faseRolAsignar.html con parametros -> roles
        ,usuarios y fases del proyecto,
         ademas de proyectoid
         """
        return render(request, "fase/faseRolAsignar.html",
                      {'fase': fase, 'usuario': usuario, 'roles': roles_disponibles, 'proyecto': proyecto, })

    fase = Fase.objects.get(id=faseid)
    """Proyecto en el cual se encuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """POST request, captura el usuario, el rol y las fases para asignar el mismo"""
    """ID rol"""
    rolid = request.POST.get('rol')

    """Usuario a ser asignado el rol"""
    user = User.objects.get(id=userid)
    """Rol a ser asignado"""
    rol = Rol.objects.get(id=rolid)
    """Permisos del rol"""
    grupo = rol.perms
    permisos = grupo.permissions.all()
    codenames = []
    for p in permisos:
        codenames.append(p.codename)

    """Crear asociacion entre fase y usuario"""
    faseUser = FaseUser.objects.create(user=user, fase=fase)

    for c in codenames:
        """Asignar los permisos del rol al grupo, en la fase correspondiente"""
        assign_perm(c, user, fase)
        """Asignar el grupo al usuario"""

    user.save()
    """Agregar asociacion al rol"""
    rol.faseUser.add(faseUser)
    rol.save()
    if proyecto.estado == "pendiente":
        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        return redirect('faseUsers', faseid=faseid, proyectoid=proyectoid)
    elif proyecto.estado == "inicializado":
        return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)


def faseRolRemover(request, proyectoid, faseid, userid):
    """
       ** proyectoRolRemover:**
        Vista utilizada para remover roles del proyecto de usuarios.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para remover roles del proyecto"""
    if request.method == 'GET':
        """Proyecto ID"""
        # proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        usuario = User.objects.get(id=userid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Lista de roles del proyecto"""
        roles = proyecto.roles.all()
        roles_del_user = []
        for r in roles:
            fasesUser_rol = r.faseUser.all()
            for fu in fasesUser_rol:
                if fu.fase == fase and fu.user == usuario:
                    roles_del_user.append(r)

        """
        Template a renderizar: faseRolAsignar.html con parametros -> roles
        ,usuarios y fases del proyecto,
         ademas de proyectoid
         """
        cantidad_roles = len(roles_del_user)
        return render(request, "fase/faseRolRemover.html", {'fase': fase, 'usuario': usuario, 'roles': roles_del_user,
                                                            'proyecto': proyecto, 'cant_roles': cantidad_roles})

    """POST request, captura el usuario, el rol y las fases para remover"""

    proyecto = Proyecto.objects.get(id=proyectoid)
    fase = Fase.objects.get(id=faseid)
    usuario = User.objects.get(id=userid)
    rolid = request.POST.get('rol')
    """Rol a remover"""
    rol = Rol.objects.get(id=rolid)

    """Eliminar asociacion entre fase y usuario"""
    rol.faseUser.filter(user=usuario, fase=fase).delete()
    """Permisos del rol"""
    grupo = rol.perms
    permisos = grupo.permissions.all()
    codenames = []
    for p in permisos:
        codenames.append(p.codename)
    for c in codenames:
        """Asignar los permisos del rol al grupo, en la fase correspondiente"""
        remove_perm(c, usuario, fase)

    usuario.save()
    """ Se le asigna el permiso para ver la fase ya que el usuario posee otro rol
        Porque no deja remover el ultimo rol --> se debe eliminar al usuario de la fase
    """
    assign_perm("view_fase", usuario, fase)

    if proyecto.estado == "pendiente":
        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        return redirect('faseTipoItem')
    elif proyecto.estado == "inicializado":
        return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)


def FaseGestionTipoItem(request, faseid, proyectoid):
    if request.method == 'GET':
        # proyectoid = request.GET.get('proyectoid')
        # faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        tipos = fase.tipoItem.all()
        tipos_enel_proyecto = proyecto.tipoItem.all()
        if len(tipos) == len(tipos_enel_proyecto):
            """No se puede agregar más tipos a la fase"""
            add_tipo = False
        else:
            add_tipo = True
        tipos_removible = list(tipos)
        tipos_no_removible = []
        itemsFase = fase.items.all()
        for t in tipos:
            for i in itemsFase:
                if i.tipoItem == t and i.estado != "deshabilitado":
                    tipos_removible.remove(t)
                    tipos_no_removible.append(t)
                    break

        return render(request, "fase/faseGestionTipoItem.html",
                      {'fase': fase, 'proyecto': proyecto, 'tipos_removible': tipos_removible,
                       'tipos_no_removible': tipos_no_removible, 'add_tipo': add_tipo})


def FaseAddTipoItem(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        tiposItem = proyecto.tipoItem.all()
        # tiposItem = list(tiposItem)
        tipositem_fase = fase.tipoItem.all()
        tipositem_fase = list(tipositem_fase)
        tipos_agregables = []
        for ti in tiposItem:
            if not ti in tipositem_fase:
                tipos_agregables.append(ti)

        return render(request, 'fase/faseAddTipoItem.html',
                      {'tiposItem': tipos_agregables, 'fase': fase, 'proyecto': proyecto})
    else:
        proyectoid = request.POST.get('proyectoid')
        faseid = request.POST.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        tipoItem = request.POST.get('tipoItem')
        tipo = TipodeItem.objects.get(id=tipoItem)
        fase.tipoItem.add(tipo)
        #fase._history_date = datetime.now()
        fase.save()
        if proyecto.estado == "pendiente":
            """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
            return redirect('faseTipoItem', faseid=faseid, proyectoid=proyectoid)

        return redirect('faseTipoItem', faseid=faseid, proyectoid=proyectoid)

def FaseRemoveTipoItem(request, proyectoid, faseid, tipoid):
    if request.method == 'GET':

        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        tipo_remover = TipodeItem.objects.get(id=tipoid)
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        tipos_enla_fase = fase.tipoItem.all()
        itemsFase = fase.items.all()
        for i in itemsFase:
            if i.tipoItem == tipo_remover and i.estado != "deshabilitado":
                return render(request, "fase/faseRemoveTipoItem.html",
                              {'tipos': tipo_remover, 'proyecto': proyecto, 'fase': fase,
                               'mensaje': "El tipo de item ya ha sido utilizado.No es posible removerlo.", })

            """Remueve del proyecto actual los tipos de Item seleccionados."""
        fase.tipoItem.remove(tipo_remover)
        fase.save()
        if proyecto.estado == "pendiente":
            """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
            return redirect('faseTipoItem', faseid=faseid, proyectoid=proyectoid)

        return redirect('faseTipoItem', faseid=faseid, proyectoid=proyectoid)



def fasesDeshabilitadas(request):
    proyectoid = request.GET.get('proyectoid')
    """Proyecto en el cual se encuentra la fase."""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Fases del proyecto para enviar al template que muestra la informacion"""
    fases = proyecto.fases.all()
    fasesDes = []
    for f in fases:
        if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente",
                                                                           proyecto)) and f.estado == "deshabilitada":
            fasesDes.append(f)

    return render(request, 'fase/fasesDeshabilitadas.html', {'proyecto': proyecto, 'fasesDes': fasesDes, })


@transaction.atomic()
@reversion.create_revision()
def itemCrear(request):
    """
               **itemCrear:**
                Vista utilizada para Crear Items.
                Solicita que el usuario que realiza el request
                cuente con los permisos para crear items o
                 de gerente del proyecto y que
                 (indirectamente) haya iniciado sesion.
    """
    seleccion = None
    """POST request, recibe los datos ingresados por el usuario para la creacion del item."""
    if request.method == "POST":
        # doc = request.FILES.get('file')
        doc = request.FILES.getlist("file[]")

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
            dato = request.POST
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

            """Almacenar la informacion de cada campo extra proveido por el usuario."""
            item.estado = "en desarrollo"
            for c in obj.campo_extra:
                item.campo_extra_valores.append(dato[c])

            for f in doc:
                archivo = Files.objects.create(file=f, item=item)
                archivo.save()
                item.archivos.append(f)
            """Guardar."""
            item.save()
            reversion.set_comment("holibb...")

            """Agregar item a fase."""
            fase.items.add(item)
            """Redirigir a la vista de la fase correspondiente."""
            return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)
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
    tipos = fase.tipoItem.all()

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
    if not (request.user.has_perm("ver_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
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
                   'archivos': list(item.archivos),
                   'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),
                   'pendientePermiso': request.user.has_perm("establecer_itemPendienteAprob", fase),
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
    itemid = request.GET.get('itemid')
    """
    Template a renderizar: gestionItem.html 
    con parametro -> proyectoid, faseid, itemid
    """
    return render(request, 'item/gestionItem.html', {'proyectoid': proyectoid, 'faseid': faseid, 'itemid': itemid, })


def itemConfigurar(request, itemid, faseid, proyectoid):
    if request.method == "GET":
        """Fase en el cual se encuentra el item."""
        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra el item."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Item a visualizar."""
        item = Item.objects.get(id=itemid)
        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("ver_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        return render(request, "item/itemConfiguracion.html",
                      {'fase': fase, 'item': item, 'proyecto': proyecto, 'archivos': list(item.archivos),
                       'campos': zip(item.tipoItem.campo_extra,
                                     item.campo_extra_valores), })


@transaction.atomic()
@reversion.create_revision()
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
        """Fase en la cual se encuentra el item a modificar."""
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

        # if item.estado == "pendiente de aprobacion" or item.estado == "aprobado" or item.estado == "en linea base":
        # mensaje = "El estado actual del item no permite la modificacion del mismo."
        """
        En caso contrario, no permite la modificacion del item y 
        vuelve a gestion de Item con mensaje de error.
        Template a renderizar: gestionItem.html con 
        parametros -> proyectoid, faseid, itemid y mensaje de error.
        """
        # return redirect('proyectoView', id=proyectoid)

        """
        Template a renderizar: itemModificar 
        con parametros -> proyectoid, faseid, item y campos extra.
        """
        return render(request, 'item/itemModificar.html',
                      {'faseid': faseid, 'proyectoid': proyectoid, 'item': item,
                       'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),
                       'archivos': list(item.archivos),
                       'pendientePermiso': request.user.has_perm("establecer_itemPendienteAprob", fase),
                       'aprobadoPermiso': request.user.has_perm("aprove_item", fase),
                       'choices': ['en desarrollo', 'pendiente de aprobacion', 'aprobado', ], })

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
    doc = request.FILES.getlist("file[]")

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
    """Actualizar el numero de version del item"""
    num = Item.objects.last()
    item.version = num.version + 1

    cont = 0
    """Actualizar campos extra del item."""
    for c in item.tipoItem.campo_extra:
        item.campo_extra_valores[cont] = dato[c]
        cont = cont + 1
    "Actualizar Archivos del item"
    for f in doc:
        archivo = Files.objects.create(file=f, item=item)
        item.archivos.append(f)

    # item._history_date = datetime.now()

    """Guardar"""
    item.save()
    reversion.set_comment("modificada...")

    """
    Template a renderizar: gestionItem con 
    parametro -> proyectoid, faseid, itemid
    """
    return redirect('proyectoView', id=dato['proyectoid'])


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

    "Verificar que si el item esta aprobado, no debe cambiar su estado si este ya posee relaciones."
    if item.estado == "aprobado":
        relaciones = item.relaciones.exclude(estado="deshabilitado")
        cambiar_estado = True
        for r in relaciones:
            relacion = Relacion.objects.get(item_from=item, item_to=r)
            if relacion.tipo == "padre" or relacion.tipo == "antecesor":
                cambiar_estado = False
                break

        if not cambiar_estado:
            mensaje_error = "No es posible cambiar el estado del item ya que este cuenta con relaciones."
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
                           'mensaje_error': mensaje_error, })

    mensaje = ""
    mensaje_error = ""
    """Verificar que el estado no sea el mismo que ya poseia."""
    if item.estado != dato['estado']:
        """Si el nuevo estado es pendiente de aprobacion."""
        if dato['estado'] == "pendiente de aprobacion":
            """Verificar que el usuario cuente con los permisos para asignar ese estado."""
            if not (request.user.has_perm("establecer_itemPendienteAprob", fase)) and not (
                    request.user.has_perm("is_gerente", proyecto)):
                """Al no contar con los permisos, niega el acceso, redirigiendo."""
                return redirect('/permissionError/')

            "Envio de correo a los usuarios que cuentan con el permiso de aprobar item"
            fuser = FaseUser.objects.filter(fase=fase)
            for u in fuser:
                if u.user.has_perm("aprove_item", fase):
                    mail = u.user.email
                    name = u.user.username
                    sendEmailViewFase.delay(mail, name, item.nombre, fase.nombre)


        """Si el nuevo estado es en desarrollo."""
        if dato['estado'] == "en desarrollo":
            """Verificar que el usuario cuente con los permisos para asignar ese estado."""
            if not (request.user.has_perm("establecer_itemDesarrollo", fase)) and not (
                    request.user.has_perm("is_gerente", proyecto)):
                """Al no contar con los permisos, niega el acceso, redirigiendo."""
                return redirect('/permissionError/')

        """Si el nuevo estado es aprobado."""
        if dato['estado'] == "aprobado":
            """Verificar que el usuario cuente con los permisos para asignar ese estado."""
            if not (request.user.has_perm("aprove_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
                """Al no contar con los permisos, niega el acceso, redirigiendo."""
                return redirect('/permissionError/')

            """Para aprobar el item es necesario identificar que tenga alguna relacion con un antecesor
            que se encuentre en una linea base cerrada, o bien con un padre(o hijo) que este aprobado."""

            """Filtrar fases no deshabilitadas del proyecto."""
            fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
            """Inicializar contador."""
            cont = 0
            """Inicializar bandera para validar si un item pertenece a la primera fase."""
            esPrimeraFase = False
            """Recorrer las fases del proyecto."""
            for fp in fasesProyecto:
                """Aumenta el contador por cada fase."""
                cont = cont + 1
                """Si la fase encontrada es igual a la actual"""
                if fp == fase:
                    """Si el contador es igual a 1."""
                    if cont == 1:
                        """Setear bandera en true."""
                        esPrimeraFase = True
                        """ROmper ciclo."""
                        break

            "Solo verificar si son items posteriores a la primera fase."
            if esPrimeraFase == False:
                """Variable para verificar si se posee una fase anterior."""
                anterior = None
                """Recorrer fases del proyecto."""
                for fp in fasesProyecto:
                    """Si la fase encontrada es igual a la fase actual."""
                    if fp == fase:
                        """Romper ciclo"""
                        break
                    """Sino, actualizar variable de fase anterior."""
                    anterior = fp

                """Bandera para verificar si un item esta listo para ser aprobado."""
                listoAprobacion = False
                """Obtener las relaciones del item."""
                itemsRelacionados = item.relaciones.all()
                """Recorrer las relaciones."""
                for ir in itemsRelacionados:
                    """Obtener relacion objeto."""
                    relacion = Relacion.objects.get(item_from=item, item_to=ir)
                    """Si el item perteece a la fase anterior y su estado es en linea base."""
                    if relacion.fase_item_to == anterior and ir.estado == "en linea base":
                        """Obtener linea base."""
                        lineaBaseItem = LineaBase.objects.get(items__id=ir.id)
                        """Si el estado de la linea base es cerrada."""
                        if lineaBaseItem.estado == "cerrada":
                            """Setear bandera en true."""
                            listoAprobacion = True
                            """Romper ciclo."""
                            break
                    """Si el item peretenece a la fase actual y su estado es aprobado, o bien en linea base."""
                    if relacion.fase_item_to == fase and (ir.estado == "aprobado" or ir.estado == "en linea base"):
                        """Setear bandera en true."""
                        listoAprobacion = True
                        break

                """Si el item no esta listo para aprobarse."""
                if listoAprobacion == False:
                    mensaje_error = "No es posible aprobar el item ya que este no posee una relacion con un item antecesor" \
                                    "en linea base cerrada, o bien, con un item padre aprobado."
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
                                   'mensaje_error': mensaje_error, })

        """Verificar que el estado del proyecto sea inicializado."""
        if proyecto.estado != "inicializado":
            """En caso contrario, no permite cambiar el estado del item y redirige a la vista de fase."""
            return redirect('faseView', faseid=dato['faseid'], proyectoid=dato['proyectoid'])

        mensaje = "Estado actualizado correctamente."
        """Actualiza estado del item."""
        item.estado = dato['estado']
        #item._history_date = datetime.now()
        """Guardar."""
        item.save()

    """
    Template a renderizar: item.html 
    con parametros -> faseid, proyectoid, item, proyecto, campos extra de item,
    permiso para establecer item como pendiente de aprobacion, 
    permiso para establecer item como parobado, choices
    con los distintos estados del item y el mensaje correspondiente.
    """
    return render(request, 'item/itemModificar.html',
                  {'faseid': dato['faseid'], 'proyectoid': dato['proyectoid'], 'item': item,
                   'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),
                   'pendientePermiso': request.user.has_perm("establecer_itemPendienteAprob", fase),
                   'aprobadoPermiso': request.user.has_perm("aprove_item", fase),
                   'choices': ['en desarrollo', 'pendiente de aprobacion', 'aprobado', ],
                   'mensaje_error': mensaje_error, })


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
        return redirect('proyectoView', id=proyectoid)

    """Verificar que el estado del item sea en desarrollo."""
    if item.estado == "pendiente de aprobacion" or item.estado == "aprobado" or item.estado == "en linea base":
        mensaje = "El estado actual del item no permite la deshabilitacion del mismo."
        """
        En caso contrario niega la deshabilitacion del mismo y 
        vuelve a gestion de item mostrando un mensaje de error.
        Template a renderizar gestionItem.html con parametros -> proyectoid, faseid, itemid y mensaje de error.
        """
        return render(request, 'home.html',
                      {'proyectoid': proyectoid, 'faseid': faseid, 'itemid': itemid, 'mensaje': mensaje, })

    """VERIFICAR SI ES POSIBLE DESHABILITAR EL ITEM TENIENDO EN CUENTA SUS RELACIONES."""
    """Obtener relaciones."""
    relaciones_item_deshabilitar = item.relaciones.all()
    """Bandera para verificar si se puede deshabilitar el item."""
    ok_deshabilitar = True
    """Recorrer relaciones."""
    for rd in relaciones_item_deshabilitar:
        """Si el estado del item es aprobado o bien, en linea base."""
        if rd.estado == "aprobado" or rd.estado == "en linea base":
            "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
            relaciones_item_afectado = rd.relaciones.exclude(id=item.id)
            """Bandera para identificar si el item puede seguir sin la relacion con el item a deshabilitar."""
            ok_sobrevivir = False
            for r in relaciones_item_afectado:
                relacion = Relacion.objects.get(item_from=r, item_to=rd)
                if relacion.tipo == "padre" and (r.estado == "aprobado" or r.estado == "en linea base"):
                    ok_sobrevivir = True
                    break
                if relacion.tipo == "antecesor" and r.estado == "en linea base":
                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                    if lineaBaseItem.estado == "cerrada":
                        ok_sobrevivir = True
                        break

            "Si un item afectado no sobrevive ya no es posible deshabilitar el item deseado."
            if not ok_sobrevivir:
                ok_deshabilitar = False

    if ok_deshabilitar:
        for rd in relaciones_item_deshabilitar:
            relaciones_uno = Relacion.objects.get(item_from=item, item_to=rd)
            relaciones_uno.delete()
            relaciones_dos = Relacion.objects.get(item_from=rd, item_to=item)
            relaciones_dos.delete()

        """Establece estado de item como deshabilitado."""
        item.estado = "deshabilitado"
        #item._history_date = datetime.now()
        """Guardar."""
        item.save()
        """Redirige a la vista de la fase correspondiente."""
        return redirect('proyectoView', id=proyectoid)
    """Redirige a la vista de la fase correspondiente."""
    return redirect('proyectoView', id=proyectoid)


def itemVerRelaciones(request, itemid, faseid, proyectoid, mensaje):
    if request.method == 'GET':

        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        varias_fases = False

        anterior = None
        siguiente = None
        if len(fasesProyecto) > 1:
            varias_fases = True
            for fp in fasesProyecto:
                if fp == fase:
                    break
                anterior = fp

            actual = False
            for fp in fasesProyecto:
                if actual == True:
                    siguiente = fp
                    break
                if fp == fase:
                    actual = True

        item_recibido = Item.objects.get(id=itemid)
        """ Recupera la lista de items antecesores a él de la tabla de relaciones"""
        items_antecesores = list(Relacion.objects.filter(tipo="sucesor", item_from=item_recibido))
        # if items_antecesores:
        """ Se encuentra la fase en donde están sus ítems antecesores"""
        # fase_antecesora = items_antecesores[0].fase

        """ Recupera la lista de items sucesores a él de la tabla de relaciones"""
        items_sucesores = list(Relacion.objects.filter(tipo="antecesor", item_from=item_recibido))
        # if items_sucesores:
        """ Se encuentra la fase en donde están sus ítems antecesores"""
        # fase_sucesora = items_sucesores[0].fase

        """ Recupera la lista de items padres de él de la tabla de relaciones"""
        items_padres = list(Relacion.objects.filter(tipo="hijo", item_from=item_recibido))
        """ Sus padres e hijos son de su misma fase"""
        fase_padre_hijo = fase

        """ Recupera la lista de items hijos de él de la tabla de relaciones"""
        items_hijos = list(Relacion.objects.filter(tipo="padre", item_from=item_recibido))
        """ Verificar si el ítem puede establecer relaciones, considerando su estado"""
        puede_relacionarse = False
        if item_recibido.estado == "aprobado" or item_recibido.estado == "en linea base":
            puede_relacionarse = True

        """Verificar si el ítem puede establecer relaciones, verificando que existan ítems disponibles"""
        habilitar_Add_relacion = False
        "Todos los id de las relaciones del item."
        relaciones = item_recibido.relaciones.all()
        relacionesId = []
        for r in relaciones:
            relacionesId.append(r.id)
        "Solo si esta en linea base puede avanzar de fase."
        siguiente = None
        itemsFaseSiguiente = None
        if item_recibido.estado == "en linea base":
            linea_base_item = LineaBase.objects.filter(items=item_recibido)
            if linea_base_item.get().estado == "cerrada":
                fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
                actual = False
                for fp in fasesProyecto:
                    if actual == True:
                        siguiente = fp
                        break
                    if fp == fase:
                        actual = True

                if siguiente is not None:
                    itemsFaseSiguiente = siguiente.items.exclude(
                        Q(estado="deshabilitado") | Q(id__in=relaciones)).order_by(
                        'id')
            else:
                itemsFaseSiguiente = None
        itemsFaseActual = fase.items.exclude(
            Q(estado="deshabilitado") | Q(id=itemid) | Q(id__in=relaciones)).order_by('id')

        "Verifica si hay al menos un ítem con el cual establecer relaciones"
        if itemsFaseActual or itemsFaseSiguiente:
            habilitar_Add_relacion = True

        return render(request, "item/ItemVerRelacion.html", {'proyecto': proyecto, 'fase': fase, 'item': item_recibido,
                                                             'antecesores': items_antecesores,
                                                             'sucesores': items_sucesores,
                                                             'padres': items_padres, 'hijos': items_hijos,
                                                             'faseAnterior': anterior,
                                                             'faseSiguiente': siguiente, 'varias_fases': varias_fases,
                                                             'puede_relacionarse': puede_relacionarse,
                                                             'habilitar_Add_relacion': habilitar_Add_relacion,
                                                             'mensaje': mensaje})


def itemRelacionesRemover(request, itemid, item_rm, faseid, proyectoid):
    """
                  **itemRelacionesRemover:**
                   Vista utilizada para remover relaciones del Item.
                   Solicita que el usuario que realiza el request
                   cuente con los permisos para remover relaciones de
                   items en la fase, o bien, los de gerente del proyecto
                   y que (indirectamente) haya iniciado sesion.
       """
    if request.method == 'GET':
        """ID del proyecto"""
        # proyectoid = request.GET.get('proyectoid')
        """Proyecto en el cual se encuentra el item."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase."""
        # faseid = request.GET.get('faseid')
        """Fase en la cual se encuentra el item."""
        fase = Fase.objects.get(id=faseid)
        # itemid = request.GET.get('itemid')
        # itemid_final = request.GET.get('itemid_final')
        item_inicio = Item.objects.get(id=itemid)
        item_final_remover = Item.objects.get(id=item_rm)
        ok_remover_final = False
        """Bandera para verificar si se puede remover la relacion."""
        ok_remover_inicio = False
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        cont = 0
        esPrimeraFase = False
        for fp in fasesProyecto:
            cont = cont + 1
            if fp == fase:
                if cont == 1:
                    esPrimeraFase = True
                    break
        if not esPrimeraFase:
            """Si el item cuenta con un estado aprobado o bien, en linea base."""
            if item_final_remover.estado == "aprobado" or item_final_remover.estado == "en linea base":
                "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
                relaciones_item_remover = item_final_remover.relaciones.exclude(id=item_inicio.id)
                """Recorrer relaciones."""
                for r in relaciones_item_remover:
                    """Obtener relacion objeto."""
                    relacion = Relacion.objects.get(item_from=r, item_to=item_final_remover)
                    """Si la relacion es de tipo padre y el estado del item es aprobado o en linea base."""
                    if relacion.tipo == "padre" and (r.estado == "aprobado" or r.estado == "en linea base"):
                        """Setear bandera en true."""
                        ok_remover_final = True
                        """Romper ciclo."""
                        break
                    """Si la relacion es de tipo antecesor y el estado del item es en linea base"""
                    if relacion.tipo == "antecesor" and r.estado == "en linea base":
                        """Obtener linea base."""
                        lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                        """Si el estado de la linea base es cerrada."""
                        if lineaBaseItem.estado == "cerrada":
                            """Setear bandera en true."""
                            ok_remover_final = True
                            """ROmper ciclo."""
                            break
            else:
                """Si no cuenta con estado aprobado o en linea base"""
                """Setear bandera en true."""
                ok_remover_final = True

            "El mismo testeo para el item del cual queremos remover la relacion."

            "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
            relaciones_item_inicio = item_inicio.relaciones.exclude(id=item_final_remover.id)
            """Recorrer relaciones."""
            for r in relaciones_item_inicio:
                """Obtener relacion objeto."""
                relacion = Relacion.objects.get(item_from=r, item_to=item_inicio)
                """Si la relacion es de tipo padre y el estado del item es aprobado o en linea base."""
                if relacion.tipo == "padre" and (r.estado == "aprobado" or r.estado == "en linea base"):
                    """Setear bandera en true."""
                    ok_remover_inicio = True
                    """Romper ciclo."""
                    break
                """Si la relacion es de tipo antecesor y el estado del item es en linea base"""
                if relacion.tipo == "antecesor" and r.estado == "en linea base":
                    """Obtener linea base."""
                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                    """Si el estado de la linea base es cerrada."""
                    if lineaBaseItem.estado == "cerrada":
                        """Setear bandera en true."""
                        ok_remover_inicio = True
                        """Romper ciclo."""
                        break
        else:
            ok_remover_inicio = True
            ok_remover_final = True

        """Si ambas banderas son true, se rompe la relacion."""
        if ok_remover_inicio and ok_remover_final:
            """Obtener relacion objeto."""
            relaciones_uno = Relacion.objects.get(item_from=item_inicio, item_to=item_final_remover)
            """Eliminar relacion objeto."""
            relaciones_uno.delete()
            """Obtener relacion objeto."""
            relaciones_dos = Relacion.objects.get(item_from=item_final_remover, item_to=item_inicio)
            """Eliminar relacion objeto."""
            relaciones_dos.delete()
            """Redirigir a la vista itemVerRelaciones."""
            return redirect('itemVerRelaciones', itemid=item_inicio.id, faseid=faseid, proyectoid=proyectoid,
                            mensaje=' ')

        """Redirigir a la vista itemVerRelaciones sin romper la relacion."""
        return redirect('itemVerRelaciones', itemid=item_inicio.id, faseid=faseid, proyectoid=proyectoid, mensaje=' ')


@transaction.atomic()
@reversion.create_revision()
def itemAddRelacion(request):
    """
                   **itemAddRelacion:**
                    Vista utilizada para agregar relaciones al Item.
                    Solicita que el usuario que realiza el request
                    cuente con los permisos para agregar relaciones
                    a items en la fase, o bien, los de gerente del proyecto
                    y que (indirectamente) haya iniciado sesion.
         """

    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de la fase"""
        faseid = request.GET.get('faseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """ID del item"""
        itemid = request.GET.get('itemid')
        """Obtener el item"""
        item = Item.objects.get(id=itemid)
        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("relacionar_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        if item.estado != "aprobado" and item.estado != "en linea base":
            return redirect('itemVerRelaciones', itemid=itemid, faseid=faseid, proyectoid=proyectoid, mensaje=' ')

        "Todos los id de las relaciones del item."
        relaciones = item.relaciones.all()
        """Array auxiliar."""
        relacionesId = []
        """Recorrer relaciones."""
        for r in relaciones:
            """Almacenar id de relaciones."""
            relacionesId.append(r.id)
        "Solo si esta en linea base puede avanzar de fase."
        """Variable correspondiente a la fase siguiente."""
        siguiente = None
        """Items de la fase siguiente."""
        itemsFaseSiguiente = None
        """Si el estado del item es en linea base."""
        if item.estado == "en linea base":
            """Filtrar linea base que aloja al item."""
            linea_base_item = LineaBase.objects.filter(items=item)
            """Si el estsado de la linea base es cerrada."""
            if linea_base_item.get().estado == "cerrada":
                """Obtener las fases del proyecto."""
                fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
                """Bandera para detectar fase actual."""
                actual = False
                """Recorrer fases del proyecto."""
                for fp in fasesProyecto:
                    """Si ya aparecio la fase actual.."""
                    if actual == True:
                        """Almacenar fase siguiente."""
                        siguiente = fp
                        """Romper ciclo."""
                        break
                    """Si encontramos a la fase actual."""
                    if fp == fase:
                        """Setear bandera en true."""
                        actual = True

                """Si fase siguiente no es None."""
                if siguiente is not None:
                    """Obtener items fase siguiente"""
                    itemsFaseSiguiente = siguiente.items.exclude(
                        Q(estado="deshabilitado") | Q(id__in=relaciones)).order_by('id')
            else:
                """SI linea base no esta cerrada no cargar items de la fase siguiente."""
                itemsFaseSiguiente = None
        """Obtener items de la fase actual."""
        itemsFaseActual = fase.items.exclude(
            Q(estado="deshabilitado") | Q(id=itemid) | Q(id__in=relaciones)).order_by('id')

        """Renderizar item/itemAddRelacion/html."""
        return render(request, 'item/itemAddRelacion.html',
                      {'proyecto': proyecto, 'fase': fase, 'item': item,
                       'itemsFaseSiguiente': itemsFaseSiguiente, 'itemsFaseActual': itemsFaseActual,
                       'faseSiguiente': siguiente, })

    else:
        """POST REQUEST"""

        """ID del proyecto"""
        proyectoid = request.POST.get('proyectoid')
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase"""
        faseid = request.POST.get('faseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """ID de item_from"""
        itemIdActual = request.POST.get('itemIdActual')
        """Obtener item."""
        itemActual = Item.objects.get(id=itemIdActual)
        """ID de item_to"""
        itemIdRelacion = request.POST.get('itemIdRelacion')
        """Obtener item."""
        itemRelacion = Item.objects.get(id=itemIdRelacion)
        """IDde fase siguiente."""
        faseSiguiente = request.POST.get('siguiente')
        """FIltrar fases del proyecto apropiadas."""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        """Recorrer Fases del proyecto."""
        for fp in fasesProyecto:
            """Obtener items de fase."""
            items = fp.items.all()
            """Recorrer items."""
            for i in items:
                """Si el item corresponde al item_to"""
                if i == itemRelacion:
                    """Si existe fase siguiente."""
                    if faseSiguiente != "no":
                        """Si fase encontrada igual a fase siguiente."""
                        if int(fp.id) == int(faseSiguiente):
                            """Crear relacion."""
                            Relacion.objects.create(tipo="antecesor", item_from=itemActual, item_to=itemRelacion,
                                                    fase_item_to=fp)
                            """Crear relacion."""
                            Relacion.objects.create(tipo="sucesor", item_from=itemRelacion, item_to=itemActual,
                                                    fase_item_to=fase)
                    """SI se encuentra a la fase actual."""
                    if fp == fase:
                        """Crear relacion."""
                        Relacion.objects.create(tipo="padre", item_from=itemActual, item_to=itemRelacion,
                                                fase_item_to=fp)
                        """Crear relacion."""
                        Relacion.objects.create(tipo="hijo", item_from=itemRelacion, item_to=itemActual,
                                                fase_item_to=fase)

        """CONTROL DE CICLO EN EL GRAFO"""
        cantidad_items_proyecto = 0
        for fp in fasesProyecto:
            cantidad_items_proyecto = cantidad_items_proyecto + int(fp.items.exclude(estado="deshabilitado").count())

        V = cantidad_items_proyecto
        adj = {}
        itemsProyecto = []
        for fp in fasesProyecto:
            itemsFase = fp.items.exclude(estado="deshabilitado").order_by('id')
            for iF in itemsFase:
                itemsProyecto.append(iF)

        itemsProyectoOrd = sorted(itemsProyecto, key=lambda x: x.id, reverse=False)

        for iP in itemsProyectoOrd:
            relaciones_por_item = []
            # relaciones = Relacion.objects.filter((Q(tipo="antecesor") | Q(tipo="padre")) & Q(item_from=iF))
            relaciones = Relacion.objects.filter(item_from=iP)
            for r in relaciones:
                relaciones_por_item.append(int(r.item_to.id))

            adj[int(iP.id)] = relaciones_por_item


        print(adj)
        """SI TIENE UN CICLO ELIMINAR RELACIONES Y REDIRIGIR A VISUALIZACION DE RELACIONES"""
        if isCyclicDisconnected(adj, V):
            relaciones_uno = Relacion.objects.get(item_from=itemActual, item_to=itemRelacion)
            relaciones_uno.delete()
            relaciones_dos = Relacion.objects.get(item_from=itemRelacion, item_to=itemActual)
            relaciones_dos.delete(),
            return redirect('itemVerRelaciones', itemid=itemIdActual, faseid=faseid, proyectoid=proyectoid,
                            mensaje="Error! No se puede relacionar porque genera un ciclo.")
        """SINO MANTENER RELACIONES Y REDIRIGIR A LA VISTA DE RELACIONES."""

        return redirect('itemVerRelaciones', itemid=itemActual.id, faseid=faseid, proyectoid=proyectoid,
                        mensaje=' ')


"""Funcion para agregar Edge"""


def addEdge(adj: dict, u, v):
    adj[u].append(v)
    adj[v].append(u)


"""FUncion auxiliar del algoritmo."""


def isCyclicConnected(adj: dict, s, V,
                      visited: dict):
    # Set parent vertex for every vertex as -1.
    parent = {}
    for key, value in adj.items():
        parent[key] = -1

    # Create a queue for BFS
    q = []

    # Mark the current node as
    # visited and enqueue it
    visited[s] = True
    q.append(s)

    while q != []:

        # Dequeue a vertex from queue and print it
        u = q.pop()

        # Get all adjacent vertices of the dequeued
        # vertex u. If a adjacent has not been visited,
        # then mark it visited and enqueue it. We also
        # mark parent so that parent is not considered
        # for cycle.
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                q.append(v)
                parent[v] = u
            elif parent[u] != v:
                return True

    return False


"""Algoritmo BFS para control de ciclos."""


def isCyclicDisconnected(adj: dict, V):
    # Mark all the vertices as not visited
    visited = {}
    for key, value in adj.items():
        visited[key] = False

    for key, value in adj.items():
        if not visited[key] and isCyclicConnected(adj, key, V, visited):
            return True
    return False


def faseGestionLineaBase(request):
    """
               **itemAddRelacion:**
                Vista utilizada para gestion de lineas base en Fase.
                Solicita que el usuario que realiza el request
                cuente con los permisos para ver lineas base en la fase,
                 o bien, los de gerente del proyecto y que
                 (indirectamente) haya iniciado sesion.
     """
    if request.method == 'GET':
        """ID de pryecto."""
        proyectoid = request.GET.get('proyectoid')
        """ID de fase."""
        faseid = request.GET.get('faseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """"Controla que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("ver_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        """Obtener lineas base de la fase, excluyendo las rotas."""
        lineasBase = fase.lineasBase.exclude(estado="rota")
        """Items disponibles para linea base."""
        items_disponibles = fase.items.filter(estado="aprobado")
        """SI existen items."""
        if items_disponibles:
            """Setear bandera en true."""
            crear_lb = True
        else:
            """Sino, setear bandera en false."""
            crear_lb = False
        """Renderizar fase/faseGestionLineaBase.html"""
        return render(request, "fase/faseGestionLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, 'crear_lb': crear_lb})


def consultarLineaBase(request, proyectoid, faseid, lineaBaseid):
    """
               **consultarLineaBase:**
                Vista utilizada para consultar de lineas base en Fase.
                Solicita que el usuario que realiza el request
                cuente con los permisos para ver lineas base en la fase,
                 o bien, los de gerente del proyecto y que
                 (indirectamente) haya iniciado sesion.
     """
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Obtener items de linea base."""
        items_lb = lineaBase.items.all()  # probablemente hace falta excluir deshabilitados
        """Renderizar fase/lineaBaseConsultar.html"""
        return render(request, "fase/lineaBaseConsultar.html", {'proyecto': proyecto, 'fase': fase,
                                                                'items': items_lb, 'lineaBase': lineaBase, })


def faseAddLineaBase(request):
    """
                   **faseAddLineaBase:**
                    Vista utilizada para agregar lineas base en Fase.
                    Solicita que el usuario que realiza el request
                    cuente con los permisos para crear lineas base en la fase,
                     o bien, los de gerente del proyecto y que
                     (indirectamente) haya iniciado sesion.
         """
    if request.method == "POST":
        """POST REQUEST."""
        """ID de proyecto."""
        proyecto = Proyecto.objects.get(id=request.POST.get('proyectoid'))
        """ID de fase"""
        fase = Fase.objects.get(id=request.POST.get('faseid'))
        """Nombre generado para la linea base"""
        nombre = request.POST.get('nombre')
        """Lista de IDs de items para la linea base"""
        items = request.POST.getlist('items')
        """Crear Linea Base."""
        lineaBase = LineaBase.objects.create(nombre=nombre, estado="abierta", creador=request.user)
        """Recorerr los IDs de items"""
        for i in items:
            """Obtener item."""
            item = Item.objects.get(id=i)
            """Actualizar estado de item."""
            item.estado = "en linea base"
            #item._history_date = datetime.now()
            """Guardar item."""
            item.save()
            """Agregar item a linea base."""
            lineaBase.items.add(item)

        """GUardar Linea Base."""
        lineaBase.save()
        """Agregar linea base a fase."""
        fase.lineasBase.add(lineaBase)
        """Guardar fase."""
        fase.save()

        """Obtener lineas base, excluyendo las rotas.(necesario para el template a renderizar)"""
        lineasBase = fase.lineasBase.exclude(estado="rota")
        """Obtener items aprobados en la fase."""
        items_disponibles = fase.items.filter(estado="aprobado")
        """Si existen items disponibles"""
        if items_disponibles:
            """Se puede crear linea base."""
            crear_lb = True
        else:
            """Si no existen items disponibles, ya no se podra crear linea base."""
            crear_lb = False

        """Renderizar fase/faseGestionLineaBase.html"""
        return render(request, "fase/faseGestionLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'linea'
                                                           'sBase': lineasBase, 'crear_lb': crear_lb})

    """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
    """Recupera de la BD el proyecto en el que se encuentra el usuario."""
    proyecto = Proyecto.objects.get(id=request.GET.get('proyectoid'))
    fase = Fase.objects.get(id=request.GET.get('faseid'))
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("create_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Si el proyecto no se encuentra inicializado."""
    if proyecto.estado != "inicializado":
        """Redireccionar a la vista de fase, interrumpiendo el proceso."""
        return redirect('faseView', faseid=fase.id, proyectoid=proyecto.id)

    """Obtener items aprobados."""
    itemsAprobados = fase.items.filter(estado="aprobado")
    """Cantidad de lineas base en fase."""
    cantidad = fase.lineasBase.all().count()
    """Generar nombre para la linea base"""
    nombre = "LineaBase" + str(cantidad + 1) + "-" + fase.nombre
    """Renderizar fase/faseAddLineaBase.html"""
    return render(request, "fase/faseAddLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                          'items': itemsAprobados, 'nombre': nombre, })


def faseConfigLineaBase(request, proyectoid, faseid, lineaBaseid):
    """
                       **faseConfigLineaBase:**
                        Vista utilizada para configurar lineas base en Fase.
                        Solicita que el usuario que realiza el request
                        cuente con los permisos para ver lineas base en la fase,
                         o bien, los de gerente del proyecto y que
                         (indirectamente) haya iniciado sesion.
             """
    if request.method == 'GET':
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener Linea Base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Verificar que el usuario cuente con los permisos necesarios para efectuar la accion."""
        if not (request.user.has_perm("ver_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        """Obtener todos los items de la linea base, ordenados por id."""
        items = lineaBase.items.all().order_by('id')
        """Filtra items de la fase aprobados."""
        items_disponibles = fase.items.filter(estado="aprobado")
        """SI existen items disonibles en la fase."""
        if items_disponibles:
            """Se puede crear una nueva linea base."""
            crear_lb = True
        else:
            """SI no existen items disponibles, no se podra crear linea base."""
            crear_lb = False

        """Renderizar fase/faseConfigLineaBase.html"""
        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': items, 'lineaBase': lineaBase,
                       'crear_lb': crear_lb})


def lineaBaseAddItem(request):
    """
                           **lineaBaseAddItem:**
                            Vista utilizada para agregar items a lineas base en Fase.
                            Solicita que el usuario que realiza el request
                            cuente con los permisos para modificar lineas base en la fase,
                             o bien, los de gerente del proyecto y que
                             (indirectamente) haya iniciado sesion.
                 """
    if request.method == 'GET':
        """ID de proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """ID de fase"""
        faseid = request.GET.get('faseid')
        """ID de linea base"""
        lineaBaseid = request.GET.get('lineaBaseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener Linea Base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)

        """Verificar que el usuario cuente con los permisos necesarios para efectuar la accion."""
        if not (request.user.has_perm("modify_lineaBase", fase)) and not (
                request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        "No se pueden agregar en una linea base cerrada o rota"
        if lineaBase.estado != "abierta":
            """Obtener items de la linea base ordenadas por id."""
            itemsLineaBase = lineaBase.items.all().order_by('id')
            """Renderizar fase/faseConfigLineaBase.html interrumpiendo el proceso."""
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        """Filtrar items disponibles en la fase."""
        items_disponibles = fase.items.filter(estado="aprobado")

        """Renderizar fase/lienaBaseAddItem.html"""
        return render(request, 'fase/lineaBaseAddItem.html',
                      {'proyecto': proyecto, 'fase': fase, 'lineaBase': lineaBase, 'items': items_disponibles, })

    else:
        """POST REQUEST."""
        """ID de proyecto"""
        proyectoid = request.POST.get('proyectoid')
        """ID de fase"""
        faseid = request.POST.get('faseid')
        """ID de linea base."""
        lineaBaseid = request.POST.get('lineaBaseid')
        """Obtener fase"""
        fase = Fase.objects.get(id=faseid)
        """Obtener proyecto"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Obtener IDs de items para la linea base."""
        items = request.POST.getlist('items')
        """Recorrer los IDs"""
        for i in items:
            """Obtener item"""
            item = Item.objects.get(id=i)
            """Actualizar estado del item."""
            item.estado = "en linea base"
            """Actualizar history date del item."""
            #item._history_date = datetime.now()
            """Guardar item."""
            item.save()
            """Agregar item a linea base."""
            lineaBase.items.add(item)
        """Guardar linea base."""
        lineaBase.save()
        """Obtener items de linea base ordenados por id"""
        itemsLineaBase = lineaBase.items.all().order_by('id')
        """Renderizar fase/faseCOnfigLineaBase.html"""
        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })


def lineaBaseRemoveItem(request, proyectoid, faseid, lineaBaseid, itemid):
    """
                               **lineaBaseRemoveItem:**
                                Vista utilizada para remover items de lineas base en Fase.
                                Solicita que el usuario que realiza el request
                                cuente con los permisos para modificar lineas base en la fase,
                                 o bien, los de gerente del proyecto y que
                                 (indirectamente) haya iniciado sesion.
                     """
    if request.method == 'GET':
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase"""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Obtener item a remover de linea base"""
        item_remover = Item.objects.get(id=itemid)
        """Verificar que el usuario cuente con los permisos necesarios para efectuar la accion."""
        if not (request.user.has_perm("modify_lineaBase", fase)) and not (
                request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        "No se pueden agregar en una linea base cerrada o rota"
        if lineaBase.estado != "abierta":
            """Obtener items de la linea base ordenadas por id."""
            itemsLineaBase = lineaBase.items.all().order_by('id')
            """Renderizar fase/faseConfigLineaBase.html interrumpiendo el proceso."""
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        """Remover item de linea base"""
        lineaBase.items.remove(item_remover)
        """Guardar LInea Base"""
        lineaBase.save()
        """Actualizar estado de item."""
        item_remover.estado = "aprobado"
        """Actualizar history date de item para version."""
        #item_remover._history_date = datetime.now()
        """Guardar item."""
        item_remover.save()
        """Obtener items de la linea base ordenados por id."""
        itemsLineaBase = lineaBase.items.all().order_by('id')
        """Renderizar fase/faseConfigLineaBase.html."""
        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })


def faseCerrarLineaBase(request, proyectoid, faseid, lineaBaseid):
    """
                                   **faseCerrarLineaBase:**
                                    Vista utilizada para cerrar lineas base en Fase.
                                    Solicita que el usuario que realiza el request
                                    sea el creador de la linea base y que
                                     (indirectamente) haya iniciado sesion.
                         """
    if request.method == 'GET':
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener Linea Base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Verificar que el usuario que desea realizar la accion sea el creador de la linea base."""
        if not (request.user == lineaBase.creador):
            """EN caso de no ser el creador, interrumpir el proceso, redirigiendo."""
            return redirect('/permissionError/')

        """Si la linea base no tiene items no se puede cerrar la linea base.."""
        if not lineaBase.items.all():
            """Obtener items de linea base."""
            itemsLineaBase = lineaBase.items.all().order_by('id')
            """Renderizar fase/faseConfigLineaBase.html interrumpiendo el proceso."""
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        """Actualizar el estado de la linea base."""
        lineaBase.estado = "cerrada"
        """Guardar Linea Base"""
        lineaBase.save()
        """Obtener lineas base de fase, exluyendo las rotas (ncesario en el template a renderizar)"""
        lineasBase = fase.lineasBase.exclude(estado="rota")

        """Renderizar fase/faseGestionLineaBase.html"""
        return render(request, "fase/faseGestionLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })


def itemHistorial(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        faseid = request.GET.get('faseid')
        itemid = request.GET.get('itemid')
        item = Item.objects.get(id=itemid)
        fase = Fase.objects.get(id=faseid)
        "Creacion de una lista con los historiales de cambios del item"
        # version_list = reversion.get_for_object(item)
        versions = Version.objects.get_for_object(item)
        entry_list = list(versions.all())

        prueba = {}
        "Obtiene los campos extras del item con sus respectivos valores"
        p2 = zip(item.tipoItem.campo_extra, item.campo_extra_valores)
        for p, k in p2:
            prueba[p] = k
        return render(request, 'item/historialitem.html',
                      {'faseid': faseid, 'proyectoid': proyectoid,
                       'item': item,
                       'campos': prueba, 'versions': versions})

@transaction.atomic()
@reversion.create_revision()
def itemReversionar(request, proyectoid, faseid, itemid, history_date):
    """
                  **itemReversiona:**
                   Vista utilizada para volver a una version anterior del Item.
                   Solicita que el usuario que realiza el request
                   cuente con los permisos para reversionar y que el
                   estado del item sea "en desarrollo"

    """

    if request.method == 'GET':

        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)

        item = Item.objects.get(id=itemid)

        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("reversionar_item", fase)) and not (
                request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        """ Se podra reversionar el item si este se encuentra en estado de desarrollo"""
        if (item.estado == 'en desarrollo'):

            num = Item.objects.last()
            item.version = num.version + 1
            verNum = 0
            versions = Version.objects.get_for_object(item)
            total = len(versions)
            for f in versions:
                verNum=verNum+1
                aux = str(f.revision.date_created)
                if (aux == history_date):
                    print("yei")
                    break
                else:
                    print("nou")
            versions[verNum-1].revision.revert()
            item.refresh_from_db()

            item.save()

            return redirect('itemConfigurar', itemid=itemid, faseid=faseid, proyectoid=proyectoid)
        else:
            return redirect('itemConfigurar', itemid=itemid, faseid=faseid, proyectoid=proyectoid)


def downloadFile(request, filename, itemid, faseid, proyectoid):
    path = '/var/www/item/descargas/'
    s3 = boto3.client('s3',
                      aws_access_key_id='AKIAUWIIW4ARQQQA4TLN',
                      aws_secret_access_key='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')
    # s3 = boto3.resource('s3',
    #                   aws_access_key_id='AKIAUWIIW4ARQQQA4TLN',
    #                  aws_secret_access_key='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')
    s3.download_file('archivositem', filename, path + filename)
    return redirect('itemConfigurar', itemid=itemid, faseid=faseid, proyectoid=proyectoid)


def cerrarFase(request, proyectoid, faseid):
    """
          **cerrarFase:**
            Vista utilizada para cerrar una Fase.
            Solicita que el usuario que realiza el request cuente
            con el permiso para cerrar la fase correspondiente
            y que (indirectamente) haya iniciado sesion
        """

    if request.method == 'GET':
        """Fase que se desea cerrar."""
        fase = Fase.objects.get(id=faseid)
        """Proyecto en el cual se encuentra la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)

        cerrar = True
        if not (request.user.has_perm("cerrar_fase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        """Se obtinen los items que no se encuentren en estado deshabilitado"""
        itemsFase = fase.items.exclude(estado="deshabilitado")
        for i in itemsFase:
            if i.estado == "en linea base":
                lineaBaseItem = LineaBase.objects.exclude(estado="rota").get(items__id=i.id)
                if lineaBaseItem.estado != "cerrada":
                    cerrar = False
                    break
            else:
                cerrar = False
                break

        """Para aprobar el item es necesario identificar que tenga alguna relacion con un antecesor
                    que se encuentre en una linea base cerrada, o bien con un padre(o hijo) que este aprobado."""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        cont = 0
        esPrimeraFase = False
        for fp in fasesProyecto:
            cont = cont + 1
            if fp == fase:
                if cont == 1:
                    esPrimeraFase = True
                    break
        "Solo verificar si son items posteriores a la primera fase."
        bandera = False

        if esPrimeraFase == False:

            for i in itemsFase:
                relaciones = i.relaciones.all()

                for r in relaciones:
                    relacion = Relacion.objects.get(item_from=i, item_to=r)

                    if relacion.tipo == "sucesor":
                        bandera = True
                        break

        if esPrimeraFase == False:

            if cerrar == True and bandera == True:
                fase.estado = "cerrada"
                fase.save()
                return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)

            return redirect('faseConfinicializada', proyectoid=proyectoid, faseid=faseid)

        if cerrar == True:
            fase.estado = "cerrada"
            fase.save()
            return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)

        return redirect('faseConfinicializada', proyectoid=proyectoid, faseid=faseid)






def itemCalculoImpacto(request):
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase"""
        faseid = request.GET.get('faseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """ID de item_from"""
        itemIdCalculo = request.GET.get('itemIdCalculo')
        """Obtener item."""
        itemCalculo = Item.objects.get(id=itemIdCalculo)
        """ID de item_to"""

        calculo = itemCalculo.costo

        """NUEVA LOGICA CALCULO DE IMPACTO"""
        adj = {}
        confirmados = []
        confirmados.append(int(itemCalculo.id))
        hijos = []
        itemsFase = fase.items.exclude(estado="deshabilitado")
        for r in itemCalculo.relaciones.all():
            if r in itemsFase:
                if Relacion.objects.filter(item_from=r, item_to=itemCalculo, tipo="hijo").exists():
                    calculo = calculo + int(r.costo)
                    confirmados.append(int(r.id))
                    hijos.append(int(r.id))
                    adj[int(r.id)] = []

        adj[int(itemCalculo.id)] = hijos

        seguir = False
        for c in confirmados:
            confirmado = Item.objects.get(id=c)
            for r in confirmado.relaciones.all():
                if r in itemsFase:
                    if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                        if int(r.id) not in confirmados:
                            seguir = True

        while seguir:
            for c in confirmados:
                confirmado = Item.objects.get(id=c)
                for r in confirmado.relaciones.all():
                    if r in itemsFase:
                        if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                            if int(r.id) not in confirmados:
                                # print("confirmado", confirmado.id, "falta", r.id)
                                calculo = calculo + int(r.costo)
                                confirmados.append(int(r.id))
                                adj[int(r.id)] = []
                                adj[int(confirmado.id)].append(int(r.id))

                """Volver a verificar"""
                seguir = False
                for c in confirmados:
                    confirmado = Item.objects.get(id=c)
                    for r in confirmado.relaciones.all():
                        if r in itemsFase:
                            if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                                if int(r.id) not in confirmados:
                                    seguir = True

        """FIltrar fases del proyecto apropiadas."""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')

        """Aqui sigue el codigo normal de calculo de impacto."""
        for fp in fasesProyecto:
            if int(fp.id) > int(fase.id):
                itemsFase = fp.items.exclude(estado="deshabilitado").order_by('id')
                confirmadosAux = []
                """Para relaciones directas."""
                for iF in itemsFase:
                    hijos = []
                    if Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="antecesor").exists():

                        """Podria existir la posibilidad de que tenga mas de un antecesor valido. Solo para el grafo."""
                        for c in confirmados:
                            if Relacion.objects.filter(item_from_id=c, item_to=iF, tipo="antecesor").exists():
                                adj[int(c)].append(int(iF.id))

                        if not int(iF.id) in confirmadosAux:
                            calculo = calculo + int(iF.costo)
                            confirmadosAux.append(int(iF.id))

                        for r in iF.relaciones.all():
                            if r in itemsFase:
                                if Relacion.objects.filter(item_from=r, item_to=iF, tipo="hijo").exists():
                                    if int(r.id) not in confirmadosAux:
                                        calculo = calculo + int(r.costo)
                                        confirmadosAux.append(int(r.id))
                                        hijos.append(int(r.id))
                                        adj[int(r.id)] = []

                        adj[int(iF.id)] = hijos
                    #  adj[int(iF.id)] = confirmadosAux

                """Para relaciones indirectas."""
                for iF in itemsFase:
                    hijos = []
                    if not Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="antecesor").exists():

                        if Relacion.objects.filter(item_from_id__in=confirmadosAux, item_to=iF).exists():
                            if not int(iF.id) in confirmadosAux:
                                calculo = calculo + int(iF.costo)
                                confirmadosAux.append(int(iF.id))

                            for r in iF.relaciones.all():
                                if r in itemsFase:
                                    if Relacion.objects.filter(item_from=r, item_to=iF, tipo="hijo").exists():
                                        if int(r.id) not in confirmadosAux:
                                            calculo = calculo + int(r.costo)
                                            confirmadosAux.append(int(r.id))
                                            hijos.append(int(r.id))
                                            adj[int(r.id)] = []

                            adj[int(iF.id)] = hijos
                        #  adj[int(iF.id)] = confirmadosAux

                confirmados = confirmadosAux
        print(adj)
        print(calculo)

        return render(request, 'item/itemCalculoImpacto.html',
                      {'faseid': faseid, 'proyectoid': proyectoid,
                       'item': itemCalculo,
                       'calculo': calculo, })

def gestionRoturaLineaBase(request,proyectoid,faseid,lineaBaseid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitudes = lineaBase.roturaslineasBase.all()
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True
        return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                'lineaBase': lineaBase, 'solicitudes': solicitudes, 'es_comite': es_comite })

def formRoturaLineaBase(request,proyectoid,faseid,lineaBaseid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        """Obtener items de linea base."""
        items = lineaBase.items.all()
        return render(request, "fase/FormularioRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                'lineaBase': lineaBase, 'items':items})
    if request.method == "POST":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        items = lineaBase.items.all()
        descripcion = request.POST.get('descripcion')
        """Se crea un objeto de tipo Rotura de Linea Base"""
        solicitud = RoturaLineaBase.objects.create(solicitante=request.user, descripcion_solicitud=descripcion,
                                                   fecha= datetime.now())
        """Recupera los items a modificar seleccionados por el usuario"""
        items_a_modificar = request.POST.getlist('items')
        for i in items_a_modificar:
            """Agrega los items a la solicitud"""
            solicitud.items_implicados.add(Item.objects.get(id=i))
        """Se guarda el objeto"""
        solicitud.save()
        """Se agrega la solicitud a la linea base"""
        lineaBase.roturaslineasBase.add(solicitud)
        lineaBase.save()
        solicitudes = lineaBase.roturaslineasBase.all()
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True

        mensaje = "Su solicitud se envió correctamente. El Comité de Control de Cambios decidirá romper o no la Línea Base."
        # VERIFICAR SI EL USUARIO QUE ENTRA A ESA PAGINA YA EMITIO O NO SU VOTO PARA NO MOSTRARLE ESE TEMPLATE
        return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                        'lineaBase': lineaBase,
                                                                        'solicitudes': solicitudes,
                                                                        'es_comite': es_comite, 'mensaje': mensaje})

def votacionRoturaLineaBase(request,proyectoid,faseid,lineaBaseid, solicituid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitud = RoturaLineaBase.objects.get(id=solicituid)
        return render(request, "fase/faseRoturaLineaBaseVotar.html", {'proyecto': proyecto, 'fase': fase,
                                                                        'lineaBase': lineaBase,
                                                                        'solicitud': solicitud,})

def AprobarRoturaLineaBase(request,proyectoid,faseid,lineaBaseid, solicituid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitud = RoturaLineaBase.objects.get(id=solicituid)
        solicitudes = lineaBase.roturaslineasBase.all()
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True
        """Registrar votos"""
        voto_anotado = False
        votos_registrados = []
        votos_registrados = solicitud.votos_registrados.all()
        votos_registrados = list(votos_registrados)
        if not request.user in votos_registrados:
            if solicitud.voto_uno == -1:
                """Se registra el voto como primer voto y se guarda al usuario que voto"""
                solicitud.voto_uno = 1
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno, se prueba en voto_dos"""
            if solicitud.voto_dos == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.voto_dos = 1
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno y voto_dos, se prueba en voto_tres"""
            if solicitud.voto_tres == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.voto_tres = 1
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True

            """
                Luego de registrar los votos, se procede a controlar si se rompe o no la Línea Base. 
                Si algún voto está en -1, quiere decir que algún miembro del Comité aún no voto.
                En caso de que todos hayan votado, se suman los valores.
                Si:
                    suma == 0, todos rechazaron --> No se rompe la linea base. 
                    suma == 1, un solo voto por la aprobación, dos rechazos --> No se rompe la linea base. 
                    suma == 2, dos votos por la aprobación, un rechazo --> Se rompe la linea base.
                    suma == 3, todos aprobaron --> Se rompe la linea base. 
            """
            if solicitud.voto_uno is not -1 and solicitud.voto_dos is not -1 and solicitud.voto_tres is not -1:
                """Ya votaron los tres miembros"""
                suma = solicitud.voto_uno + solicitud.voto_dos + solicitud.voto_tres
                if suma < 2 and suma >= 0:
                    solicitud.estado = "rechazado"
                    solicitud.save()
                    # Acciones de rechazo de solicitud de Rotura Linea Base
                    mensaje = "Su voto se registro correctamente. Se rechazó la rotura de la Línea Base."
                    return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                    'lineaBase': lineaBase,
                                                                                    'solicitudes': solicitudes,
                                                                                    'es_comite': es_comite,
                                                                                    'mensaje': mensaje})
                if suma >= 2 and suma <= 3:
                    solicitud.estado = "aprobado"
                    solicitud.save()
                    # Acciones de aprobacion de solicitud de Rotura Linea Base
                    """Establecer a la línea base como rota"""
                    lineaBase.estado = "rota"
                    lineaBase.save()
                    for i in lineaBase.items.all():
                        i.estado = "en revision"
                        #i._history_date = datetime.now()
                        """Guardar"""
                        i.save()
                        for r in i.relaciones.all():
                            relacionItem = Relacion.objects.filter(item_from=r, item_to=i, tipo="antecesor").exists()
                            if not relacionItem:
                                r.estado = "en revision"
                                #r._history_date = datetime.now()
                                """Guardar"""
                                r.save()
                                esta_en_LB = LineaBase.objects.filter(items__id=r.id).exists()
                                if esta_en_LB:
                                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                                    """Si el estado de la linea base es cerrada."""
                                    if lineaBaseItem.estado == "cerrada":
                                        lineaBaseItem.estado = "comprometida"
                                        solicitud = RoturaLineaBaseComprometida.objects.create(comprometida_estado="pendiente")
                                        solicitud.save()
                                        lineaBaseItem.roturaLineaBaseComprometida.add(solicitud)
                                        lineaBaseItem.save()

                                    if lineaBaseItem.estado == "abierta":
                                        lineaBaseItem.items.remove(r)
                                        lineaBaseItem.save()


                    mensaje = "Su voto se registro correctamente. Se aprobo la rotura de la Línea Base."
                    return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                    'lineaBase': lineaBase,
                                                                                    'solicitudes': solicitudes,
                                                                                    'es_comite': es_comite,
                                                                                    'mensaje': mensaje})

            else:
                """Aún no votaron todos los miembros"""
                # Redirigir a la lista de solicitudes y mostrarle un mensaje de que se registro su voto.

                mensaje = "Su voto se registro correctamente. La rotura se decidirá cuando todos los miembros del Comité emitan su voto."
                # VERIFICAR SI EL USUARIO QUE ENTRA A ESA PAGINA YA EMITIO O NO SU VOTO PARA NO MOSTRARLE ESE TEMPLATE
                return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                'lineaBase': lineaBase,
                                                                                'solicitudes': solicitudes,
                                                                                'es_comite': es_comite, 'mensaje': mensaje})
        else:
            mensaje = " "
            # VERIFICAR SI EL USUARIO QUE ENTRA A ESA PAGINA YA EMITIO O NO SU VOTO PARA NO MOSTRARLE ESE TEMPLATE
            return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                            'lineaBase': lineaBase,
                                                                            'solicitudes': solicitudes,
                                                                            'es_comite': es_comite, 'mensaje': mensaje})

def RechazarRoturaLineaBase(request,proyectoid,faseid,lineaBaseid, solicituid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitud = RoturaLineaBase.objects.get(id=solicituid)
        solicitudes = lineaBase.roturaslineasBase.all()
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True
        """Registrar votos"""
        voto_anotado = False
        votos_registrados = []
        votos_registrados = solicitud.votos_registrados.all()
        votos_registrados = list(votos_registrados)
        if not request.user in votos_registrados:
            if solicitud.voto_uno == -1:
                """Se registra el voto como primer voto y se guarda al usuario que voto"""
                solicitud.voto_uno = 0
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno, se prueba en voto_dos"""
            if solicitud.voto_dos == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.voto_dos = 0
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno y voto_dos, se prueba en voto_tres"""
            if solicitud.voto_tres == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.voto_tres = 0
                solicitud.votos_registrados.add(request.user)
                solicitud.save()
                voto_anotado = True

            """
                Luego de registrar los votos, se procede a controlar si se rompe o no la Línea Base. 
                Si algún voto está en -1, quiere decir que algún miembro del Comité aún no voto.
                En caso de que todos hayan votado, se suman los valores.
                Si:
                    suma == 0, todos rechazaron --> No se rompe la linea base. 
                    suma == 1, un solo voto por la aprobación, dos rechazos --> No se rompe la linea base. 
                    suma == 2, dos votos por la aprobación, un rechazo --> Se rompe la linea base.
                    suma == 3, todos aprobaron --> Se rompe la linea base. 
            """
            if solicitud.voto_uno is not -1 and solicitud.voto_dos is not -1 and solicitud.voto_tres is not -1:
                """Ya votaron los tres miembros"""
                suma = solicitud.voto_uno + solicitud.voto_dos + solicitud.voto_tres
                if suma < 2 and suma >= 0:
                    solicitud.estado = "rechazado"
                    solicitud.save()
                    # Acciones de rechazo de solicitud de Rotura Linea Base
                    # Se podría enviar correo al solicitante para avisarle que se rechazó su solicitud
                    mensaje = "Su voto se registro correctamente. Se rechazó la rotura de la Línea Base."
                    return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                    'lineaBase': lineaBase,
                                                                                    'solicitudes': solicitudes,
                                                                                    'es_comite': es_comite,
                                                                                    'mensaje': mensaje})
                if suma >= 2 and suma <= 3:
                    solicitud.estado = "aprobado"
                    solicitud.save()
                    # Acciones de aprobacion de solicitud de Rotura Linea Base
                    """Establecer a la línea base como rota"""
                    lineaBase.estado = "rota"
                    lineaBase.save()
                    for i in lineaBase.items.all():
                        i.estado = "en revision"
                        #i._history_date = datetime.now()
                        """Guardar"""
                        i.save()
                        for r in i.relaciones.all():
                            relacionItem = Relacion.objects.filter(item_from=r, item_to=i, tipo="antecesor").exists()
                            if not relacionItem:
                                r.estado = "en revision"
                                #r._history_date = datetime.now()
                                """Guardar"""
                                r.save()
                                esta_en_LB = LineaBase.objects.filter(items__id=r.id).exists()
                                if esta_en_LB:
                                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                                    """Si el estado de la linea base es cerrada."""
                                    if lineaBaseItem.estado == "cerrada":
                                        lineaBaseItem.estado = "comprometida"
                                        solicitud = RoturaLineaBaseComprometida.objects.create(comprometida_estado="pendiente")
                                        solicitud.save()
                                        lineaBaseItem.roturaLineaBaseComprometida.add(solicitud)
                                        lineaBaseItem.save()
                                    if lineaBaseItem.estado == "abierta":
                                        lineaBaseItem.items.remove(r)
                                        lineaBaseItem.save()
                    mensaje = "Su voto se registro correctamente. Se aprobo la rotura de la Línea Base."
                    return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                    'lineaBase': lineaBase,
                                                                                    'solicitudes': solicitudes,
                                                                                    'es_comite': es_comite,
                                                                                    'mensaje': mensaje})

            else:
                """Aún no votaron todos los miembros"""
                # Redirigir a la lista de solicitudes y mostrarle un mensaje de que se registro su voto.

                mensaje = "Su voto se registro correctamente. La rotura se decidirá cuando todos los miembros del Comité emitan su voto."
                # VERIFICAR SI EL USUARIO QUE ENTRA A ESA PAGINA YA EMITIO O NO SU VOTO PARA NO MOSTRARLE ESE TEMPLATE
                return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                                'lineaBase': lineaBase,
                                                                                'solicitudes': solicitudes,
                                                                                'es_comite': es_comite, 'mensaje': mensaje})
        else:
            mensaje = " "
            # VERIFICAR SI EL USUARIO QUE ENTRA A ESA PAGINA YA EMITIO O NO SU VOTO PARA NO MOSTRARLE ESE TEMPLATE
            return render(request, "fase/faseGestionRoturaLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                                            'lineaBase': lineaBase,
                                                                            'solicitudes': solicitudes,
                                                                            'es_comite': es_comite, 'mensaje': mensaje})

def votacionRoturaLineaBaseComprometida(request,proyectoid,faseid,lineaBaseid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        items_aprobados = []
        items_en_revision = []
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        items_lb = lineaBase.items.all()
        for i in items_lb:
            if i.estado == "aorobado":
                items_aprobados.append(i)
            if i.estado == "en revision":
                items_en_revision.append(i)
        solicitud_romper = []
        solicitud_romper = lineaBase.roturaLineaBaseComprometida.all()
        solicitud_romper = list(solicitud_romper)
        solicitud = solicitud_romper.pop()
        return render(request, "fase/faseRoturaLineaBaseVotarComprometida.html", {'proyecto': proyecto, 'fase': fase,'lineaBase': lineaBase,
                                                                                  'items_aprobados': items_aprobados,
                                                                                  'items_en_revision': items_en_revision, 'solicitud':solicitud})
def AprobarRoturaLineaBaseComprometida(request,proyectoid,faseid,lineaBaseid,solicituid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitud = RoturaLineaBaseComprometida.objects.get(id=solicituid)
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True
        """Registrar votos"""
        voto_anotado = False
        votos_registrados = []
        votos_registrados = solicitud.registrados_votos_comprometida.all()
        votos_registrados = list(votos_registrados)
        if not request.user in votos_registrados:
            if solicitud.uno_voto_comprometida == -1:
                """Se registra el voto como primer voto y se guarda al usuario que voto"""
                solicitud.uno_voto_comprometida = 1
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno, se prueba en dos_voto_comprometida"""
            if solicitud.dos_voto_comprometida == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.dos_voto_comprometida = 1
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno y voto_dos, se prueba en tres_voto_comprometida"""
            if solicitud.tres_voto_comprometida == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.tres_voto_comprometida = 1
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True

            """
                Luego de registrar los votos, se procede a controlar si se rompe o no la Línea Base. 
                Si algún voto está en -1, quiere decir que algún miembro del Comité aún no voto.
                En caso de que todos hayan votado, se suman los valores.
                Si:
                    suma == 0, todos rechazaron --> No se rompe la linea base. 
                    suma == 1, un solo voto por la aprobación, dos rechazos --> No se rompe la linea base. 
                    suma == 2, dos votos por la aprobación, un rechazo --> Se rompe la linea base.
                    suma == 3, todos aprobaron --> Se rompe la linea base. 
            """
            if solicitud.uno_voto_comprometida is not -1 and solicitud.dos_voto_comprometida is not -1 and solicitud.tres_voto_comprometida is not -1:
                """Ya votaron los tres miembros"""
                suma = solicitud.uno_voto_comprometida + solicitud.dos_voto_comprometida + solicitud.tres_voto_comprometida
                if suma < 2 and suma >= 0:
                    solicitud.comprometida_estado = "rechazado"
                    solicitud.save()
                    # Acciones de rechazo de solicitud de Rotura Linea Base
                    mensaje = "Su voto se registro correctamente. Se rechazó la rotura de la Línea Base."
                    lineasBase = fase.lineasBase.all()
                    return render(request, "fase/faseGestionLineaBase.html",
                                  {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })
                if suma >= 2 and suma <= 3:
                    solicitud.comprometida_estado = "aprobado"
                    solicitud.save()
                    # Acciones de aprobacion de solicitud de Rotura Linea Base
                    """Establecer a la línea base como rota"""
                    lineaBase.estado = "rota"
                    lineaBase.save()
                    for i in lineaBase.items.all():
                        i.estado = "en revision"
                        #i._history_date = datetime.now()
                        """Guardar"""
                        i.save()
                        for r in i.relaciones.all():
                            relacionItem = Relacion.objects.filter(item_from=r, item_to=i, tipo="antecesor").exists()
                            if not relacionItem:
                                r.estado = "en revision"
                                #r._history_date = datetime.now()
                                """Guardar"""
                                r.save()
                                esta_en_LB = LineaBase.objects.filter(items__id=r.id).exists()
                                if esta_en_LB:
                                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                                    """Si el estado de la linea base es cerrada."""
                                    if lineaBaseItem.estado == "cerrada":
                                        lineaBaseItem.estado = "comprometida"
                                        solicitud_romper = RoturaLineaBaseComprometida.objects.create(comprometida_estado="pendiente")
                                        solicitud_romper.save()
                                        lineaBaseItem.roturaLineaBaseComprometida.add(solicitud_romper)
                                        lineaBaseItem.save()
                                    if lineaBaseItem.estado == "abierta":
                                        lineaBaseItem.items.remove(r)
                                        lineaBaseItem.save()

                    lineasBase = fase.lineasBase.all()
                    return render(request, "fase/faseGestionLineaBase.html",
                                  {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })

            else:
                """Aún no votaron todos los miembros"""
                # Redirigir a la lista de solicitudes y mostrarle un mensaje de que se registro su voto.

                lineasBase = fase.lineasBase.all()
                return render(request, "fase/faseGestionLineaBase.html",
                              {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })
        else:
            lineasBase = fase.lineasBase.all()
            return render(request, "fase/faseGestionLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })

def RechazarRoturaLineaBaseComprometida(request,proyectoid,faseid,lineaBaseid, solicituid):
    if request.method == "GET":
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """Obtener linea base."""
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        solicitud = RoturaLineaBase.objects.get(id=solicituid)
        solicitudes = lineaBase.roturaslineasBase.all()
        es_comite = False
        comite_miembros = proyecto.comite.all()
        if request.user in comite_miembros:
            es_comite = True
        """Registrar votos"""
        voto_anotado = False
        votos_registrados = []
        votos_registrados = solicitud.registrados_votos_comprometida.all()
        votos_registrados = list(votos_registrados)
        if not request.user in votos_registrados:
            if solicitud.uno_voto_comprometida == -1:
                """Se registra el voto como primer voto y se guarda al usuario que voto"""
                solicitud.uno_voto_comprometida = 0
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno, se prueba en dos_voto_comprometida"""
            if solicitud.dos_voto_comprometida == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.dos_voto_comprometida = 0
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True
            """ Si ya se guardo un voto en voto_uno y dos_voto_comprometida, se prueba en tres_voto_comprometida"""
            if solicitud.tres_voto_comprometida == -1 and not voto_anotado:
                """Se registra el voto como segundo voto y se guarda al usuario que voto"""
                solicitud.tres_voto_comprometida = 0
                solicitud.registrados_votos_comprometida.add(request.user)
                solicitud.save()
                voto_anotado = True

            """
                Luego de registrar los votos, se procede a controlar si se rompe o no la Línea Base. 
                Si algún voto está en -1, quiere decir que algún miembro del Comité aún no voto.
                En caso de que todos hayan votado, se suman los valores.
                Si:
                    suma == 0, todos rechazaron --> No se rompe la linea base. 
                    suma == 1, un solo voto por la aprobación, dos rechazos --> No se rompe la linea base. 
                    suma == 2, dos votos por la aprobación, un rechazo --> Se rompe la linea base.
                    suma == 3, todos aprobaron --> Se rompe la linea base. 
            """
            if solicitud.uno_voto_comprometida is not -1 and solicitud.dos_voto_comprometida is not -1 and solicitud.tres_voto_comprometida is not -1:
                """Ya votaron los tres miembros"""
                suma = solicitud.uno_voto_comprometida + solicitud.dos_voto_comprometida + solicitud.tres_voto_comprometida
                if suma < 2 and suma >= 0:
                    solicitud.comprometida_estado = "rechazado"
                    solicitud.save()
                    # Acciones de rechazo de solicitud de Rotura Linea Base
                    # Se podría enviar correo al solicitante para avisarle que se rechazó su solicitud
                    lineasBase = fase.lineasBase.all()
                    return render(request, "fase/faseGestionLineaBase.html",
                                  {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })
                if suma >= 2 and suma <= 3:
                    solicitud.comprometida_estado = "aprobado"
                    solicitud.save()
                    # Acciones de aprobacion de solicitud de Rotura Linea Base
                    """Establecer a la línea base como rota"""
                    lineaBase.estado = "rota"
                    lineaBase.save()
                    for i in lineaBase.items.all():
                        i.estado = "en revision"
                        #i._history_date = datetime.now()
                        """Guardar"""
                        i.save()
                        for r in i.relaciones.all():
                            relacionItem = Relacion.objects.filter(item_from=r, item_to=i, tipo="antecesor").exists()
                            if not relacionItem:
                                r.estado = "en revision"
                                #r._history_date = datetime.now()
                                """Guardar"""
                                r.save()
                                esta_en_LB = LineaBase.objects.filter(items__id=r.id).exists()
                                if esta_en_LB:
                                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                                    """Si el estado de la linea base es cerrada."""
                                    if lineaBaseItem.estado == "cerrada":
                                        lineaBaseItem.estado = "comprometida"
                                        solicitud_romper = RoturaLineaBaseComprometida.objects.create(comprometida_estado="pendiente")
                                        solicitud_romper.save()
                                        lineaBaseItem.roturaLineaBaseComprometida.add(solicitud_romper)
                                        lineaBaseItem.save()
                                    if lineaBaseItem.estado == "abierta":
                                        lineaBaseItem.items.remove(r)
                                        lineaBaseItem.save()
                    mensaje = "Su voto se registro correctamente. Se aprobo la rotura de la Línea Base."
                    lineasBase = fase.lineasBase.all()
                    return render(request, "fase/faseGestionLineaBase.html",
                                  {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })

            else:
                """Aún no votaron todos los miembros"""
                # Redirigir a la lista de solicitudes y mostrarle un mensaje de que se registro su voto.

                mensaje = "Su voto se registro correctamente. La rotura se decidirá cuando todos los miembros del Comité emitan su voto."
                lineasBase = fase.lineasBase.all()
                return render(request, "fase/faseGestionLineaBase.html",
                              {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })
        else:
            mensaje = " "
            lineasBase = fase.lineasBase.all()
            return render(request, "fase/faseGestionLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })


def itemTrazabilidad(request):
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Obtener proyecto."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase"""
        faseid = request.GET.get('faseid')
        """Obtener fase."""
        fase = Fase.objects.get(id=faseid)
        """ID de item_from"""
        itemIdTrazabilidad = request.GET.get('itemIdTrazabilidad')
        """Obtener item."""
        itemTrazabilidad = Item.objects.get(id=itemIdTrazabilidad)
        """ID de item_to"""
        """
            TRAZABILIDAD HACIA LA DERECHA
            SUCESORES E HIJOS. Y LOS HIJOS Y SUCESORES DE ESTOS HASTA LLEGAR AL FINAL
        """
        adj = {}
        confirmados = []
        confirmados.append(int(itemTrazabilidad.id))
        hijos = []
        itemsFase = fase.items.exclude(estado="deshabilitado")
        for r in itemTrazabilidad.relaciones.all():
            if r in itemsFase:
                if Relacion.objects.filter(item_from=r, item_to=itemTrazabilidad, tipo="hijo").exists():
                    confirmados.append(int(r.id))
                    hijos.append(int(r.id))
                    adj[int(r.id)] = []

        adj[int(itemTrazabilidad.id)] = hijos


        seguir = False
        for c in confirmados:
            confirmado = Item.objects.get(id=c)
            for r in confirmado.relaciones.all():
                if r in itemsFase:
                    if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                        if int(r.id) not in confirmados:
                            seguir = True


        while seguir:
            for c in confirmados:
                confirmado = Item.objects.get(id=c)
                for r in confirmado.relaciones.all():
                    if r in itemsFase:
                        if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                            if int(r.id) not in confirmados:
                                #print("confirmado", confirmado.id, "falta", r.id)
                                confirmados.append(int(r.id))
                                adj[int(r.id)] = []
                                adj[int(confirmado.id)].append(int(r.id))

                """Volver a verificar"""
                seguir = False
                for c in confirmados:
                    confirmado = Item.objects.get(id=c)
                    for r in confirmado.relaciones.all():
                        if r in itemsFase:
                            if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="hijo").exists():
                                if int(r.id) not in confirmados:
                                    seguir = True


        """FIltrar fases del proyecto apropiadas."""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')



        """Aqui sigue el codigo normal de calculo de impacto."""
        for fp in fasesProyecto:
            if int(fp.id) > int(fase.id):
                itemsFase = fp.items.exclude(estado="deshabilitado").order_by('id')
                confirmadosAux = []
                """Para relaciones directas."""
                for iF in itemsFase:
                    hijos = []
                    if Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="antecesor").exists():

                        """Podria existir la posibilidad de que tenga mas de un antecesor valido. Solo para el grafo."""
                        for c in confirmados:
                            if Relacion.objects.filter(item_from_id=c, item_to=iF, tipo="antecesor").exists():
                                adj[int(c)].append(int(iF.id))


                        if not int(iF.id) in confirmadosAux:
                            confirmadosAux.append(int(iF.id))

                        for r in iF.relaciones.all():
                            if r in itemsFase:
                                if Relacion.objects.filter(item_from=r, item_to=iF, tipo="hijo").exists():
                                    if int(r.id) not in confirmadosAux:
                                        confirmadosAux.append(int(r.id))
                                        hijos.append(int(r.id))
                                        adj[int(r.id)] = []

                        adj[int(iF.id)] = hijos
                      #  adj[int(iF.id)] = confirmadosAux


                """Para relaciones indirectas."""
                for iF in itemsFase:
                    hijos = []
                    if not Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="antecesor").exists():

                        if Relacion.objects.filter(item_from_id__in=confirmadosAux, item_to=iF).exists():
                            if not int(iF.id) in confirmadosAux:
                                confirmadosAux.append(int(iF.id))

                            for r in iF.relaciones.all():
                                if r in itemsFase:
                                    if Relacion.objects.filter(item_from=r, item_to=iF, tipo="hijo").exists():
                                        if int(r.id) not in confirmadosAux:
                                            confirmadosAux.append(int(r.id))
                                            hijos.append(int(r.id))
                                            adj[int(r.id)] = []

                            adj[int(iF.id)] = hijos
                        #  adj[int(iF.id)] = confirmadosAux

                confirmados = confirmadosAux

        """
            TRAZABILIDAD HACIA ATRAS --> Antecesores y padres
        """
        confirmados = []
        confirmados.append(int(itemTrazabilidad.id))
        padres = []
        itemsFase = fase.items.exclude(estado="deshabilitado")
        for r in itemTrazabilidad.relaciones.all():
            if r in itemsFase:
                if Relacion.objects.filter(item_from=r, item_to=itemTrazabilidad, tipo="padre").exists():
                    confirmados.append(int(r.id))
                    padres.append(int(r.id))
                    if int(r.id) in adj.keys():
                        adj[int(r.id)].append(int(itemTrazabilidad.id))
                    else:
                        lista_item = []
                        lista_item.append(int(itemTrazabilidad.id))
                        adj[int(r.id)] = lista_item

        #adj[int(itemTrazabilidad.id)] = padres

        seguir = False
        for c in confirmados:
            confirmado = Item.objects.get(id=c)
            for r in confirmado.relaciones.all():
                if r in itemsFase:
                    if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="padre").exists():
                        if int(r.id) not in confirmados:
                            seguir = True

        while seguir:
            for c in confirmados:
                confirmado = Item.objects.get(id=c)
                for r in confirmado.relaciones.all():
                    if r in itemsFase:
                        if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="padre").exists():
                            if int(r.id) not in confirmados:
                                # print("confirmado", confirmado.id, "falta", r.id)
                                confirmados.append(int(r.id))
                                if int(r.id) in adj.keys():
                                    adj[int(r.id)].append(int(confirmado.id))
                                else:
                                    lista_item = []
                                    lista_item.append(int(confirmado.id))
                                    adj[int(r.id)] = lista_item


                """Volver a verificar"""
                seguir = False
                for c in confirmados:
                    confirmado = Item.objects.get(id=c)
                    for r in confirmado.relaciones.all():
                        if r in itemsFase:
                            if Relacion.objects.filter(item_from=r, item_to=confirmado, tipo="padre").exists():
                                if int(r.id) not in confirmados:
                                    seguir = True

        """FIltrar fases del proyecto apropiadas."""
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('-id')

        """Aqui sigue el codigo normal de calculo de impacto."""
        for fp in fasesProyecto:
            if int(fp.id) < int(fase.id):
                itemsFase = fp.items.exclude(estado="deshabilitado").order_by('id')
                confirmadosAux = []
                """Para relaciones directas."""
                for iF in itemsFase:
                    padres = []
                    if Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="sucesor").exists():

                        """Podria existir la posibilidad de que tenga mas de un sucesor valido. Solo para el grafo."""
                        for c in confirmados:
                            if Relacion.objects.filter(item_from_id=c, item_to=iF, tipo="sucesor").exists():
                                if int(iF.id) in adj.keys():
                                    adj[int(iF.id)].append(int(c))
                                else:
                                    lista_item = []
                                    lista_item.append(c)
                                    adj[int(iF.id)]= lista_item



                        if not int(iF.id) in confirmadosAux:
                            confirmadosAux.append(int(iF.id))

                        for r in iF.relaciones.all():
                            if r in itemsFase:
                                if Relacion.objects.filter(item_from=r, item_to=iF, tipo="padre").exists():
                                    if int(r.id) not in confirmadosAux:
                                        confirmadosAux.append(int(r.id))
                                        padres.append(int(r.id))
                                        if int(r.id) in adj.keys():
                                            adj[int(r.id)].append(int(iF.id))
                                        else:
                                            lista_item = []
                                            lista_item.append(int(iF.id))
                                            adj[int(r.id)] = lista_item

                     #   adj[int(iF.id)] = padres
                    #  adj[int(iF.id)] = confirmadosAux

                """Para relaciones indirectas."""
                for iF in itemsFase:
                    padres = []
                    if not Relacion.objects.filter(item_from_id__in=confirmados, item_to=iF, tipo="sucesor").exists():

                        if Relacion.objects.filter(item_from=iF, item_to_id__in=confirmadosAux).exists():
                            if not int(iF.id) in confirmadosAux:
                                confirmadosAux.append(int(iF.id))

                            for r in iF.relaciones.all():
                                if r in itemsFase:
                                    if Relacion.objects.filter(item_from=r, item_to=iF, tipo="padre").exists():
                                        if int(r.id) not in confirmadosAux:
                                            confirmadosAux.append(int(r.id))
                                            padres.append(int(r.id))
                                            if int(r.id) in adj.keys():
                                                adj[int(r.id)].append(int(iF.id))
                                            else:
                                                lista_item = []
                                                lista_item.append(int(iF.id))
                                                adj[int(r.id)] = lista_item

                         #   adj[int(iF.id)] = padres
                        #  adj[int(iF.id)] = confirmadosAux

                confirmados = confirmadosAux
        print(adj)

        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        lista_items = []
        for key,value in adj.items():
            item_key = Item.objects.get(id=key)
            if not item_key in lista_items:
                lista_items.append(item_key)
            for v in adj[key]:
                item_value = Item.objects.get(id=int(v))
                if not item_value in lista_items:
                    lista_items.append(item_value)

        relaciones = []
        for r in Relacion.objects.all():
            if r.tipo == "antecesor" or r.tipo== "padre":
                relaciones.append(r)



        return render(request, 'item/TrazabilidadItem.html',{'fasesProyecto': fasesProyecto, 'proyecto':proyecto,
                                                             'lista_item': sorted(lista_items, key=lambda x: x.id,reverse=False),
                                                             'relaciones':relaciones})


