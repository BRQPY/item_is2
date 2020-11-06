#!/bin/bash
cd ..
source is2virtual/bin/activate
cd /var/www/item/item_is2/
echo "Desplegando pruebas..."


python manage.py test gestionUser.tests


python manage.py test proyecto.tests


python manage.py test fase.tests

echo "FInalizando..."
