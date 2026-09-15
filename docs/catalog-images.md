# Imágenes del catálogo

Los 19 PNG locales se identificaron mediante ByMykel/CSGO-API y sus URLs de Steam. El catálogo de procedencia está en `apps/core/static/core/images/catalog.json`; se conserva como referencia, no se consulta para resolver imágenes en tiempo de ejecución.

La asociación activa pertenece a `Item.imagen_url` y `Caja.imagen_url` en la base de datos. Los serializers la exponen directamente. Para añadir una skin, identificar arma, acabado y variante exactos, guardar la imagen local y asignar su ruta al registro. Karambit Doppler usa Phase 2. La asociación histórica de Butterfly Tiger corresponde a Tiger Tooth.

`cases.0003_import_catalog_images` migra asociaciones vacías con una instantánea histórica ubicada junto a la migración. `seed_catalog` completa objetos y cajas faltantes sin reemplazar precios ni contenido existente. Los recursos del juego pertenecen a sus titulares; no se afirma afiliación con Valve ni Key-Drop.

El frontend utiliza `object-fit: contain`, contenedores proporcionados y un recurso neutro para imágenes ausentes o fallidas. El resultado de apertura y el inventario muestran la imagen enviada por la API para ese objeto, nunca la imagen de otro índice.
