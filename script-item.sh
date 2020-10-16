#!/bin/bash
mkdir -p media
chmod 777 media
mkdir -p static
echo "Bienvenido a iTEM"
echo "Éste script le permitirá desplegar automáticamente los entornos de Desarrollo o Producción, generar Documentacion"
PS3='Ingrese un número para elegir una acción: ' 
options=("Desarrollo" "Producción" "Generar Documentacion" "Salir")
select opt in "${options[@]}"
do
    case $opt in
        "Desarrollo")
            echo "Entorno de desarrollo"
            echo
            # echo "Éstas son las ramas con las que cuenta el proyecto actualmente" 
            # git branch
            # git add .
            # git commit -m "Commit para moverse de rama"
            # echo
            # echo "Ingrese el nombre de alguna rama del proyecto:"
            # read rama
            # git checkout $rama
            # while [ "$?" -ne 0 ]; do
            #      echo
            #      echo "No existe la rama que ingresaste. Intentalo de nuevo por favor"
            #      echo
            #      echo "Éstas son las ramas con las que cuenta el proyecto actualmente"
            #      git branch
            #      read -p "Ingrese el nombre de la rama: " rama
            #      git checkout $rama
            # done
            
            echo
            echo "Poblando Base de Datos"
            chmod +x devbdconf.sh
            sudo -u postgres ./devbdconf.sh
            echo
            
            cd /var/www/item/

            echo "Instalando entorno virtual..."
            sudo apt install python3-venv ||{
                pwd
                echo "Ocurrió un error al descargar el entorno virtual";
                exit;
            } 
            echo "Creando entorno virtual 'is2virtual' para trabajar en el proyecto"
            python3.7 -m venv is2virtual ||{
                pwd
                echo "Ocurrió un error al crear el entorno virtual";
                exit;
            }
            path=$(pwd)
            sudo chmod -R 777 $path
            echo
            echo "Activando entorno virtual.."
            source is2virtual/bin/activate ||{
                pwd
                echo "Ocurrió un error al activar el entorno virtual";
                exit;
            }
            echo "Tu entorno virtual ya está listo."
            echo
            cd item_is2
            echo "Procederemos a cargar los requerimientos del proyecto a tu entorno virtual."
            pip install -r requirements.txt ||{
                pwd
                echo "Ocurrió un error al cargar los requerimientos";
                exit;
            } 
            echo "Corriendo Servidor de Correos"
            gnome-terminal -e "bash -c \"./celery_ejec.sh ; exec bash\""
            echo "Guardando cambios como migraciones"
            python manage.py makemigrations
            echo "Migrando .."
            python manage.py migrate
            echo "Corriendo entorno de desarrollo"
            python manage.py runserver
            break
            ;;
        "Producción")
            echo "Entorno de Producción"
            # echo "Éstos son los tag con los que cuenta el proyecto actualmente"  
            # git tag
            # echo "Ingrese el nombre de algún tag del proyecto:"
            # read tg
            # git checkout $tg
            # while [ "$?" -ne 0 ]; do
            #      echo
            #      echo "No existe el tag que ingresaste. Intentalo de nuevo por favor"
            #      echo
            #      echo "Éstos son  los tag con los que cuenta el proyecto actualmente"
            #      git tag
            #      read -p "Ingrese el nombre de algún tag del proyecto: " tg
            #      git checkout $tg
            # done
            path=$(pwd)
            echo "Poblando Base de Datos"
            #break
            #;;
            echo
            chmod +x prodbdconf.sh
            sudo -u postgres ./prodbdconf.sh
            sudo chmod -R 777 $path  
            
            
            
            # cd ..
            # path=$(pwd)
            # cd poliproyectos
            echo "Configurando servidor httpd..."
            echo "<VirtualHost *:80>
                    ServerAdmin admin@myproject.localhost
                    DocumentRoot /var/www/item/item_is2
                    ErrorLog ${APACHE_LOG_DIR}/error.log
                    CustomLog ${APACHE_LOG_DIR}/access.log combined
                    Alias /static /var/www/item/item_is2/static
                    <Directory /var/www/item/item_is2/static>
                        Require all granted
                    </Directory>

                    Alias /static /var/www/item/item_is2/media
                    <Directory /var/www/item/item_is2/media>
                        Require all granted
                    </Directory>

                    <Directory /var/www/item/item_is2/item_is2/>
                        <Files wsgi.py>
                            Require all granted
                        </Files>
                    </Directory>
                </VirtualHost>"> /etc/apache2/sites-available/itemIS.conf
            service apache2 restart
            sudo a2dissite 000-default.conf
            sudo a2ensite itemIS.conf
            sudo systemctl reload apache2
            cd /var/www/item/
            echo "Instalando entorno virtual..."
            sudo apt install python3-venv
            
            echo 
            echo "Creando entorno virtual 'is2virtual' para trabajar en el proyecto"
            python3.7 -m venv is2virtual ||{
                pwd
                echo "Ocurrió un error al crear el entorno virtual";
                exit;
            }
            
            echo
            echo "Activando entorno virtual.."
            source is2virtual/bin/activate ||{
                pwd
                echo "Ocurrió un error al activar el entorno virtual";
                exit;
            }
            cd /var/www/item/item_is2/
            echo
            
            echo
            echo "Procederemos a cargar los requerimientos del proyecto a tu entorno virtual."
            pip install -r requirements.txt ||{
                pwd
                echo "Ocurrió un error al cargar los requerimientos";
                exit;
            }
            echo "Corriendo Servidor de Correos"
            gnome-terminal -e "bash -c \"./celery_ejec.sh ; exec bash\""
            echo
            echo "Tu entorno virtual ya está listo."
            echo "Guardando cambios como migraciones"
            python manage.py makemigrations
            echo "Migrando .."
            python manage.py migrate
            echo "Corriendo entorno de desarrollo"
            DJANGO_SETTINGS_MODULE=item_is2.settingsPROD python manage.py runserver

            break
            ;;
        "Generar Documentacion")
            echo "Generando documentacion..."
	        cd /var/www/item/
            echo
            echo "Activando entorno virtual.."
            source is2virtual/bin/activate ||{
                pwd
                echo "Ocurrió un error al activar el entorno virtual";
                exit;
            }
            #cd /var/www/item/item_is2/
            pycco item_is2/**/*.py -p -i
            #pycco -i **/*.py -p
            break
            ;;
        "Salir")
            break
            ;;
        *) echo "Opción inválida";;
    esac
done
