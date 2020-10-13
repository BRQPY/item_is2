#!/bin/bash
mkdir -p media
chmod 777 media
mkdir -p static
echo "Bienvenido a iTEM"
echo "Éste script le permitirá desplegar automáticamente los entornos de Desarrollo o Producción, generar Documentacion o realizar Testing"
PS3='Ingrese un número para elegir una acción: ' 
options=("Desarrollo" "Producción" "Generar Documentacion" "Pruebas Unitarias" "Salir")
select opt in "${options[@]}"
do
    case $opt in
        "Desarrollo")
            echo "Entorno de desarrollo"
            echo "Éstas son las ramas con las que cuenta el proyecto actualmente"    
            #echo "Elija uno de los siguientes tags:"
            git branch
            echo "Ingrese el nombre de alguna rama del proyecto:"
            read rama
            git checkout $rama
            while [ "$?" -ne 0 ]; do
                 echo
                 echo "No existe la rama que ingresaste. Intentalo de nuevo por favor"
                 echo
                 echo "Éstas son las ramas con las que cuenta el proyecto actualmente"
                 git branch
                 read -p "Ingrese el nombre de la rama: " rama
                 git checkout $rama
            done
            echo
            path=$(pwd)
            sudo chmod -R 777 $path  
            echo "Instalando entorno virtual..."
            sudo apt install python3-venv
            echo 
            echo "Creando entorno virtual 'is2virtual' para trabajar en el proyecto"
            python3.7 -m venv is2virtual
            #virtualenv venv --python=python3
            echo
            echo "Activando entorno virtual.."
            source is2virtual/bin/activate
            echo
            echo "Actualizando el gestor de paquetes de Python 'pip'"
            pip install --upgrade pip
            echo
            echo "Procederemos a cargar los requerimientos del proyecto a tu entorno virtual."
            pip install -r requirements.txt
            echo
            echo "Tu entorno virtual ya está listo."
            echo "Poblando Base de Datos"
            #chmod +x devbdconf.sh
            #sudo -u postgres ./devbdconf.sh
            break
            ;;
        "Producción")
            echo "Entorno de Producción"
            echo "Éstos son los tag con los que cuenta el proyecto actualmente"  
            git tag
            echo "Ingrese el nombre de algún tag del proyecto:"
            read tg
            git checkout $tg
            while [ "$?" -ne 0 ]; do
                 echo
                 echo "No existe el tag que ingresaste. Intentalo de nuevo por favor"
                 echo
                 echo "Éstos son  los tag con los que cuenta el proyecto actualmente"
                 git tag
                 read -p "Ingrese el nombre de algún tag del proyecto: " tg
                 git checkout $tg
            done
            path=$(pwd)
            sudo chmod -R 777 $path  
            echo "Instalando entorno virtual..."
            sudo apt install python3-venv
            echo 
            echo "Creando entorno virtual 'is2virtual' para trabajar en el proyecto"
            python3.7 -m venv is2virtual
            #virtualenv venv --python=python3
            echo
            echo "Activando entorno virtual.."
            source is2virtual/bin/activate
            echo
            echo "Actualizando el gestor de paquetes de Python 'pip'"
            pip install --upgrade pip
            echo
            echo "Procederemos a cargar los requerimientos del proyecto a tu entorno virtual."
            #pip install -r requirements.txt COMENTADO SOLO PARA NO TARDAR MIL AÑOS
            echo
            echo "Tu entorno virtual ya está listo."
            echo "Poblando Base de Datos"
            #break
            #;;
            echo
            # chmod +x prodbdconf.sh
            # sudo -u postgres ./prodbdconf.sh
            # cd ..
            # path=$(pwd)
            # cd poliproyectos
            echo "Configurando servidor httpd..."
            echo "<VirtualHost *:80>
                    ServerAdmin admin@myproject.localhost
                    ServerName itemis2.localhost
                    ServerAlias www.itemis2.localhost
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
            break
            ;;
        "Generar Documentacion")
            echo "Generando documentacion..."
	        pycco -i **/*.py -p
            break
            ;;
        "Pruebas Unitarias")
            ./manage.py test
            break
            ;;
        "Salir")
            break
            ;;
        *) echo "Opción inválida";;
    esac
done