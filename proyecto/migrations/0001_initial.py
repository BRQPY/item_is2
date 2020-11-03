# Generated by Django 3.0.3 on 2020-11-01 19:50

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampoExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Fase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=40)),
                ('descripcion', models.CharField(default=None, max_length=200)),
                ('estado', models.CharField(default=None, max_length=40)),
            ],
            options={
                'permissions': (('create_item', 'Can create item'), ('aprove_item', 'Can aprove item'), ('modify_item', 'Can modify item'), ('unable_item', 'Can unable item'), ('reversionar_item', 'Reversionar item'), ('relacionar_item', 'Relacionar item'), ('change_item', 'Can change item'), ('establecer_itemPendienteAprob', 'Establecer ítem como pendiente de aprobación.'), ('establecer_itemDesarrollo', 'Establecer ítem como en desarrollo.'), ('obtener_trazabilidadItem', 'Obtener trazabilidad de ítem.'), ('ver_item', 'Visualizar ítem.'), ('deshabilitar_item', 'Deshabilitar Item'), ('obtener_calculoImpacto', 'Obtener cálculo de impacto de ítem.'), ('create_lineaBase', 'Crear Línea Base.'), ('modify_lineaBase', 'Modificar Linea Base.'), ('ver_lineaBase', 'Ver Línea Base.'), ('solicitar_roturaLineaBase', 'Solicitar rotura de línea base.'), ('cerrar_fase', 'cerrar fase')),
            },
        ),
        migrations.CreateModel(
            name='FaseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fase', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='proyecto.Fase')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default=None, max_length=100)),
                ('campo_extra_valores', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=40), blank=True, default=list, size=None)),
                ('fecha', models.CharField(default=None, max_length=40)),
                ('estado', models.CharField(blank=True, max_length=40, null=True)),
                ('observacion', models.CharField(blank=True, default=None, max_length=200)),
                ('costo', models.IntegerField(blank=True, default=0)),
                ('version', models.IntegerField(default=0, editable=False)),
                ('archivos', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=40), blank=True, default=list, size=None)),
                ('faseid', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.CharField(blank=True, max_length=400)),
                ('fecha_inicio', models.CharField(max_length=200)),
                ('fecha_fin', models.CharField(max_length=200)),
                ('estado', models.CharField(default=None, max_length=100, null=True)),
                ('comite', models.ManyToManyField(default=None, related_name='comite', to=settings.AUTH_USER_MODEL)),
                ('creador', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creador', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Proyecto',
                'verbose_name_plural': 'Proyectos',
                'ordering': ['nombre'],
                'permissions': (('is_gerente', 'Can do anything in project'), ('inicialize_proyecto', 'Can inicialize proyecto'), ('cancel_proyecto', 'Can cancel proyecto'), ('create_tipoItem', 'Crear tipo de item'), ('import_tipoItem', 'Importar tipo de item'), ('view_tipoItem', 'Visualizar tipo de ítem.'), ('change_tipoItem', 'Modificar tipo de item'), ('delete_tipoItem', 'Eliminar tipo de item'), ('add_miembros', 'Can add miembros'), ('delete_miembros', 'Can delete miembros'), ('view_miembros', 'Can view miembros'), ('create_rol', 'Can create rol'), ('change_rol', 'Can change rol'), ('delete_rol', 'Can delete rol'), ('view_rol', 'Can view rol'), ('assign_rol', 'Can assign rol'), ('remove_rol', 'Can remove rol'), ('create_comite', 'Can create comite'), ('change_comite', 'Can change comite'), ('view_comite', 'Can view_comite comite'), ('break_lineaBase', 'Romper Línea Base.')),
            },
        ),
        migrations.CreateModel(
            name='TipodeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombreTipo', models.CharField(max_length=40)),
                ('descripcion', models.CharField(max_length=200)),
                ('campo_extra', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=40), blank=True, default=list, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='RoturaLineaBaseComprometida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uno_voto_comprometida', models.SmallIntegerField(default=-1)),
                ('dos_voto_comprometida', models.SmallIntegerField(default=-1)),
                ('tres_voto_comprometida', models.SmallIntegerField(default=-1)),
                ('comprometida_estado', models.CharField(default='pendiente', max_length=40)),
                ('registrados_votos_comprometida', models.ManyToManyField(default=None, related_name='comprometidavotantes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoturaLineaBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion_solicitud', models.CharField(default=None, max_length=200)),
                ('voto_uno', models.SmallIntegerField(default=-1)),
                ('voto_dos', models.SmallIntegerField(default=-1)),
                ('voto_tres', models.SmallIntegerField(default=-1)),
                ('fecha', models.CharField(default=None, max_length=40)),
                ('estado', models.CharField(default='pendiente', max_length=40)),
                ('items_implicados', models.ManyToManyField(default=None, related_name='items_implicados', to='proyecto.Item')),
                ('solicitante', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solicitante', to=settings.AUTH_USER_MODEL)),
                ('votos_registrados', models.ManyToManyField(default=None, related_name='votantes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default=None, max_length=40)),
                ('faseUser', models.ManyToManyField(default=None, to='proyecto.FaseUser')),
                ('perms', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Relacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(default=None, max_length=40)),
                ('fase_item_to', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='proyecto.Fase')),
                ('item_from', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='item_from', to='proyecto.Item')),
                ('item_to', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='item_to', to='proyecto.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ProyectoFase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fase', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='proyecto.Fase')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='proyecto.Proyecto')),
            ],
        ),
        migrations.AddField(
            model_name='proyecto',
            name='fases',
            field=models.ManyToManyField(default=None, through='proyecto.ProyectoFase', to='proyecto.Fase'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='gerente',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='gerente', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='roles',
            field=models.ManyToManyField(default=None, to='proyecto.Rol'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='tipoItem',
            field=models.ManyToManyField(default=None, to='proyecto.TipodeItem'),
        ),
        migrations.AddField(
            model_name='proyecto',
            name='usuarios',
            field=models.ManyToManyField(default=None, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='LineaBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default=None, max_length=40)),
                ('estado', models.CharField(default=None, max_length=40)),
                ('creador', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('items', models.ManyToManyField(default=None, to='proyecto.Item')),
                ('roturaLineaBaseComprometida', models.ManyToManyField(blank=True, default=None, related_name='comprometida', to='proyecto.RoturaLineaBaseComprometida')),
                ('roturaslineasBase', models.ManyToManyField(blank=True, default=None, to='proyecto.RoturaLineaBase')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='relaciones',
            field=models.ManyToManyField(default=None, through='proyecto.Relacion', to='proyecto.Item'),
        ),
        migrations.AddField(
            model_name='item',
            name='tipoItem',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='tipoItem', to='proyecto.TipodeItem'),
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, default=None, null=True, upload_to='')),
                ('item', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='proyecto.Item')),
            ],
        ),
        migrations.AddField(
            model_name='fase',
            name='items',
            field=models.ManyToManyField(default=None, to='proyecto.Item'),
        ),
        migrations.AddField(
            model_name='fase',
            name='lineasBase',
            field=models.ManyToManyField(default=None, to='proyecto.LineaBase'),
        ),
        migrations.AddField(
            model_name='fase',
            name='tipoItem',
            field=models.ManyToManyField(default=None, to='proyecto.TipodeItem'),
        ),
        migrations.CreateModel(
            name='CampoExtraValores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=40)),
                ('campoExtra', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='campoExtra', to='proyecto.CampoExtra')),
            ],
        ),
    ]
