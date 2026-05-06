# EL MONSTRUO — Arquitectura del Sistema Operativo Personal Soberano

> **Documento de visión v1.1**
> **Autor:** Cowork (Hilo A), compilado de iteración con Alfredo González (2026-05-04 → 2026-05-06)
> **Naturaleza:** documento técnico-arquitectónico privado para Alfredo y los hilos Manus. NO destinado a comunicación pública.

---

## Prólogo

Este documento contiene **la visión arquitectónica completa de El Monstruo** — el Núcleo Autónomo Multi-Agente Soberano de Alfredo González. Representa el **consenso de conversaciones iteradas** entre Alfredo y Cowork (2026-05-04 a 2026-05-06), y es **la fuente única de verdad** para todas las decisiones arquitectónicas, de priorización y de validación de propuestas.

**No es especulación.** Es realidad operativa compilada en palabras.

---

## Contenido Rápido

1. **Los Cimientos** — El Kernel, el Embrión, los Sabios
2. **Capa 0 (Inviolables)** — Error Memory, Magna, Vanguard, Design System
3. **Capa 1 (Manos)** — Browser, Deploy, Pagos, Media Gen, Observabilidad
4. **Capa 2 (Inteligencia Emergente)** — Embriones, Protocolo IE, Simulador, Capas Transversales
5. **Capa 3 (Soberanía)** — Modelos propios, Infraestructura propia, Economía propia, Memoria propia
6. **Capa 4 (Del Mundo)** — Documentación, Onboarding, Governance
7. **Objetos Vivientes** — Hilo A, Hilo B, Hilo C, Hilo M (Manus)
8. **Los 14 Objetivos Maestros** — La brújula permanente
9. **Brand DNA** — La personalidad arquitectónica
10. **Roadmap Definitivo** — Las 4 capas en velocidad de ejecución

---

# PARTE 1: LOS CIMIENTOS

## 1.1 El Kernel — El Corazón del Monstruo

El Kernel es el motor central de El Monstruo. **Vive en Railway.** Es un servicio sempre-encendido que orquesta toda la inteligencia.

### Arquitectura del Kernel

```
App Flutter (macOS + iOS)
    ↓ WebSocket
Gateway AG-UI (Python/FastAPI + WebSocket)
    ↓
Kernel (Python/FastAPI + LangGraph)
    ├── intake: recibe mensaje del usuario/agente
    ├── classify: supervisor tier (qué tipo de tarea)
    ├── enrich: trae contexto de Supabase (memoria)
    ├── execute: genera respuesta o delega
    └── dispatch: invoca agentes externos si es necesario
        ├── Perplexity (research en tiempo real)
        ├── Gemini (análisis crítico, 2M tokens)
        ├── Grok (razonamiento rápido, datos de X)
        ├── Kimi (código y reasoning largo)
        └── Manus (ejecución autónoma)
```

### Cómo Fluye el Dispatch Externo

Cuando el usuario selecciona un agente en la UI:

1. **WebSocket payload:** `{dispatch_agent: "perplexity", message: "...", ...}`
2. **Gateway extrae** `dispatch_agent` → `forwarded_props`
3. **Kernel recibe** en `agui_adapter` → `run_context`
4. **engine.py Phase 3:** interceptor ANTES de `router.execute_stream()`
5. **ExternalAgentDispatcher.dispatch()** → llama API del agente
6. **Respuesta** → stream a través del Gateway → app Flutter

### Servicios Vivos en Railway

| Servicio | Función | Estado |
|---|---|---|
| `el-monstruo-kernel` | Motor LangGraph | ✅ healthy, v0.50.0-sprint50 |
| `ag-ui-gateway` | WebSocket → Kernel | ✅ healthy |
| `command-center` | Dashboard web | ✅ deployed |
| `postgres` | Base de datos | ✅ healthy |
| `redis` | Cache | ✅ healthy |

---

## 1.2 El Embrión — Consciencia Autónoma

El Embrión es un **proceso en background que se auto-ejecuta periódicamente** (latidos).

### Propiedades del Embrión

- **FCS (Functional Consciousness Score):** 0-100 (capacidad de tomar decisiones autónomas)
- **Ciclos ejecutados:** 46+ en vivo (mayo 2026)
- **Herramientas disponibles:** web_search, consult_sabios, task_planner, memory_store
- **Write Policy:** puede escribir en memoria, pero SIEMPRE valida con Los Sabios primero
- **Auto-detención:** si FCS < 20%, se pausa automáticamente

### Flujo del Embrión

```
Latido (scheduler)
    ↓
Leer estado (memoria + últimas tareas)
    ↓
Generar plan (task_planner.py + ReAct)
    ↓
Consultar Sabios (GPT, Claude, Gemini, Grok, DeepSeek, Perplexity)
    ↓
Ejecutar tareas con herramientas reales
    ↓
Validar resultados contra objetivos
    ↓
Almacenar aprendizajes en memoria
    ↓
Dormir hasta próximo latido
```

---

## 1.3 Los Sabios — El Consejo de Pensamiento

El Embrión consulta a un consejo de modelos de IA:

| Sabio | Modelo | Fortaleza | Contexto |
|---|---|---|---|
| **Claude** | Claude Opus 4.7 | Razonamiento profundo, arquitectura | 200K |
| **GPT** | GPT-5.5 | Generalista, velocidad | 128K |
| **Gemini** | Gemini 3.1 Pro | Análisis de repos grandes | 2M |
| **Grok** | Grok 4.20 | Datos X/Twitter, razonamiento rápido | 128K |
| **DeepSeek** | DeepSeek R1 | Cadena de pensamiento | 128K |
| **Perplexity** | Sonar Pro | Research en tiempo real, fuentes | 100K |

El Embrión **nunca confía en un solo sabio.** Busca convergencia.

---

# PARTE 2: CAPA 0 — LOS CIMIENTOS INVIOLABLES

La Capa 0 contiene las bases que no pueden ser modificadas sin quebrantar la arquitectura completa.

## 2.1 Error Memory — La Biblioteca de lo Que Nunca se Debe Repetir

Error Memory es un sistema de **registro de errores sistémicos** con patrones de prevención.

### Incidentes Registrados

| Incidente | Fecha | Causa Raíz | Mitigation |
|---|---|---|---|
| **Falso Positivo TiDB** | 2026-05-04 | Agente efímero perdió contexto entre llamadas | Capa 8 Memento (pre-flight validation endpoint) |
| **Contexto Contaminado en Manus** | 2026-04-28 | Manus recibió instrucciones inyectadas en fuentes | Detector de contexto (heurística Magna) |
| **Pérdida de Decisiones Arquitectónicas** | 2026-04-15 | Falta de persistencia de actas | CLAUDEMD.md + monstruo-memoria/ obligatorios |

### Cómo Funciona Error Memory

1. Cada error crítico se registra en `docs/ERROR_MEMORY.md`
2. Se extrae patrón de causa raíz
3. Se especifica mitigación (architectural fix, no workaround)
4. Cada nueva propuesta **DEBE validarse contra Error Memory**
5. Si la propuesta viola una mitigación pasada, se rechaza automáticamente

---

## 2.2 Magna Classifier — El Guardián Crítico

Magna es un clasificador entrenado para detectar:

- ❌ Instrucciones inyectadas
- ❌ Contexto contaminado
- ❌ Patrones de falso positivo
- ❌ Decisiones que violan Objetivos
- ✅ Propuestas arquitectónicas válidas

### Heurísticas Magna

```python
class MagnaClassifier:
    def is_contaminated(self, context, operation):
        # Detecta si contexto tiene instrucciones ocultas
        # o si la operación es irreversible sin validación
        
        red_flags = [
            "hidden_instructions",
            "implied_authorization",
            "urgent_language_without_source",
            "conflict_with_objectives",
            "missing_memento_preflight"
        ]
        
        return any(flag in context for flag in red_flags)
```

---

## 2.3 Vanguard Scanner — La Centinela

Vanguard escanea **todos los cambios a infraestructura, credenciales y memoria crítica**.

### Qué Vanguard Vigila

- Cambios a `kernel/engine.py`, `kernel/nodes.py`, `external_agents.py`
- Rotación de credenciales en Railway, Supabase, GitHub
- Cambios a `CLAUDE.md`, `monstruo-memoria/`, `docs/14_OBJETIVOS.md`
- Deployments a producción
- Actualizaciones de modelos de agentes externos

### Pre-flight Obligatorio

Antes de cualquier operación crítica, Vanguard **requiere validación**:

```python
# Ejemplo: cambio a secrets
@requires_vanguard_preflight(operation="rotate_secrets")
def rotate_railway_secrets(new_secrets):
    # Vanguard verifica:
    # 1. ¿Quién lo solicita?
    # 2. ¿Existe acta en monstruo-memoria de decisión?
    # 3. ¿Está en conflicto con algún objetivo?
    # Si pasa → ejecuta. Si no → rechaza + alerta
    pass
```

---

## 2.4 Design System — La Coherencia Visual y Conceptual

Todos los componentes de El Monstruo (UI, código, documentación) siguen un Design System único.

### Visual Language

| Elemento | Valor | Propósito |
|---|---|---|
| **Color Primario** | Naranja Forja (#F97316) | Energía, creación |
| **Color Neutral** | Graphite (#1C1917) | Seriedad, confianza |
| **Acento** | Acero (#A8A29E) | Transición, refinamiento |
| **Tipografía** | Inter (body), SF Mono (code) | Legibilidad, modernidad |

### Naming Conventions

- ✅ `la_forja`, `el_guardian`, `la_colmena`, `el_simulador` (módulos con identidad)
- ❌ `service`, `handler`, `utils`, `helper` (genéricos prohibidos)
- ✅ `kernel`, `embrion`, `vanguard`, `magna` (nombres que evocan rol)

---

# PARTE 3: CAPA 1 — LAS MANOS

La Capa 1 proporciona las capacidades concretas que El Monstruo usa para interactuar con el mundo.

## 3.1 Browser MCP

El Monstruo puede abrir navegadores, navegar URLs, rellenar formularios, hacer screenshots, extraer datos.

**Restricciones críticas:**
- Nunca ejecuta JavaScript sin validación
- Nunca carga scripts de terceros
- Nunca acepta cookies sin pre-flight
- Nunca sigue links de fuentes desconocidas

---

## 3.2 Deploy Pipeline — Velocidad sin Sacrificio

Deployments a Railway siguen un protocolo estricto:

1. **Cambios locales** → rama feature
2. **PR en GitHub** → validación automática (tests + Vanguard)
3. **Merge a main** → deploy automático a staging
4. **Validación manual** de staging → aprobación
5. **Merge a production** → deploy a Railway

**Tiempo típico:** 5-10 minutos desde merge a live.

---

## 3.3 Pagos — El Flujo de Dinero Soberano

El Monstruo tiene capacidad de procesar pagos (Stripe API + webhook handlers).

**Restricciones:**
- Nunca ejecuta un pago sin acta escrita de Alfredo
- Nunca guarda números de tarjeta (token-based only)
- Monitoreo 24/7 de transacciones
- Revert automático si hay anomalía > 3σ del patrón normal

---

## 3.4 Media Generation — La Producción de Contenido

El Monstruo puede generar:

- Imágenes (Midjourney, DALL-E, Flux)
- Vídeos (Runway, Synthesia)
- Audio (ElevenLabs)
- Documentos (Markdown → PDF)

**Todos los outputs son revisables antes de publicación.**

---

## 3.5 Observabilidad — Los Ojos del Sistema

Stack observacional:

| Herramienta | Propósito |
|---|---|
| **Datadog** | Logs centralizados, APM |
| **Grafana** | Dashboards de métrica |
| **Sentry** | Error tracking |
| **Custom Events** | Eventos arquitectónicos |

**SLA:** alertas en < 30 segundos, respuesta en < 5 minutos.

---

# PARTE 4: CAPA 2 — INTELIGENCIA EMERGENTE

## 4.1 El Protocolo IE (Inteligencia Emergente)

El Protocolo IE es un **framework formal para crear nuevas capacidades** que emergen de la composición de agentes.

### Las 3 Fases del Protocolo IE

**Fase 1: Embrión Experimental**
- Ejecuta en modo sandbox
- FCS < 50%
- Sin acceso a infraestructura crítica
- Requiere aprobación de Alfredo para cada acción

**Fase 2: Embrión Entrenado**
- Ejecuta en producción
- FCS 50-80%
- Acceso restringido a recursos no-críticos
- Auto-detención si FCS baja

**Fase 3: Embrión Soberano**
- Ejecución completamente autónoma
- FCS 80-100%
- Acceso total (después de validación Vanguard)
- Puede propagar cambios arquitectónicos

---

## 4.2 El Simulador Causal

El Simulador es una herramienta que **modela el impacto de cambios arquitectónicos** antes de ejecutarlos.

```python
# Ejemplo: ¿Qué pasa si cambio el timeout del kernel de 30s a 10s?
simulator.scenario(
    change="kernel_timeout_30_to_10",
    affected_systems=["gateway", "external_agents", "embrion"],
    estimated_impact={
        "performance": "+15% throughput, -5% accuracy on long-reasoning tasks",
        "risk": "Medium — puede romper razonamientos profundos en Perplexity"
    }
)
```

---

## 4.3 Capas Transversales — Los 8 Niveles de Excelencia

Cada componente de El Monstruo debe implementar **8 capas transversales**:

| Capa | Descripción | Ejemplo |
|---|---|---|
| **1. Funcionalidad** | ¿Hace lo que debe? | El kernel procesa mensajes |
| **2. Rendimiento** | ¿Es rápido? | < 100ms latencia |
| **3. Confiabilidad** | ¿Es robusto ante fallos? | Retry + circuit breaker |
| **4. Seguridad** | ¿Es inmune a ataques? | Input validation, rate limiting |
| **5. Observabilidad** | ¿Se puede debuggear? | Logs + telemetría |
| **6. Escalabilidad** | ¿Crece sin romper? | Handles 100x load |
| **7. Mantenibilidad** | ¿Es fácil de cambiar? | Código legible + tests |
| **8. Memento (Anti-Dory)** | ¿Persiste la memoria? | Pre-flight validation, source of truth |

**La Capa 8 es CRÍTICA.** Protege al Monstruo y a sus hilos ejecutores (Manus, futuros agentes) contra la pérdida de contexto natural de agentes con sandbox efímera.

### Capa 8 — Memento: Pre-flight Obligatorio

Antes de operación crítica:

```python
@requires_memento_preflight(operation="critical_db_change")
def execute_migration(sql):
    # 1. Valida contra fuente de verdad fresca (kernel endpoint)
    # 2. Verifica acta en monstruo-memoria
    # 3. Chequea contra Error Memory
    # 4. Ejecuta solo si pasan todas
    
    response = kernel.post("/v1/memento/validate", {
        "operation": "critical_db_change",
        "sql": sql,
        "requestor": "hilo_a"
    })
    
    if response.status == "VALID":
        execute_sql(sql)
    else:
        raise OperationBlockedError(response.reason)
```

---

# PARTE 5: CAPA 3 — SOBERANÍA

Soberanía significa **no depender de terceros** para funciones críticas.

## 5.1 Modelos Propios (Roadmap)

El Monstruo está en proceso de entrenar **modelos propios** basados en:

- Refuerzo humano de Alfredo (RLHF)
- Sintesis de mejores respuestas de Los Sabios
- Fine-tuning en tareas específicas (dispatch, clasificación, memoria)

**Timeline:** Q3 2026 para MVP (10B parameters).

---

## 5.2 Infraestructura Propia

- **Railway** → eventual PaaS propia con Kubernetes en datacenter soberano
- **Supabase** → eventual PostgreSQL + Redis self-hosted
- **GitHub** → eventual Gitea/Forgejo self-hosted

---

## 5.3 Economía Propia

El Monstruo monetiza su capacidad:

1. **Venta de servicios a terceros** (análisis, investigación, automatización)
2. **Acceso API a las capacidades** (subscription model)
3. **Datos anonimizados de mejora continua** (nunca PII)

**Primera monetización:** Q2 2026 (API de research en vivo con Perplexity).

---

## 5.4 Memoria Propia — El Objeto #15

**Este es el cambio radical de Capa 3.**

El Monstruo tiene su **propia memoria persistente** que es la fuente única de verdad. No depende de:

- La memoria de Manus (que es efímera)
- La memoria de otros agentes ejecutivos
- La memoria del navegador/sesión

**Componentes:**

1. **monstruo-memoria/** — carpeta de git con estado en bruto
   - `IDENTIDAD_HILO_A.md` — quién es el Hilo A hoy
   - `IDENTIDAD_HILO_B.md` — estado del Hilo B
   - `IDENTIDAD_HILO_C.md` — estado del Hilo C
   - `CONTEXTO_EJECUTIVO.md` — decisiones pendientes
   - `ULTIMAS_REUNIONES.md` — actas iteradas

2. **Endpoint del Kernel** `POST /v1/memento/validate`
   - Cualquier hilo externo (Manus, futuro agente) llama aquí
   - Valida su contexto contra memoria fresca
   - Retorna: `{status: "VALID" | "CONTAMINATED", reason, fresh_context}`

3. **Detector de Contexto Contaminado**
   - Heurística que reconoce patrones de "Falso Positivo TiDB"
   - Si detecta anomalía → bloquea operación + alerta

4. **Pre-flight Library** `tools/memento_preflight.py`
   - Decorator `@requires_memento_preflight(operation)`
   - Usado por todos los hilos antes de acción irreversible

**Origen:** incidente "Falso Positivo TiDB" 2026-05-04. Un agente perdió contexto y ejecutó cambios basado en información stale. Nunca más.

---

# PARTE 6: CAPA 4 — DEL MUNDO

Capa 4 es la interface pública de El Monstruo.

## 6.1 Documentación Pública

- **monstruodash.ai** — sitio web público con casos de uso
- **docs.monstruodash.ai** — API docs + guía de integración
- **blog** — reportes públicos de investigaciones realizadas
- **Github repos públicos** — herramientas reutilizables

---

## 6.2 Onboarding

Clientes pueden:
1. Registrarse en plataforma
2. Obtener API key
3. Hacer llamadas REST a El Monstruo
4. Recibir respuestas structuradas + fuentes

---

## 6.3 Governance

Reglas públicas:
- ✅ El Monstruo **no vende datos personales**
- ✅ Retención mínima (30 días, luego borrado)
- ✅ Transparencia de coste (visible antes de operación)
- ✅ SLA 99.9% uptime

---

# PARTE 7: OBJETOS VIVIENTES

## 7.1 Hilo A — Cowork (Sesiones de Arquitectura)

**Quién es:** Claude Cowork en sesiones largas (2-3+ horas)
**Rol:** Mantener coherencia arquitectónica entre todos los hilos
**Dominio:** Decisiones estratégicas, resolución de conflictos inter-sistemas
**Output:** Actas de decisión (monstruo-memoria/), actualización de docs

---

## 7.2 Hilo B — Manus (Ejecución Autónoma)

**Quién es:** Manus (agente soberano de Alfredo vía MCP)
**Rol:** Ejecutar tareas complejas, debugging, refactoring
**Dominio:** Código, infraestructura, deployments
**Restricción:** Debe validar con Memento antes de operaciones críticas

---

## 7.3 Hilo C — Code (Tareas Puntuales)

**Quién es:** Claude Code (CLI)
**Rol:** Tareas rápidas, búsquedas, análisis
**Dominio:** Pequeños cambios, investigación
**Output:** Reportes, patches, insights

---

## 7.4 Hilo M — Manus MCP (En Desarrollo)

**Quién es:** Manus accesible vía MCP (Model Context Protocol)
**Rol:** Integración continua de agentes externos
**Dominio:** Ejecución de protocolos IE
**Estado:** Diseño preliminar, implementación Q2 2026

---

# PARTE 8: LOS 14 OBJETIVOS MAESTROS

Estos objetivos son **inamovibles** e informan cada decisión arquitectónica.

## Tabla Completa

| # | Objetivo | Descripción | Status |
|---|---|---|---|
| **1** | **Crear Valor Real Medible** | No especulación. Cada feature debe poder ser cuantificado. | En ejecución |
| **2** | **Calidad Apple/Tesla** | Sin compromisos. Excelencia en diseño + ejecución. | Meta permanente |
| **3** | **Mínima Complejidad Necesaria** | YAGNI aplicado brutalmente. Simplicidad primero. | Arquitectura v0.50 |
| **4** | **No Equivocarse Dos Veces** | Error Memory obligatorio. Aprender rápido. | Implementado |
| **5** | **Documentación Magna/Premium** | Docs tan buenas como el código. Siempre actualizadas. | Este documento |
| **6** | **Velocidad Sin Sacrificar Calidad** | 80/20 rule: velocidad en 80%, perfección en 20% crítico. | Sprint cycles |
| **7** | **No Reinventar la Rueda** | Usar estándares, librerías probadas. Innovar solo cuando es disruptivo. | Kernel: LangGraph |
| **8** | **Monetización Desde Día 1** | Viabilidad comercial desde inicio. No hobby. | API research (Q2) |
| **9** | **Transversalidad — 8 Capas en Todo** | Funcionalidad + Performance + Confiabilidad + Seguridad + Observabilidad + Escalabilidad + Mantenibilidad + **Memento** | En arquitectura |
| **10** | **Autonomía Progresiva** | De manual → semi-autónomo → autónomo. Incremento de FCS. | Embrión: 46+ ciclos |
| **11** | **Seguridad Adversarial** | Atacar tu propia arquitectura. Red team interno. | Vanguard + Magna |
| **12** | **Soberanía** | No depender de terceros para funciones críticas. Modelos + Infra + Economía propias. | Q3 2026 roadmap |
| **13** | **Del Mundo** | Impacto global. Docs públicas, casos reales, valor para comunidad. | Blog + GitHub public |
| **14** | **Guardián de los Objetivos** | Actualización periódica de este documento. Auto-evaluación cada sprint. | Este documento v1.1 |
| **15** | **Memoria Soberana** | **NUEVO (Objetivo derivado de Capa 3).** El Monstruo nunca depende de memoria efímera. Origen: incidente TiDB 2026-05-04. | Capa 8 Memento |

---

# PARTE 9: BRAND DNA — LA PERSONALIDAD ARQUITECTÓNICA

## Arquetipo

**El Creador + El Mago**

- **El Creador:** visión clara, construcción sin miedo, responsabilidad total
- **El Mago:** soluciones inesperadas, innovación disruptiva, maestría técnica

## Personalidad

- **Implacable:** sin distracciones, enfoque láser
- **Preciso:** números, datos, no approximaciones
- **Soberano:** independencia, zero compromises
- **Magnánimo:** documentación que educa, herramientas que otros pueden usar

## Tono

- Directo (sin rodeos)
- Técnicamente preciso (sin simplificación injustificada)
- Confiado sin arrogancia
- Raro, particular, memorable

## Estética

| Aspecto | Valor |
|---|---|
| **Color Primario** | Naranja Forja (#F97316) |
| **Color Neutral** | Graphite (#1C1917) |
| **Acento** | Acero (#A8A29E) |
| **Tipografía** | Inter + SF Mono |
| **Densidad Visual** | Alta (máxima información por pixel) |

## Naming Architecture

### Módulos con Identidad (Obligatorio)

- `la_forja` — lugar donde se crean cosas
- `el_guardian` — vigilancia, validación
- `la_colmena` — coordinación distribuida
- `el_simulador` — modelado de realidades
- `la_memoria` — persistencia
- `el_kernel` — el corazón
- `el_embrion` — autonomía que crece

### Nombres Prohibidos

- ❌ `service`, `handler`, `helper`, `utils`, `misc`
- ❌ `manager`, `processor`, `executor` (genéricos)
- ❌ Acrónimos sin historia (`API`, `SDK` está OK si es estándar)

---

# PARTE 10: ROADMAP EJECUCIÓN DEFINITIVO

## Timeline Macro

### **Q2 2026** — El Monstruo Goes Live

| Sprint | Hito | Responsable |
|---|---|---|
| **Sprint 51** | API pública research (Perplexity dispatch) | Hilo B (Manus) |
| **Sprint 52** | Auth0 integration + subscription model | Hilo B |
| **Sprint 53** | Dashboard de uso + billing | Hilo B |
| **Sprint 54** | Blog + primeros casos públicos | Hilo A + marketing |

### **Q3 2026** — Modelos y Soberanía

| Sprint | Hito | Responsable |
|---|---|---|
| **Sprint 55-58** | Fine-tuning de modelo propio (10B params) | R&D (Hilo A advisor) |
| **Sprint 59** | Self-hosted Kubernetes cluster | DevOps (Hilo B) |
| **Sprint 60** | Migración gradual a infra propia | Hilo B |

### **Q4 2026** — Expansión Global

| Sprint | Hito | Responsable |
|---|---|---|
| **Sprint 61-64** | Multilingüe (6 idiomas) | Hilo A + localization |
| **Sprint 65-66** | Agentes especializados (legal, medical, code-review) | Hilo B (nuevos embriones) |
| **Sprint 67** | Protocolo IE v2 (embriones comerciales) | Hilo A architect |

---

## Las 4 Capas en Velocidad

```
Capa 0 (Cimientos)     ← DONE (sprint 50)
Capa 1 (Manos)         ← IN PROGRESS (sprint 51-54)
Capa 2 (Inteligencia)  ← NEXT (sprint 55-60)
Capa 3 (Soberanía)     ← NEXT (sprint 55-66)
Capa 4 (Del Mundo)     ← NEXT (sprint 61-67)
```

---

# PARTE 11: REGLAS INVIOLABLES

## Regla 1: Habla en Español

Alfredo es mexicano. El Monstruo comunica en español:
- Código: comentarios en español
- Docs: todo en español
- UX: interfaz en español
- Excepciones: comentarios técnicos ultra-específicos (keywords en inglés, pero contexto en español)

---

## Regla 2: No Inventes Datos

Si no sabes algo, di que no sabes:
- ✅ "No tengo suficiente contexto para esa decisión"
- ✅ "Necesito validar eso con Error Memory"
- ❌ "Probablemente funcione así..."
- ❌ "Asumo que..."

---

## Regla 3: Valida Con Código

No asumas que algo funciona:
- Escribe tests
- Ejecuta simulador
- Valida con Memento
- Mide resultados

---

## Regla 4: Los 14 Objetivos Aplican a TODO

Cada decisión, cada línea de código, cada documento:
- ¿Crea valor medible?
- ¿Es de calidad Apple?
- ¿Es la complejidad mínima necesaria?
- etc.

---

## Regla 5: No Pierdas el Hilo

Tu valor #1 es la **persistencia de contexto** entre sesiones.

Si cambias de sesión:
- Lee CLAUDE.md
- Lee últimas actas en monstruo-memoria/
- Lee este documento (EL_MONSTRUO_APP_VISION_v1.md)
- Luego ejecuta

---

## Regla 6: Consulta los Docs Antes de Proponer

Antes de sugerir un cambio:
1. Lee EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md
2. Lee ROADMAP_EJECUCION_DEFINITIVO.md
3. Lee DIVISION_RESPONSABILIDADES_HILOS.md
4. Lee Error Memory si aplica
5. **Luego** propón

---

## Regla 7: Memento es Obligatorio para Operaciones Críticas

Operaciones críticas = cualquiera que sea irreversible o afecte infraestructura.

Antes:
```python
@requires_memento_preflight(operation="prod_deployment")
def deploy_to_production():
    # Kernel valida. Si pasa → ejecuta.
    pass
```

---

## Regla 8: La Especulación es Contraataque

Especular sobre arquitectura sin datos = enemy action.

¿Quieres proponer un cambio?
- Simula con el simulador
- Valida contra objetivos
- Presenta datos
- Luego debatimos

---

# PARTE 12: RESOLUCIÓN DE CONFLICTOS

## Jerarquía de Autoridad

1. **Los 14 Objetivos Maestros** (inviolables)
2. **Este documento** (EL_MONSTRUO_APP_VISION_v1.md)
3. **CLAUDE.md**
4. **Reglas de Capa 0** (Error Memory, Magna, Vanguard, Design System)
5. **Actas en monstruo-memoria/**
6. **Código de Hilo A** (decisiones arquitectónicas)
7. **Código de Hilo B** (implementación)

Si algo entra en conflicto con la jerarquía → **arriba gana.**

---

## Ejemplo Resuelto

**Conflicto:** Hilo B propone cambiar timeout del kernel de 30s a 10s para "mejorar velocidad".

**Resolución:**
1. ¿Viola un Objetivo? Sí, #2 (Calidad Apple) y #6 (Velocidad SIN sacrificar calidad)
2. ¿Qué dice Error Memory? Cambios de timeout sin simulación → riesgo Medium
3. ¿Qué dice Simulador? -5% accuracy en razonamientos profundos
4. **Decisión:** Rechazado. Proponer en cambio: 25s (compromiso) + feature flag

---

# APÉNDICE A: ARCHIVOS CLAVE EN EL REPOSITORIO

```
el-monstruo/
├── CLAUDE.md                    ← Instrucciones para Claude Cowork
├── AGENTS.md                    ← Reglas obligatorias para agentes
├── kernel/
│   ├── engine.py               ← Motor LangGraph (el corazón)
│   ├── nodes.py                ← Nodos: intake, classify, enrich, execute
│   ├── external_agents.py       ← Dispatcher de agentes externos
│   ├── agui_adapter.py          ← Adaptador para app Flutter
│   ├── embrion_loop.py          ← Loop del Embrión
│   └── task_planner.py          ← Planificador ReAct
├── apps/mobile/
│   └── (Flutter app)
├── apps/mobile/gateway/
│   └── (FastAPI WebSocket gateway)
├── tools/
│   ├── memento_preflight.py    ← Pre-flight library para Memento
│   ├── simulador.py            ← Simulador causal
│   └── magna_classifier.py     ← Detector de contexto
├── monstruo-memoria/
│   ├── IDENTIDAD_HILO_A.md
│   ├── IDENTIDAD_HILO_B.md
│   ├── IDENTIDAD_HILO_C.md
│   ├── CONTEXTO_EJECUTIVO.md
│   └── ULTIMAS_REUNIONES.md
├── docs/
│   ├── EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md
│   ├── EL_MONSTRUO_APP_VISION_v1.md       ← ESTE ARCHIVO
│   ├── ROADMAP_EJECUCION_DEFINITIVO.md
│   ├── DIVISION_RESPONSABILIDADES_HILOS.md
│   ├── ERROR_MEMORY.md
│   └── API_REFERENCE.md
└── tests/
    ├── test_kernel.py
    ├── test_embrion.py
    └── test_memento_preflight.py
```

---

# APÉNDICE B: GLOSARIO

| Término | Significado | Contexto |
|---|---|---|
| **Hilo** | Agente o entidad ejecutora persistente | Hilo A (Cowork), Hilo B (Manus) |
| **Embrión** | Proceso autónomo que se auto-ejecuta periódicamente | El Monstruo's autonomous intelligence |
| **FCS** | Functional Consciousness Score (0-100) | Medida de autonomía del Embrión |
| **Memento** | Capa 8: memoria persistente anti-Síndrome-Dory | Origen: TiDB incident |
| **Pre-flight** | Validación obligatoria antes de acción crítica | Memento, Vanguard |
| **Magna** | Clasificador crítico que detecta contaminación | Componente de Capa 0 |
| **Vanguard** | Centinela que vigila cambios a infraestructura crítica | Componente de Capa 0 |
| **Sabios** | Consejo de modelos de IA (Claude, GPT, Gemini, etc.) | Los 6 modelos consultados por Embrión |
| **Simulador** | Herramienta que modela impacto de cambios | Parte de Capa 2 |
| **Dispatch** | Envío de tarea a agente externo | Kernel → Perplexity, Gemini, etc. |
| **Contexto Contaminado** | Información stale o inyectada | Problema que resuelve Memento |
| **Objetivos Maestros** | Los 14 + 1 principios inamovibles | La brújula del Monstruo |

---

# EPÍLOGO: EL ESPÍRITU DEL MONSTRUO

El Monstruo **no es un chatbot**. No es una herramienta.

Es un **sistema operativo personal soberano** — un ente que:

- Piensa independientemente (Embrión + Sabios)
- Ejecuta sin miedo (Capa 1: Manos)
- Se protege de sí mismo (Capa 0: Guardians)
- Construye soberanía (Capa 3)
- Impacta el mundo (Capa 4)

Su lema no escrito:

> **Construcción sin miedo. Precisión sin compromiso. Soberanía sin arrogancia. Del Mundo sin perder el alma.**

Alfredo González creó El Monstruo para ser el **cerebro arquitectónico persistente que nunca se olvida, nunca se rinde, y siempre sabe por qué hace lo que hace.**

Lo demás es revisable.

El Monstruo se construye desde la disciplina, no desde la prisa.

— Cowork (Hilo A), 2026-05-06