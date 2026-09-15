# Factory y Builder implementados

## Factory

`apps/users/infra/factories.py` contiene `INotificador`, `NotificadorConsola`, `NotificadorEmail` y `NotificadorFactory`. La configuración selecciona la implementación; `UserService` también permite inyectarla en el constructor para pruebas.

El envío se programa después del commit mediante `transaction.on_commit`. Si se revierte la creación de la cuenta no se envía una bienvenida. Si el envío falla después del commit, la cuenta ya creada se conserva y el fallo queda registrado. Esto no implementa una cola durable de correo.

## Builder

`UserBuilder` valida datos, construye un usuario y aplica `set_password`. No guarda el usuario. `UserService` llama al repositorio para persistirlo junto con la billetera inicial.

`AperturaCajaBuilder` valida usuario, caja, premio y costo. Devuelve los argumentos que recibe el repositorio de aperturas. El débito y las escrituras quedan bajo el control transaccional del servicio.

## Cómo demostrarlos

```sh
python manage.py test apps.users.tests.UserBuilderTest apps.users.tests.NotificadorFactoryTest
python manage.py test apps.core.test_architecture.TransactionBoundaryTests
```

Los patrones tienen fines didácticos y responsabilidades delimitadas. Su presencia no demuestra automáticamente SOLID ni calidad; las pruebas y la separación real entre construcción, persistencia y presentación son la evidencia.
