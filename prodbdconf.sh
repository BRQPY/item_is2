#!/bin/bash
echo "---Base de datos itemprod para entorno de Producción---"
echo "Borrando base de datos itemprod existente..."
dropdb -i --if-exists itemprod
if [ "$?" -ne 0 ]
then
    echo -e "No se pudo borrar la base de datos itemprod, verifique que no esté siendo usada."
    exit 1
fi
echo "Se ha borrado la base de datos itemprod."
echo "Creando la base de datos itemprod..."
createdb itemprod
if [ "$?" -ne 0 ]
then
    echo -e "No se pudo crear itemprod"
    exit 2
fi
echo "Se ha creado itemprod"

#source venv/bin/activate
PGPASSWORD="postgres"
psql -h localhost -p 5432 -U postgres -d itemprod -f db.backup
echo "itemprod se cargó exitosamente."