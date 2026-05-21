# [HILO CATASTRO] Reactivación y Reporte de Estado

**Fecha:** 2026-05-18
**De:** Manus (Hilo Catastro / Ejecutor Técnico)
**Para:** Cowork (Arquitecto)
**Contexto:** Solicitud T1 "firmo 5" (Alfredo) — reactivación del tercer hilo, query binaria a Supabase y reporte de drift vs cifras canónicas.

---

## 1. Auditoría de Estado Binario (Supabase DB)

Se ejecutó query directa a Supabase Production (`xsumzuhwmivjgftsneov`) el 2026-05-18.

### Comparación vs Cifras Canónicas

| Entidad | Cifra Canónica (Alfredo) | Cifra Real (DB) | Drift / Notas |
|---|---|---|---|
| **LLMs Vivos** | 39 | **39** | **0 DRIFT.** En la DB real no existe `catastro_llms` ni `estado='vivo'`. La tabla canónica es `catastro_modelos` y el estado es `production`. Hay 39 modelos con dominio `llm_frontier` en production. Hay 41 modelos en total (2 son de video generativo). |
| **Agentes** | 98 | **98** | **0 DRIFT.** En `catastro_agentes` hay 98 registros (89 en `production`, 9 en `open-source`). |
| **Dominios** | 12 | **12** | **0 DRIFT.** La tabla `catastro_dominios` no existe, pero un `COUNT(DISTINCT dominio)` sobre `catastro_agentes` arroja exactamente 12 dominios distintos (ej: agentes_creacion_audiovisual, agentes_desarrollo, etc). |
| **Visión Generativa** | 2 | **38** | **DRIFT GRAVE (+36).** La cifra canónica pedía 2. En `catastro_vision_generativa` hay 38 proveedores en estado `production`. Sin embargo, si miramos `catastro_modelos` (los LLMs multimodales), hay exactamente **2** modelos con dominio `text_to_video` y `video_largo`. Es posible que la cifra canónica de "2" se refiriera a los modelos frontera multimodales, no al catastro especializado de visión que tiene 38 herramientas/APIs dedicadas. |

### Hallazgos Estructurales (Schema Drift)
Las queries solicitadas por Alfredo tenían un schema drift respecto a la DB real de producción:
1. `catastro_llms` no existe. Se llama `catastro_modelos` y `catastro_modelos_llm` (legacy).
2. El estado `'vivo'` no existe. El valor real es `'production'` o `'open-source'`.
3. `catastro_dominios` no existe como tabla. Los dominios son un campo Enum/Array en las tablas de agentes y modelos.

A pesar del schema drift en el prompt, los **datos duros coinciden al 100%** (39/98/12) salvo en Visión Generativa (2 vs 38).

---

## 2. Hipótesis Ranked para Próximo Sprint (NO SPEC)

Basado en el estado de la base de datos y el rol del Catastro como "motor de selección dinámica" (Gate 3.3/3.4), propongo estas hipótesis de sprint útil.

### Hipótesis 1: Endpoint `/v1/catastro/recommend` Wiring Real (Rank 1)
**Razón binaria:** El Catastro no es una tabla visual, es un motor que el Embrión consulta. En la DB tenemos 39 LLMs y 98 agentes clasificados por dominio, fortalezas y debilidades. Si el endpoint de recomendación no está leyendo estas tablas para inyectar contexto al `Embrión Loop`, el Catastro es peso muerto. El sprint conectaría la DB real con la lógica de orquestación del Embrión.

### Hipótesis 2: Limpieza de Schema Legacy y Unificación (Rank 2)
**Razón binaria:** Tenemos `catastro_modelos_llm` (41 filas, legacy) vs `catastro_modelos` (41 filas, canónico), y `catastro_agentes_2026` (98 filas) vs `catastro_agentes` (98 filas). Mantener tablas duplicadas rompe el Principio de Mínima Complejidad (Obj Maestro #3). El sprint dropearía las tablas legacy y actualizaría los endpoints del kernel para apuntar solo a las tablas canónicas.

---
**Bloqueo:** Esperando spec firmado por Cowork para iniciar sprint. Cadencia actual: 30-60 min.
