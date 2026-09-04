# Wiki: Justificación de la Estructura de Carpetas

> **Entrega No. 1 — Arquitectura de Software 2026**  
> Proyecto: **VaultDrop**  
> Documento técnico explicativo de la organización arquitectónica del código fuente.

---

## 1. Visión General de la Arquitectura

Para el desarrollo de **VaultDrop**, se adoptó una arquitectura **modular y por capas limpias (Layered / Hexagonal Architecture)** inspirada en principios de Domain-Driven Design (DDD). 

El objetivo primordial es garantizar el **desacoplamiento total** entre la capa de transporte HTTP (Django Rest Framework), la lógica de negocio (Service Layer), las reglas del dominio (Entidades y Builders) y el acceso a datos (Patrón Repository).

```text
vaultdrop/
├── apps/                        # Módulos / Bounded Contexts del sistema
│   ├── core/                   # Transversal: Home, plantillas base, CSS/JS y Exception Handler
│   ├── users/                  # Contexto: Autenticación, Usuarios y Notificaciones
│   ├── wallet/                 # Contexto: Billetera virtual, Saldo y Transacciones contables
│   ├── cases/                  # Contexto: Catálogo de Cajas, Ítems y Probabilidades
│   └── openings/               # Contexto: Orquestación de Aperturas e Inventario de Usuario
├── docs/                       # Documentación técnica y contenido para GitHub Wiki
├── project/                    # Configuración global del proyecto Django (settings, urls, wsgi)
├── requirements.txt            # Dependencias del proyecto
└── manage.py                   # Entrypoint CLI de Django
```

---

## 2. Anatomía Interna de una Aplicación

Cada aplicación dentro del directorio `apps/` sigue una separación estricta de responsabilidades:

| Capa / Archivo | Responsabilidad | Principio SOLID Aplicado |
| :--- | :--- | :--- |
| **`models.py`** | Definición del esquema de datos y restricciones de integridad física (claves primarias, foráneas, tipos decimales para saldos y probabilidades). **No contiene lógica de negocio.** | **Single Responsibility (SRP):** Únicamente persistencia y mapeo relacional. |
| **`repositories.py`** | Interfaces abstractas (`IRepository`) e implementaciones con Django ORM (`DjangoRepository`). Aísla el acceso a base de datos. | **Dependency Inversion (DIP):** Las capas superiores dependen de abstracciones, no del ORM directo. |
| **`domain/builders.py`** | Construcción fluida y validación paso a paso de entidades complejas antes de su persistencia (`UserBuilder`, `AperturaCajaBuilder`). | **Builder Pattern & SRP:** Centraliza la validez del objeto sin ensuciar el modelo con lógica de ensamble. |
| **`infra/factories.py`** | Creación y resolución polimórfica de dependencias externas (`NotificadorFactory` -> Consola vs Email). | **Factory Pattern & Open/Closed (OCP):** Nuevos canales de notificación se agregan sin tocar servicios existentes. |
| **`services.py`** | **Service Layer / Capa de Aplicación.** Orquesta los casos de uso, transacciones atómicas (`transaction.atomic()`), débitos y validaciones de negocio. | **SRP & High Cohesion:** Único lugar donde reside la lógica de negocio del sistema. |
| **`serializers.py`** | Contratos de datos (DTOs) para validación de formato de entrada y serialización de salida en JSON. | **Separation of Concerns:** Desacopla la estructura de la API del esquema interno de base de datos. |
| **`api_views.py` / `views.py`** | **Capa de Presentación.** Exposición REST mediante `APIView` (control total de la petición HTTP, códigos 200, 201, 400, 404, 409). | **Thin Views:** Captura la petición, delega al Service y retorna la respuesta. Cero cálculos o reglas de negocio. |
| **`tests.py`** | Pruebas unitarias de dominio y de integración con `APITestCase`. | **Quality Assurance:** Cobertura de caminos felices y de excepción. |

---

## 3. Delimitación de Dominios (Bounded Contexts)

La división en 5 módulos responde a fronteras de dominio claras:

1. **`apps.users`**: Se enfoca exclusivamente en la identidad del usuario, ciclo de vida de la cuenta y notificación de bienvenida.
2. **`apps.wallet`**: Gestiona la economía virtual, garantizando que todo débito o recarga genere una auditoría contable inmutable (`Transaccion`).
3. **`apps.cases`**: Catálogo pasivo de cajas disponibles, definición de ítems y matriz de probabilidades de drop.
4. **`apps.openings`**: Caso de uso transaccional principal. Coordina la compra de la caja con `WalletService`, ejecuta el sorteo estocástico y transfiere el ítem al inventario.
5. **`apps.core`**: Recursos compartidos transversales (estilos estáticos, layout base, ruleta visual y el manejador global de excepciones).

---

## 4. Beneficios Técnicos y Justificación

* **Testabilidad Aislada:** Al inyectar repositorios y servicios por constructor (ej. `AperturaCajaService(randomizer=FixedRandomizer(10))`), se pueden probar algoritmos probabilísticos y flujos de negocio mediante mocks sin tocar la base de datos.
* **Prevención de "Fat Models" y "Fat Views":** Cumple estrictamente la regla de negocio de la rúbrica, garantizando que ni una vista ni un modelo acumulen lógica de orquestación.
* **Evolución Independiente:** Permite migrar en el futuro el catálogo o el inventario a microservicios independientes sin necesidad de reescribir la capa de aplicación.

