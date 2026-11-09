# VaultDrop

Simulador académico de cajas con créditos virtuales. Backend Django y DRF; frontend JavaScript modular. No procesa dinero real ni envía objetos a Steam.

## Ejecutar localmente

Con el entorno virtual del proyecto activo:

```sh
python manage.py migrate
python manage.py seed_catalog
python manage.py runserver 127.0.0.1:8000
```

El seed crea registros faltantes sin reemplazar precios o contenido de cajas existentes. No es necesario volver a crear las cuentas. Las imágenes permanecen locales y sus rutas se almacenan en la base de datos.

Con Docker Compose, Nginx queda como punto de entrada en `http://127.0.0.1/` (puerto configurable con `HTTP_PORT`): las rutas `/api/v1/` y la web van a Django, y `/api/v2/catalogo/` va al microservicio Flask del catalogo. Compose usa PostgreSQL; sin Docker se sigue usando SQLite.

Antes de levantar, copiar `.env.example` a `.env` y llenar `DJANGO_SECRET_KEY` y `POSTGRES_PASSWORD` con `openssl rand -hex 32`.

```sh
cp .env.example .env
docker compose up --build -d
docker compose down
```

El despliegue en EC2 está en [docs/docker-local.md](docs/docker-local.md).

## Validar

```sh
python manage.py check
python manage.py test apps --noinput
node --test tests/frontend.test.mjs
python -m unittest discover -s services/catalog_service -p "tests.py"
```

`requirements.lock.txt` captura las versiones probadas; para reproducir el entorno usar `pip install -r requirements.lock.txt` con Python 3.14. Se conserva `requirements.txt` como declaración original de dependencias.

## Documentación

- [Arquitectura implementada y SOLID](docs/arquitectura-actual.md)
- [Secuencia de apertura](docs/wiki-diagrama-secuencia.md)
- [API y evolución hacia Gateway](docs/wiki-api-gateway.md)
- [Docker local y alcance de AWS](docs/docker-local.md)
- [Migracion a Microservicios (Strangler Pattern)](docs/wiki-migracion-strangler.md)

La alineación con el curso se basa en los temas compartidos, no en una rúbrica privada. Factory y Builder se mantienen con responsabilidades explícitas. Los servicios coordinan las transacciones y los repositorios contienen las escrituras ORM.
