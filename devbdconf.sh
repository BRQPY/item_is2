#!/bin/bash
echo "---Creando Base de datos itemdev para entorno de Desarrollo---"
echo "Borrando base de datos itemdev existente..."
dropdb -i --if-exists itemdev
if [ "$?" -ne 0 ]
then
    echo -e "No se pudo borrar la base de datos itemdev, verifique que no esté siendo usada."
    exit 1
fi
echo "Se ha borrado la base de datos itemdev."
echo "Creando la base de datos itemdev..."
createdb itemdev
if [ "$?" -ne 0 ]
then
    echo -e "No se pudo crear itemdev"
    exit 2
fi
echo "Se ha creado itemdev"

source is2virtual/bin/activate
PGPASSWORD="postgres"
psql -h localhost -p 5432 -U postgres -d itemdev -f db.backup
echo "devbd se cargó exitosamente."