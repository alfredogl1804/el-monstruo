# Sprint 90 — Capa Transversal C1 (Motor de Ventas) E2E · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque post-Sprint 89
> **Sprint asignado:** Hilo Manus Ejecutor
> **Dependencias:** Sprint 87 NUEVO E2E + Sprint 88 Embriones colectivos + Sprint 89 Guardian Autónomo
> **Cierra:** Objetivo #9 (Transversalidad Universal) Capa C1 al 70%+ y avanza Objetivo #1 (Crear Empresas) hacia 80%+

---

## Contexto

Sprint 87 NUEVO entrega "frase → empresa con tráfico real" pero la pieza de **monetización primaria** queda implícita: una landing convierte visitantes en leads/clientes, pero no hay un **Motor de Ventas activo** que persiga, califique, y cierre.

Capa C1 es la primera de las 6 capas transversales del Objetivo #9 que se activan post-cimientos. Es la capa que permite que el Monstruo no solo cree empresas, sino que **les genere ingresos desde el día 1** (Objetivo #1 + Objetivo #8 conectados).

Sprint 90 NO implementa Stripe (eso es Sprint 95+ DIFERIDO). Implementa el funnel de ventas: captura → calificación → seguimiento → cierre. La transacción financiera es post-v1.0.

## Objetivo del Sprint

Activar el Motor de Ventas como capa transversal funcional: cualquier empresa generada por el pipeline E2E (Sprint 87) tiene automáticamente un funnel de ventas conectado que captura leads, los califica con un Embrión, los enrolla en un email sequence, y reporta métricas vivas al Guardian (Sprint 89).

## Decisiones arquitectónicas firmes

### Decisión 1 — Reutilizar Embrión Estratega + Embrión Ventas existentes

Los 9 Embriones del Sprint 88 ya incluyen:
- Embrión Estratega (define ICP, value prop, objeciones)
- Embrión Ventas (drafts outreach, qualifies leads, suggests next actions)

Sprint 90 NO crea Embriones nuevos. Conecta los 2 existentes al funnel E2E vía orchestrator.

### Decisión 2 — Schema Supabase para el funnel

Migration `024_sprint90_motor_ventas_schema.sql`:

```sql
CREATE TABLE ventas_leads (
    id BIGSERIAL PRIMARY KEY,
    e2e_run_id TEXT REFERENCES e2e_runs(id),
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    email TEXT NOT NULL,
    nombre TEXT,
    empresa TEXT,
    telefono TEXT,
    fuente_captura TEXT NOT NULL,            -- 'landing_form' | 'chatbot' | 'cta_inline'
    raw_payload JSONB,
    qualification_status TEXT DEFAULT 'pending'
        CHECK (qualification_status IN ('pending','qualified','disqualified','contacted','converted','lost')),
    qualification_score NUMERIC(3,2),         -- 0.00 a 1.00
    qualified_by_embrion TEXT,                -- 'estratega' | 'ventas' | 'colectivo'
    qualification_reasoning TEXT,
    next_action TEXT,
    next_action_due_at TIMESTAMPTZ
);

CREATE INDEX idx_ventas_leads_status ON ventas_leads (qualification_status, captured_at DESC);
CREATE INDEX idx_ventas_leads_e2e ON ventas_leads (e2e_run_id);

CREATE TABLE ventas_secuencias (
    id TEXT PRIMARY KEY,                      -- 'seq_<lead_id>_<n>'
    lead_id BIGINT REFERENCES ventas_leads(id),
    paso_n INT NOT NULL,
    canal TEXT NOT NULL CHECK (canal IN ('email','sms','llamada')),
    contenido TEXT NOT NULL,                  -- markdown
    enviado_at TIMESTAMPTZ,
    abierto_at TIMESTAMPTZ,                   -- email tracking
    respondido_at TIMESTAMPTZ,
    metadata JSONB
);

CREATE TABLE ventas_metrics_daily (
    fecha DATE PRIMARY KEY,
    leads_capturados INT DEFAULT 0,
    leads_qualified INT DEFAULT 0,
    leads_disqualified INT DEFAULT 0,
    leads_converted INT DEFAULT 0,
    conversion_rate NUMERIC(5,2),
    tiempo_medio_qualified_to_converted_hours NUMERIC(8,2)
);
```

### Decisión 3 — Patrón "consultar Catastro en runtime" se EXTIENDE a este Sprint

El Motor de Ventas usa LLMs para escribir outreach. **NO hardcodear modelo** (`gpt-4`, `claude-3.5`, etc.). Cada call a LLM consulta el Catastro v1.x en runtime con criterios:
- Macroárea 1 (Razonamiento) score >= 70
- Idioma soportado: español + inglés (mínimo)
- Costo por 1M tokens dentro del top 50% Trono Score

Si el Catastro no tiene candidato → fallback heurístico (templates pre-escritos por industria).

### Decisión 4 — Capa Memento aplicada en cada operación crítica de ventas

Operaciones de ventas que pasan por `tools/memento_preflight.py`:
- `lead_capture_persist` — antes de INSERT a `ventas_leads`
- `lead_qualification_run` — antes de invocar Embrión calificador
- `secuencia_step_send` — antes de enviar email/sms (operación irreversible)
- `metrics_daily_compute` — antes de calcular métricas de cierre

### Decisión 5 — 3 niveles de calificación (correlativo con Guardian Sprint 89)

| Nivel | Criterio | Acción automática |
|---|---|---|
| Cold | score < 0.4 | Auto-marca disqualified, sin secuencia |
| Warm | 0.4 <= score < 0.7 | Enrolla en secuencia automatizada estándar (3 emails) |
| Hot | score >= 0.7 | Notifica a humano (Telegram/email Alfredo) + secuencia premium (5 emails) |

### Decisión 6 — Guardian (Sprint 89) recibe métricas del Motor de Ventas

El Sprint 89 Guardian agrega 1 métrica nueva al scoring:
- Objetivo #1 (Crear Empresas) ahora incluye `% de e2e_runs con leads_qualified > 0 last 7d`

Esto cierra el círculo: el Guardian valida no solo que se cree la empresa, sino que **comercializa**.

## Bloques del Sprint

### Bloque 1 — Schema + endpoints REST (30-45 min)
- Migration 024 (3 tablas)
- `kernel/ventas/routes.py` con `POST /v1/ventas/leads/capture`, `GET /v1/ventas/leads/list`, `GET /v1/ventas/metrics/daily`

### Bloque 2 — Embrión Calificador conectado (30-45 min)
- `kernel/ventas/qualifier.py` invoca Embrión Estratega + Embrión Ventas
- Modo `quorum 2-de-2` (ambos Embriones tienen que coincidir en cold/warm/hot)
- Persistencia en `ventas_leads.qualification_status`

### Bloque 3 — Secuencias automatizadas (30-45 min)
- `kernel/ventas/secuencias.py` con templates por industria + Embrión Ventas drafting
- Cron 1h: detecta leads con `next_action_due_at <= NOW()` y dispara siguiente paso
- Email gateway: `tools/email_send.py` ya existe, extender para tracking

### Bloque 4 — Conexión al pipeline E2E Sprint 87 (15-30 min)
- `kernel/e2e/orchestrator.py` paso final: si la empresa generada tiene CTA de captura, conecta al Motor de Ventas automáticamente
- Test: 1 frase E2E que genere empresa + capture lead simulado + lo califique

### Bloque 5 — Métricas diarias + integración Guardian (20-30 min)
- Cron 23:55 CST: computa `ventas_metrics_daily`
- Guardian Sprint 89 lee esta tabla para Objetivo #1 scoring

### Bloque 6 — Capa Memento aplicada (15-20 min)
- 4 operations registradas en catálogo
- Tests con mock de preflight

### Bloque 7 — Tests + smoke productivo (30-45 min)
- Test del qualifier con 3 casos sintéticos (cold, warm, hot)
- Test de secuencias con dry-run sin envío real
- Test de métricas diarias
- Smoke contra producción real con 1 lead simulado

## ETA total recalibrada

7 bloques × ~30 min promedio = **3-5 horas reales** al ritmo demostrado del Hilo Ejecutor.

(ETA magna previa pre-recalibración: 1-2 semanas. Recalibración 5-10x aplicada.)

## Métricas de éxito

| Métrica | Target |
|---|---|
| 1 lead simulado capturado, calificado, enrolado, métrica computada | ✅ |
| Tests acumulados | ≥ 450 PASS |
| Suite Sprint 86 + 87 + 88 + 89 + 90 | regresión cero |
| Tiempo medio captura → calificación | < 60s P95 |
| Guardian Sprint 89 lee métricas Sprint 90 | ✅ |
| Sin LLM hardcoded — todo desde Catastro | ✅ |

## Disciplina obligatoria

- Capa Memento aplicada en 4 operations críticas
- Brand DNA aplicado en templates de outreach (forja + graphite + acero, tono Alfredo)
- Anti-Dory: lectura fresh de `qualification_status` antes de cada step
- Standby duro 7 días: ANULADO por política Cowork (Apéndice 1.2)

## Zona primaria

```
kernel/ventas/* (nuevo módulo completo)
kernel/ventas/routes.py
kernel/ventas/qualifier.py
kernel/ventas/secuencias.py
kernel/ventas/cron.py
kernel/e2e/orchestrator.py (modificación quirúrgica del paso final)
scripts/024_sprint90_motor_ventas_schema.sql
scripts/run_migration_024.py
scripts/_smoke_sprint90_motor_ventas.py
tests/test_sprint90_motor_ventas_*.py
bridge/MOTOR_VENTAS_OPERATIONAL_GUIDE.md
```

## NO TOCÁS

- `kernel/catastro/*` (zona Catastro, solo lectura desde Motor de Ventas)
- `kernel/memento/*` (zona cerrada)
- `kernel/embriones/*` (zona Sprint 88, solo se invocan, no se modifican)
- `kernel/guardian/*` (zona Sprint 89, solo se EXTIENDE en métrica Obj #1)
- `kernel/e2e/pipeline.py` salvo donde el orchestrator lo invoca

## Próximo sprint después

Sprint 91 — Capa Transversal C2 (Motor de SEO + Contenido) E2E.

— Cowork (Hilo B)
