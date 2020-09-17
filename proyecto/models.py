from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords




class TipodeItem(models.Model):
    nombreTipo = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=40)
    campo_extra = ArrayField(models.CharField(max_length=40), default=list, blank=True)
    history = HistoricalRecords()

class Files(models.Model):
    file = models.FileField(null=True, blank=True, default=None)



class Item(models.Model):

    tipoItem = models.ForeignKey(TipodeItem, on_delete=models.CASCADE, default=None, related_name="tipoItem")
    nombre = models.CharField(max_length=40, null=False, default=None)
    campo_extra_valores = ArrayField(models.CharField(max_length=40), default=list, blank=True)
    #file = models.FileField(upload_to='media', blank=True)
    fecha= models.CharField(max_length=40, null=False, default=None)
    estado = models.CharField(max_length=40, blank=True, null=True)
    observacion = models.CharField(max_length=50, blank=True, default= None)
    #relaciones_items = ArrayField(models.CharField(max_length=200), default=list, blank=True)
    costo= models.IntegerField(default=0, blank=True)
    relaciones = models.ManyToManyField('self', default=None, through='Relacion', symmetrical=False)
    dateCreacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    version = models.IntegerField(default=0, editable=False)
    history = HistoricalRecords()
    archivos = models.ManyToManyField(Files,default=None)

    __history_date = None
    @property
    def _history_date(self):
        return self.__history_date


    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value



class LineaBase(models.Model):
    nombre = models.CharField(max_length=40, null=False, default=None)
    items = models.ManyToManyField(Item, default=None)
    estado = models.CharField(max_length=40, default=None)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)

class Fase(models.Model):
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=40, default=None)
    estado = models.CharField(max_length=40, default=None)
    items = models.ManyToManyField(Item, default=None)
    tipoItem = models.ManyToManyField(TipodeItem, default=None)
    history = HistoricalRecords()
    lineasBase = models.ManyToManyField(LineaBase, default=None)
    class Meta:
        permissions = (
            ("create_item", "Can create item"),
            ("aprove_item", "Can aprove item"),
            ("modify_item", "Can modify item"),
            ("unable_item", "Can unable item"),
            ("reversionar_item", "Reversionar item"),
            ("relacionar_item", "Relacionar item"),
            ("change_item", "Can change item"),
            ("establecer_itemPendienteAprob", "Establecer ítem como pendiente de aprobación."),
            ("establecer_itemDesarrollo", "Establecer ítem como en desarrollo."),
            ("obtener_trazabilidadItem", "Obtener trazabilidad de ítem."),
            ("ver_item", "Visualizar ítem."),
            ("deshabilitar_item", "Deshabilitar Item"),
            ("obtener_calculoImpacto", "Obtener cálculo de impacto de ítem."),
            ("create_lineaBase", "Crear Línea Base."),
            ("modify_lineaBase", "Modificar Linea Base."),
            ("ver_lineaBase", "Ver Línea Base."),
            ("break_lineaBase", "Romper Línea Base."),
            ("solicitar_roturaLineaBase", "Solicitar rotura de línea base."),
        )


class FaseUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, default=None)
    history = HistoricalRecords()

class Relacion(models.Model):
    tipo = models.CharField(max_length=40, default=None)
    fase_item_to = models.ForeignKey(Fase, default=None, on_delete=models.CASCADE)
    item_from = models.ForeignKey(Item, default=None, on_delete=models.CASCADE, related_name='item_from')
    item_to = models.ForeignKey(Item, default=None, on_delete=models.CASCADE, related_name='item_to')

class Rol(models.Model):
    nombre = models.CharField(max_length=40, default=None)
    perms = models.ForeignKey(Group, on_delete=models.CASCADE, default=None, null=True)
    faseUser = models.ManyToManyField(FaseUser, default=None)
    history = HistoricalRecords()


class Proyecto(models.Model):
    nombre = models.CharField(max_length=200, blank=False, null=False)
    descripcion = models.CharField(max_length=400, blank=True, null=False)
    fecha_inicio = models.CharField(max_length=200, blank=False, null=False)
    fecha_fin = models.CharField(max_length=200, blank=False, null=False)
    gerente = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='gerente')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True, related_name='creador')
    estado = models.CharField(max_length=100, default=None, null=True)
    usuarios = models.ManyToManyField(User, default=None)
    comite = models.ManyToManyField(User, default=None, related_name='comite')
    roles = models.ManyToManyField(Rol, default=None)
    fases = models.ManyToManyField(Fase, default=None, through='ProyectoFase')
    tipoItem = models.ManyToManyField(TipodeItem, default=None)
    history = HistoricalRecords()

    class Meta:
        permissions = (
            ("is_gerente", "Can do anything in project"),
            ("inicialize_proyecto", "Can inicialize proyecto"),
            ("cancel_proyecto", "Can cancel proyecto"),
            ("create_tipoItem", "Crear tipo de item"),
            ("import_tipoItem", "Importar tipo de item"),
            ("view_tipoItem", "Visualizar tipo de ítem."),
            ("change_tipoItem", "Modificar tipo de item"),
            ("delete_tipoItem", "Eliminar tipo de item"),
            ("add_miembros", "Can add miembros"),
            ("delete_miembros", "Can delete miembros"),
            ("view_miembros", "Can view miembros"),
            ("create_rol", "Can create rol"),
            ("change_rol", "Can change rol"),
            ("delete_rol", "Can delete rol"),
            ("view_rol", "Can view rol"),
            ("assign_rol", "Can assign rol"),
            ("remove_rol", "Can remove rol"),
            ("create_comite", "Can create comite"),
            ("change_comite", "Can change comite"),
            ("view_comite", "Can view_comite comite"),
            ("aprobar_rotura_lineaBase", "Romper Línea Base."),

        )

        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['nombre']


class ProyectoFase(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, default=None)
    history = HistoricalRecords()


