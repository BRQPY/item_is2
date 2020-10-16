#!/bin/bash
cd ..
source is2virtual/bin/activate
cd /var/www/item/item_is2/
python manage.py test fase.tests

