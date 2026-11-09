# Auditoría de UI/UX

Revisión de usabilidad, navegación y formularios de la Entrega 2. Se midió en un navegador real sobre el stack de Docker, en todas las pantallas, con anchos de 1024, 375 y 320 px, en español e inglés.

## Método

- **Contraste:** cálculo WCAG de cada texto contra su fondo. Mínimo 4,5:1.
- **Áreas táctiles:** tamaño real de cada control. Mínimo WCAG 2.2 AA de 24 px; recomendado 44 px en móvil.
- **Formularios:** etiquetas, tipos de campo, autocompletado, validación y envío con Enter.
- **Navegación:** botón Atrás, enlaces directos, foco del teclado, títulos y estado activo.
- **Seguridad de acciones:** confirmación en operaciones que no se pueden deshacer y doble envío.

## Resultados

| Área | Antes | Después |
|---|---|---|
| Botón Atrás del navegador | Salía de la aplicación | Vuelve a la pantalla anterior |
| Enlace directo a una pantalla | No existía; recargar volvía al inicio | `#wallet`, `#inventory`, `#profile`, `#case-4` |
| Título de la pestaña | Siempre "VaultDrop" | Cambia con la pantalla |
| Foco tras navegar o actuar | Se perdía en `body` | Pasa al contenido principal |
| Pantalla activa | Solo visual | `aria-current="page"` |
| Contraste mínimo medido | 2,44:1 en fechas, historial y avisos | Ningún texto bajo 4,5:1 |
| Controles menores de 24 px | Selector de idioma y logo móvil | Ninguno |
| Acciones de inventario en móvil | Menos de 44 px | 44 px |
| Navegación a 320 px | Se desbordaba 47 px | Sin desbordamiento |
| Campos sin etiqueta | Perfil (3), monto y orden | Ninguno |
| Perfil | Correo como texto, sin autocompletado | Tipo `email` y autocompletado |
| Login y registro | Sin autocompletado de gestores | `username`, `email`, `current-password`, `new-password` |
| Reglas de contraseña | Solo se veían al fallar | Texto de ayuda visible |
| Registro | Sin enlace a login | Enlace "¿Ya tienes una cuenta?" |
| Enter en monto y perfil | No hacía nada | Envía el formulario |
| Límites del monto | Solo `min=1` | `0.01` a `10000`, igual que el servidor |
| Vender o enviar un objeto | Un clic, sin confirmación | Pide confirmación |
| Doble clic al registrarse | Enviaba dos veces | El botón se desactiva al enviar |
| Mensajes de éxito | Podían no anunciarse | Región `aria-live` permanente |
| Cambiar idioma | Volvía al inicio | Conserva la pantalla |

## Lo que se mantiene sin cambios

- La barra superior sigue por debajo de 44 px de alto. Cumple el mínimo AA de 24 px, y agrandarla no cabe a 320 px.
- Los iconos de la barra son emoji decorativos, ocultos para lectores de pantalla.
- La confirmación usa el diálogo nativo del navegador, que ya es accesible y bilingüe por su texto.

## Límites de esta auditoría

La medición automática no sustituye una prueba con personas ni con un lector de pantalla real. No se evaluaron textos sobre fondos con degradado o imagen, porque su contraste no se puede calcular de forma fiable. La página de límite de intentos de Nginx es bilingüe, pero estática porque no pasa por Django.
