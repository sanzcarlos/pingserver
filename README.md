# PingServer

## Codigo Fuente

Lo primero que tenemos que hacer es obtener el código fuente de la aplicación:

```
cd /usr/src/
git clone https://github.com/sanzcarlos/pingserver
```

### Actualización del código fuente

Para Actualizar el código fuente tenemos que ejecutar el siguiente comando:

```
cd /usr/src/pingserver
git pull
```

### Generación del Entorno Virtual

Vamos a crear un directorio donde esten todos los entornos virtuales que necesitamos:

```
mkdir /usr/src/venv
```

Una vez que tenemos nuestro directorio para entornos virtuales, vamos a crear el entorno virtual de nuestra apliación

```
cd /usr/src/venv
virtualenv pingserver
```

Activamos nuestro entorno virtual e instalamos los paquetes que necesitamos para nuestra aplicación:

```
source pingserver/bin/activate
pip install -r /usr/src/pingserver/requirements.txt 
```

#### Actualización de los paquetes

Si necesitamos actulizar los paquetes, tenemos que ejecutar el siguiente comando:

```
source /usr/src/venv/pingserver/bin/activate
pip install --upgrade -r /usr/src/pingserver/requirements.txt
```

## Instalación

Toda la instalación que vamos a explicar a continuación esta basada en CentOS 7, si está utilizando otra distribución tendrá que adaptar la configuración a la distribución en cuestion.

Vamos a crear un archivo con el servicio que hemos implementado `/etc/systemd/system/pingserver.service`

```
[Unit]
Description=Gunicorn instance to PingServer
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/usr/src/pingserver
Environment="PATH=/usr/src/venv/pingserver/bin"
ExecStart=/usr/src/venv/pingserver/bin/gunicorn --workers 3 --access-logfile /usr/src/pingserver/logs/pingserver-access.log --error-logfile /usr/src/pingserver/logs/pingserver-error.log --bind unix:/run/pingserver wsgi:app

[Install]
WantedBy=multi-user.target
```

A continuación tenemos que crearnos el archivo de configuración de Nginx `/etc/nginx/conf.d/pingserver.cong`

Vamos a crear un archivo con el servicio que hemos implementado `/etc/systemd/system/pingserver.service`

```
server {
    listen       8000;
    server_name  0.0.0.0 localhost;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/pingserver;
    }
}
```

Ya tenemos todo preparado para terminar la implementación del PingServer con Gunicorn y NGINX.

Tenemos que habilitar y activar el servicio de PingServer

```
systemctl enable pingserver.service
systemctl start pingserver.service
systemctl status pingserver.service
```

Tambien tenemos que reiniciar el servicio de NGINX

```
systemctl restart nginx.service
```

En nuestra configuración estanmos utilizando el puerto `8000`, tendremos que habilitar este puerto en el firewall del sistema

```
firewall-cmd --zone=public --permanent --add-port=8000/tcp
firewall-cmd --reload
```