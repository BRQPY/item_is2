from django.shortcuts import render, redirect
from .models import Proyecto, Fase, Rol, FaseUser, TipodeItem
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.decorators import permission_required
from django.contrib.postgres.fields import ArrayField

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
        proyecto = Proyecto.objects.create(nombre = nombre, descripcion=descripcion, fecha_inicio=fechaini, fecha_fin=fechafin, gerente=gerente)
        """Asignar el creador"""
        proyecto.creador=creador
        """Agregar creador a lista de usuarios"""
        proyecto.usuarios.add(creador)
        """Agregar permisos de gerente y permiso para Ver Proyecto al gerente"""
        assign_perm("is_gerente", gerente, proyecto)
        assign_perm("view_proyecto", gerente, proyecto)
        """Agregar gerente a lista de usuarios"""
        proyecto.usuarios.add(gerente)
        """Estado de proyecto creado: pendiente"""
        proyecto.estado="pendiente"
        """Guardar"""
        proyecto.save()
        """Vista a redirigir: homeView"""
        return redirect("/home/")

    else:
        """GET request, envia lista de usuarios para elegir el gerente y muestra el template para la creacion de proyecto."""
        usuarios = User.objects.all()
        """Template a renderizar: proyectoCrear.html"""
        return render(request, 'proyecto/proyectoCrear.html', {'usuarios': usuarios, })

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
    """Template a renderizar: proyecto.html con parametros -> proyectoid y fases del proyecto"""
    return render(request, 'proyecto/proyecto.html', {'proyecto': proyecto, 'fases':fases, })

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
    if not(request.user.has_perm("view_proyecto", proyecto)):
        return redirect('/permissionError/')

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

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
    proyecto.fecha_inicio = fechaini
    proyecto.fecha_fin = fechafin
    """Guardar"""
    proyecto.save()

    """Template a renderizar: gestionProyecto con parametro -> proyectoid"""
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

def proyectoDeshabilitar(request):
    """
       **proyectoDeshabilitar:**
        Vista utilizada para visualizar Deshabilitar Proyecto.
        Solicita que el usuario que realiza el request cuente
        con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para deshabilitar el proyecto"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')

        """Proyecto a deshabilitar"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Template a renderizar: proyectoDeshabilitar.html con parametro -> proyectoid"""
        return render(request, 'proyecto/proyectoDeshabilitar.html', {'proyectoid': proyectoid, })

    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Confirmar accion -> si"""
    if request.POST.get('pregunta') == "si":
        """Proyecto a deshabilitar"""
        proyecto = Proyecto.objects.get(id=proyectoid)

        """Deshabilitar proyecto, cambio de estado"""
        proyecto.estado = "deshabilitado"
        proyecto.save()

        """Template a renderizar: home.html"""
        return redirect("/home/")

    """Confirmar accion -> no"""
    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })

def faseView(request, faseid, proyectoid):
    """
       **faseView:**
        Vista utilizada solo para demostracion.
        Permite acceder a la fase si el usuario
        fue asignado con un rol correspondiente
    """
    fase = Fase.objects.get(id=faseid)
    proyecto = Proyecto.objects.get(id=proyectoid)
    if not (request.user.has_perm("view_fase", fase)) and not(request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    return render(request, 'fase/fase.html', {'fase': fase, 'proyecto': proyecto, })

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

    """Template a renderizar; proyectoUser.html con parametros -> proyectoid y usuarios del proyecto"""
    return render(request, 'proyecto/proyectoUser.html', {'proyectoid': proyectoid, 'usuarios': usuarios, })

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

        """Gerente del proyecto"""
        gerente = Proyecto.objects.get(id=proyectoid).gerente
        usuarios = []
        """Lista de usuarios posibles a ser agregados"""
        users = User.objects.all()
        for u in users:
            """
            Filtrar que no se pueda agregar un usuario staff, 
            gerente. Tampoco puede ser el usuario que realiza
            el request ni los usuarios ya agregados al proyecto
            """
            if u.is_staff == False and u != request.user and u != gerente and not(u in proyecto.usuarios.all()):
                usuarios.append(u)
        """
        Template a renderizar: proyectoUserAdd.html con parametros
         -> usuarios posibles para agregar y proyectoid
        """
        return render(request, "proyecto/proyectoUserAdd.html", {'usuarios': usuarios, 'proyectoid': proyectoid, })

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

    """
    Template a renderizar: gestionProyecto.html con parametro -> proyectoid
    """
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

def proyectoUserRemove(request):
    """
       **proyectoUserRemove:**
        Vista utilizada para remover miembros del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """

    """GET request, muestra el template correspondiente para remover miembros del proyecto"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto al cual remover miembros"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        proyecto = Proyecto.objects.get(id=proyectoid)
        """Gerente del proyecto"""
        gerente = Proyecto.objects.get(id=proyectoid).gerente
        usuarios = []
        """Lista de miembros del proyecto"""
        u = proyecto.usuarios.all()
        for user in u:
            """
            Filtrar que no se pueda remover un usuario staff,
            gerente. Tampoco puede ser el usuario que realiza
            el request.
            """
            if user.is_staff == False and user != request.user and user != gerente:
                usuarios.append(user)

        """
         Template a renderizar: proyectoUserRemove.html con parametro->
         usuarios posibles para remover y proyectoid
        """
        return render(request, "proyecto/proyectoUserRemove.html", {'usuarios': usuarios, 'proyectoid': proyectoid, })

    """POST request, captura la lista de usuarios para remover del proyecto"""
    """Lista de usuarios a remover"""
    users = request.POST.getlist('users')
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto del cual remover"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    for u in users:
        """Usuario a remover"""
        user = User.objects.get(id=u)
        """Remover usuario"""
        proyecto.usuarios.remove(user)
        """Remover permiso para ver el proyecto"""
        remove_perm("view_proyecto", user, proyecto)
        if user in proyecto.comite.all():
            """Si el usuario era miembro del Comite de Control de Cambio. removerlo."""
            proyecto.comite.remove(user)
            """Remover permiso para aprobar la rotura de linea base."""
            remove_perm("aprobar_rotura_lineaBase", user, proyecto)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

def proyectoComite(request):
    """
       **proyectoComite:**
        Vista utilizada para mostrar Gestion de Comite
        de Control de Cambios del Proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """ID del proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Lista de miembros del comite para mostrar en el template"""
    comite = proyecto.comite.all()
    """Template a renderizar: proyectoComite.html con parametros -> proyectoid y comite de control de cambios"""
    return render(request, 'proyecto/proyectoComite.html', {'proyectoid': proyectoid, 'comite': comite, })

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

        miembros = []
        """Lista de usuarios del proyecto"""
        users = proyecto.usuarios.all()
        for u in users:
            """Filtrar que no sean usuarios que ya pertenecen al comite"""
            if not(u in proyecto.comite.all()):
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
        """Agregar el permiso para aprobar rotura de linea base"""
        assign_perm("aprobar_rotura_lineaBase", user, proyecto)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

def proyectoComiteRemove(request):
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
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')

        """Proyecto en el cual remover miembros del comite"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')
        """Lista de miembros del comite"""
        miembros = proyecto.comite.all()
        """
         Template a renderizar: proyectoComiteRemove.html con parametros ->
         miembros del comite y proyectoid
         """
        return render(request, "proyecto/proyectoComiteRemove.html", {'miembros': miembros, 'proyectoid': proyectoid, })

    """POST request, captura una lista de miembros para remover del comite"""
    """Lista de miembros"""
    users = request.POST.getlist('miembros')
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto del cual remover los miembros del comite"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    for u in users:
        """Usuario a remover del comite"""
        user = User.objects.get(id=u)
        """Remover usuario del comite"""
        proyecto.comite.remove(user)
        """Remover permisos para aprobar rotura de linea base"""
        remove_perm("aprobar_rotura_lineaBase", user, proyecto)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })

def proyectoRol(request):
    """
       **proyectoRol:**
        Vista utilizada para mostrar Gestion de Roles en el proyecto.
        Solicita que el usuario que realiza el request cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """ID del proyecto"""
    proyectoid = request.GET.get('proyectoid')
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
    return render(request, 'proyecto/proyectoRol.html', {'proyectoid': proyectoid, 'roles': roles, })

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
        """Nombre del Rol"""
        nombre = request.POST.get('nombre')
        """Verificar si ya existe un rol con el nombre especificado, este debe ser unico"""
        if Rol.objects.filter(nombre=nombre).exists():
            """Template a renderizar: proyectoRolCrear.html con parametros -> mensaje de error"""
            return render(request, 'proyecto/proyectoRolCrear.html', {'mensaje':"Lo sentimos, el nombre del Rol ya ha sido asignado.", })

        """Crear el rol con el nombre especificado"""
        rol = Rol.objects.create(nombre=nombre)
        """Crear grupo de permisos con el nombre especificado"""
        grupo = Group.objects.create(name=nombre)
        """Lista de permisos de proyecto para el rol"""
        permisos = request.POST.getlist('perms')

        for p in permisos:
            if int(p) == 1:
                """Permiso Proyecto ID=1 corresponde a Crear Fase"""
                permiso = Permission.objects.get(codename="add_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 2:
                """Permiso Proyecto ID=2 corresponde a Modificar Fase"""
                permiso = Permission.objects.get(codename="change_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 3:
                """Permiso Proyecto ID=3 corresponde a Remover Fase"""
                permiso = Permission.objects.get(codename="delete_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 4:
                """Permiso Proyecto ID=4 corresponde a Ver Fase"""
                permiso = Permission.objects.get(codename="view_fase")
                grupo.permissions.add(permiso)
            elif int(p) == 5:
                """Permiso Proyecto ID=5 corresponde a Crear Item"""
                permiso = Permission.objects.get(codename="create_item")
                grupo.permissions.add(permiso)
            elif int(p) == 6:
                """Permiso Proyecto ID=6 corresponde a Aprobar Item"""
                permiso = Permission.objects.get(codename="aprobar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 7:
                """Permiso Proyecto ID=7 corresponde a Deshabilitar Item"""
                permiso = Permission.objects.get(codename="deshabilitar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 8:
                """Permiso Proyecto ID=8 corresponde a Reversionar Item"""
                permiso = Permission.objects.get(codename="reversionar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 9:
                """Permiso Proyecto ID=9 corresponde a Relacionar Item"""
                permiso = Permission.objects.get(codename="relacionar_item")
                grupo.permissions.add(permiso)
            elif int(p) == 10:
                """Permiso Proyecto ID=10 corresponde a Modificar Item"""
                permiso = Permission.objects.get(codename="change_item")
                grupo.permissions.add(permiso)
            elif int(p) == 11:
                """Permiso Proyecto ID=11 corresponde a Establecer Item Pendiente de Aprobacion"""
                permiso = Permission.objects.get(codename="establecer_itemPendienteAprob")
                grupo.permissions.add(permiso)
            elif int(p) == 12:
                """Permiso Proyecto ID=12 corresponde a Establecer Item Desarrollo"""
                permiso = Permission.objects.get(codename="establecer_itemDesarrollo")
                grupo.permissions.add(permiso)
            elif int(p) == 13:
                """Permiso Proyecto ID=13 corresponde a Obtener Trazabilidad de Item"""
                permiso = Permission.objects.get(codename="obtener_trazabilidadItem")
                grupo.permissions.add(permiso)
            elif int(p) == 14:
                """Permiso Proyecto ID=14 corresponde a Ver Item"""
                permiso = Permission.objects.get(codename="view_item")
                grupo.permissions.add(permiso)
            elif int(p) == 15:
                """Permiso Proyecto ID=15 corresponde a Obtener Calculo de Impacto"""
                permiso = Permission.objects.get(codename="obtener_calculoImpacto")
                grupo.permissions.add(permiso)
            elif int(p) == 16:
                """Permiso Proyecto ID=16 corresponde a Crear Linea Base"""
                permiso = Permission.objects.get(codename="create_lineaBase")
                grupo.permissions.add(permiso)
            elif int(p) == 17:
                """Permiso Proyecto ID=17 corresponde a Romper Linea Base"""
                permiso = Permission.objects.get(codename="romper_lineaBase")
                grupo.permissions.add(permiso)
            elif int(p) == 18:
                """Permiso Proyecto ID=18 corresponde a Solicitar Rotura de Linea Base"""
                permiso = Permission.objects.get(codename="solicitar_roturaLineaBase")
                grupo.permissions.add(permiso)

        """Establecer el grupo de permisos al rol"""
        rol.perms = grupo
        """Guardar ROl"""
        rol.save()
        """Proyecto al cual agregar rol"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Agregar rol a proyecto"""
        proyecto.roles.add(rol)

        """Template a renderizar: gestion Proyecto.html con parametro -> proyectoid"""
        return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })
    else:
        """GET request, muestra el template correspondiente para la creacion del rol"""
        """ID Proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Template a renderizar: proyectoRolCrear.html con parametro -> proyectoid"""
        return render(request, "proyecto/proyectoRolCrear.html", {'proyectoid': proyectoid, })

def proyectoRolModificar(request):
    """
       **proyectoRolModificar:**
        Vista utilizada para modificar roles del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    seleccion = None
    permisos = None
    """ID Proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """POST request, captura la nueva informacion para el rol para actualizarlo"""
    if request.method == "POST":
        """Boton Modificar presionado en el template"""
        if 'changerol' in request.POST:
            """ID del rol"""
            rolid = request.POST.get('rolid')
            """Permisos nuevos para el rol"""
            permisos = request.POST.getlist('perms')
            """Nuevo nombre del rol"""
            nombre = request.POST.get('nombre')
            """ID del proyecto"""
            proyectoid = request.POST.get('proyectoid')
            """Verificar si el nombre asignado ya corresponde al nombre de otro rol"""
            if Rol.objects.filter(nombre=nombre).exclude(id=rolid).exists():
                """Proyecto correspondiente"""
                proyecto = Proyecto.objects.get(id=proyectoid)
                """Roles del Proyecto"""
                roles = proyecto.roles.all()
                """
                Template a renderizar: proyectoRolModificar.html con parametros -> 
                roles del proyecto, proyectoid y mensaje de error
                """
                return render(request, "proyecto/proyectoRolModificar.html",
                              {'roles': roles, 'select': None, 'proyectoid': proyectoid, 'permisos': None,
                               'mensaje': "Lo sentimos, el nombre del Rol ya ha sido asignado.", })

            """Rol a modificar"""
            rol = Rol.objects.get(id=rolid)
            vector = []
            """Grupo a poseer los nuevos permisos"""
            grupo = Group.objects.get(name=rol.nombre)
            grupo.name = nombre
            """Asignar nuevo nombre al rol"""
            rol.nombre = nombre

            for p in permisos:
                """Permiso Proyecto ID=1 corresponde a Crear Fase"""
                if int(p) == 1:
                    permiso = Permission.objects.get(codename="add_fase")
                    vector.append(permiso)
                elif int(p) == 2:
                    """Permiso Proyecto ID=2 corresponde a Modificar Fase"""
                    permiso = Permission.objects.get(codename="change_fase")
                    vector.append(permiso)
                elif int(p) == 3:
                    """Permiso Proyecto ID=3 corresponde a Remover Fase"""
                    permiso = Permission.objects.get(codename="delete_fase")
                    vector.append(permiso)
                elif int(p) == 4:
                    """Permiso Proyecto ID=4 corresponde a Ver Fase"""
                    permiso = Permission.objects.get(codename="view_fase")
                    vector.append(permiso)
                elif int(p) == 5:
                    """Permiso Proyecto ID=5 corresponde a Crear Item"""
                    permiso = Permission.objects.get(codename="create_item")
                    vector.append(permiso)
                elif int(p) == 6:
                    """Permiso Proyecto ID=6 corresponde a Aprobar Item"""
                    permiso = Permission.objects.get(codename="aprobar_item")
                    vector.append(permiso)
                elif int(p) == 7:
                    """Permiso Proyecto ID=7 corresponde a Deshabilitar Item"""
                    permiso = Permission.objects.get(codename="deshabilitar_item")
                    vector.append(permiso)
                elif int(p) == 8:
                    """Permiso Proyecto ID=8 corresponde a Reversionar Item"""
                    permiso = Permission.objects.get(codename="reversionar_item")
                    vector.append(permiso)
                elif int(p) == 9:
                    """Permiso Proyecto ID=9 corresponde a Relacionar Item"""
                    permiso = Permission.objects.get(codename="relacionar_item")
                    vector.append(permiso)
                elif int(p) == 10:
                    """Permiso Proyecto ID=10 corresponde a Modificar Item"""
                    permiso = Permission.objects.get(codename="change_item")
                    vector.append(permiso)
                elif int(p) == 11:
                    """Permiso Proyecto ID=11 corresponde a Establecer Item Pendiente de Aprobacion"""
                    permiso = Permission.objects.get(codename="establecer_itemPendienteAprob")
                    vector.append(permiso)
                elif int(p) == 12:
                    """Permiso Proyecto ID=12 corresponde a Establecer Item Desarrollo"""
                    permiso = Permission.objects.get(codename="establecer_itemDesarrollo")
                    vector.append(permiso)
                elif int(p) == 13:
                    """Permiso Proyecto ID=13 corresponde a Obtener Trazabilidad de Item"""
                    permiso = Permission.objects.get(codename="obtener_trazabilidadItem")
                    vector.append(permiso)
                elif int(p) == 14:
                    """Permiso Proyecto ID=14 corresponde a Ver Item"""
                    permiso = Permission.objects.get(codename="view_item")
                    vector.append(permiso)
                elif int(p) == 15:
                    """Permiso Proyecto ID=15 corresponde a Obtener Calculo de Impacto"""
                    permiso = Permission.objects.get(codename="obtener_calculoImpacto")
                    vector.append(permiso)
                elif int(p) == 16:
                    """Permiso Proyecto ID=16 corresponde a Crear Linea Base"""
                    permiso = Permission.objects.get(codename="create_lineaBase")
                    vector.append(permiso)
                elif int(p) == 17:
                    """Permiso Proyecto ID=17 corresponde a Romper Linea Base"""
                    permiso = Permission.objects.get(codename="romper_lineaBase")
                    vector.append(permiso)
                elif int(p) == 18:
                    """Permiso Proyecto ID=18 corresponde a Solicitar Rotura de Linea Base"""
                    permiso = Permission.objects.get(codename="solicitar_roturaLineaBase")
                    vector.append(permiso)

            """Agregar permisos al grupo"""
            grupo.permissions.set(vector)
            """Guardar grupo"""
            grupo.save()
            """Agregar grupo de permisos al rol"""
            rol.perms = grupo
            """Guardar Rol"""
            rol.save()

            """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
            return render(request, 'proyecto/gestionProyecto.html', {'proyectoid': proyectoid, })


        else:
            """Boton MOdificar no ha sido presionado en el template"""
            """ID Proyecto"""
            proyectoid = request.POST.get('proyectoid')
            """ID del Rol"""
            rolid = request.POST.get('roles')
            """Rol a MOdificar"""
            rol = Rol.objects.get(id=rolid)
            """Verificar si el rol ha sido asignado previamente"""
            if rol.faseUser.filter().exists():
                """Proyecto correspondiente"""
                proyecto = Proyecto.objects.get(id=proyectoid)
                """Lista de roles del proyecto"""
                roles = proyecto.roles.all()

                """
                Template a renderizar: proyectoRolModificar.html con parametro -> 
                roles del proyecto, proyectoid y 
                mensaje de error
                """
                return render(request, "proyecto/proyectoRolModificar.html",
                              {'roles': roles, 'select': None, 'proyectoid': proyectoid, 'permisos': None,
                               'mensaje': "Lo sentimos, no es posible modificar un rol previamente asignado.", })

            """Si el rol no ha sido asignado"""
            """Actualizar los datos para visualizar en el template"""
            seleccion = rol
            permisos = []
            """Permisos del rol"""
            perms = rol.perms.permissions.all()
            for p in perms:
                permisos.append(p.codename)

    """GET request, muestra el template correspondiente a la modificacion de roles"""
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Roles del proyecto"""
    roles = proyecto.roles.all()

    """Template a renderizar: proyectoRolModificar.html con parametros -> roles del proyecto, proyectoid"""
    return render(request, "proyecto/proyectoRolModificar.html", {'roles': roles, 'select': seleccion, 'proyectoid': proyectoid, 'permisos': permisos, })



def proyectoRolEliminar(request):
    """
       **proyectoRolEliminar:**
        Vista utilizada para remover roles del proyecto.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para remover roles del proeycto"""
    if request.method == 'GET':
        """ID del proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Lista de roles del proyecto"""
        roles = proyecto.roles.all()
        """
        Template a renderizar: proyectoRolEliminar.html con parametros -> roles
        del proyecto y proyectoid
         """
        return render(request, "proyecto/proyectoRolEliminar.html", {'roles': roles, 'proyectoid': proyectoid, })

    """POST request, captura el rol para remover del proyecto"""
    """ID del proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Lista de roles del proyecto"""
    roles = proyecto.roles.all()
    """ID del rol a remover"""
    rolid = request.POST.get('roles')
    """Rol a remover"""
    rol = Rol.objects.get(id=rolid)
    """Verificar si el rol ha sido asignado previamente"""
    if rol.faseUser.filter().exists():
        """
        Template a renderizar: proyectoRolEliminar.html con parametros -> roles
        del proyecto, proyectoid
        y mensaje de error
        """
        return render(request, "proyecto/proyectoRolEliminar.html", {'roles': roles, 'proyectoid': proyectoid,
                                        'mensaje': "Lo sentimos, no puede remover un rol previamente asignado."})

    """Si el rol no ha sido asignado previamente"""
    proyecto.roles.remove(rol)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })




def proyectoRolAsignar(request):

    """
       **proyectoRolAsignar:**
        Vista utilizada para asignar roles del proyecto a usuarios.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para asignar roles del proyecto"""
    if request.method == 'GET':
        """Proyecto ID"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Lista de usuarios del proyecto"""
        usuarios = proyecto.usuarios.all()
        """Lista de roles del proyecto"""
        roles = proyecto.roles.all()
        """Lista de fases del proyecto"""
        fases = proyecto.fases.all()
        """
        Template a renderizar: proyectoRolAsignar.html con parametros -> roles
        ,usuarios y fases del proyecto,
         ademas de proyectoid
         """
        return render(request, "proyecto/proyectoRolAsignar.html", {'fases': fases, 'usuarios': usuarios, 'roles': roles, 'proyectoid': proyectoid, })

    """POST request, captura el usuario, el rol y las fases para asignar el mismo"""
    """ID User"""
    userid = request.POST.get('users')
    """ID rol"""
    rolid = request.POST.get('roles')
    """ID fase"""
    fases = request.POST.getlist('fases')
    """ID proyecto"""
    proyectoid = request.POST.get('proyectoid')
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

    for f in fases:
        fase = Fase.objects.get(id=f)
        """Verificar si el usuario ya cuenta con el rol"""
        if rol.faseUser.filter(user=user, fase=fase).exists():
            proyecto = Proyecto.objects.get(id=proyectoid)
            usuarios = proyecto.usuarios.all()
            roles = proyecto.roles.all()
            fases = proyecto.fases.all()
            """
             Template a renderizar: proyectoRolAsignar.html con parametros -> roles,
             usuario y fases del proyecto, ademas
             de proyecto id y mensaje de error
             """
            return render(request, "proyecto/proyectoRolAsignar.html",
                            {'fases': fases, 'usuarios': usuarios, 'roles': roles,
                            'proyectoid': proyectoid,
                            'mensaje': "El usuario ya cuenta con el rol en alguna de las fases seleccionadas.", })


    for f in fases:
        fase = Fase.objects.get(id=f)
        """Crear asociacion entre fase y usuario"""
        faseUser = FaseUser.objects.create(user=user, fase=fase)
        for c in codenames:
            """Agregar asociacion al rol"""
            rol.faseUser.add(faseUser)
            """Asignar los permisos del rol al grupo, en la fase correspondiente"""
            assign_perm(c, grupo, fase)
            """Asignar el grupo al usuario"""
            user.groups.add(grupo)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })






def proyectoRolRemover(request):
    """
       ** proyectoRolRemover:**
        Vista utilizada para remover roles del proyecto de usuarios.
        Solicita que el usuario que realiza el request
        cuente con los permisos de gerente del proyecto
        y que (indirectamente) haya iniciado sesion
    """
    """GET request, muestra el template correspondiente para remover roles del proyecto"""
    if request.method == 'GET':
        """ID proyecto"""
        proyectoid = request.GET.get('proyectoid')
        """Proyecto correspondiente"""
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Verificar permiso necesario en el proyecto correspondiente"""
        if not (request.user.has_perm("is_gerente", proyecto)):
            return redirect('/permissionError/')

        """Usuarios del proyecto"""
        usuarios = proyecto.usuarios.all()
        """Roles del proyecto"""
        roles = proyecto.roles.all()
        """Fases del proyecto"""
        fases = proyecto.fases.all()

        """
        Template a renderizar: proyectoRolRemover.html con parametros roles,
        fases y usuarios del proyecto, 
        ademas de proyectoid
        """
        return render(request, "proyecto/proyectoRolRemover.html", {'fases': fases, 'usuarios': usuarios, 'roles': roles, 'proyectoid': proyectoid, })

    """POST request, captura el usuario, el rol y las fases para remover"""
    """ID user"""
    userid = request.POST.get('users')
    """ID rol"""
    rolid = request.POST.get('roles')
    """ID fases"""
    fases = request.POST.getlist('fases')
    """ID proyecto"""
    proyectoid = request.POST.get('proyectoid')
    """Usuario al cual remover el rol"""
    user = User.objects.get(id=userid)
    """Rol a remover"""
    rol = Rol.objects.get(id=rolid)
    """Permisos del rol"""
    grupo = rol.perms
    permisos = grupo.permissions.all()
    codenames = []
    for p in permisos:
        codenames.append(p.codename)

    for f in fases:
        fase = Fase.objects.get(id=f)
        """Verificar si el rol ha sido asignado previamente"""
        if not rol.faseUser.filter(user=user, fase=fase).exists():
            proyecto = Proyecto.objects.get(id=proyectoid)
            usuarios = proyecto.usuarios.all()
            roles = proyecto.roles.all()
            fases = proyecto.fases.all()
            """
            Template a renderizar: proyectoRolRemover.html con parametros -> fases,
            roles y usuarios del proyecto,
            ademas de proyectoid y mensaje de error
            """

            return render(request, "proyecto/proyectoRolRemover.html",
                          {'fases': fases, 'usuarios': usuarios, 'roles': roles,
                           'proyectoid': proyectoid,
                           'mensaje': "El usuario no cuenta con el rol en alguna de las fases seleccionadas.", })


    for f in fases:
        fase = Fase.objects.get(id=f)
        """Eliminar asociacion entre fase y usuario"""
        FaseUser.objects.filter(user=user, fase=fase).delete()
        for c in codenames:
            """Remover los permisos del rol, al grupo en la fase correspondiente"""
            remove_perm(c, grupo, fase)
            """Agregar el grupo al usuario"""
            user.groups.add(grupo)

    """Template a renderizar: gestionProyecto.html con parametro -> proyectoid"""
    return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })

def proyectoTipodeItem(request):
    """ID del proyecto"""
    proyectoid = request.GET.get('proyectoid')
    """Proyecto correspondiente"""
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')

    """Lista de miembros del comite para mostrar en el template"""
    tipoItem = proyecto.tipoItem.all()
    """Template a renderizar: proyectoComite.html con parametros -> proyectoid y tipos de item"""
    return render(request, 'proyecto/proyectoTipodeItem.html', {'proyectoid': proyectoid, 'comite': tipoItem, })

def crear_tipo_form(request):

    if request.method=="POST":
        """Recibe el POST con los datos del formulario para la creación de un Tipo de Item"""
        dato = request.POST
        """Recupera de la BD el proyecto en el que se encuentra el usuario."""
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Se asignan variables con los valores del POST para poder crear el tipo de Item"""
        nombre1= dato['nombretipo']
        descrip = dato['descripciontipo']
        campo = dato['Campos'].split(',')
        """Creación de un objeto Tipo de Item con los valores recibidos en el post"""
        obj = TipodeItem.objects.create(nombre=nombre1,descripcion=descrip)
        """Ciclo para agregar los campos extra creados por el usuario al objeto del tipo "Tipo de Item" """
        for c in campo:
            obj.campo_extra.append(c)
        """Se guarda en la BD el objeto creado"""
        obj.save()
        """Se asigna el proyecto en el cual se encuentra proyectoidel usuario el nuevo tipo de Item creado"""
        proyecto.tipoItem.add(obj)
        return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })

    """En caso de recibir un método GET, renderiza al html creartipo.html"""
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')
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
    return render(request, "proyecto/gestionartipodeitem.html", {'proyectoid': proyectoid, 'tipos': tipos})


def modificar_tipo_de_item(request):
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
    seleccion= None
    if request.method=="POST":
        """
        Consulta si el post recibido es el de la selección de 
        un Tipo de Item o el post para guardar la información modificada.
        """
        if 'cambio' in request.POST:
            proyectoid = request.POST.get('proyectoid')
            proyecto = Proyecto.objects.get(id=proyectoid)
            dato= request.POST
            """Recibe el POST con los datos del formulario para la modificación de un Tipo de Item"""
            """Creación de un objeto Tipo de Item con los valores recibidos en el post"""
            obj = proyecto.tipoItem.get(id=dato['tipodeitem_id'])
            """Se guarda en el objeto Tipo de Item los valores de modificación establecidos por el usuario."""
            obj.nombre = dato['nombretipo']
            obj.descripcion= dato['descripciontipo']
            cambios= request.POST.getlist('campos')
            campos_add= dato['camposadd'].split(",")
            """Se crea un vector para guardar los cambios en los campos extras"""
            cambios_campos= []
            for c in cambios:
                if c is not '':
                    """
                    Agrega campos que no sean igual a un espacio en blanco,
                    pues estos fueron eliminados por el usuario.
                    """
                    cambios_campos.append(c)
            for cc in campos_add:
                """Guarda los campos extra filtrados, es decir, sin espacios en blanco."""
                cambios_campos.append(cc)
            obj.campo_extra=cambios_campos
            """Guarda las modificaciones en la BD"""
            obj.save()
            return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })
        else:
            proyectoid = request.POST.get('proyectoid')
            proyecto = Proyecto.objects.get(id=proyectoid)
            """
            Se asigna a la variable "tipos" todos los Tipos de Item 
            con los que cuenta el proyecto en el cual se encuentra el usuario
            """
            tipos = proyecto.tipoItem.all()
            """POST para la seleccion de un Tipo de Item"""
            """Guarda en la variable seleccion el tipo de Item seleccionado por el usuario."""
            seleccion = TipodeItem.objects.get(id=request.POST['tipo'])
            return render(request, "proyecto/modifTipodeItem.html",
                          {'proyectoid': proyectoid, 'tipos': tipos, 'select': seleccion})

    """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
    """Recupera de la BD el proyecto en el que se encuentra el usuario."""
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')
    """
    Se asigna a la variable "tipos" todos los Tipos de Item
    con los que cuenta el proyecto en el cual se encuentra el usuario
    """

    tipos = proyecto.tipoItem.all()
    return render(request, "proyecto/modifTipodeItem.html", {'proyectoid': proyectoid, 'tipos':tipos, 'select':seleccion})


def importar_tipo_de_item(request):

    """
       **importar_tipo_de_item:**
        View para la importación de
        Tipos de Item al proyecto.
    """
    if request.method=="POST":
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """Recibe los tipos de Item que el usuario desea importar al proyecto actual."""
        elegidos = request.POST.getlist('importados')
        """Ciclo para recorrer los tipos de Item seleccionados por el usuario."""
        tipos = TipodeItem.objects.all()
        for e in elegidos:
            tipo = tipos.get(id=e)
            """Agrega al proyecto actual los tipos de Item seleccionados."""
            proyecto.tipoItem.add(tipo)
        return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })

    """Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario"""
    """Recupera de la BD el proyecto en el que se encuentra el usuario."""
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')
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
    return render(request,"proyecto/importartipo.html",{'tipos':tipos_de_item, 'proyectoid': proyectoid})

def remover_tipo_de_item(request):
    """
       **remover_tipo_de_item:**
        View para remover un tipo de Item
    """
    if request.method == "POST":
        """
        Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario
        Recupera de la BD el proyecto en el que se encuentra el usuario.
        """
        proyectoid = request.POST.get('proyectoid')
        proyecto = Proyecto.objects.get(id=proyectoid)
        """
        Recupera de la BD todos los Tipos de Item con los que 
        cuenta el proyecto en el cual se encuentra el usuario.
        """

        tipos_enel_proyecto = proyecto.tipoItem.all()
        """Recibe los tipos de Item que el usuario desea remover del proyecto actual."""
        eliminados= request.POST.getlist('eliminados')
        """Ciclo para recorrer los tipos de Item seleccionados por el usuario."""
        for e in eliminados:
            tipo = tipos_enel_proyecto.get(id=e)
            """Agrega del proyecto actual los tipos de Item seleccionados."""
            proyecto.tipoItem.remove(tipo)
        return render(request, "proyecto/gestionProyecto.html", {'proyectoid': proyectoid, })

    """
    Se recibe el ID del proyecto en el cual se encuentra actualmente el Usuario
    Recupera de la BD el proyecto en el que se encuentra el usuario.
    """
    proyectoid = request.GET.get('proyectoid')
    proyecto = Proyecto.objects.get(id=proyectoid)
    """Verificar permiso necesario en el proyecto correspondiente"""
    if not (request.user.has_perm("is_gerente", proyecto)):
        return redirect('/permissionError/')
    """
    Recupera de la BD todos los Tipos de Item con los
    que cuenta el proyecto en el cual se encuentra el usuario.
    """
    tipos_enel_proyecto = proyecto.tipoItem.all()
    """Renderiza la página cargandola con todos los tipos de Item en el proyecto."""
    proyectoid = request.GET.get('proyectoid')
    return render(request, "proyecto/removertipo.html",{'tipos':tipos_enel_proyecto, 'proyectoid': proyectoid})