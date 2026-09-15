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

## Validar

```sh
python manage.py check
python manage.py test apps --noinput
node --test tests/frontend.test.mjs
```

`requirements.lock.txt` captura las versiones probadas; para reproducir el entorno usar `pip install -r requirements.lock.txt` con Python 3.14. Se conserva `requirements.txt` como declaración original de dependencias.

## Documentación

- [Arquitectura implementada y SOLID](docs/arquitectura-actual.md)
- [Secuencia de apertura](docs/wiki-diagrama-secuencia.md)
- [API y evolución hacia Gateway](docs/wiki-api-gateway.md)
- [Docker local y alcance de AWS](docs/docker-local.md)

La alineación con el curso se basa en los temas compartidos, no en una rúbrica privada. Factory y Builder se mantienen con responsabilidades explícitas. Los servicios coordinan las transacciones y los repositorios contienen las escrituras ORM.
