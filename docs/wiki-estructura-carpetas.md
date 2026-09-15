# Estructura de carpetas

```text
apps/
  core/       HTTP común, resumen de cuenta e idempotencia
    static/core/js/
      vaultdrop.js   Controlador de eventos y coordinación
      api.js         Cliente HTTP, CSRF y reintentos
      store.js       Adaptación de datos recibidos para mostrarlos
      views.js       Generación de HTML
      reel.js        Animación del premio confirmado
  users/      Registro, perfil, repositorios y notificaciones
    domain/builders.py
    infra/factories.py
  wallet/     Servicio y repositorio de saldo e historial
  cases/      Catálogo y probabilidades
    data/     Datos iniciales para el comando no destructivo
  openings/   Servicio de apertura e inventario
    domain/builders.py
project/      Configuración y rutas principales
tests/        Pruebas del cliente JavaScript
docs/         Arquitectura, contratos, decisiones y límites
```

Los modelos y serializers pertenecen a su módulo. Las operaciones de negocio atraviesan servicios y repositorios. El archivo `core/account.py` compone la lectura para la interfaz y conoce serializers de varios módulos deliberadamente. No existe una capa genérica que intente abstraer todo Django.
