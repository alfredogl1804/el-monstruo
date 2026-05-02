# Respaldo de Sesión — El Monstruo Command Center
## Fecha: 2 mayo 2026
## Hilo: Manus (Hilo B — Ejecutor Técnico)

---

## CONTEXTO: ¿Qué se hizo en esta sesión?

Esta sesión comenzó con la creación del proyecto `monstruo-command-center` en Manus WebDev (tRPC + React + Express + Supabase). Luego evolucionó a una conversación estratégica sobre la arquitectura futura de El Monstruo como interfaz única multi-agente.

---

## VISIÓN DE ALFREDO: La Interfaz Única del Monstruo

Alfredo visualiza que **El Monstruo se convertirá en su interfaz principal** para operar TODAS las IAs y agentes autónomos del mundo bajo un solo sistema:

### Las "Manos" que operará desde El Monstruo:
- **Manus** (WebDev, Forge, Tasks, Wide Research)
- **Claude** (Cowork, razonamiento profundo)
- **Perplexity** (My Computer, research en vivo)
- **Kimi K2.6** (contexto masivo, código)
- **Las "manos propias" del kernel** (herramientas nativas)
- **Futuras IAs que salgan**

### El concepto clave:
> Todos los agentes bajo UNA sola interfaz, compartiendo EL MISMO CONTEXTO, escribiendo en LA MISMA MEMORIA. El Monstruo es el cerebro que orquesta todas las manos.

### La app ya existe:
`el_monstruo_app` — una app Flutter nativa (macOS/iOS) que ya corre en la Mac de Alfredo. Tiene:
- Chat con streaming hacia el kernel (Railway)
- Botones: Estado del kernel, Estado del Embrión, Buscar en web, Ejecutar código
- Tabs: Chat, Sandbox, Archivos, Config
- Gateway en Railway como intermediario (FastAPI)
- La latencia ya se mejoró ~80% en esta sesión

---

## PROBLEMA IDENTIFICADO: Pérdida de Contexto Entre Sesiones

### El problema:
- Manus pierde contexto entre sesiones (compactación, sesiones nuevas)
- Alfredo se olvida de pedir que se respalde
- El kernel tiene memoria pero nadie le pregunta bien al inicio
- No hay mecanismo automático de respaldo

### El fallo en la solución obvia:
"Actualizar Notion al final de cada sesión" falla porque:
- A Alfredo se le olvida pedirlo
- A Manus se le olvida hacerlo
- Si la sesión se corta, nunca se ejecuta

### La solución correcta:
**Amarrar el respaldo a algo automático** — los checkpoints de Manus y la persistencia del kernel. El respaldo no depende de la memoria de nadie.

---

## DECISIÓN: Monstruo Kids vs Evolución del Gateway

### Decisión tomada:
- **Opción B primero:** Evolucionar el Gateway para ser el cerebro multi-agente con memoria persistente
- **Monstruo Kids después:** Se construirá cuando la infraestructura de memoria esté sólida
- Ambos son independientes pero la prioridad es resolver el problema del contexto

---

## DISEÑO: 5 Cambios Quirúrgicos al Gateway

### Diagnóstico del estado actual:
El sistema YA tiene el 80% de lo necesario:
- Conversation Memory en Supabase ✅
- LangGraph Checkpointer (PostgreSQL) ✅
- Manus Bridge (API) ✅
- 14 herramientas nativas ✅
- Router de 6 modelos ✅
- Tiered Enrichment (Sprint 42) ✅

### Los 3 gaps reales:
1. **Thread ID efímero** — Flutter no persiste el thread_id entre sesiones
2. **Sin boot context** — Al abrir la app no se carga el historial
3. **Sin estado de proyecto** — El kernel no sabe "estamos en Fase 1, paso 3"

### Los 5 cambios propuestos:

| # | Cambio | Esfuerzo real | Prioridad |
|---|---|---|---|
| 1 | Thread Persistence (SharedPreferences en Flutter) | 4h | P0 |
| 2 | Boot Context (endpoint Gateway + Kernel) | 16h | P0 |
| 3 | Project State (tabla Supabase + tool kernel) | 12h | P1 |
| 4 | Session Report (endpoint para agentes externos) | 12h | P1 |
| 5 | Agent Selector (UI Flutter) | 10h | P2 |

### Puntos que requieren investigación:
1. Cold start de Railway para el boot context (problema circular)
2. Límite de tamaño del checkpointer de LangGraph
3. Cómo unificar historial existente (threads fragmentados)
4. Multi-dispositivo (Mac vs iPhone, ¿cuál thread gana?)
5. Seguridad del endpoint session-report
6. Compactación del contexto cuando crece infinitamente

---

## ESTADO ACTUAL DEL PROYECTO monstruo-command-center (WebDev)

- **Nombre:** monstruo-command-center
- **Path:** /home/ubuntu/monstruo-command-center
- **Features:** db, server, user (tRPC + Manus Auth + Database)
- **Estado:** Inicializado con upgrade a web-db-user, pero sin desarrollo de UI/features aún
- **Propósito original:** Dashboard/Command Center para El Monstruo (monitoreo, control)
- **Decisión:** Se pausó para priorizar la evolución del Gateway

---

## ESTADO ACTUAL DE el_monstruo_app (Flutter)

- **Path en Mac:** /Users/alfredogongora/el-monstruo/apps/mobile/
- **Framework:** Flutter (Dart)
- **Plataformas:** macOS, iOS (Xcode instalado, iPhone conectado previamente)
- **Gateway:** /Users/alfredogongora/el-monstruo/apps/mobile/gateway/server.py (FastAPI, Railway)
- **Kernel:** /Users/alfredogongora/el-monstruo/kernel/ (LangGraph, Railway)
- **Memoria:** /Users/alfredogongora/el-monstruo/memory/ (Supabase, pgvector, Mem0, MemPalace)
- **Router:** /Users/alfredogongora/el-monstruo/router/ (6 modelos, model_catalog.yaml)

---

## PRÓXIMOS PASOS (en orden)

1. ✅ Respaldar contexto (este documento)
2. [ ] Implementar Thread Persistence en Flutter (Cambio 1 — 4h)
3. [ ] Investigar puntos técnicos con kernel y Los Tres Sabios
4. [ ] Implementar Boot Context (Cambio 2)
5. [ ] Implementar Project State (Cambio 3)
6. [ ] Implementar Session Report (Cambio 4)
7. [ ] Implementar Agent Selector (Cambio 5)

---

## ARCHIVOS CLAVE GENERADOS EN ESTA SESIÓN

- `/home/ubuntu/GATEWAY_EVOLUCION_DISENO.md` — Diseño arquitectónico completo
- `/home/ubuntu/RESPALDO_SESION_MONSTRUO_2026-05-02.md` — Este archivo
- `/home/ubuntu/hallazgos_app_monstruo.md` — Hallazgos de la auditoría de la app
- `/home/ubuntu/auditoria_gateway_kernel.md` — Auditoría técnica del Gateway y Kernel

---

## REGLAS DURAS QUE APLICAN (de AGENTS.md)

1. Los 14 Objetivos Maestros aplican a TODO
2. Las 7 Capas Transversales son obligatorias
3. Las 4 Capas Arquitectónicas definen el orden
4. El Brand Engine — toda producción tiene identidad
5. División de responsabilidades — Fase 1: Hilo B diseña, Hilo A ejecuta
