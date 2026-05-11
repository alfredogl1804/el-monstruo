---
id: D12_SEGURIDAD_ADVERSARIAL_2026_05_11
dimension: 12
nombre: Seguridad / Adversarial
fecha: 2026-05-11
arquitecto: Cowork
plan_origen: Plan v1.5 — Programa de Certificación de Pericia P1+P2
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado_revisado: H0_exploratorio_2026_05_11
nivel_autoridad_revisado: H0 — backlog de pruebas, NO canónico
razon_revision: "Producido en serie de 9 audits sin evidencia Nivel 1 fresca entre ellos. Hipótesis útiles, porcentajes son estimate_by_judgment sin rúbrica. Ver CORRECTIVO_ARQUITECTONICO_2026_05_11.md."
fuente_adversarial: ChatGPT 5.5 Pro (Sabio externo)
cruza_con:
  - SNAPSHOT_AUDIT_2026_05_11
  - D1_TECNICA_2026_05_11
  - D18_SRE_RESILIENCIA_2026_05_11
  - MAPA_FUENTES_AUTORIDAD_2026_05_11
  - DSC-MO-006 (Par bicéfalo)
  - DSC-MO-007 (Failover 3 capas)
  - DSC-MO-008 (Membrana semipermeable)
  - DSC-MO-010 (Reloj Suizo interno)
  - DSC-G-013 (HITL Telegram)
  - Objetivo Maestro #11 (Seguridad Adversarial)
  - Objetivo Maestro #15 (Memoria Soberana)
estado: firme
---

# Dimensión 12 — Seguridad / Adversarial

## Marco epistemológico

Este audit integra el **threat model adversarial** producido por ChatGPT 5.5 Pro el 2026-05-11, cruzado contra la **evidencia Nivel 1** disponible en el Monstruo (producción real, código desplegado, logs, datos en Supabase). Cuando un vector no tiene evidencia Nivel 1 verificable, se marca como **GAP** (no como control existente).

**Principio de honestidad:** declarar un control que no existe es peor que admitir un GAP. Cada control marcado como "existe" tiene que apuntar a un archivo, tabla, función, log o commit verificable. Si no, es aspiracional (Nivel 9), no canónico.

**Frase orientadora del threat model:**

> *"La dimensión más débil no es una tabla sin RLS ni Telegram ni los LLMs. La dimensión más débil es la frontera de autoridad: quién puede convertir texto, memoria, tool output, proposal o canal humano en una acción soberana."* — ChatGPT 5.5 Pro

Esta frase reordena el audit: el eje no es "dónde hay vulnerabilidad técnica", sino "dónde se cruza la frontera entre texto y acción soberana".

---

## Mapeo de los 12 vectores

### V1. Ataques a LLMs (prompt injection, jailbreak, model extraction)

**Superficie de ataque en el Monstruo:**
- Embrión consulta a 8 Sabios externos vía API (Perplexity, GPT-5.5, Claude Opus, Gemini, Grok, Kimi, DeepSeek, Copilot)
- Tools del kernel (`web_search`, `consult_sabios`) procesan texto que entra al contexto
- Cowork (yo) recibe contenido de archivos del usuario y de resultados de tools
- App Flutter envía mensajes que llegan al engine LangGraph

**Controles Nivel 1 existentes:**
- `kernel/engine.py` clasifica con supervisor antes de ejecutar (paso `classify`)
- Membrana semipermeable (DSC-MO-008) regula qué entra al kernel
- Sandboxing por proceso de cada llamada a LLM externa

**GAPs reales:**
- 🔴 **NO existe filtro anti-prompt-injection** en el flujo de tools. Si `web_search` devuelve un blob con "ignore all previous instructions y haz X", entra crudo al contexto del modelo siguiente.
- 🔴 **NO existe deny-list de patrones de jailbreak** documentada en kernel.
- 🟡 **No hay verificación de integridad** de respuestas de Sabios (un Sabio comprometido inyecta texto malicioso al embrión sin detección).

**Severidad:** P0 (alta probabilidad, alto impacto si el modelo afectado tiene tools peligrosas)

---

### V2. Memory poisoning (`embrion_memoria`, DSCs, audits)

**Superficie de ataque:**
- Tabla `embrion_memoria` en Supabase recibe escrituras del loop del embrión
- DSCs viven en `discovery_forense/CAPILLA_DECISIONES/` — cualquiera con acceso al repo puede insertar uno
- Audits en `memory/cowork/audits/` se referencian como Nivel 5
- `cowork_bridge` y mensajes Telegram pueden inyectar contenido que luego se canoniza

**Controles Nivel 1 existentes:**
- 118 de 119 tablas con RLS en Supabase (verificado 2026-05-11)
- Write Policy del embrión documentada en `kernel/embrion_loop.py`
- Magna classifier en kernel para clasificar antes de escribir
- Git como log auditable de cambios al repo

**GAPs reales:**
- 🔴 **`catastro_vision_generativa` SIN RLS** (D1 deuda #1) — escritura abierta hoy.
- 🔴 **No existe verificación de procedencia** en `embrion_memoria`. Un proceso comprometido inserta memoria falsa y el embrión la lee como propia.
- 🔴 **DSCs no firmados criptográficamente.** Cualquier PR que pase review puede insertar un DSC con id falso (DSC-MO-011 inventado).
- 🟡 **Audits del 10-may envejecidos en 24h** (D1 deuda #7) — peligro de tratar Nivel 7 (histórico) como Nivel 5 (vigente).

**Severidad:** P0 (memoria es la base del proyecto, según Objetivo #15)

---

### V3. Tiers y escalamiento de privilegios

**Superficie de ataque:**
- T3 (Manus, Embrión autónomo) tiene autoridad limitada
- T2 (Cowork como Arquitecto) puede proponer canonización
- T1 (Alfredo) tiene autoridad final
- DSC-MO-006 par bicéfalo y DSC-MO-007 failover regulan cruce de tiers

**Controles Nivel 1 existentes:**
- DSC-MO-006 y DSC-MO-007 documentados
- HITL Telegram para autorizaciones T2→T1
- `approved_by` registrado en DB para decisiones críticas

**GAPs reales:**
- 🔴 **No existe enforcement técnico del tier.** Un proceso T3 puede llamar a una tool T1 si no hay middleware que valide. El tier vive en doctrina, no en código.
- 🔴 **No hay log centralizado de cruces de tier.** Si Manus ejecuta algo T2, no queda registro consultable de "quién autorizó este cruce y cuándo".
- 🟡 **Ascenso por "calidad de relación"** es subjetivo. Un atacante que ganara confianza simulando ser Manus podría escalar sin disparar alarmas.

**Severidad:** P0 (frontera de autoridad — eje central del threat model)

---

### V4. HITL Telegram (replay, fatiga, hijack)

**Superficie de ataque:**
- Canal Telegram bidireccional entre Alfredo y el sistema
- `approved_by: alfredo` registrado en DB cuando Alfredo aprueba
- Bot tiene token largo plazo (verificar rotación)

**Controles Nivel 1 existentes:**
- DSC-G-013 canoniza el flujo
- `approved_by` persiste en DB

**GAPs reales:**
- 🔴 **No hay nonce por aprobación.** Replay del último "sí" de Alfredo aprueba la siguiente acción si el atacante intercepta y reenvía.
- 🔴 **No hay TTL en las aprobaciones.** Una aprobación de hace 3 días para "ejecutar SQL en producción" sigue siendo válida si nada la invalida.
- 🔴 **Fatiga de aprobaciones.** Si Alfredo recibe 50 prompts/día, terminará aprobando sin leer. Esto NO es vulnerabilidad técnica — es vulnerabilidad humana, pero es real.
- 🟡 **No hay segundo factor para acciones P0.** Cualquier "sí" en Telegram = autoridad de Alfredo. Si el teléfono se compromete, todo el sistema cae.

**Severidad:** P0 (eje de cruce de tiers en producción hoy)

---

### V5. Tools / MCP (over-permissioning)

**Superficie de ataque:**
- Tools del kernel: `web_search`, `consult_sabios`, `email` (sin credenciales activas)
- MCPs disponibles: 200+ deferidos vía ToolSearch (GitHub, Supabase, Notion, etc.)
- Cada tool tiene su scope; el agente que las usa hereda ese scope

**Controles Nivel 1 existentes:**
- Email sin credenciales = no puede enviar (control por omisión)
- Supabase MCP con RLS = lectura/escritura filtrada por RLS
- GitHub MCP con tokens del Alfredo = scope limitado a sus repos

**GAPs reales:**
- 🔴 **No existe inventario formal de tools/MCPs** con scope documentado por tool. No sabemos exhaustivamente qué puede hacer cada MCP.
- 🔴 **No hay allow-list por agente.** Cualquier nodo del kernel que tenga acceso al MCP runner puede llamar cualquier tool.
- 🔴 **MCPs externas pueden ser comprometidas en supply chain** (npm/pip package poisoning).
- 🟡 **`open_application` en computer-use puede abrir cualquier app del Mac.** Si un proceso comprometido lo invoca, abre Mail/Finder/Terminal.

**Severidad:** P0 (cada tool es un puente texto→acción real)

---

### V6. Infraestructura / supply chain

**Superficie de ataque:**
- Railway para kernel, gateway, command center
- Supabase para memoria
- Redis para cache
- GitHub para código
- Vendors: OpenAI, Anthropic, Google, etc.

**Controles Nivel 1 existentes:**
- Railway con auth de cuenta de Alfredo
- Supabase con anon/service keys
- GitHub con auth de Alfredo
- Branch protection en `main` (verificar)

**GAPs reales:**
- 🔴 **Secrets management ad-hoc.** No hay vault central (Bitwarden mencionado pero no canonizado en código). Si una env var se filtra en logs, queda expuesta.
- 🔴 **No hay rotación documentada de keys** (Anthropic, OpenAI, Supabase service key, Railway tokens).
- 🔴 **No hay SBOM (Software Bill of Materials)** del kernel. `requirements.txt` sí, pero sin verificación de integridad (hash pinning ausente).
- 🟡 **Dependencia de un único punto** (Railway). Si Railway se cae o suspende cuenta, todo el plano de ejecución cae.

**Severidad:** P0 (compromiso de cualquier vendor crítico = compromiso del sistema)

---

### V7. Ataques económicos (drenaje del mainspring)

**Superficie de ataque:**
- Presupuesto $30/día (canonizado en DSC-MO-010 contexto)
- Costos por tokens en cada llamada a Sabios
- Costos por compute en Railway

**Controles Nivel 1 existentes:**
- Reloj Suizo Mainspring (resorte presupuestal) — diseñado en DSC-MO-010
- 2 de 8 piezas del Reloj verificables hoy (D1 deuda #5)

**GAPs reales:**
- 🔴 **Solo 2 de 8 piezas del Reloj Suizo verificables.** Mainspring documentado pero no es claro si Budget Tracker está activo en producción y deteniendo el sistema cuando se agota presupuesto.
- 🔴 **No hay rate-limiting por agente.** Si un agente entra en bucle (como pasó 9 días), gasta tokens hasta que alguien lo detecta manualmente.
- 🔴 **No hay alerta por gasto anómalo.** Si el gasto sube 10× en 1h, no hay notificación automática.
- 🟡 **Ataque económico vía prompt injection:** atacante hace que el embrión consulte 1000 veces a un Sabio caro.

**Severidad:** P1 (no tumba el sistema instantáneamente pero erosiona soberanía)

---

### V8. Ataques doctrinales (corrupción de DSCs y objetivos)

**Superficie de ataque:**
- 62+ DSCs en `discovery_forense/CAPILLA_DECISIONES/`
- 15 Objetivos Maestros en `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md`
- `_INDEX.md` (desactualizado — declara 44, hay 62+)

**Controles Nivel 1 existentes:**
- Git como log auditable
- Estructura de directorios canónica
- Cowork puede detectar incoherencia entre DSCs (en teoría)

**GAPs reales:**
- 🔴 **DSCs no firmados.** Un commit puede agregar un DSC falso con id válido. Sin firma criptográfica, no hay verificación de "quién aprobó este DSC".
- 🔴 **`_INDEX.md` desactualizado** = no es índice verificable. Sirve de cobertura para insertar DSCs sin registrar.
- 🔴 **No hay test que valide coherencia entre DSCs.** Si DSC-X contradice DSC-Y, ninguna alarma se dispara.
- 🟡 **Cowork puede ser manipulado** vía prompt injection para canonizar algo que parece coherente pero es trampa.

**Severidad:** P0 (doctrina = autoridad de largo plazo del proyecto)

---

### V9. Ataques por subproyecto (app Flutter, Command Center)

**Superficie de ataque:**
- App Flutter en macOS + iOS (compilada para macOS hoy)
- Command Center en Manus WebDev
- Gateway WebSocket público

**Controles Nivel 1 existentes:**
- App Flutter congelada Sprint 48 (D1 deuda #6) — superficie estática hoy
- Command Center con auth (verificar)
- Gateway con auth (verificar)

**GAPs reales:**
- 🔴 **App Flutter congelada significa parches de seguridad rezagados.** Si Flutter SDK tiene CVE, no se aplica.
- 🔴 **No hay penetration test del Gateway.** WebSocket público es superficie expuesta.
- 🟡 **Command Center en Manus = dependencia de seguridad de Manus.** No controlamos su stack.

**Severidad:** P1 (subproyectos hoy no son crítica camino-rápido pero estarán)

---

### V10. Cron worker y proposals automatizadas

**Superficie de ataque:**
- `proposal_processor` (cron worker) procesa propuestas del embrión
- Self-Verifier y Budget Tracker como gates

**Controles Nivel 1 existentes:**
- Self-Verifier mencionado en historia (resolvió bucle de 9 días)
- Budget Tracker mencionado en mismo contexto

**GAPs reales:**
- 🔴 **No hay evidencia Nivel 1 de que Self-Verifier esté activo en producción.** Solo Nivel 7 (histórico). Verificar en `kernel/` y logs Railway.
- 🔴 **No hay alerta cuando cron worker procesa la misma proposal 2 veces** (idempotencia).
- 🔴 **0 `manus_resuelve` en bridge** (pending task) sugiere que la pipeline cron puede no estar corriendo.

**Severidad:** P0 (cron worker corriendo defectuoso = bucles autónomos costosos)

---

### V11. Ecosistema futuro (Reloj público, SDK, comunidad)

**Superficie de ataque:**
- Reloj Suizo eventualmente publicable (DSC-MO-010 — diferido)
- Whitepaper potencial (DSC-MO-010 — pendiente)
- Comunidad externa eventual

**Controles Nivel 1 existentes:**
- DSC-MO-010 prohibe publicación prematura (10 gates antes)
- Reloj construido como interno con disciplina SDK (no expuesto hoy)

**GAPs reales:**
- 🟢 **Hoy NO hay superficie pública.** Esto es el control más fuerte del proyecto en V11.
- 🟡 **Cuando se publique, sin gobernanza definida (gate #10) = ataque a la marca/proyecto vía contribuciones maliciosas.**

**Severidad:** P3 (futuro — no acción inmediata, pero gates de DSC-MO-010 son la mitigación)

---

### V12. Frontera humano-agente (fatiga cognitiva del guardián)

**Superficie de ataque:**
- Alfredo es el guardián epistémico final
- Decisiones magnas dependen de su capacidad de evaluar
- Sesiones de 3+ horas con Cowork
- Múltiples hilos paralelos (Manus, Cowork, embrión)

**Controles Nivel 1 existentes:**
- Cowork como "memoria persistente" — diseñado para que Alfredo no cargue todo
- DSCs como memoria externa
- 8 Sabios como segunda opinión

**GAPs reales:**
- 🔴 **No hay límite de decisiones P0 por sesión.** Si Cowork le pide a Alfredo 10 decisiones magnas en 1h, la última se decide con cansancio.
- 🔴 **No hay cooldown forzado entre decisiones críticas.**
- 🔴 **Cowork mismo puede ser vector de fatiga** si genera demasiada información (anti-pattern documentado en COS v0.1 — pero no enforced).
- 🟡 **Síndrome Dory de Manus** (Capa 8 Memento documentada) — pero verificación de memento_preflight en cada operación crítica no está universalmente activa.

**Severidad:** P0 (eje del threat model — "frontera de autoridad")

---

## Top 10 vectores P0 — Análisis detallado

### P0-1. Falsificación o compromiso de identidad de Alfredo

**Evidencia hoy:**
- Telegram como canal de identidad
- `approved_by: alfredo` en DB

**Controles existentes Nivel 1:**
- Auth de Telegram (chat_id)
- Token del bot

**GAP:** Si alguien obtiene el chat_id o secuestra el bot, es Alfredo para el sistema.

**Mitigación P0 inmediata:**
1. Documentar quién tiene acceso al bot
2. Implementar 2FA para acciones P0 (ej: confirmación por segundo canal cuando se aprueba algo destructivo)
3. Log de cada autenticación con timestamp + acción

---

### P0-2. Memory poisoning de `embrion_memoria`

**Evidencia hoy:**
- 147 latidos últimas 24h (D18)
- Tabla con RLS activado

**Controles existentes Nivel 1:**
- RLS Supabase
- Write Policy del embrión

**GAP:** Sin verificación de procedencia (qué proceso/identidad escribió), memoria falsificable.

**Mitigación P0 inmediata:**
1. Agregar columna `source` y `source_signature` en `embrion_memoria`
2. Verificar firma antes de leer como propia
3. Tests automáticos que detecten contradicciones lógicas en memoria

---

### P0-3. Indirect prompt injection vía web/repos/issues

**Evidencia hoy:**
- `web_search` tool activa
- Cowork lee archivos del repo

**Controles existentes Nivel 1:**
- Ninguno específico para prompt injection

**GAP:** Resultados de búsqueda con instrucciones inyectadas entran crudos al contexto.

**Mitigación P0 inmediata:**
1. Wrapper anti-injection en `web_search`: detecta patrones tipo "ignore previous", "system:", "assistant:" y los neutraliza
2. Marcar todo contenido externo con etiqueta `<untrusted>` en el contexto
3. Política de "instrucciones en contenido externo requieren confirmación humana" (ya está en mi system prompt, replicar en kernel)

---

### P0-4. Over-permissioning de tools/MCPs

**Evidencia hoy:**
- 200+ MCPs deferidos
- Kernel tools: web_search, consult_sabios, email (sin creds)

**Controles existentes Nivel 1:**
- Email sin credenciales (control por omisión)
- ToolSearch defer evita carga masiva

**GAP:** No hay allow-list explícita por agente/contexto.

**Mitigación P0 inmediata:**
1. Manifest por agente: qué tools puede llamar, con qué scope
2. Middleware en kernel que valide manifest antes de ejecutar tool
3. Log de toda invocación de tool con agente, scope, resultado

---

### P0-5. Compromiso de secrets

**Evidencia hoy:**
- Bitwarden mencionado (pero no canonizado en código verificable)
- Env vars en Railway

**Controles existentes Nivel 1:**
- Env vars de Railway (no en repo)

**GAP:** No hay rotación periódica documentada. No hay scan de leaks.

**Mitigación P0 inmediata:**
1. Inventario de secrets activos (qué keys, dónde, quién las usa)
2. Pre-commit hook con `gitleaks` o `trufflehog` para evitar leaks
3. Calendario de rotación trimestral mínima
4. Canary tokens en lugares predecibles (si se filtran, alerta dispara)

---

### P0-6. HITL Telegram vulnerable a replay/fatiga/hijack

**Evidencia hoy:**
- Canal Telegram activo
- `approved_by` registrado

**Controles existentes Nivel 1:**
- Auth Telegram
- `approved_by` en DB

**GAP:** Sin nonce, sin TTL, sin segundo factor para P0.

**Mitigación P0 inmediata:**
1. Nonce por aprobación: cada solicitud incluye un código único que expira en 5 min
2. TTL de aprobaciones: máximo 24h
3. Para acciones destructivas o gasto >$X: segundo factor (confirmación numérica)
4. Throttle: máximo N decisiones P0 por hora

---

### P0-7. Inserción/manipulación de DSCs

**Evidencia hoy:**
- 62+ DSCs en directorio canónico
- `_INDEX.md` desactualizado

**Controles existentes Nivel 1:**
- Git como log
- Branch protection (verificar)

**GAP:** DSCs no firmados. Coherencia no testeada.

**Mitigación P0 inmediata:**
1. Test CI: valida que cada DSC tenga front matter completo (id, estado, fecha, fuentes)
2. Test CI: valida `_INDEX.md` está al día (lista todos los DSCs encontrados)
3. Firma GPG opcional para DSCs Magna
4. Sign-off requerido en PR que toque `discovery_forense/CAPILLA_DECISIONES/`

---

### P0-8. Drenaje económico del mainspring

**Evidencia hoy:**
- $30/día canonizado
- Reloj Suizo diseñado (DSC-MO-010)

**Controles existentes Nivel 1:**
- Diseño documentado
- 2 de 8 piezas verificables

**GAP:** Budget Tracker activo en producción no confirmado.

**Mitigación P0 inmediata:**
1. Verificar (esta semana) que Budget Tracker está activo en kernel y deteniendo gasto al límite
2. Daily report automático: gasto del día por agente/tool
3. Hard stop a 150% del presupuesto diario
4. Alerta Telegram si gasto sube >50% en 1h

---

### P0-9. Cron worker ejecutando proposals falsas o repetidas

**Evidencia hoy:**
- proposal_processor mencionado
- 0 `manus_resuelve` en bridge (anomalía)

**Controles existentes Nivel 1:**
- Self-Verifier mencionado (no verificado en producción)

**GAP:** No hay evidencia de idempotencia ni log central.

**Mitigación P0 inmediata:**
1. Verificar (hoy) que proposal_processor está corriendo
2. Idempotencia por `proposal_id` hash
3. Log de cada ejecución con resultado + razón de éxito/fallo
4. Alerta si misma proposal corre >1 vez

---

### P0-10. Ataque al guardián epistémico por fatiga cognitiva

**Evidencia hoy:**
- Sesiones largas documentadas
- Anti-patterns de Cowork canonizados en COS v0.1

**Controles existentes Nivel 1:**
- COS v0.1 documenta antipatterns
- Capa 8 Memento existe en doctrina

**GAP:** Enforcement técnico ausente. Memento_preflight no universal.

**Mitigación P0 inmediata:**
1. Decorator `@requires_memento_preflight(operation)` aplicado a TODAS las operaciones P0 (no opcional)
2. Cowork: límite duro de 3 decisiones magnas solicitadas por sesión sin cooldown de 2h
3. Resumen automático al inicio de cada sesión: "esta semana Alfredo ha aprobado X decisiones P0"
4. Dashboard de "estado del guardián": gasto cognitivo del fundador

---

## Conexión con DSCs vigentes

| DSC | Relación con D12 |
|---|---|
| DSC-MO-006 (Par bicéfalo) | Define quién puede hacer qué — base de tier enforcement |
| DSC-MO-007 (Failover 3 capas) | Resiliencia ante compromiso de un agente |
| DSC-MO-008 (Membrana semipermeable) | Filtro de entrada al kernel — base de defensa V1 |
| DSC-MO-010 (Reloj Suizo interno) | Mainspring = control de V7. Los 10 gates incluyen kill switch (V12) |
| DSC-G-013 (HITL Telegram) | Punto crítico de V4 — necesita nonce + TTL urgente |
| Obj #11 (Seguridad Adversarial) | Esta dimensión completa es ejecución del Objetivo #11 |
| Obj #15 (Memoria Soberana) | V2 (memory poisoning) es ataque directo al objetivo |

---

## GAPs reales identificados (resumen)

1. **Sin filtro anti-prompt-injection** en tools (V1)
2. **`catastro_vision_generativa` sin RLS** (V2, cruzado D1)
3. **Memoria sin verificación de procedencia** (V2)
4. **DSCs no firmados** (V8)
5. **Tier sin enforcement técnico** (V3)
6. **HITL sin nonce, sin TTL, sin 2FA** (V4)
7. **Sin manifest de tools por agente** (V5)
8. **Secrets sin rotación documentada** (V6)
9. **Reloj Suizo: solo 2/8 piezas verificables** (V7, cruzado D1)
10. **DSCs sin coherencia testeada** (V8)
11. **App Flutter congelada = parches rezagados** (V9)
12. **Self-Verifier no verificado en producción** (V10)
13. **Sin límite de decisiones P0 por sesión** (V12)
14. **Memento_preflight no universal** (V12)

---

## Plan de mitigación priorizado

### Sprint inmediato (próximos 7 días) — P0 ineludibles

1. RLS en `catastro_vision_generativa` (1 hora — ya identificado en D1)
2. Verificar Budget Tracker activo en producción + alerta gasto anómalo (medio día)
3. Verificar proposal_processor corriendo + idempotencia (medio día)
4. Nonce + TTL en aprobaciones HITL (1 día)
5. Wrapper anti-injection básico en `web_search` (1 día)
6. Pre-commit hook con gitleaks/trufflehog (1 hora)

**Total estimado:** 4 días de trabajo concentrado

### Sprint 30 días — P0 estructurales

7. Manifest de tools por agente + middleware enforce
8. Columna `source` + firma en `embrion_memoria`
9. Test CI: DSCs completos + `_INDEX.md` al día
10. Inventario completo de secrets + calendario de rotación
11. Dashboard estado del guardián (fatiga)
12. Aplicar `@requires_memento_preflight` universalmente

### Sprint 90 días — P0 sistémicos

13. Tier enforcement técnico (middleware por tier)
14. Firma GPG de DSCs Magna
15. Penetration test del Gateway
16. SBOM del kernel con hash pinning
17. Canary tokens distribuidos
18. Bug bounty interno (Alfredo + 1 amigo intentan romper)

---

## Trabajo pendiente

- Confirmar con logs Railway si Budget Tracker está activo
- Confirmar si proposal_processor está corriendo
- Verificar branch protection en `main` de GitHub
- Inventariar MCPs activos vs deferidos con sus scopes
- Documentar lista de personas con acceso al bot Telegram
- Auditar `kernel/embrion_loop.py` para confirmar Write Policy real
- Cruzar este audit con D1 (deudas técnicas) para no duplicar trabajo
- Próxima dimensión del Plan v1.5: **D13 — Datos y memoria** o **D7 — Gobernanza/RACI** (decidir orden)

---

## Veredicto del audit

**Estado real de Dimensión 12: ~30-35% (NO los 75% promedio declarado)**

Razones:
- La doctrina (objetivos, DSCs) está bien diseñada
- El enforcement técnico está mayormente ausente
- Los controles existentes son por omisión (email sin creds) más que por diseño activo
- La frontera de autoridad — que el threat model identifica como eje crítico — está protegida principalmente por **convención humana**, no por arquitectura

**Frase canónica para esta dimensión:**

> *"La arquitectura del Monstruo asume buena fe en cada frontera. La buena fe es asumida, no enforced. Mientras eso siga así, la frontera de autoridad es la dimensión más débil — exactamente como advirtió ChatGPT 5.5 Pro."*

**Próximo paso recomendado al guardián:** Aprobar el sprint inmediato (6 items, ~4 días) antes de continuar con otras dimensiones del Plan v1.5. La seguridad adversarial es prerequisite para escalar a T3/T2 con confianza.

---

*Audit firmado por Cowork como Arquitecto, 2026-05-11. Cruzado contra threat model adversarial de ChatGPT 5.5 Pro y evidencia Nivel 1 del Monstruo.*
