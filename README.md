# VaultDrop

VaultDrop es una simulacion academica para EAFIT inspirada en la apertura de cajas
virtuales. Permite explorar cajas, girar una ruleta para obtener un item, gestionar
un inventario y consultar una billetera de creditos virtuales. No procesa dinero real,
no permite retirar ganancias y no es una plataforma de apuestas.

## Objetivo del proyecto

El proyecto busca demostrar, en un entorno controlado, el flujo completo de una
plataforma de cajas: registro e inicio de sesion, creditos iniciales, apertura con
probabilidades, inventario, ventas simuladas, envios simulados a Steam y movimientos
de billetera. Tambien sirve como ejercicio de arquitectura por capas, repositorios,
servicios, builders y factory de notificaciones.

## Stack

- Python y Django
- Django REST Framework para el listado y apertura de cajas
- SQLite para desarrollo
- HTML, CSS y JavaScript para la interfaz principal

## Ejecucion local


```powershell
python -m venv .venv
cd .\VaultDrop
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en el navegador. Para ejecutar las pruebas:

```powershell
python manage.py test
```

## Despliegue

Para un despliegue real se necesita un servidor WSGI/ASGI, una base de datos
persistente, HTTPS y variables de entorno. Antes de publicar:

1. Cambia `SECRET_KEY` por un secreto seguro y configura `DEBUG=False`.
2. Define `ALLOWED_HOSTS` con el dominio real y ejecuta `python manage.py collectstatic`.
3. Sustituye SQLite por PostgreSQL u otra base de datos administrada para producción.
4. Configura un backend de correo real si se usa `NOTIFICACION_MODE=REAL`.
5. Ejecuta `python manage.py migrate` durante el proceso de despliegue.

El comando de aplicación de referencia es:

```powershell
gunicorn project.wsgi:application
```

Gunicorn no forma parte todavía de `requirements.txt`; debe añadirse al entorno de
produccion o sustituirse por el servidor WSGI elegido. Las variables disponibles son
`NOTIFICACION_MODE`, `EMAIL_BACKEND` y las variables habituales de Django para
secretos, hosts y base de datos.

## Carpeta `figma_export`

`figma_export` es un prototipo independiente generado desde Figma Make. Contiene
otra interfaz React/Vite, su propio `package.json`, `pnpm-lock.yaml` y punto de
entrada `src/App.tsx`; Django no la importa ni la sirve. Se puede eliminar del
despliegue de Django sin afectar la aplicacion actual. Conviene conservarla solo si
se necesita como referencia visual, prototipo o fuente para una futura migracion de
la interfaz. Si ya no cumple ninguna de esas funciones, puede eliminarse como parte
de una limpieza explicita del repositorio.
