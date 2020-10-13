from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import  EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
from django.template.loader import get_template
from gestionUser.tasks import sendEmailView







@login_required
def gestionUserView(request):

    """
       **gestionUserView:**
        Vista que muestra el menu de Gestion de Usuarios.
        Solicita que el usuario que realiza el request haya
        iniciado sesion en el sistema.

    """

    """
    Template a renderizar: gestionUser.html
    """
    if request.method == 'GET':
        users = User.objects.all().exclude(username="AnonymousUser")
        user_confirmados = []
        user_deshabilitados = []
        user_pendientes = []
        for u in users:
            if u.is_staff == False and u.is_active and u.username != "AnonymousUser" and u.has_perm("perms.view_menu"):
                user_confirmados.append(u)
            if u.has_perm("perms.view_menu") == False and u.is_active:
                user_pendientes.append(u)
            if u.is_staff == False and u.is_active == False:
                user_deshabilitados.append(u)

        return render(request, 'gestionUser/gestionUser.html',{'confirmados':user_confirmados,
                                                               'pendientes': user_pendientes,
                                                               'deshabilitados': user_deshabilitados,
                                                               'usuarios':users,
                                                               'perm_confirmar_user' : request.user.has_perm("perms.assign_perms"),
                                                               'perm_enable_user': request.user.has_perm("perms.perms.unable_user"),
                                                               'perm_unable_user': request.user.has_perm("perms.unable_user"),
                                                               })



@permission_required('perms.assign_perms', login_url='/permissionError/')

def confUserView(request):
    """
       **confUserView:**
        Vista utilizada para confirmar a los usuarios que aun
        no cuentan con los permisos para acceder al sistema.
        Solicita que el usuario que realiza el request cuente
        con el permiso para asignar permisos a otros usuarios
        y que (indirectamente) haya iniciado sesion
    """
    usuarios = []
    u = User.objects.all()
    """
    Lista de todos los usuarios del sistema.
    """
    for user in u:
        """
        Filtrar solamente los usuarios que tengan el acceso restringido. Tambien que
        el usuario este activo.
        """
        if user.has_perm("perms.view_menu") == False and user.is_active and user.username != "AnonymousUser":
            usuarios.append(user)

    """
    GET request, muestra el template correspondiente para confirmar el acceso a los usuarios.
    """
    if request.method == "GET":
        """
        Template a renderizar: conf.html.
        """
        return render(request, 'gestionUser/conf.html', {'usuarios': usuarios, })

    """
    POST request, captura una lista de usuarios a confirmar.
    """
    if request.method == "POST":
        permiso = Permission.objects.get(codename="view_menu")
        users = request.POST.getlist('users')
        for u in users:
            """
            Conceder el acceso a los usuarios elegidos, asignando el permiso para ver el menu principal.
            """
            usuario = User.objects.get(id=u)
            usuario.user_permissions.add(permiso)
            usuario.save()
            #mail = usuario.email
            #name = usuario.username
            #messages.success(request, "Permisos asignados exitosamente!")
            #sendEmailView.delay(mail, name)
            
        """
        Template a renderizar: gestionUser.html.
        """
        return redirect('gestionUserView')



@permission_required('perms.assign_perms', login_url='/permissionError/')
def gestionPermsView(request):
    """
       **gestionPermsView:**
        Vista que muestra la seccion de Permisos del Sistema.
        Solicita que el usuario que realiza el request
        cuente con los permisos para asignar permisos
        a otros usuarios y que (indirectamente)
        haya iniciado sesion en el sistema.
    """
    """
    Template a renderizar: permisos.html
    """
    return render(request, "gestionUser/permisos.html")



@permission_required('perms.assign_perms', login_url='/permissionError/')
def addPermsView(request):
    """
       **addPermsView:**
        Vista utilizada para agregar Permisos del Sistema
        a los usuarios.
        Solicita que el usuario que realiza el request
        cuente con el permiso para asignar permisos a
        otros usuarios y que (indirectamente) haya iniciado
        sesion.
    """
    seleccion = None
    """
    POST request, captura una un usuario y una lista de permisos para agregar al mismo.
    """
    if request.method=="POST":
        """
        Boton Guardar fue presionado en el template
        """
        if 'addperm' in request.POST:
            user = request.POST.get('usuario')
            """
            Permisos a agregar al usuarios
            """
            permisos = request.POST.getlist('perms')
            """
            Usuario a agregar permisos.
            """
            usuario = User.objects.get(id=user)
            for p in permisos:
                if int(p) == 1:
                    """
                    Permiso id=1 corresponde a Ver Menu
                    """
                    permiso = Permission.objects.get(codename="view_menu")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """
                        Usuario ya cuenta con el permiso
                        """
                        if (pe == permiso):
                            """
                            Template a renderizar: already.html
                            """
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 2:
                    """Permiso id=2 corresponde a Asignar Permisos"""
                    permiso = Permission.objects.get(codename="assign_perms")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 3:
                    """Permiso id=3 corresponde a Agregar Usuarios"""
                    permiso = Permission.objects.get(codename="add_user")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 4:
                    """Permiso id=4 corresponde a Modificar Usuarios"""
                    permiso = Permission.objects.get(codename="change_user")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 5:
                    """Permiso id=5 corresponde a Deshabilitar Usuarios"""
                    permiso = Permission.objects.get(codename="unable_user")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 6:
                    """Permiso id=6 corresponde a Ver Usuarios"""
                    permiso = Permission.objects.get(codename="view_user")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 7:
                    """Permiso id=7 corresponde a Ver Reporte"""
                    permiso = Permission.objects.get(codename="view_report")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
                elif int(p) == 8:
                    """Permiso id=8 corresponde a Agregar Proyecto"""
                    permiso = Permission.objects.get(codename="add_proyecto")
                    perm = Permission.objects.filter(user=usuario)
                    for pe in perm:
                        """Usuario ya cuenta con el permiso"""
                        if (pe == permiso):
                            """Template a renderizar: already.html"""
                            return render(request, "gestionUser/already.html")

                    usuario.user_permissions.add(permiso)
                    usuario.save()
            """Template a renderizar: permisos.html"""
            return render(request, "gestionUser/permisos.html")

        else:
            """Boton Guardar no presionado en el template"""
            users = request.POST.get('usuarios')
            usuario = User.objects.get(id=users)
            """Actualizar informacion en teplate segun usuario seleccionado"""
            seleccion = usuario

    """GET request, envia usuarios del sistema al template para ser seleccionados y agregar los permisos"""
    usuarios = []
    u = User.objects.all()
    for user in u:
        """Filtrar que usuarios no sean staff ni el mismo usuario que ha realizado el request. Tambien
        que no sea un usuario deshabilitado."""
        if user.is_staff == False and user != request.user and user.is_active and user.username != "AnonymousUser" and user.has_perm("perms.view_menu"):
            usuarios.append(user)
    """Template a renderizar: addPerms.html"""
    return render(request, "gestionUser/addPerms.html", {'usuarios':usuarios, 'select':seleccion, })



@permission_required('perms.assign_perms', login_url='/permissionError/')
def removePermsView(request):
    """
       **removePermsView:**
        Vista utilizada para remover Permisos del Sistema
        a los usuarios.
        Solicita que el usuario que realiza el request cuente
        con el permiso para asignar permisos a otros usuarios
        y que (indirectamente) haya iniciado sesion
    """
    seleccion = None
    permisos = None
    dic = {"view_menu": "Ver Menu",
           "assign_perms": "Asignar Permisos",
           "unable_user": "Deshabilitar Usuario",
           "view_report": "Consultar Reporte",
           "add_user": "Crear Usuario",
           "change_user": "Modificar Usuario",
           "view_user": "Visualizar Usuario",
           "add_proyecto": "Crear Proyecto",
           }
    """POST request, captura una un usuario y una lista de permisos para remover del mismo."""
    if request.method == "POST":
        """Boton Remover presionado en el template."""
        if 'removeperm' in request.POST:
            user = request.POST.get('usuario')
            """Lista de permisos a remover."""
            permisos = request.POST.getlist('perms')
            """Usuario a remover permisos."""
            usuario = User.objects.get(id=user)
            for p in permisos:
                """Remover permisos correspondientes al usuario"""
                permiso = Permission.objects.get(codename=p)
                usuario.user_permissions.remove(permiso)

            """Template a renderizar: permisos.html."""
            return render(request, "gestionUser/permisos.html")


        else:
            """Boton Remover no presionado en el template"""
            users = request.POST.get('usuarios')
            usuario = User.objects.get(id=users)
            perms = Permission.objects.filter(user=usuario)
            """Actualizar informacion en teplate segun usuario seleccionado"""
            permisos = perms
            seleccion = usuario
            dic = dic

    """GET request, envia lista de usuarios para ser seleccionados y remover los permisos"""
    usuarios = []
    u = User.objects.all()
    for user in u:
        """Filtrar que los usuarios nos sean staff o igual al usuario que realizar el request. Tambien
        que no sea un usuario deshabilitado"""
        if user.is_staff == False and user != request.user and user.is_active and user.username != "AnonymousUser" and user.has_perm("perms.view_menu"):
            usuarios.append(user)

    """Template a renderizar: removePerms.html"""
    return render(request, "gestionUser/removePerms.html", {'usuarios': usuarios, 'select': seleccion,
                                                            'permisos': permisos,
                                                            'dic': dic, })


@permission_required('auth.view_user', login_url='/permissionError/')
def verUserView(request):
    """
       **verUserView:**
        Vista utilizada para ver la informacion
        de los usuarios del sistema.
        Solicita que el usuario que realiza el request
        cuente con el permiso para ver usuarios y
        que (indirectamente) haya iniciado sesion
    """

    seleccion = None
    permisos = None
    """POST request, captura un usuario y la informacion del mismo para mostrar."""
    if request.method == "POST":
        users = request.POST.get('usuarios')
        """Usuario a mostrar la informacion."""
        usuario = User.objects.get(id=users)
        """Permisos del usuario."""
        permisos = Permission.objects.filter(user=usuario)
        perms = []
        for p in permisos:
            perms.append(p.codename)

        """Actualizacion de la informacion a mostrar en el template."""
        seleccion = usuario
        permisos = perms

    """GET request, envia la lista de los usuarios a ser seleccionados para visualizar la informacion."""
    usuarios = []
    u = User.objects.all()
    for user in u:
        """Filtrar que el usuario no sea staff"""
        if user.is_staff == False and user.has_perm("perms.view_menu") == True and user.username != "AnonymousUser":
            usuarios.append(user)

    """Template a renderizar: verUser.html"""
    return render(request, "gestionUser/verUser.html", {'usuarios': usuarios, 'select': seleccion, 'permisos': permisos})



@permission_required('auth.change_user', login_url='/permissionError/')

def changeUserView(request):
    """
       **changeUserView:**
        Vista utilizada para modificar los usuarios
        del sistema.
        Solicita que el usuario que realiza el request
        cuente con el permiso para modificar usuarios y
        que (indirectamente) haya iniciado sesion
    """
    seleccion = None
    """POST request, captura un usuario y la informacion nueva para actualizar el mismo."""
    if request.method == "POST":
        """Boton Modificar presionado en el template."""
        if 'changeuser' in request.POST:
            """Nueva informacion para el usuario"""
            userid = request.POST.get('usuario')
            username = request.POST.get('nombre')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            """Usuario a modificar."""
            usuario = User.objects.get(id=userid)
            """Actualizar usuario."""
            usuario.username = username
            usuario.first_name = firstname
            usuario.last_name = lastname
            usuario.save()

            """Template a renderizar: gestionUser.html."""
            return redirect('gestionUserView')

        else:
            """Boton Modificar no presionado en el template."""
            users = request.POST.get('usuarios')
            """Actualizar informacion a mostrar en el template."""
            usuario = User.objects.get(id=users)
            seleccion = usuario

    """GET requet, envia una lista de usuarios para ser sleccionados y modificados."""
    usuarios = []
    u = User.objects.all()
    for user in u:
        """Filtrar que el usuario no sea staff. Tambien que no este deshabilitado"""
        if user.is_staff == False and user.is_active and user.username != "AnonymousUser" and user.has_perm("perms.view_menu"):
            usuarios.append(user)

    """Template a renderizar: changeUser.html"""
    return render(request, "gestionUser/changeUser.html", {'usuarios': usuarios, 'select': seleccion, })



@permission_required('perms.unable_user', login_url='/permissionError/')
def unableUserView(request):
    """
       **unableUserView:**.
        Vista utilizada para deshabilitar los usuarios
        del sistema.Solicita que el usuario que realiza
        el request cuente con el permiso para deshabilitar
        usuarios y que (indirectamente) haya iniciado sesion
    """
    """GET request, envia una lista de usuarios para ser sleccionados y deshabilitados."""
    if request.method == 'GET':
        usuarios = []
        u = User.objects.all()
        for user in u:
            """Filtrar que el usuario no sea staff, que no sea el usuario que realizo el request y
            que no este ya deshabilitado."""
            if user.is_staff == False and user != request.user and user.is_active and user.username != "AnonymousUser" and user.has_perm("perms.view_menu"):
                usuarios.append(user)
        """Template a renderizar: unableUser.html"""
        return render(request, "gestionUser/unableUser.html", {'usuarios': usuarios, })

    """POST request, captura una lista de usuarios para deshabilitar."""
    users = request.POST.getlist('users')
    for u in users:
        """Usuario a Deshabilitar"""
        usuario = User.objects.get(id=u)
        """Usuario puesto como inactivo(deshabilitado)"""
        usuario.is_active = False
        usuario.save()

    """Template a renderizar gestionUser.html"""
    return redirect('gestionUserView')


@permission_required('perms.unable_user', login_url='/permissionError/')
def enableUserView(request):
    """
       **enableUserView:**.
        Vista utilizada para volver a habilitar los usuarios
        deshabilitados del sistema.Solicita que el usuario que realiza
        el request cuente con el permiso para deshabilitar
        usuarios y que (indirectamente) haya iniciado sesion
    """
    """GET request, envia una lista de usuarios para ser sleccionados y habilitados."""
    if request.method == 'GET':
        usuarios = []
        u = User.objects.all()
        for user in u:
            """Filtrar que el usuario no sea staff, que no sea el usuario que realizo el request y
            que este deshabilitado."""
            if user.is_staff == False and user != request.user and user.is_active == False:
                usuarios.append(user)
        """Template a renderizar: enableUser.html"""
        return render(request, "gestionUser/enableUser.html", {'usuarios': usuarios, })

    """POST request, captura una lista de usuarios para habilitar."""
    users = request.POST.getlist('users')
    for u in users:
        """Usuario a Habilitar"""
        usuario = User.objects.get(id=u)
        """Usuario puesto como activo(habilitado)"""
        usuario.is_active = True
        usuario.save()

    """Template a renderizar gestionUser.html"""
    return redirect('gestionUserView')

def ConfigView(request):
    if request.method == 'GET':
        user = request.POST.get('usuario')
        users = request.POST.getlist('usuario')
        print(users)
        for u in User.objects.all():
            print(u.username, u.id)
        return render(request, 'gestionUser/ConfigurarUser.html',{'user':user})