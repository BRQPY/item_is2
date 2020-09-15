from django.shortcuts import render, redirect
from proyecto.models import Proyecto, Fase, TipodeItem, Item, FaseUser, User, Rol, Relacion, LineaBase
from guardian.shortcuts import assign_perm, remove_perm
from proyecto.views import proyectoView, faseView
from django.db.models import Q


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

def faseVerProyectoInicializado(request ,faseid, proyectoid):
    if request.method == 'GET':
        """Proyecto en el cual crear la fase."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        items = fase.items.exclude(estado="deshabilitado").order_by('id')
        return render(request, 'fase/FaseProyectoInicializado.html', {'proyecto': proyecto, 'fase': fase,
                                                                  'items': items,
                                                                  })
def faseUsers(request,faseid,proyectoid):
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
                contador_roles_por_user=0
        cant_user = len(user_sin_repetidos)
        cant_usuarios_proyecto = len(proyecto.usuarios.all())
        """Verificar si se puede ser agregando usuarios a la fase. Debe tomar en cuenta la cantidad de usuarios en el proyecto"""
        if cant_user == cant_usuarios_proyecto:
            agregar_mas_users = False
        else:
            agregar_mas_users = True
        """Template a renderizar: fase.html con parametros -> fase, proyecto, items de fase."""
        return render(request, 'fase/faseUsers.html', {'fase': fase, 'proyecto': proyecto,
                                                        'userRol': zip(user_sin_repetidos, roles_por_user, cant_roles_por_user),
                                                        'cant_user': cant_user, 'cant_roles_proyecto':cant_roles_proyecto,
                                                        'agregar_mas_users': agregar_mas_users })
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
    fases = proyecto.fases.all()
    fasesUser = []
    for f in fases:
        if (request.user.has_perm("view_fase", f) or request.user.has_perm("is_gerente", proyecto)):
            fasesUser.append(f)
    """Redirigir a la vista del proyecto correspondiente."""
    return render(request, 'proyecto/proyectoListarFases.html', {'proyecto': proyecto, 'fases': fases,
                                                                 'fasesUser': sorted(fasesUser, key=lambda x: x.id,
                                                                                     reverse=False), })

def FaseConfigInicializada(request):
    """Fase a visualizar."""
    faseid = request.GET.get('faseid')
    proyectoid = request.GET.get('proyectoid')
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
    return render(request, 'fase/faseConfiguracionInicializada.html', {'fase': fase, 'proyecto': proyecto, 'items': items,
                                                                        'userRol': zip(user_sin_repetidos, roles_por_user),
                                                                        'cant_user':cant_user,
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

        return render(request,'fase/faseAddUser.html', {'usuarios':usuarios, 'roles':roles, 'fase': fase, 'proyecto':proyecto})
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
            return redirect('faseUsers', faseid= faseid, proyectoid=proyectoid)
        elif proyecto.estado == "inicializado":
            return redirect('faseUsers', faseid= faseid, proyectoid=proyectoid)
def FaseRemoveUser(request,proyectoid,faseid,userid):
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
def faseRolAsignar(request,proyectoid,faseid,userid):

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
        #proyectoid = request.GET.get('proyectoid')
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
        return render(request, "fase/faseRolAsignar.html", {'fase': fase, 'usuario': usuario, 'roles': roles_disponibles, 'proyecto': proyecto, })


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

def faseRolRemover(request,proyectoid,faseid,userid):
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
        #proyectoid = request.GET.get('proyectoid')
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
                                                            'proyecto': proyecto, 'cant_roles':cantidad_roles })

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
    assign_perm("view_fase",usuario,fase)

    if proyecto.estado == "pendiente":
        """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
        return redirect('faseTipoItem')
    elif proyecto.estado == "inicializado":
        return redirect('faseViewInicializado', faseid=faseid, proyectoid=proyectoid)
def FaseGestionTipoItem(request,faseid,proyectoid):
    if request.method == 'GET':
        #proyectoid = request.GET.get('proyectoid')
        #faseid = request.GET.get('faseid')
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
        return render(request, "fase/faseGestionTipoItem.html",
                      {'fase': fase, 'proyecto': proyecto, 'tipos_removible': tipos_removible,
                       'tipos_no_removible': tipos_no_removible,'add_tipo':add_tipo })

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

        return render(request, 'fase/faseAddTipoItem.html', { 'tiposItem': tipos_agregables, 'fase': fase, 'proyecto': proyecto})
    else:
        proyectoid = request.POST.get('proyectoid')
        faseid = request.POST.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        tipoItem = request.POST.get('tipoItem')
        tipo = TipodeItem.objects.get(id=tipoItem)
        fase.tipoItem.add(tipo)
        fase.save()
        if proyecto.estado == "pendiente":
            """Template a renderizar: ProyectoInicializadoConfig.html con parametro -> proyectoid"""
            return redirect('faseTipoItem', faseid=faseid, proyectoid=proyectoid)

def FaseRemoveTipoItem(request,proyectoid,faseid,tipoid):
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

        return render(request, "item/itemConfiguracion.html", {'fase': fase, 'item': item, 'proyecto': proyecto,
                                    'campos': zip(item.tipoItem.campo_extra, item.campo_extra_valores),})

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
        if item.estado == "pendiente de aprobacion" or item.estado == "aprobado" or item.estado == "en linea base":
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
            mensaje = "No es posible cambiar el estado del item ya que este cuenta con relaciones."
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
            fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
            cont = 0
            esPrimeraFase = False
            for fp in fasesProyecto:
                cont = cont+1
                if fp == fase:
                    if cont == 1:
                        esPrimeraFase = True
                        break
            "Solo verificar si son items posteriores a la primera fase."
            if esPrimeraFase == False:
                anterior = None
                for fp in fasesProyecto:
                    if fp == fase:
                        break
                    anterior = fp

                listoAprobacion = False
                itemsRelacionados = item.relaciones.all()
                for ir in itemsRelacionados:
                    relacion = Relacion.objects.get(item_from=item, item_to=ir)
                    if relacion.fase_item_to == anterior and ir.estado == "en linea base":
                        lineaBaseItem = LineaBase.objects.get(items__id=ir.id)
                        if lineaBaseItem.estado == "cerrada":
                            listoAprobacion = True
                            break
                    if relacion.fase_item_to == fase and (ir.estado == "aprobado" or ir.estado == "en linea base"):
                        listoAprobacion = True
                        break

                if listoAprobacion == False:
                    mensaje = "No es posible aprobar el item ya que este no posee una relacion con un item antecesor" \
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
                                   'mensaje': mensaje, })

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
    if item.estado == "pendiente de aprobacion" or item.estado == "aprobado" or item.estado == "en linea base":
        mensaje = "El estado actual del item no permite la deshabilitacion del mismo."
        """
        En caso contrario niega la deshabilitacion del mismo y 
        vuelve a gestion de item mostrando un mensaje de error.
        Template a renderizar gestionItem.html con parametros -> proyectoid, faseid, itemid y mensaje de error.
        """
        return render(request, 'item/gestionItem.html',
                      {'proyectoid': proyectoid, 'faseid': faseid, 'itemid': itemid, 'mensaje': mensaje, })

    "VERIFICAR SI ES POSIBLE DESHABILITAR EL ITEM TENIENDO EN CUENTA SUS RELACIONES."
    relaciones_item_deshabilitar = item.relaciones.all()
    ok_deshabilitar = True
    for rd in relaciones_item_deshabilitar:
        if rd.estado == "aprobado" or rd.estado == "en linea base":
            "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
            relaciones_item_afectado = rd.relaciones.exclude(id=item.id)
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
        """Guardar."""
        item.save()
        """Redirige a la vista de la fase correspondiente."""
        return redirect('proyectoView', id=proyectoid)

    """Redirige a la vista de la fase correspondiente."""
    return redirect('proyectoView', id=proyectoid)


def itemVerRelaciones(request,itemid, faseid, proyectoid):
    if request.method =='GET':
        """ID del proyecto"""
        #proyectoid = request.GET.get('proyectoid')
        """Proyecto en el cual se encuentra el item."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase."""
        #faseid = request.GET.get('faseid')
        """Fase en la cual se encuentra el item."""
        fase = Fase.objects.get(id=faseid)
        #itemid = request.GET.get('itemid')
        item_recibido = Item.objects.get(id=itemid)
        """ Recupera la lista de items antecesores a él de la tabla de relaciones"""
        items_antecesores = list(Relacion.objects.filter(tipo="sucesor", item_from=item_recibido))
        #if items_antecesores:
        """ Se encuentra la fase en donde están sus ítems antecesores"""
            #fase_antecesora = items_antecesores[0].fase

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

        return render(request, "item/ItemVerRelacion.html", {'proyecto': proyecto, 'fase': fase, 'item': item_recibido,
                                                             'antecesores': items_antecesores, 'sucesores':items_sucesores,
                                                             'padres': items_padres, 'hijos': items_hijos, })


def itemRelacionesRemover(request,itemid,item_rm, faseid, proyectoid):
    if request.method =='GET':
        """ID del proyecto"""
        #proyectoid = request.GET.get('proyectoid')
        """Proyecto en el cual se encuentra el item."""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """ID de fase."""
        #faseid = request.GET.get('faseid')
        """Fase en la cual se encuentra el item."""
        fase = Fase.objects.get(id=faseid)
        #itemid = request.GET.get('itemid')
        #itemid_final = request.GET.get('itemid_final')
        item_inicio = Item.objects.get(id=itemid)
        item_final_remover = Item.objects.get(id=item_rm)
        ok_remover_final = False
        if item_final_remover.estado == "aprobado" or item_final_remover.estado == "en linea base":
            "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
            relaciones_item_remover = item_final_remover.relaciones.exclude(id=item_inicio.id)
            for r in relaciones_item_remover:
                relacion = Relacion.objects.get(item_from=r, item_to=item_final_remover)
                if relacion.tipo == "padre" and (r.estado == "aprobado" or r.estado == "en linea base"):
                    ok_remover_final = True
                    break
                if relacion.tipo == "antecesor" and r.estado == "en linea base":
                    lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                    if lineaBaseItem.estado == "cerrada":
                        ok_remover_final = True
                        break
        else:
            ok_remover_final = True

        "El mismo testeo para el item del cual queremos remover la relacion."
        ok_remover_inicio = False
        "Debe verificar que el item no quede sin al menos una relacion a otro item aprobado o antecesor en linea base."
        relaciones_item_inicio = item_inicio.relaciones.exclude(id=item_final_remover.id)
        for r in relaciones_item_inicio:
            relacion = Relacion.objects.get(item_from=r, item_to=item_inicio)
            if relacion.tipo == "padre" and (r.estado == "aprobado" or r.estado == "en linea base"):
                ok_remover_inicio = True
                break
            if relacion.tipo == "antecesor" and r.estado == "en linea base":
                lineaBaseItem = LineaBase.objects.get(items__id=r.id)
                if lineaBaseItem.estado == "cerrada":
                    ok_remover_final = True
                    break

        if ok_remover_inicio and ok_remover_final:
            relaciones_uno = Relacion.objects.get(item_from=item_inicio, item_to=item_final_remover)
            relaciones_uno.delete()
            relaciones_dos = Relacion.objects.get(item_from=item_final_remover, item_to=item_inicio)
            relaciones_dos.delete()
            return redirect('itemVerRelaciones', itemid=item_inicio.id, faseid=faseid, proyectoid=proyectoid)

        return redirect('itemVerRelaciones', itemid=item_inicio.id, faseid=faseid, proyectoid=proyectoid)


def itemAddRelacion(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        itemid = request.GET.get('itemid')
        item = Item.objects.get(id=itemid)
        """Verificar que el usuario cuente con los permisos necesarios."""
        if not (request.user.has_perm("relacionar_item", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        if item.estado != "aprobado" and item.estado != "en linea base":
            return redirect('itemVerRelaciones', itemid=itemid, faseid=faseid, proyectoid=proyectoid)

        "Todos los id de las relaciones del item."
        relaciones = item.relaciones.all()
        relacionesId = []
        for r in relaciones:
            relacionesId.append(r.id)
        "Solo si esta en linea base puede avanzar de fase."
        siguiente = None
        itemsFaseSiguiente = None
        if item.estado == "en linea base":
            fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
            actual = False
            for fp in fasesProyecto:
                if actual == True:
                    siguiente = fp
                    break
                if fp == fase:
                    actual = True

            if siguiente is not None:
                itemsFaseSiguiente = siguiente.items.exclude(Q(estado="deshabilitado") | Q(id__in=relaciones)).order_by(
                    'id')

        itemsFaseActual = fase.items.exclude(
            Q(estado="deshabilitado") | Q(id=itemid) | Q(id__in=relaciones)).order_by('id')

        return render(request, 'item/itemAddRelacion.html',
                      {'proyecto': proyecto, 'fase': fase, 'item': item,
                       'itemsFaseSiguiente': itemsFaseSiguiente, 'itemsFaseActual': itemsFaseActual,
                       'faseSiguiente': siguiente, })

    else:
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        faseid = request.POST.get('faseid')
        fase = Fase.objects.get(id=faseid)
        itemIdActual = request.POST.get('itemIdActual')
        itemActual = Item.objects.get(id=itemIdActual)
        itemIdRelacion = request.POST.get('itemIdRelacion')
        faseSiguiente = request.POST.get('siguiente')
        fasesProyecto = proyecto.fases.exclude(estado="deshabilitada").order_by('id')
        itemRelacion = Item.objects.get(id=itemIdRelacion)
        for fp in fasesProyecto:
            items = fp.items.all()
            for i in items:
                if i == itemRelacion:
                    if faseSiguiente != "no":
                        if int(fp.id) == int(faseSiguiente):
                            Relacion.objects.create(tipo="antecesor", item_from=itemActual, item_to=itemRelacion,
                                                    fase_item_to=fp)
                            Relacion.objects.create(tipo="sucesor", item_from=itemRelacion, item_to=itemActual,
                                                    fase_item_to=fase)
                    if fp == fase:
                        Relacion.objects.create(tipo="padre", item_from=itemActual, item_to=itemRelacion,
                                                fase_item_to=fp)
                        Relacion.objects.create(tipo="hijo", item_from=itemRelacion, item_to=itemActual,
                                                fase_item_to=fase)

        return redirect('itemVerRelaciones', itemid=itemActual.id, faseid=faseid, proyectoid=proyectoid)


def faseGestionLineaBase(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        if not (request.user.has_perm("ver_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        lineasBase = fase.lineasBase.exclude(estado="rota")

        return render(request, "fase/faseGestionLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })


def faseAddLineaBase(request):
    if request.method=="POST":
        """
        Consulta si el post recibido es el de la selección de 
        un Tipo de Item o el post para guardar la información modificada.
        """
        proyecto = Proyecto.objects.get(id=request.POST.get('proyectoid'))
        fase = Fase.objects.get(id=request.POST.get('faseid'))
        nombre = request.POST.get('nombre')
        items = request.POST.getlist('items')

        lineaBase = LineaBase.objects.create(nombre=nombre, estado="abierta", creador=request.user)
        for i in items:
            item = Item.objects.get(id=i)
            item.estado = "en linea base"
            item.save()
            lineaBase.items.add(item)

        lineaBase.save()
        fase.lineasBase.add(lineaBase)
        fase.save()

        lineasBase = fase.lineasBase.exclude(estado="rota")
        """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
        return render(request, 'fase/faseGestionLineaBase.html',
                      {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })

    """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
    """Recupera de la BD el proyecto en el que se encuentra el usuario."""
    proyecto = Proyecto.objects.get(id=request.GET.get('proyectoid'))
    fase = Fase.objects.get(id=request.GET.get('faseid'))
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("create_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    if proyecto.estado != "inicializado":
        return redirect('faseView', faseid=fase.id, proyectoid=proyecto.id)


    itemsAprobados = fase.items.filter(estado="aprobado")
    for i in itemsAprobados:
        print(i.estado)
    cantidad = fase.lineasBase.all().count()
    nombre = "LineaBase" + str(cantidad+1) + "-" + fase.nombre
    return render(request, "fase/faseAddLineaBase.html", {'proyecto': proyecto, 'fase': fase,
                                                             'items': itemsAprobados, 'nombre': nombre, })

def faseConfigLineaBase(request,proyectoid,faseid,lineaBaseid):
    if request.method == 'GET':
        #proyectoid = request.GET.get('proyectoid')
        #faseid = request.GET.get('faseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        if not (request.user.has_perm("ver_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')
        items = lineaBase.items.all().order_by('id')

        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': items, 'lineaBase': lineaBase, })

def lineaBaseAddItem(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        faseid = request.GET.get('faseid')
        lineaBaseid = request.GET.get('lineaBaseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        if not (request.user.has_perm("modify_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        "No se pueden agregar en una linea base cerrada o rota"
        if lineaBase.estado != "abierta":
            itemsLineaBase = lineaBase.items.all().order_by('id')
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        items_disponibles = fase.items.filter(estado="aprobado")

        return render(request, 'fase/lineaBaseAddItem.html',
                      {'proyecto': proyecto, 'fase': fase,'lineaBase': lineaBase, 'items': items_disponibles, })

    else:
        proyectoid = request.POST.get('proyectoid')
        faseid = request.POST.get('faseid')
        lineaBaseid = request.POST.get('lineaBaseid')
        fase = Fase.objects.get(id=faseid)
        proyecto = Proyecto.objects.get(id=proyectoid)
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        items = request.POST.getlist('items')
        for i in items:
            item = Item.objects.get(id=i)
            lineaBase.items.add(item)
        lineaBase.save()
        itemsLineaBase = lineaBase.items.all().order_by('id')
        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

def lineaBaseRemoveItem(request,proyectoid,faseid,lineaBaseid,itemid):
    if request.method == 'GET':

        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        item_remover = Item.objects.get(id=itemid)
        if not (request.user.has_perm("modify_lineaBase", fase)) and not (request.user.has_perm("is_gerente", proyecto)):
            """Al no contar con los permisos, niega el acceso, redirigiendo."""
            return redirect('/permissionError/')

        "No se pueden agregar en una linea base cerrada o rota"
        if lineaBase.estado != "abierta":
            itemsLineaBase = lineaBase.items.all().order_by('id')
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        lineaBase.items.remove(item_remover)
        lineaBase.save()
        item_remover.estado = "aprobado"
        item_remover.save()
        itemsLineaBase = lineaBase.items.all().order_by('id')
        return render(request, "fase/faseConfigLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

def faseCerrarLineaBase(request):
    if request.method == 'GET':
        proyectoid = request.GET.get('proyectoid')
        faseid = request.GET.get('faseid')
        lineaBaseid = request.GET.get('lineaBaseid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        fase = Fase.objects.get(id=faseid)
        lineaBase = LineaBase.objects.get(id=lineaBaseid)
        if not(request.user == lineaBase.creador):
            return redirect('/permissionError/')
        if not lineaBase.items.all():
            itemsLineaBase = lineaBase.items.all().order_by('id')
            return render(request, "fase/faseConfigLineaBase.html",
                          {'fase': fase, 'proyecto': proyecto, 'items': itemsLineaBase, 'lineaBase': lineaBase, })

        lineaBase.estado = "cerrada"
        lineaBase.save()
        lineasBase = fase.lineasBase.exclude(estado="rota")

        return render(request, "fase/faseGestionLineaBase.html",
                      {'fase': fase, 'proyecto': proyecto, 'lineasBase': lineasBase, })



