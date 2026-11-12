# VaultDrop

Simulador académico de apertura de cajas con créditos virtuales. No procesa dinero real ni envía objetos a Steam.

## Qué incluye

- **Cuenta:** registro y acceso con usuario o correo.
- **Cajas:** catálogo, probabilidades visibles y ruleta de apertura.
- **Inventario:** venta y envío simulado, de uno o varios objetos a la vez.
- **Mejorador:** entrega hasta 6 objetos por uno de mayor valor. La probabilidad es el valor entregado sobre el valor objetivo, con un máximo de 80 %.
- **Caja gratis diaria**, historial de aperturas y mejoras, y clasificación de mejores premios.
- **Billetera** con historial de movimientos filtrable por tipo y referencia en pesos desde una API externa.
- **Panel administrador** en `/admin/`, con estadísticas de cada caja.
- **Alianza con HanZi Mentor:** reto de pinyin en `/reto-pinyin/` con su catálogo, y una caja de demostración que su app abre desde su servidor.
- **Interfaz en español e inglés.**

## Arquitectura

| Componente | Función |
|---|---|
| Nginx | API Gateway y límite de intentos de login |
| Django y DRF | Web, autenticación, billetera, aperturas, inventario y panel |
| Flask | Microservicio de consulta del catálogo |
| PostgreSQL | Base de datos |
| Redis y Celery | Broker y worker de notificaciones |
| HanZi Mentor | Servicio del equipo aliado, consumido desde Django |

El detalle y los diagramas están en [docs/arquitectura-entrega-2.md](docs/arquitectura-entrega-2.md).

## Ejecutar localmente

Sin Docker se usa SQLite, las tareas corren en el mismo proceso y el catálogo lo sirve Django. Con el entorno virtual del proyecto activo:

```sh
pip install -r requirements.lock.txt
python manage.py migrate
python manage.py seed_catalog
python manage.py runserver 127.0.0.1:8000
```

El seed crea registros faltantes sin reemplazar precios o contenido de cajas existentes. No es necesario volver a crear las cuentas. Las imágenes permanecen locales y sus rutas se almacenan en la base de datos.

Con Docker Compose, Nginx queda como punto de entrada en `http://127.0.0.1/` (puerto configurable con `HTTP_PORT`): las rutas `/api/v1/` y la web van a Django, y `/api/v2/catalogo/` va al microservicio Flask del catalogo. Compose usa PostgreSQL; sin Docker se sigue usando SQLite.

Antes de levantar, copiar `.env.example` a `.env` y llenar `DJANGO_SECRET_KEY` y `POSTGRES_PASSWORD` con `openssl rand -hex 32`. `HANZI_CATALOGO_URL` es opcional: sin ella, el reto de pinyin muestra un aviso y el resto funciona.

```sh
cp .env.example .env
docker compose up --build -d
docker compose down
```

Para entrar al panel en `/admin/`, crear un administrador. Sin Docker se usa el mismo comando, sin el prefijo `docker compose exec web`:

```sh
docker compose exec web python manage.py createsuperuser
```

Con Docker, el catálogo inicial solo se carga cuando no hay ninguna caja, para que una caja borrada desde el panel no reaparezca. El despliegue en EC2 está en [docs/docker-local.md](docs/docker-local.md).

## Validar

Las pruebas de Flask necesitan las dependencias de `services/catalog_service/requirements.txt`.

```sh
python manage.py check
python manage.py test apps --noinput
node --test tests/frontend.test.mjs
python -m unittest discover -s services/catalog_service -p "tests.py"
```

`requirements.lock.txt` captura las versiones probadas; para reproducir el entorno usar `pip install -r requirements.lock.txt` con Python 3.14. Se conserva `requirements.txt` como declaración original de dependencias.

## Traducciones

La interfaz está en español e inglés con gettext. Los catálogos compilados (`.mo`) van en el repositorio, así que ejecutar el proyecto no requiere gettext. Después de cambiar textos, con gettext instalado:

```sh
python manage.py makemessages -l es -l en --ignore="services/*" --ignore="tests/*" --no-location --no-wrap
python manage.py makemessages -d djangojs -l es -l en --ignore="services/*" --ignore="tests/*" --no-location --no-wrap
python manage.py compilemessages
```

## Documentación

- [Arquitectura de la Entrega 2](docs/arquitectura-entrega-2.md)
- [Arquitectura implementada y SOLID](docs/arquitectura-actual.md)
- [Secuencia de apertura](docs/wiki-diagrama-secuencia.md)
- [API y Gateway](docs/wiki-api-gateway.md)
- [Docker local y despliegue en AWS](docs/docker-local.md)
- [Estructura de carpetas](docs/wiki-estructura-carpetas.md)
- [Migracion a Microservicios (Strangler Pattern)](docs/wiki-migracion-strangler.md)
- [Auditoría de UI/UX](docs/auditoria-ui-ux.md)

Factory y Builder se mantienen con responsabilidades explícitas. Los servicios coordinan las transacciones y los repositorios contienen las escrituras ORM.
