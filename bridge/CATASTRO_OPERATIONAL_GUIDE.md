# El Catastro · Guía Operativa

> Hilo Manus Catastro · Sprint 86 Bloque 7 · 2026-05-04 · v0.86.7
>
> Esta guía es para **humanos** (Alfredo) y **Cowork** que necesitan consultar, interpretar y operar el Catastro de modelos del Monstruo. Para detalles de implementación, ver `kernel/catastro/`.

---

## ¿Qué es El Catastro?

El Catastro es el **registro vivo** de modelos de IA, herramientas y proveedores que el Monstruo conoce, evalúa y recomienda. Es la fuente de verdad para responder preguntas como *"¿Cuál es el mejor modelo para razonamiento legal LATAM hoy?"* o *"¿Qué LLM debo usar para coding con presupuesto bajo?"*.

A diferencia de un benchmark estático, el Catastro:

1. **Se actualiza solo** vía cron diario que ingiere de Artificial Analysis, OpenRouter y Hugging Face.
2. **Valida cruzadamente** cada cambio mediante un quórum de 6 LLMs curadores (Claude Opus, GPT-5.4, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro).
3. **Calcula un score relativo** (Trono Score) por dominio con z-scores intra-dominio sobre 5 métricas ponderadas: Quality (40%), Cost Efficiency (25%), Speed (15%), Reliability (10%), Brand Fit (10%).
4. **Persiste atómicamente** vía función PL/pgSQL (transacción server-side, no rollback parcial).
5. **Expone resultados** vía REST `/v1/catastro/*` y como tools nativas del FastMCP.

---

## Arquitectura en una mirada

```
fuentes externas (AA + OR + HF)
        ↓ pipeline.run()
quorum_validator (6 LLMs)
        ↓ persistence.persist() · RPC atómica
catastro_modelos · catastro_eventos · catastro_curadores
        ↓ recompute_trono(p_dominio) · z-scores SQL
catastro_trono_view (materializada con bandas)
        ↓
RecommendationEngine (cache LRU 60s)
        ↓
REST /v1/catastro/* + FastMCP tools + Dashboard
```

---

## Cómo consultar El Catastro

### Vía REST (curl, Postman, navegador)

| Endpoint | Auth | Para qué sirve |
|---|---|---|
| `POST /v1/catastro/recommend` | Bearer | Top N modelos por trono_global filtrable por dominio/use_case |
| `GET /v1/catastro/modelos/{id}` | Bearer | Ficha detallada con todas las métricas |
| `GET /v1/catastro/dominios` | Bearer | Lista de dominios con conteos por macroárea |
| `GET /v1/catastro/status` | Bearer | Snapshot de salud técnica (cache, db, fuentes) |
| `GET /v1/catastro/dashboard/summary` | **Público*** | Resumen para Alfredo/Cowork (read-only) |
| `GET /v1/catastro/dashboard/timeline?days=14` | **Público*** | Histórico runs/eventos/drift por día |
| `GET /v1/catastro/dashboard/curators` | **Público*** | Trust scores y tendencia de curadores |
| `GET /v1/catastro/dashboard/` | **Público*** | HTML render con Chart.js |

*\*Auth pública por defecto. Endurecer con `CATASTRO_DASHBOARD_REQUIRE_AUTH=true` en Railway sin redeploy de código.*

### Ejemplo: recomendación

```bash
curl -X POST https://el-monstruo-mvp.up.railway.app/v1/catastro/recommend \
  -H "X-API-Key: $MONSTRUO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "use_case": "razonamiento legal LATAM con citas verificables",
    "dominio": "llm_frontier",
    "top_n": 3
  }'
```

Respuesta esperada (ejemplo):

```json
{
  "modelos": [
    {
      "id": "claude-opus-4.7",
      "nombre": "Claude Opus 4.7",
      "trono_global": 88.5,
      "trono_low": 82.0,
      "trono_high": 95.0,
      "rank_dominio": 1,
      "macroarea": "inteligencia",
      "dominio": "llm_frontier"
    },
    ...
  ],
  "dominio_consultado": "llm_frontier",
  "queried_at": "2026-05-04T22:31:00Z",
  "cache_hit": false,
  "degraded": false
}
```

### Vía MCP (clientes Claude Desktop, Cursor, etc.)

El Catastro expone 4 tools en el sub-servidor FastMCP montado en `/mcp`:

| Tool MCP | Equivalente REST |
|---|---|
| `catastro_recommend` | `POST /v1/catastro/recommend` |
| `catastro_get_modelo` | `GET /v1/catastro/modelos/{id}` |
| `catastro_list_dominios` | `GET /v1/catastro/dominios` |
| `catastro_status` | `GET /v1/catastro/status` |

---

## Cómo leer el Dashboard

El dashboard HTML está en `https://el-monstruo-mvp.up.railway.app/v1/catastro/dashboard/` y tiene 3 paneles:

### Panel 1 · Resumen (`/summary`)

| Campo | Significado | Acción si rojo |
|---|---|---|
| `trust_level` | `healthy` / `degraded` / `down` | Verificar `degraded_reason`, revisar logs Railway |
| `modelos_total` / `production` | Total y los que están listos para recomendar | Si `production=0`: pipeline nunca corrió o todo está en preview |
| `dominios_count` | Cuántos dominios tienen al menos 1 modelo | Si baja súbitamente: probable rollback de migration |
| `last_run_at` | Timestamp del último cron exitoso | Si > 36h: cron muerto, revisar Railway scheduler |
| `drift_detected` | Eventos `prioridad in ('alta','critica')` últimos 7d | Si > 5: ingesta inestable, contactar Hilo Manus Catastro |
| `cache_entries` | Snapshot del LRU (no es indicador de salud) | — |

### Panel 2 · Timeline (`/timeline?days=14`)

Gráfica diaria de:
- **runs**: cuántas veces corrió el pipeline ese día (esperado: 1/día con cron diario).
- **eventos**: total de eventos del Catastro (descubrimientos + validaciones + drift).
- **avg_failure_rate**: tasa promedio de fallos en persistencia ese día (ideal: 0).

> Lectura sana: línea de runs estable en 1, eventos entre 5-50, `avg_failure_rate` siempre `null` o `0`.

### Panel 3 · Curators (`/curators`)

Trust score por curador (los 6 LLMs sabios). `trust_delta_7d` indica si subió o bajó:

- **trust_score > 0.85**: curador confiable, su voto pesa.
- **trust_score 0.70-0.85**: aceptable, monitorear.
- **trust_score < 0.70**: candidato a revisión manual; puede tener algoritmo de validación obsoleto o el modelo backend cambió.

`invocations_7d` muestra el uso real. Si un curador tiene `invocations_7d=0` por más de 14 días, considerar desactivarlo.

---

## Interpretación del Trono Score

Trono Score combina 5 métricas con z-scores **intra-dominio**:

```
Para cada modelo m en dominio d:
  z_X = (m.X - mean_d.X) / std_d.X    para X en {Q, CE, S, R, BF}

  trono_global = round(50 + 10 * (0.40·z_Q + 0.25·z_CE + 0.15·z_S + 0.10·z_R + 0.10·z_BF), 2)
  clamp [0, 100]
```

| Rango | Lectura |
|---|---|
| **trono_global > 70** | Top tier del dominio (≥ 2σ sobre la media) |
| **trono_global 55-70** | Sobre la media (≥ 0.5σ encima) |
| **trono_global 45-55** | Promedio del dominio (zona neutral) |
| **trono_global 30-45** | Bajo la media (sub-óptimo) |
| **trono_global < 30** | Significativamente inferior |
| **trono_global = 50.0 exacto** | Solo 1 modelo en dominio (modo `neutral`, banda ancha) |

**Bandas de confianza**:
- `trono_low` y `trono_high` reflejan la incertidumbre. Cuanto más estrecha la banda, más confiable la posición relativa.
- Banda ancha (>20 puntos) → pocos curadores votaron, o el modelo es nuevo, o las métricas son volátiles.

---

## Cómo interpretar Trust Deltas

Cada vez que el quórum vota un cambio en un modelo, los curadores que **acertaron con la mayoría** suben su `trust_score`, y los que **disintieron** lo pierden:

| `trust_delta_7d` | Lectura |
|---|---|
| **> +0.05** | Curador en racha, votos consistentes con consenso |
| **+0.01 a +0.05** | Sano, ligero refuerzo |
| **-0.01 a +0.01** | Estable |
| **-0.01 a -0.05** | Curador empezando a disentir, monitorear |
| **< -0.05** | **Atención**: drift del curador, posible cambio de comportamiento del modelo backend |

---

## Estados degraded vs failed

El Catastro nunca crashea. Si algo falla, **degrada gracefulmente**:

| `degraded_reason` | Causa | Severidad | Acción |
|---|---|---|---|
| `no_db_factory_configured` | Faltan `SUPABASE_URL` o `SUPABASE_SERVICE_ROLE_KEY` | **Alta** | Configurar envs en Railway |
| `supabase_down` | Supabase no responde o RLS bloquea | **Alta** | Verificar status Supabase |
| `no_runs_yet` | Tablas existen pero pipeline nunca corrió | Media | Hilo Ejecutor debe correr `scripts/run_first_catastro_pipeline.py` |
| `cache_miss_only` | Cache vacío, próxima query lo llena | Baja | Esperar 1 query (auto-resuelve) |

---

## Cron diario

El pipeline corre **automáticamente** una vez por día (configurable en Railway). Cada run:

1. Ingiere de las 3 fuentes externas (AA + OR + HF).
2. Detecta cambios y los pasa al quórum (6 LLMs).
3. Persiste vía RPC atómica (`catastro_apply_quorum_outcome`).
4. Recalcula Trono por dominio (`catastro_recompute_trono_all`).
5. Invalida cache LRU.
6. Emite eventos para auditoría.

Si la `failure_rate_observed` del run > `CATASTRO_FAILURE_RATE_THRESHOLD` (default 10%), se loguea `WARNING` y se incrementa `drift_detected`. No se aborta el run; los modelos exitosos quedan persistidos.

---

## Troubleshooting rápido

| Síntoma | Diagnóstico | Solución |
|---|---|---|
| Dashboard muestra `degraded=true` permanente | Variables de entorno faltantes | Configurar `SUPABASE_*` y `MONSTRUO_API_KEY` en Railway |
| `recommend` retorna lista vacía | Vista `catastro_trono_view` vacía o pipeline nunca corrió | Hilo Ejecutor: correr migrations 016+018+019 + primer pipeline |
| `recommend` siempre cache_hit=false | Cache LRU desactivado o TTL=0 | Verificar `CATASTRO_CACHE_TTL_SECONDS` (default 60) |
| Timeline solo tiene 1 punto con datos | Cron diario no se está ejecutando | Verificar Railway cron schedule + logs |
| Trust scores idénticos entre todos los curadores | Quórum nunca corrió (todos los modelos llegan ya validados) | Estado normal en MVP — Trust evoluciona con el tiempo |
| Latencia alta (>2s) en `recommend` | Cache miss + DB lenta | Aumentar TTL cache; verificar índices Supabase |

---

## Variables de entorno que importan

| Variable | Default | Función |
|---|---|---|
| `SUPABASE_URL` | — | URL del proyecto Supabase |
| `SUPABASE_SERVICE_ROLE_KEY` | — | Service role para RLS bypass |
| `MONSTRUO_API_KEY` | — | Bearer key para auth REST/MCP |
| `ARTIFICIAL_ANALYSIS_API_KEY` | — | Fuente primaria; si falta → modo degraded |
| `OPENROUTER_API_KEY` | (opcional) | Fuente secundaria |
| `HF_TOKEN` | (opcional) | Fuente terciaria |
| `CATASTRO_CACHE_TTL_SECONDS` | `60` | TTL del cache LRU |
| `CATASTRO_DRY_RUN` | `false` | Si `true`, pipeline no toca DB |
| `CATASTRO_SKIP_PERSIST` | `false` | Si `true`, calcula Trono pero no persiste |
| `CATASTRO_DASHBOARD_REQUIRE_AUTH` | `false` | Si `true`, dashboard pide X-API-Key |
| `CATASTRO_FAILURE_RATE_THRESHOLD` | `0.10` | Threshold para alertar drift en cron |

---

## Quién hace qué

| Rol | Responsabilidad | Hilo |
|---|---|---|
| Diseño + código + tests | Manus Catastro | Hilo B |
| Ejecutar migrations + cron real | Manus Ejecutor | Hilo A |
| Audit técnico | Cowork (Claude) | — |
| Decisiones de producto | Alfredo | — |
| Operación 24/7 | El Monstruo (auto) | — |

Si algo falla y no sabes a quién contactar: **escribe al bridge** (`bridge/manus_to_cowork.md` o `bridge/cowork_to_manus.md`) o, si urgente, escala a Alfredo.

---

## Referencias técnicas

- Código: `kernel/catastro/{schema,sources,quorum,pipeline,persistence,trono,recommendation,catastro_routes,mcp_tools,dashboard,cron}.py`
- Migrations: `scripts/01[6-9]_sprint86_*.sql`
- Tests: `tests/test_sprint86_{schema,bloque2-7}.py` (223 PASS + 4 skipped)
- Smoke E2E: `scripts/_smoke_{catastro_mcp,trono,catastro_first_run,dashboard}_sprint86.py`
- Doctrina sprint: `bridge/sprint86_preinvestigation/` y `bridge/manus_to_cowork.md`
- Reportes de cierre: secciones B3-B7 al final de `bridge/manus_to_cowork.md`

---

*Esta guía vive en el bridge para que Alfredo y Cowork la consulten sin entrar al código. Si algo cambia (nuevo endpoint, nuevo dominio, nueva variable), actualizar acá primero.*
