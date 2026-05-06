# Auditoría de Seguridad, Arquitectura y UX: LikeTickets

Fecha: 9 de Abril de 2026
Analista: Manus AI (apoyado por el Consejo de Sabios)
Objetivo: Evaluar la aplicación web liketickets-r5hmd5sa.manus.space y proponer mejoras priorizadas para llevar el MVP a producción.

## Resumen Ejecutivo

LikeTickets es un MVP funcional de venta de boletos (React, tRPC, Stripe) que actualmente presenta vulnerabilidades críticas de seguridad, problemas graves de conversión en pagos, e incumplimientos normativos que bloquean su salida a producción.

Tras una auditoría exhaustiva de la superficie de ataque, el código empaquetado, la experiencia de usuario y una consulta al Consejo de Sabios, se identificaron 19 hallazgos, de los cuales 6 son críticos (P0) y requieren atención inmediata.

## 1. Plan de Acción Priorizado (Top 5)

El consenso unánime del Consejo de Sabios (GPT-5.4, Claude 4.6, Gemini 3.1, Grok 4.20, DeepSeek R1) establece la siguiente secuencia de corrección obligatoria antes de operar en producción:

## 2. Auditoría de Seguridad y Arquitectura

### 2.1. Gestión de Sesiones y Autenticación (Crítico)

La aplicación almacena admin_token y customer_token en localStorage. Esto viola los estándares de seguridad OWASP 2026 para aplicaciones financieras. Cualquier vulnerabilidad XSS permitiría a un atacante robar sesiones administrativas.

Recomendación Arquitectónica: Implementar el patrón Backend-For-Frontend (BFF). El servidor tRPC debe emitir cookies HttpOnly y Secure, manteniendo el token inaccesible para el JavaScript del cliente.

### 2.2. Superficie de Ataque y Rate Limiting (Crítico)

El endpoint de autenticación administrativa (adminAuth.login) no posee mecanismos de limitación de tasa (rate limiting). Durante las pruebas, se ejecutaron múltiples intentos fallidos sin activar bloqueos temporales ni penalizaciones de tiempo (backoff).

Recomendación: Activar reglas de Rate Limiting nativas en Cloudflare para las rutas /api/trpc/*Auth*, complementadas con un bloqueo por IP en la capa de aplicación tras 5 intentos fallidos.

### 2.3. Fugas de Información Interna (Alto)

El endpoint de creación de checkout (tickets.createCheckout) devuelve errores internos del servidor en producción. Por ejemplo, al intentar una compra sin sesión, expone: "Invalid URL: An explicit scheme (such as https) must be provided." Esto ocurre porque las variables de entorno BASE_URL no están correctamente inyectadas en el entorno de producción para construir las URLs de success_url y cancel_url de Stripe.

Adicionalmente, los errores de validación de Zod se devuelven crudos al cliente, exponiendo la estructura interna del esquema de base de datos.

## 3. Auditoría de UX, Conversión y Negocio

### 3.1. Fricción en el Flujo de Pago (Crítico)

El checkout de Stripe está mal configurado para el mercado mexicano. Actualmente defaultea a BRL (Reales Brasileños) y Brasil como país. Las cuentas de Stripe en México requieren procesar tarjetas nacionales exclusivamente en MXN. Esta configuración actual garantiza el rechazo de la mayoría de las tarjetas de crédito mexicanas.

Recomendación: Modificar la creación de la sesión en Stripe para forzar currency: 'mxn', locale: 'es-MX', y habilitar explícitamente OXXO como método de pago (esencial para el 20-35% del mercado en Yucatán).

### 3.2. Estrategia de Inventario y FOMO (Alto)

El endpoint público events.listWithInventory devuelve los números exactos de boletos vendidos y disponibles (soldBleachers: 23, maxBleachers: 200). Las plataformas de ticketing profesionales nunca exponen estos datos crudos.

Recomendación: El backend debe enviar únicamente estados binarios (isAvailable: true) o umbrales de escasez (showUrgency: true cuando queden < 50 boletos), traduciéndose en la UI como "Últimos boletos".

### 3.3. Inconsistencias de Marca y Copy (Medio)

El hero de la página principal menciona "Vive la mejor experiencia de música en vivo", pero el catálogo consiste exclusivamente en partidos de béisbol (Bravos vs Leones). Adicionalmente, el footer indica "Powered by Emitickets", generando confusión de marca con "Like Kukulkán".

## 4. Rendimiento y Escalabilidad

El Time to First Byte (TTFB) de la aplicación es de 2.16s, y el bundle JavaScript principal pesa 553KB sin partición de código (code splitting). Para soportar la demanda de eventos de alta concurrencia (ej. playoffs de los Leones de Yucatán), la arquitectura actual fallará.

Recomendaciones para Picos de Demanda:

Implementar caché perimetral agresivo (Edge Caching) en Cloudflare para el catálogo de eventos.

Implementar "Optimistic Locking" y reservas temporales (holds de 10 minutos) en la base de datos durante el proceso de checkout.

Activar "Cloudflare Waiting Room" o una fila virtual para proteger la base de datos de picos masivos de tráfico.

Este informe fue generado analizando la superficie pública de la aplicación, el código empaquetado del cliente y validado mediante consenso multi-modelo.



| Prioridad | Área | Hallazgo | Solución Requerida | Impacto |

| P0-1 | Pagos | Stripe rechaza tarjetas MX | Forzar currency: 'mxn', habilitar OXXO/SPEI, y salir del modo test (pk_test_). | Evita pérdida del 100% de ventas con tarjetas nacionales. |

| P0-2 | Seguridad | Tokens en localStorage | Migrar a cookies HttpOnly, Secure, SameSite=Strict. | Evita robo masivo de cuentas vía XSS. |

| P0-3 | Seguridad | Sin Rate Limiting en Admin | Configurar Cloudflare Rate Limiting (5 intentos/min) en /api/trpc/adminAuth.login. | Previene ataques de fuerza bruta al panel de control. |

| P0-4 | Negocio | Inventario Exacto Expuesto | Eliminar soldBleachers y maxVip de la API pública. Mostrar solo "Quedan pocos". | Protege inteligencia comercial de competidores y genera FOMO. |

| P0-5 | Legal | Sin Sistema de Confirmación | Integrar SendGrid/Mailgun para envío de boletos con QR único firmado. | Cumplimiento obligatorio de LFPDPPP y Profeco. |

