from django.db import models


class permisos(models.Model):

    class Meta:
        permissions = (
            ("view_menu", "Can view menu"),
            ("assign_perms", "Can assign perms"),
            ("unable_user", "Can unable user"),
            ("view_report", "Van view report"),

        )
