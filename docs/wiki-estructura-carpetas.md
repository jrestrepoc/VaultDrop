# Estructura de carpetas

```text
apps/
  core/       HTTP común, resumen de cuenta, idempotencia y base del panel
    admin.py       Configuración del panel e historial de solo lectura
    hanzi.py       Adapter del catálogo de HanZi Mentor
    unit_of_work.py  Unidad de trabajo sobre transaction.atomic
    static/core/js/
      vaultdrop.js   Controlador de eventos y coordinación
      api.js         Cliente HTTP, CSRF y reintentos
      store.js       Estado, rutas, selección y datos recibidos
      views.js       Generación de HTML
      reel.js        Animaciones de la ruleta y del mejorador
  users/      Registro, acceso, perfil, repositorios y notificaciones
    domain/builders.py
    authentication.py    Acceso con usuario o correo
    notifications.py     Contrato INotificador
    infra/factories.py   Notificadores MOCK, SIMULADO y REAL
    tasks.py             Tareas de Celery y notificador en cola
    admin.py
  wallet/     Servicio y repositorio de saldo e historial
    infra/exchange_rates.py   Adapter de la API de tasas de cambio
    admin.py
  cases/      Catálogo, probabilidades y estadísticas del panel
    data/       Datos iniciales para el comando no destructivo
    services.py Regla de probabilidades que suman 100 %
    admin.py
  openings/   Apertura, caja gratis, inventario y mejorador
    domain/builders.py
    inventory.py   Venta, envío y reserva atómica de objetos
    upgrades.py    Probabilidad y resultado de las mejoras
    composition.py Arma InventoryService con su notificador
    admin.py
services/
  catalog_service/   Microservicio Flask del catálogo
    locale/          Traducciones de sus errores
locale/       Catálogos gettext en español e inglés
project/      Configuración, rutas principales y Celery
tests/        Pruebas del cliente JavaScript
docs/         Arquitectura, contratos, decisiones y límites
compose.yaml  Orquestación de todos los servicios
nginx.conf    API Gateway y límite de intentos
```

Los modelos y serializers pertenecen a su módulo. Las operaciones de negocio atraviesan servicios y repositorios; las vistas solo adaptan HTTP.
