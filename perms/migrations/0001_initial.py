# Generated by Django 3.0.3 on 2020-04-08 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='permisos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_menu', 'Can view menu'), ('assign_perms', 'Can assign perms'), ('unable_user', 'Can unable user'), ('view_report', 'Van view report')),
            },
        ),
    ]
