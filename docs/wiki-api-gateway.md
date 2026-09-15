# API Gateway: situación actual y evolución

VaultDrop expone una API versionada desde un único proceso Django. No hay un API Gateway instalado. El frontend usa módulos JavaScript, no React. La API admite autenticación por token y sesión; el navegador utiliza sesión y CSRF.

## Rutas implementadas

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/v1/cajas/` | Catálogo público |
| GET | `/api/v1/cajas/{id}/` | Contenido de una caja |
| POST | `/api/v1/cajas/{id}/abrir/` | Apertura autenticada |
| GET | `/api/v1/account/` | Usuario, saldo, historial e inventario propios |
| GET | `/api/v1/wallet/me/` | Billetera propia |
| POST | `/api/v1/wallet/deposit/` | Recarga virtual entre 0,01 y 10.000 créditos |
| GET | `/api/v1/inventory/` | Inventario propio |
| POST | `/api/v1/inventory/{id}/sell/` | Venta virtual |
| POST | `/api/v1/inventory/{id}/send/` | Envío simulado |
| POST | `/api/v1/auth/register/` | Registro y token |
| POST | `/api/v1/auth/login/` | Autenticación por token |
| PATCH | `/api/v1/auth/profile/` | Actualizar el perfil propio |

Las mutaciones POST de apertura, recarga, venta y envío admiten `Idempotency-Key`. Debe conservarse la misma clave al reintentar la misma operación y usarse otra para una acción nueva. La respuesta de apertura conserva los campos existentes y añade `account`. Las ventas y recargas devuelven `account` actualizado. Los importes se serializan como cadenas decimales.

## Qué aportaría una pasarela

Podría concentrar límites de tráfico, terminación TLS, enrutamiento y observabilidad. No reemplaza la autorización de cada objeto, las transacciones o la validación del negocio. Los serializers facilitan un contrato explícito, pero sus cambios deben versionarse o mantenerse compatibles deliberadamente.

Dividir este monolito en microservicios exigiría resolver transacciones entre servicios, autenticación, propiedad de datos y recuperación de fallos. No basta con cambiar una ruta en una pasarela. Para el alcance actual se conserva un solo backend.
