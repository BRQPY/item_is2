#!/bin/bash
#cd /var/www/item/item_is2/
#celery -A item_is2 worker -l INFO
#source entornov/is2/bin/activate
cd ..
source is2virtual/bin/activate
cd /var/www/item/item_is2/
celery -A item_is2 worker -l INFO
