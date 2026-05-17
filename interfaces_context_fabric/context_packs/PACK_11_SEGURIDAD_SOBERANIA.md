# PACK 11 — Seguridad y Soberanía como capa de UI

> **Estado:** CANON_VIGENTE
> **Fuentes:** SRC-001 Cap 7 (SMP) + SRC-001 Cap 17 (Seguridad operacional) + AGENTS.md Reglas Duras 6/7/8 + DSC-S-001..007 + DSC-LF-005

---

## Tesis del pack

La seguridad del Monstruo NO es una pestaña de "Settings" enterrada. Es una **capa transversal** que afecta cómo se diseñan TODAS las interfaces — desde el copywriting de un toggle hasta el prompt de confirmación de una acción HITL hasta la animación de un toast de error. Si ChatGPT ignora esta capa al diseñar UI, produce piezas que el resto del sistema rechaza como cuerpos extraños.

---

## Privacidad como física (no como policy)

> *"La gente no confía en empresas, confía en matemática. Bitcoin no es seguro porque alguien lo prometa, es seguro porque mover un BTC sin la private key es matemáticamente imposible. El SMP aplica este principio a memoria personal AI. Pasamos de policy a physics."*
> — APP_VISION Cap 7, citado verbatim

Esta postura tiene **5 implicaciones de copywriting** que ChatGPT debe aplicar:

Primero, el lenguaje de promesas queda prohibido. Frases como "nosotros nunca leemos tus datos" o "tu privacidad es nuestra prioridad" violan el principio. La forma canónica es **lenguaje de imposibilidad técnica**: "ni nosotros podemos leer tus datos, porque la clave nunca sale de tu Secure Enclave".

Segundo, los toggles de privacidad NO ofrecen opciones — articulan invariantes. Un toggle correcto dice "audit log de qué leyó el Monstruo" (con default ON), no "permitir que el Monstruo registre lo que lee" (con default OFF que sugiere que sin el toggle el Monstruo no registra nada — falso).

Tercero, los onboardings de capabilities sensibles (Vault, Photos, Health) explican **el TEE/Secure Enclave/Shamir** brevemente, no esquivan la complejidad. Asume que el usuario es adulto.

Cuarto, los errores y prompts de confirmación HITL en flujos sensibles muestran **la pieza criptográfica que se está activando** — no la esconden. "Esta acción genera una firma con tu clave SMP local" es preferible a "confirmar acción".

Quinto, cualquier feature que viole estas reglas (un toggle confuso, un copy de promesa, un "trust us") es deuda magna que rompe el contrato con el usuario.

---

## Cap 17 — Seguridad Operacional Soberana

APP_VISION Cap 17 firma que el Monstruo opera bajo **3 axiomas adicionales a los criptográficos**:

| # | Axioma | Implicación UI |
|---|---|---|
| 1 | Cero secrets en plaintext en código/docs/logs versionados | El Cockpit Settings NO muestra API keys "para verificar" — solo muestra "configurada/no configurada" |
| 2 | RLS por defecto en todo dato persistido | Cualquier UI que muestre data del backend asume que la query falló si el usuario no tiene scope — handling visible, no silencioso |
| 3 | Audit log accesible al usuario sobre TODO lo que el sistema hizo en su nombre | Memento UI (C7) muestra el feed de "qué hizo el Monstruo por mí esta semana" como ciudadano de primera clase |

Estos 3 axiomas conviven con las **8 Reglas Duras** del AGENTS.md (#6 cero plaintext, #7 RLS universal, #8 identidad auditable + rotación). Para cualquier sprint UI que toque data del usuario, ChatGPT tiene que verificar que el design sirve los 3 axiomas — no los rompe en nombre de "mejor UX".

---

## DSC-S-001 a DSC-S-007 (firmados post-incidente P0)

El 2026-05-06 hubo un incidente de credenciales en repo público. La capilla firmó 7 DSCs que canonizan reglas de copywriting + arquitectura para que el incidente NO se repita. Las que tocan UI directamente:

**DSC-S-001 — cero secrets en plaintext.** Implicación UI: las pantallas de Settings + Admin (C15) NUNCA renderizan el valor real de un token. Renderizan **estado** ("configurada"/"vencida"/"falta") + acciones ("rotar"/"reconfigurar"). Cualquier UI que diga "click to reveal API key" es violación.

**DSC-S-005 — cleanup default a archive.** Implicación UI: cualquier botón "delete" debe primero ofrecer "archive" (reversible). El "delete permanente" requiere segundo paso explícito + 30 días + confirmación humana. La frase del botón es "Archivar" (default), NO "Eliminar". Esto es regla magna para Memento, FinOps, Hilos Manus, Bridge.

**DSC-S-007 — naming canónico SUPABASE_SERVICE_KEY.** Implicación UI: la nomenclatura visible al usuario debe usar nombres canónicos. NO renombrar para "claridad" — el sistema ya canonizó el naming.

---

## DSC-LF-005 — SSE obligatorio en endpoints LLM

> Único hit "Schema-First" del corpus completo en el grep transversal.

La doctrina firma que cualquier endpoint que invoque LLM debe usar **Server-Sent Events (SSE)** para streaming, NO REST/JSON convencional. Implicación UI: cualquier surface que muestra output LLM (D1 Home, D3 Pendientes, C2 Threads) debe diseñarse para **streaming progresivo**, no para "esperar y mostrar todo de una". Esto cambia el padding, la jerarquía visual, el comportamiento del scroll, el manejo de errores parciales.

---

## Las 5 propiedades del SMP (APP_VISION Cap 7)

| Propiedad | Definición | Implicación UI |
|---|---|---|
| 1. End-to-end encryption | Datos cifrados en device antes de salir | Las capabilities trabajan offline en device cuando posible — la UI lo refleja con sutil indicador de "procesando local" |
| 2. Zero-knowledge backend | Backend NO puede leer aunque quiera | Settings/Privacy comunica esto explícitamente con lenguaje de física |
| 3. Local-first compute | Cómputo sensible en TEE/Secure Enclave | La latencia de capabilities sensibles puede ser mayor — el design respeta esa latencia con loading states honestos |
| 4. Shamir Secret Sharing | Recovery sin "olvidé mi password" | El onboarding incluye un paso de **Shamir setup** (3-de-5 trusted parties). Esto es UI nueva, NO existe en mercado de productores. ChatGPT debe diseñar este flow |
| 5. Auditable y open source | La layer crítica es auditable | Settings/Security incluye link al repo público de la layer crítica — soberanía visible |

---

## El modo confidente (Cap 6) como caso límite de seguridad UI

El modo confidente NO se anuncia. NO tiene tutorial. NO tiene botón. Vive dentro del input universal de Daily Home y se activa por **detección de tono íntimo**.

Implicación de seguridad UI brutal: una persona en crisis a las 2am tipea cosas que NO deberían vivir nunca en logs externos. Por lo tanto:

Primero, todo el procesamiento del modo confidente se hace en device. NO sale del Secure Enclave a backend para nada.

Segundo, NO hay analytics, NO hay telemetría, NO hay event tracking sobre activación del modo confidente. La activación es invisible para el sistema mismo.

Tercero, los logs de error que sí salen a Sentry/Datadog tienen **redaction obligatoria** de cualquier mensaje que pasó por modo confidente. El usuario NO puede recuperar contenido — y el equipo del Monstruo tampoco.

Cuarto, el output del modo confidente NO se persiste en Cronos por defecto. El usuario opta IN explícitamente si quiere conservar la conversación, frase a frase.

Quinto, ChatGPT diseñando esto debe **resistir el reflejo de hacer la feature visible**. La discoverability sería crueldad.

---

## El Cockpit Security (X1) — superficie fuera de canon, decisión pendiente

El Command Center PWA implementa una superficie `security` que NO está en la lista de 15 superficies del Cockpit canónico. La decisión pendiente es:

Si esta superficie debe **legitimarse** y agregarse al canon (porque la seguridad merece superficie propia, no enterrada en Settings).

O si debe **absorberse** dentro de Settings + Admin (C15) o dentro de Memento (C7) — porque seguridad como pestaña separada implica que el resto del sistema no es seguro por default, lo cual viola el axioma "privacidad como física".

ChatGPT en iter 002 debe firmar esta decisión.

---

## Los 5 toggles de Cap 4 Conexiones (D4)

APP_VISION Cap 4 declara que la superficie Conexiones (D4) ofrece toggle granular sobre 8 conexiones (WhatsApp, Mail, Calendar, Maps, Photos, Files, Drive, Pay) con **audit log accesible**. La parte interesante es que cada toggle NO es booleano simple — es un menú de scope:

| Scope | Función |
|---|---|
| Read-only | El Monstruo lee pero no actúa |
| Read + Suggest | Lee + propone acciones HITL |
| Read + Auto-Act (low-risk) | Lee + actúa automáticamente acciones reversibles |
| Read + Auto-Act (any) | Confianza Emergente full |
| Off | Cero conexión |

Esto es UI compleja que ChatGPT debe diseñar. La forma genérica del switch toggle de iOS NO sirve.

---

## Cierre

La capa de seguridad y soberanía es la **piedra angular invisible** del Monstruo. Si ChatGPT en iter 002 produce specs UI que ignoran esta capa, las specs son rechazables sin más discusión por violar regla 7 de Cap 0 ("privacidad como física"). Cada decisión arquitectónica debe pasar por el filtro: ¿esto sirve a la inviolabilidad criptográfica, o la erosiona en nombre de UX?
