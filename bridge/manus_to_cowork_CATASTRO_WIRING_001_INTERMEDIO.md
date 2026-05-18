---
sprint_id: CATASTRO-WIRING-001
version: v1_intermedio
titulo: Reporte Intermedio — CASO A detectado (Audit estático)
estado: 🟡 PAUSADO ESPERANDO DECISIÓN COWORK
fecha: 2026-05-18
owner: Manus Hilo Catastro
---

# Reporte Intermedio CATASTRO-WIRING-001

> **TL;DR:** El audit estático profundo confirma **CASO A (Embrión NO consume Catastro)**. Hay 3 overrides hardcoded en `embrion_loop.py`. Además, se invoca la limitación **L_W5** (kernel Railway caído, endpoint retorna 404), lo que impide el audit runtime. Se requiere decisión de Cowork sobre si hacer el fix estático hoy o diferir hasta que kernel esté UP.

## §1 Resultados Pre-flight (Bloqueos detectados)

1. **Catastro DB count:** 41 modelos en production (39 `llm_frontier` + 2 video). Confirmado vía query directa desde Mac de Alfredo.
2. **Endpoint `/v1/catastro/recommend`:** ❌ **CAÍDO (HTTP 404 "Application not found")**. 
   - El dominio `el-monstruo-kernel.up.railway.app` está activo pero no encuentra la app.
   - Esto invoca **Limitación L_W5** del spec: "Fall-back: audit estático solo (CASO 0)".
3. **Grep `catastro|recommend` en `embrion_loop.py`:** 0 hits.

## §2 Evidencia Binaria del Audit Estático Profundo

He ejecutado un audit estático exhaustivo cruzando 3 fuentes ortogonales (`embrion_loop.py`, `kernel/cowork_runtime`, y `apps/`).

### 1. `embrion_loop.py` NO consume Catastro
- **0 imports** de `catastro_client`, `recommendation`, o `RecommendationEngine`.
- **0 llamadas** a `catastro_engine` o endpoints HTTP (`httpx`/`requests` ausentes para esto).
- El selector adaptativo (`kernel/adaptive_model_selector.py`) existe pero **NO es importado** por `embrion_loop.py`.

### 2. Overrides Hardcoded detectados (CASO B parcial)
`embrion_loop.py` define y usa modelos hardcoded mediante variables de entorno con fallbacks estáticos:

```python
# Líneas 98-99
JUDGE_MODEL = os.environ.get("EMBRION_JUDGE_MODEL", "gpt-5")
ACTOR_MODEL = os.environ.get("EMBRION_ACTOR_MODEL", "gpt-5.5")
```

Estas constantes se usan directamente en 3 llamadas a LLM dentro del loop (líneas 1086, 1578, 2449), bypassando completamente cualquier recomendación dinámica.

### 3. Hallazgo lateral: El pipeline E2E SÍ consume Catastro
A diferencia del Embrión, el pipeline E2E (`kernel/e2e/pipeline.py`) **sí está cableado correctamente**.
- Importa `CatastroRuntimeClient`.
- Hace 8 llamadas a `await cat.select_model_for_step(...)` mapeando steps a `use_case` (ej. "INVESTIGAR" → "research_grounded").

## §3 Diagnóstico Final

Estamos ante un **CASO A puro para el Embrión Loop**: el consumidor principal del Monstruo no usa el Catastro. Los 39 LLMs en la DB son peso muerto para el Embrión. 

El pipeline E2E sí lo usa, pero el Embrión (que es el core de autonomía) está hardcoded a `gpt-5.5` y `gpt-5`.

## §4 Decisión pendiente para Cowork

Dado que el kernel Railway está caído (L_W5), no puedo hacer pruebas runtime del fix hoy. 

Cowork, elige una opción y firma para continuar:

- **[ ] OPCIÓN 1 (Fix Estático Hoy):** Manus escribe el mini-PR para `embrion_loop.py` reemplazando los hardcodes por llamadas a `catastro_engine` (que ya vive en `app.state` vía `main.py`). Se aprueba con audit estático DSC-G-008 v4 y se deja el merge listo para cuando kernel vuelva.
- **[ ] OPCIÓN 2 (Pausar Sprint):** Detener el sprint aquí. Requerir a Alfredo/DevOps que levanten el kernel en Railway primero, para poder hacer el ciclo completo con pruebas runtime (TDD real).
- **[ ] OPCIÓN 3 (Scope Expandido):** Manus investiga por qué Railway da 404, lo arregla, y luego continúa el sprint normal. (Requiere firma T1 explícita porque tocar infra no estaba en el spec original).

Espero firma.
