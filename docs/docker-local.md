# Docker y AWS en el contexto del curso

Se incluye `Dockerfile` y `compose.yaml` para un entorno académico local. Se usa Python 3.14 y las versiones exactas de la instalación comprobada. El contenedor ejecuta migraciones y el seed no destructivo, guarda SQLite en un volumen y expone el puerto 8002 de localhost para no interferir con la sesión habitual en 8000.

```sh
docker compose up --build
docker compose exec web python manage.py test apps --noinput
docker compose down
```

El volumen se conserva al detener los contenedores. Esta configuración usa `runserver` y DEBUG, por lo que es exclusivamente de desarrollo. No se ejecutó aquí: Docker no está instalado/disponible en esta sesión. El build de la imagen y su arranque siguen pendientes de comprobar en una máquina con Docker.

No se creó infraestructura AWS. Una práctica posterior puede separar servidor WSGI, PostgreSQL, archivos estáticos, secretos por entorno, HTTPS, logs y copias de seguridad. Esa práctica necesita conocer la consigna y validar costos y permisos; la arquitectura local no demuestra por sí sola disponibilidad, tolerancia a fallos ni escalabilidad en AWS.
