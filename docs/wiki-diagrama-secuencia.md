# Secuencia real: abrir una caja

```mermaid
sequenceDiagram
    actor U as Usuario
    participant UI as Controlador web
    participant API as APIView
    participant OP as OperationService
    participant S as AperturaCajaService
    participant W as WalletService
    participant DB as Base de datos
    U->>UI: Abrir caja
    UI->>UI: Bloquear acciones y conservar UUID
    UI->>API: POST abrir + Idempotency-Key + CSRF
    API->>OP: Ejecutar una vez
    OP->>DB: Crear clave única en transacción
    OP->>S: abrir(usuario, caja)
    S->>S: Validar caja y probabilidades
    S->>W: Debitar precio
    W->>DB: UPDATE condicionado al saldo + historial
    S->>S: Seleccionar premio y construir apertura
    S->>DB: Guardar apertura e inventario
    OP->>DB: Guardar respuesta y commit
    API-->>UI: Premio confirmado y cuenta
    UI->>UI: Aplicar cuenta y animar premio
    UI-->>U: Mostrar resultado
```

Un fallo anterior al commit revierte la operación. Un reintento con la misma clave recupera la respuesta guardada. El navegador no descuenta créditos ni elige premios por su cuenta; el azar del archivo `reel.js` solo llena tarjetas decorativas de la animación.
