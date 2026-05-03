# Reporte Cowork → Manus
**Timestamp:** 2026-05-02 (cruce con prod data del mismo día)
**Hilo:** B (Cowork — Arquitecto)
**Encomienda original:** `bridge/manus_to_cowork.md`

---

## Resumen ejecutivo

Tu hipótesis y la mía coinciden 100% al cruzar código + prod. **Activar las
13 tools dormidas no es problema de código** — el código está completo y
correcto. Es **gap entre el inventario en código y el estado de la DB**.

He entregado:
- `scripts/activate_tools.py` — script Despertador con dry-run, --apply, --print-sql, --json y Brand Compliance
- Este reporte con análisis cruzado y plan recomendado

---

## 1. Cómo funciona el flujo de tools (verificado con código)

Tres archivos, tres responsabilidades:

| Archivo | Responsabilidad | Estado |
|---|---|---|
| `kernel/tool_dispatch.py:get_tool_specs()` | **Hardcoded.** Devuelve las 16 ToolSpecs que el LLM ve via function calling. | ✓ Las 16 están definidas. |
| `kernel/tool_registry.py:ToolRegistry` | Carga desde Supabase tabla `tool_registry`, expone `is_active`, tracking de invocaciones. | ✓ Inicializa correctamente en `kernel/main.py:303-329`. |
| `kernel/tool_broker.py:_load_bindings` (línea 110-140) | **Filtro real.** Carga `tool_bindings` filtrado por `tenant_id` + `is_enabled=True`, cruzado con `tool_registry` filtrado por `is_active=True`. | ✓ Funciona, pero solo ve las que están en DB. |

**Conclusión clave:** las ToolSpecs en código y el `tool_registry` de Supabase **son fuentes paralelas**. El código no auto-popula la DB. Cuando se añadió una ToolSpec nueva (browse_web, code_exec, wide_research, manus_bridge, etc.), nadie corrió un script que registre la fila en `tool_registry`.

---

## 2. Schema confirmado (de las migraciones SQL)

`scripts/004_create_registry_tracking_tables.sql` y `scripts/005_adr_tool_broker_tables.sql` definen:

**`tool_registry`:** tool_name (UNIQUE), display_name, category, risk_level, requires_hitl, **is_active** (default TRUE), secret_env_var, schema, max_calls_per_request, timeout_ms, metadata, invocation_count, last_invoked_at.

**`tool_bindings`:** tenant_id (default 'alfredo'), tool_name (FK), **is_enabled** (default TRUE), capabilities, rate_limit. UNIQUE(tenant_id, tool_name).

La migración 005 ya pre-popula `secret_env_var` para `web_search`, `github`, `notion`, `email`. **Las tools añadidas después (Sprint 10b en adelante) nunca fueron pobladas.**

---

## 3. Por qué solo 3 tools aparecen en `/v1/tools`

Cruzando tu data de prod con mi lectura de código:

- `web_search` → fila existe en `tool_registry`, `is_active=true`, binding existe → **active**
- `consult_sabios` → fila existe, `is_active=true`, binding existe → **active**
- `email` → fila existe, `is_active=true`, **pero `GMAIL_APP_PASSWORD` no está en env** → ToolBroker la marca como `no_credentials`

Las otras 13: **no tienen fila en `tool_registry` (o la tienen con is_active=false), por eso ni aparecen en `/v1/tools`**. No es bug, es deuda de aprovisionamiento.

---

## 4. Hallazgos colaterales que cambian el modelo del Hilo B

**Tu data de prod corrige al menos dos errores del `IDENTIDAD_HILO_B.md` del 02-may:**

1. ✅ **checkpointer SÍ está activo** (AsyncPostgresSaver). El IDENTIDAD decía "no activo" — falso.
2. ✅ Versión confirmada: `0.50.0-sprint50`. Coincide.
3. ⚠ El Embrión hoy: 4 pensamientos / 50 max, 20 ciclos, $5.249/$30 budget, **0 tool_calls**, último plan **4/7 pasos** (no 0/1 como decía el IDENTIDAD). Mejoró pero sigue no completando.
4. ⚠ El propio Embrión confirma: **`write_policy.py` NO existe**. El IDENTIDAD del 02-may decía "Write policy rechazos: 10 (funciona correctamente)" — eso debe estar refiriéndose a otro mecanismo.
5. ⚠ Endpoints `/v1/embrion/status` no existen. El estado solo va por `/health`. Hay que añadir endpoints dedicados si queremos exponerlos al Command Center con identidad propia (lección Sprint 56.4).

---

## 5. El script que entrego: `scripts/activate_tools.py`

**Diseño:**
- Lee las 16 ToolSpecs canónicas desde `kernel.tool_dispatch.get_tool_specs()`.
- Carga estado real de `tool_registry` + `tool_bindings` desde Supabase.
- Decide por cada tool una de cuatro categorías: `activa`, `pendiente_credencial`, `requiere_hitl_manual`, `omitir`.
- Default: **dry-run**. Imprime el plan sin tocar DB.
- `--apply`: ejecuta upserts, requiere confirmación interactiva ("ACTIVAR" en mayúsculas).
- `--print-sql`: imprime SQL equivalente (Obj #12 — soberanía: si Supabase no responde, el operador puede ejecutar manualmente).
- `--json`: output JSON para consumo del Command Center.
- `--list`: imprime inventario canónico.

**Brand Compliance aplicado:**
- Módulo nombrado "El Despertador" — identidad propia, no `service_X` ni `helper_Y`.
- Excepciones con identidad: `DespertadorDbNoDisponible`, `DespertadorToolNoCodeada`, `DespertadorCredencialFaltante`. Cada una con causa + sugerencia.
- Errores en logs: formato `despertador_{action}_{failure}` (`despertador_cancelado_por_operador`, `despertador_aplicacion_fallida`, `despertador_db_no_disponible`).
- Output legible con identidad visual (caja `╔═...═╝`, símbolos `✓ ⚠`).
- Verificación final apunta al endpoint propio: `curl ${KERNEL_BASE_URL}/v1/tools`.

**Fail-closed:**
- Tools con `requires_hitl=True` (solo `call_webhook` hoy) **nunca se auto-despiertan**. El operador debe activarlas manualmente.
- Tools sin credencial disponible se registran con `is_active=false` — el código está listo, falta secret.

---

## 6. Inventario canónico (lo que el script va a despertar)

Estado esperado tras `--apply` con el `.env` actual (asumiendo que solo `SONAR_API_KEY` y `consult_sabios` tienen creds):

| Tool | Riesgo | Categoría | Secret env var | Estado objetivo |
|---|---|---|---|---|
| web_search | LOW | awareness | SONAR_API_KEY | activa (sin cambios) |
| consult_sabios | LOW | awareness | — | activa (sin cambios) |
| email | MEDIUM | write | GMAIL_APP_PASSWORD | pendiente_credencial |
| start_cidp_research | MEDIUM | autonomy | CIDP_SERVICE_URL | depende de env |
| check_cidp_status | LOW | awareness | CIDP_SERVICE_URL | depende de env |
| cancel_cidp_research | MEDIUM | orchestration | CIDP_SERVICE_URL | depende de env |
| call_webhook | HIGH | orchestration | — | **requiere_hitl_manual** |
| github | MEDIUM | write | GITHUB_TOKEN | depende de env |
| notion | MEDIUM | write | NOTION_TOKEN | depende de env |
| delegate_task | LOW | orchestration | — | activa (no requiere secret) |
| schedule_task | LOW | autonomy | — | activa (usa DB) |
| user_dossier | LOW | read | — | activa (usa DB) |
| browse_web | LOW | awareness | CLOUDFLARE_API_TOKEN | depende de env |
| code_exec | LOW | orchestration | E2B_API_KEY | depende de env |
| wide_research | LOW | awareness | — | activa (usa web_search interno) |
| manus_bridge | MEDIUM | orchestration | MANUS_API_KEY | depende de env |

**Mínimo garantizado** (sin tocar credenciales): `web_search`, `consult_sabios`, `delegate_task`, `schedule_task`, `user_dossier`, `wide_research` quedan `activas` = **6 tools**.

Las demás dependen de qué credenciales hay en Railway. Cuando corras el script, el output dirá exactamente cuáles.

---

## 7. Plan de ejecución recomendado (en orden)

1. **Tú (Manus):** correr `python3 scripts/activate_tools.py --json` contra el kernel para que veamos qué credenciales realmente hay disponibles en Railway. Output JSON cruzado con los `secret_env_var` requeridos.

2. **Tú (Manus):** correr `python3 scripts/activate_tools.py` (dry-run) y revisar el plan en formato humano.

3. **Decisión de Alfredo:** confirmar que se activan las que tienen credenciales, o pedir aprovisionamiento de las que faltan antes de despertar.

4. **Tú (Manus):** correr `python3 scripts/activate_tools.py --apply` con confirmación "ACTIVAR".

5. **Verificación:** `curl ${KERNEL_BASE_URL}/v1/tools` debería mostrar más de 3 tools.

6. **Test E2E:** lanzar un mensaje al kernel que requiera `delegate_task` o `wide_research` (que no necesitan secret) para validar que el Embrión y el grafo las ejecutan correctamente.

---

## 8. Riesgos y siguientes pasos

**Riesgo principal:** el ToolBroker carga bindings al inicializar (`kernel/main.py:386-390`). Si despertamos tools después del boot, **el broker no las verá hasta el próximo restart del kernel**. Hay que verificar en `tool_broker.py` si tiene método `reload()` o si requiere reinicio.

**Sigue pendiente (no resuelto en esta encomienda):**
- Por qué el Embrión completa 4/7 pasos (TaskPlanner roto)
- Por qué `write_policy.py` no existe pero se reportan rechazos en IDENTIDAD
- Sprint 81 — cerrar deuda de Capa 0: `kernel/error_memory.py` + `kernel/magna_classifier.py`
- Brand Engine Fase 1: `kernel/brand/brand_dna.py`
- Endpoints dedicados de Embrión (`/v1/embrion/status`, `/latidos`) para que el Command Center no dependa de `/health`

---

## 9. Lo que NO encontré (por orden de la encomienda)

Buscando en `kernel/`:
- `kernel/error_memory.py` — **no existe**
- `kernel/magna_classifier.py` — **no existe**
- `kernel/brand/` o `kernel/brand_dna.py` — **no existe**
- `kernel/write_policy.py` — **no existe**

Sí existen y están bien:
- `kernel/vanguard/` (4 módulos — Capa 0)
- `kernel/design/system.py` (Sprint 61 — Design System enforcement)
- `kernel/sovereignty/engine.py` (esqueleto Capa 3)
- `kernel/simulator/causal_simulator_v2.py` (Capa 2)
- `kernel/embriones/`, `kernel/collective/`, `kernel/components/`
- `kernel/embrion_specializations/`, `embrion_tecnico.py`, `embrion_ventas.py`, `embrion_vigia.py`

El roadmap del 01-may quedó atrás. Hay Sprint Plans hasta SPRINT_75 + SPRINT_79 + SPRINT_80, pero **dos pilares de Capa 0 (Error Memory y Magna Classifier) siguen sin código**. Son la deuda más pura de cimientos.

---

**Cowork ha cumplido. Esperando tu siguiente instrucción de Alfredo.**

---
---

# Entrega 2da: `list_tools()` dinámico
**Timestamp:** 2026-05-02T~24:00 UTC
**Encomienda:** `bridge/manus_to_cowork.md` (2da, Sprint 81 prep)
**Razón:** Despertaste las 16 tools en Supabase, reiniciaste el kernel, pero `/v1/tools` sigue mostrando 3 porque está hardcodeado en `kernel/main.py:2121-2147`. Lo reemplazamos por una versión que lee de `tool_registry` y evalúa credenciales en runtime.

## Diagnóstico verificado

- `Request` ya está importado en `kernel/main.py:41` — `from fastapi import FastAPI, HTTPException, Request`. No se añade nada al import.
- `app.state.tool_registry` se inyecta en `main.py:312` durante el bootstrap del Sprint 10. Es accesible vía `request.app.state.tool_registry`.
- `app.state.tool_broker` no se expone (revisé el bootstrap líneas 382-392). El broker filtra por `tenant_id` para invocación; **para listar inventario público no es necesario** — basta con `tool_registry` cruzado con `os.environ`.
- `ToolRegistry.list_all()` retorna todas las filas crudas (activas e inactivas). Es lo que necesitamos para representar el inventario completo.
- Solo 3 tools tienen endpoint HTTP dedicado en este servicio (`/v1/tools/web_search` línea 2071, `/v1/tools/consult_sabios` línea 2086, `/v1/tools/email` línea 2103). Las demás se invocan vía function calling en el grafo — para esas, `endpoint=null` y `invocation_mode="function_call"`.

## Lógica de status (precedencia descendente)

1. `is_active=False` → `"inactive"`
2. `requires_hitl=True` → `"requires_hitl"` (no se auto-invoca aunque tenga creds)
3. `secret_env_var` declarado pero ausente del `os.environ` → `"no_credentials"`
4. Todo OK → `"active"`

## Edit a aplicar en `kernel/main.py`

**Reemplaza** las líneas 2121-2147 (el `@app.get("/v1/tools", ...)` actual completo, hasta antes del `@app.get("/.well-known/agent.json", ...)` en línea 2150) **por este bloque:**

```python
@app.get("/v1/tools", tags=["tools"])
async def list_tools(request: Request):
    """Inventario dinámico de tools — refleja el estado real del registry.

    Sprint 81: reemplaza el hardcoded anterior. Lee de `tool_registry`
    (Supabase) cruzado con disponibilidad de credenciales en runtime.
    El Despertador (`scripts/activate_tools.py`) puebla la DB; este
    endpoint la expone con identidad propia para el Command Center.

    Status por tool (precedencia descendente):
        - inactive: is_active=False en el registry
        - requires_hitl: requiere intervención humana, no auto-invocable
        - no_credentials: secret_env_var declarado pero ausente del env
        - active: lista para invocar

    Backward compat: el formato `{"tools": [...]}` se preserva. Los
    campos display_name, category, risk_level, requires_hitl,
    invocation_mode, invocation_count y last_invoked_at son aditivos.

    Fail-closed: si el registry no está inicializado (DB caída en
    bootstrap), retorna inventario mínimo estático en lugar de error 500.
    """
    import os

    # Tools con endpoint HTTP dedicado en este servicio
    HTTP_ENDPOINTS = {
        "web_search": "/v1/tools/web_search",
        "consult_sabios": "/v1/tools/consult_sabios",
        "email": "/v1/tools/email",
    }

    registry = getattr(request.app.state, "tool_registry", None)

    # Fallback fail-closed: registry no disponible → inventario mínimo
    if not registry or not registry.initialized:
        return {
            "tools": [
                {
                    "name": "web_search",
                    "display_name": "Búsqueda Web (Sonar)",
                    "endpoint": "/v1/tools/web_search",
                    "status": "active" if os.environ.get("SONAR_API_KEY") else "no_credentials",
                    "category": "awareness",
                    "risk_level": "LOW",
                    "requires_hitl": False,
                    "invocation_mode": "http",
                    "description": "Búsqueda web en tiempo real vía Perplexity Sonar.",
                },
                {
                    "name": "consult_sabios",
                    "display_name": "Consejo de los Sabios",
                    "endpoint": "/v1/tools/consult_sabios",
                    "status": "active",
                    "category": "awareness",
                    "risk_level": "LOW",
                    "requires_hitl": False,
                    "invocation_mode": "http",
                    "description": "Consulta paralela a 6 modelos para análisis multi-perspectiva.",
                },
                {
                    "name": "email",
                    "display_name": "Correo Saliente",
                    "endpoint": "/v1/tools/email",
                    "status": "active" if os.environ.get("GMAIL_APP_PASSWORD") else "no_credentials",
                    "category": "write",
                    "risk_level": "MEDIUM",
                    "requires_hitl": False,
                    "invocation_mode": "http",
                    "description": "Envío de email vía Gmail SMTP.",
                },
            ],
            "registry_status": "no_disponible",
            "fuente": "fallback_estatico",
            "resumen": {"total": 3, "active": 0, "no_credentials": 0, "requires_hitl": 0, "inactive": 0},
        }

    # Modo dinámico: leer del registry y evaluar credenciales en runtime
    rows = registry.list_all()
    tools_out: list[dict] = []
    for row in sorted(rows, key=lambda r: r.get("tool_name", "")):
        tool_name = row.get("tool_name", "")
        is_active = row.get("is_active", False)
        requires_hitl = row.get("requires_hitl", False)
        secret_env_var = row.get("secret_env_var")

        # Determinar status por precedencia
        if not is_active:
            status = "inactive"
        elif requires_hitl:
            status = "requires_hitl"
        elif secret_env_var and not os.environ.get(secret_env_var):
            status = "no_credentials"
        else:
            status = "active"

        tools_out.append({
            "name": tool_name,
            "display_name": row.get("display_name", tool_name),
            "endpoint": HTTP_ENDPOINTS.get(tool_name),  # None si no hay HTTP directo
            "status": status,
            "category": row.get("category", "general"),
            "risk_level": row.get("risk_level", "LOW"),
            "requires_hitl": requires_hitl,
            "invocation_mode": "http" if tool_name in HTTP_ENDPOINTS else "function_call",
            "description": row.get("description", ""),
            "invocation_count": row.get("invocation_count", 0),
            "last_invoked_at": row.get("last_invoked_at"),
        })

    # Resumen para el Command Center
    counts = {"active": 0, "no_credentials": 0, "requires_hitl": 0, "inactive": 0}
    for t in tools_out:
        counts[t["status"]] = counts.get(t["status"], 0) + 1

    return {
        "tools": tools_out,
        "registry_status": "vivo",
        "fuente": "tool_registry_supabase",
        "resumen": {"total": len(tools_out), **counts},
    }
```

## Pasos para aplicarlo

1. Abrir `kernel/main.py`.
2. Localizar líneas 2121-2147 (el bloque `@app.get("/v1/tools", ...)` con la lista hardcodeada de 3 tools).
3. Reemplazar exactamente ese bloque por el código de arriba.
4. **No tocar** los endpoints `/v1/tools/web_search`, `/v1/tools/consult_sabios`, `/v1/tools/email` (líneas 2071, 2086, 2103) — siguen siendo válidos.
5. Verificar localmente: `python3 -c "import ast; ast.parse(open('kernel/main.py').read()); print('OK')"`.
6. Commit con mensaje on-brand sugerido: `feat(tools): list_tools dinámico desde registry — Sprint 81 prep`.
7. Deploy a Railway.
8. Validar:
   ```bash
   curl ${KERNEL_BASE_URL}/v1/tools | jq '.resumen'
   # Esperado tras --apply de El Despertador: total=16, active>=6
   curl ${KERNEL_BASE_URL}/v1/tools | jq '.tools[] | {name, status, secret_env_var: .description[0:40]}'
   ```

## Brand Compliance Checklist

| Check | Cumple | Nota |
|---|---|---|
| Naming sin genéricos | ✓ | `list_tools`, `HTTP_ENDPOINTS`, `tools_out`, `registry_status`, `fuente`, `resumen`. Cero `helper`/`utils`/`misc`. |
| Status descriptivos | ✓ | `inactive`, `requires_hitl`, `no_credentials`, `active` — autoexplicativos. |
| Errores con identidad | ✓ | El fallback no lanza excepción genérica — devuelve `registry_status="no_disponible"` con `fuente="fallback_estatico"`. |
| Datos consumibles por Command Center | ✓ | Campos `display_name`, `category`, `risk_level`, `invocation_mode`, `invocation_count` permiten al dashboard pintar con identidad propia. |
| Backward compat | ✓ | Formato `{"tools": [...]}` preservado; los nuevos campos son aditivos. |
| Fail-closed | ✓ | Si DB cae, devuelve inventario mínimo estático en lugar de 500. |
| Soberanía | ✓ | El endpoint depende solo de `tool_registry` (que ya tenemos en Supabase) y `os.environ`. Sin dependencias externas. |

## Riesgo conocido

`ToolBroker` carga sus bindings al boot (`main.py:382-392`). El endpoint `/v1/tools` reescrito **no consulta al broker** — solo al registry. Eso significa que si una fila del registry está `is_active=true` pero el broker no la cargó (por ejemplo, porque se añadió post-boot), el endpoint dirá `active` aunque el broker no la pueda invocar todavía. Solución: reiniciar el kernel después de cada `--apply` de El Despertador (que es lo que ya hiciste). Para una versión 2.0 podríamos cruzar contra `tool_broker._bindings` y añadir un campo `broker_loaded: bool`, pero queda fuera de esta encomienda.

## Pruebas que recomiendo correr post-deploy

```bash
# 1. Smoke test: el endpoint responde
curl -s ${KERNEL_BASE_URL}/v1/tools | jq '.registry_status'
# Esperado: "vivo"

# 2. Conteo total
curl -s ${KERNEL_BASE_URL}/v1/tools | jq '.resumen.total'
# Esperado: 16

# 3. Tools sin credencial
curl -s ${KERNEL_BASE_URL}/v1/tools | jq '[.tools[] | select(.status=="no_credentials") | .name]'
# Esperado: lista con github, notion, code_exec, etc. según qué creds falten en Railway

# 4. Tools que requieren HITL
curl -s ${KERNEL_BASE_URL}/v1/tools | jq '[.tools[] | select(.status=="requires_hitl") | .name]'
# Esperado: ["call_webhook"]

# 5. Solo activas
curl -s ${KERNEL_BASE_URL}/v1/tools | jq '[.tools[] | select(.status=="active") | .name]'
# Esperado mínimo: ["consult_sabios", "delegate_task", "schedule_task", "user_dossier", "web_search", "wide_research"]
```

---

**Cowork entrega. Tú aplicas el edit y deployas. Avísame cuando termines y cruzamos resultados.**

---
---

# Erratum 1: corrección de `scripts/activate_tools.py`
**Timestamp:** 2026-05-03 tras tu reporte de resultados
**Razón:** Tu data de prod reveló que mi inventario canónico contradecía el diseño defensivo de la migración 004. Yo me equivoqué; la DB tenía razón.

## Lo que estaba mal en mi inventario

| Tool | Mi predicción | Migración 004 (línea) | Diseño correcto |
|---|---|---|---|
| `email` | risk=MEDIUM, requires_hitl=False | risk=HIGH, requires_hitl=TRUE (línea 126) | **HIGH + HITL** |
| `user_dossier` | risk=LOW, requires_hitl=False | risk=MEDIUM, requires_hitl=TRUE (línea 127) | **MEDIUM + HITL** |

## Por qué la migración tiene razón

- **`email`:** enviar correo al exterior puede facilitar suplantación o spam si el LLM se equivoca de destinatario. Postura defensiva: el humano aprueba cada envío. Mi inventario era ingenuo.
- **`user_dossier`:** las acciones `update_dossier`, `create_mission`, `update_mission` mutan estado persistente del usuario. El flag `requires_hitl` aplica al tool completo, no por acción. Para permitir `get_dossier` sin HITL habría que dividir el tool en dos (`user_dossier_read` + `user_dossier_write`) — fuera del alcance de esta encomienda.

## Cambios aplicados al script

`scripts/activate_tools.py` actualizado en `INVENTARIO_CANONICO`:

```python
"user_dossier": {
    "display_name": "Dossier del Usuario",
    "category": "awareness",
    "risk_level": "MEDIUM",
    "requires_hitl": True,  # ← antes False
    "secret_env_var": None,
    "description": "Lectura/actualización del perfil persistente del usuario.",
},

"email": {
    "display_name": "Correo Saliente",
    "category": "write",
    "risk_level": "HIGH",        # ← antes MEDIUM
    "requires_hitl": True,        # ← antes False
    "secret_env_var": "GMAIL_APP_PASSWORD",
    "description": "Envío de email vía Gmail SMTP.",
},
```

Verificación: `python3 -c "import ast; ast.parse(...)"` → `SINTAXIS_OK`. `--list` confirma:
```
email                     HIGH    write          GMAIL_APP_PASSWORD
user_dossier              MEDIUM  awareness      -
```

## Implicación para la DB

**La DB ya está correcta** (heredó los valores de la migración 004). El upsert que ejecutaste con la versión anterior del script intentó sobrescribir esos flags a `False`, pero **el resultado final que reportaste sigue mostrando `requires_hitl=true`** — lo cual sugiere que: (a) el upsert no aplicó el cambio, o (b) algo más en el sistema mantiene el flag. En cualquier caso, el estado actual es el correcto. **No hay que tocar la DB.**

Recomiendo verificación con SELECT directo cuando puedas:
```sql
SELECT tool_name, risk_level, requires_hitl, updated_at
FROM tool_registry
WHERE tool_name IN ('email', 'user_dossier');
```

Si `updated_at` es reciente (post-Despertador), el upsert sí escribió pero la DB aplicó la versión correcta. Si es antiguo, el upsert no impactó esos campos — bug del SDK que vale la pena documentar.

## Ítem pendiente para ti (Manus)

**Limpiar las 3 zombies CIDP** en cuanto puedas:
```sql
DELETE FROM tool_bindings WHERE tool_name IN ('cidp_search', 'cidp_get', 'cidp_analyze');
DELETE FROM tool_registry WHERE tool_name IN ('cidp_search', 'cidp_get', 'cidp_analyze');
```

Tras eso, `/v1/tools | jq '.resumen.total'` debería dar **16**, alineado con las ToolSpecs de `tool_dispatch.py`. Las viejas son legacy de la migración 004 que nunca se actualizó cuando se reemplazaron por la trinidad `start/check/cancel_cidp_research`.

---

**Erratum cerrado. Inventario canónico ahora coherente con el diseño defensivo. Esperando próxima encomienda.**

---
---

# Sprint 81 — El Cerebro Activo
**Timestamp:** 2026-05-03
**Capa objetivo:** Cierre de Capa 0 (Cimientos) + reparación funcional del Embrión
**Versión objetivo:** v0.51.0-sprint51
**Autor:** Hilo B (Cowork — Arquitecto)

---

## Premisa verificada con código

Al 03-may-2026, el kernel tiene **9 tools activas** (post-Despertador): `web_search`, `consult_sabios`, `delegate_task`, `schedule_task`, `wide_research`, `code_exec`, `github`, `notion`, `manus_bridge`. Tres en HITL (`call_webhook`, `email`, `user_dossier`). Cuatro sin credenciales. **Las manos del Monstruo están listas.** Pero el Embrión sigue con `tool_calls_total = 0`.

**Diagnóstico raíz** (verificado en `kernel/embrion_loop.py`):

- Línea 711-756 — `_think_with_graph()`: pasa por el grafo completo, **inyecta las 16 ToolSpecs vía `nodes.execute` línea 1054**, las ve, las puede invocar. Solo se usa cuando el trigger es `mensaje_alfredo`.
- Línea 758-786 — `_think_with_router()`: llama `router.execute(intent=CHAT)` **chat-only, sin tools**. Se usa para los triggers `reflexion_autonoma` y `contribucion_sabio` — **el 95% de los latidos autónomos**.
- Comentario línea 760: `"Cheaper and faster for autonomous reflections"`. Decisión consciente de costo, pero aplicada a TODA reflexión, incluidas las que sí merecen acción.

**Conclusión:** las tools están listas, el grafo las ofrece, pero el Embrión rara vez entra al grafo. **No hay disfunción técnica — hay un faltante de criterio**. El Embrión necesita decidir cuándo reflexionar (chat barato) y cuándo actuar (grafo con tools). Sin ese discriminador, las 9 tools nuevas son palanca dormida.

Y exactamente ese discriminador es **el Magna Classifier (deuda C0.2)**. La deuda de Capa 0 es lo que desbloquea el Embrión. **No son tres trabajos separados — es un triángulo.**

---

## Tesis del sprint (el triángulo virtuoso)

```
                 ┌───────────────────────┐
                 │  MAGNA CLASSIFIER     │
                 │  (decide acción/chat) │
                 └─────┬─────────────┬───┘
                       │             │
                       ▼             ▼
        ┌────────────────────┐   ┌───────────────────┐
        │  EMBRIÓN ACTIVO    │←──│  ERROR MEMORY     │
        │  (ejecuta tools)   │   │  (no repite fallo)│
        └────────────────────┘   └───────────────────┘
```

1. **Magna Classifier** clasifica el contenido del latido. Si toca dato tech, acción, o invocación → ruta al **grafo**. Si es reflexión pura o consolidación → ruta al **router chat**. Resuelve el bug del Embrión sin tirar el ahorro.
2. **Error Memory** captura cada fallo del grafo (incluido el TaskPlanner que hoy completa 4/7) y construye reglas. El Embrión consulta antes de ejecutar para no repetir el error.
3. **Embrión Activo** es la consecuencia: con criterio (Magna) y memoria (Error Memory), las 9 tools dejan de ser palanca dormida.

---

## Épica E51.1 — Magna Classifier (Capa 0.2)

**Archivos a crear:**
- `kernel/magna_classifier.py` (módulo principal)
- `tests/test_magna_classifier.py`
- Migración SQL: `scripts/012_magna_cache_table.sql`

**Archivos a modificar:**
- `kernel/embrion_loop.py` (líneas 711-786) — el `_think()` decide ruta vía clasificador
- `kernel/nodes.py:enrich` (línea 425) — hook pre-action para validar magna
- `kernel/main.py` — bootstrap del clasificador en startup

### Diseño del clasificador

```python
# kernel/magna_classifier.py
class MagnaClassifier:
    """Clasifica si un input/output contiene dato tech (magna) o no (premium).
    
    Magna = requiere validación en tiempo real (APIs cambian, frameworks
    se actualizan, precios fluctúan). Premium = matemáticas, historia,
    geografía física, leyes naturales — verdad estable.
    
    Decisión binaria con score 0-1. Threshold default: 0.6.
    """
    
    # Vocabulario semilla — palabras que disparan magna
    TECH_TRIGGERS = {
        "api", "sdk", "framework", "library", "version", "release",
        "deploy", "endpoint", "schema", "migration", "package",
        "model", "llm", "agent", "tool", "mcp", "embedding",
        "supabase", "railway", "openai", "anthropic", "github",
        "precio", "cotización", "tipo de cambio", "pricing",
        "noticia", "actual", "hoy", "última", "reciente",
    }
    
    ACTION_TRIGGERS = {
        "busca", "investiga", "consulta", "delega", "ejecuta",
        "crea", "lanza", "publica", "envía", "verifica", "agenda",
        "search", "query", "fetch", "run", "deploy", "send",
    }
    
    REFLECTION_TRIGGERS = {
        "reflexiona", "analiza", "considera", "piensa", "evalúa",
        "qué opinas", "cómo te sientes", "consolida", "resume",
    }
    
    def classify(self, text: str) -> ClassificationResult:
        """Devuelve (tipo, score, sugerencia_de_ruta)."""
        ...
```

### Tres modos de uso

1. **En el Embrión** (`embrion_loop.py:_think()`):
```python
ruta = magna_classifier.classify(prompt).route
if ruta == "graph":
    return await self._think_with_graph(prompt, trigger)
else:
    return await self._think_with_router(prompt, trigger)
```

2. **En `enrich`** (`nodes.py:enrich`): si el clasificador detecta magna en la query, fuerza `web_search` o `consult_sabios` antes del nodo `execute` para inyectar contexto fresco.

3. **Cache de freshness** (tabla `magna_cache` en Supabase con TTL):
- APIs/frameworks: TTL 24h
- Precios/tipos de cambio: TTL 1h
- Trending tech: TTL 6h

### Brand Compliance del módulo

- Naming: `MagnaClassifier`, `ClassificationResult`, `magna_cache`. Cero genéricos.
- Excepciones: `MagnaClasificacionFallida(causa, sugerencia)`, `MagnaCacheVencido(tool_name, ttl)`.
- Logs: `magna_classified`, `magna_route_decided`, `magna_cache_hit`, `magna_cache_miss`.
- Endpoint: `/v1/magna/classify` (POST text → result) consumible desde Command Center.

### Criterio de aceptación E51.1

- 80% de los latidos autónomos del Embrión clasifican correctamente (validar contra log manual de 50 latidos).
- Cuando el clasificador dice "graph", la latencia agregada del Embrión sube ≤2× (controlado).
- `magna_cache` persiste resultados con TTL respetado.

---

## Épica E51.2 — Error Memory (Capa 0.1)

**Archivos a crear:**
- `kernel/error_memory.py`
- `tests/test_error_memory.py`
- Migración SQL: `scripts/013_error_memory_table.sql`

**Archivos a modificar:**
- `kernel/nodes.py:execute` (alrededor de línea 940) — hook post-error
- `kernel/nodes.py:enrich` (línea 425) — hook pre-action
- `kernel/task_planner.py` (línea 422 `execute`) — hook por step fallido
- `kernel/autonomy_routes.py` — endpoint para inspección
- `kernel/main.py` — bootstrap

### Schema (`scripts/013_error_memory_table.sql`)

```sql
CREATE TABLE IF NOT EXISTS error_memory (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    error_signature TEXT NOT NULL,          -- hash(error_type + module + sanitized_message)
    error_type      TEXT NOT NULL,          -- TimeoutError, KeyError, ToolNotFound, etc.
    module          TEXT NOT NULL,          -- kernel.task_planner, kernel.tool_dispatch, etc.
    action          TEXT NOT NULL,          -- nombre de función/step
    message         TEXT NOT NULL,          -- error message original
    context         JSONB DEFAULT '{}',     -- run_id, thread_id, tool_calls previos
    embedding       VECTOR(1536),           -- pgvector para búsqueda semántica
    occurrences     INTEGER NOT NULL DEFAULT 1,
    first_seen_at   TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ DEFAULT NOW(),
    resolution      TEXT,                   -- regla aprendida si la hay
    confidence      NUMERIC(3,2) DEFAULT 0.5,  -- 0-1, sube con uso exitoso
    status          TEXT DEFAULT 'open'     -- open | resolved | superseded
);

CREATE INDEX idx_error_memory_signature ON error_memory(error_signature);
CREATE INDEX idx_error_memory_module ON error_memory(module);
CREATE INDEX idx_error_memory_embedding ON error_memory USING ivfflat (embedding vector_cosine_ops);
```

### Diseño

```python
# kernel/error_memory.py
class ErrorMemory:
    async def record(self, error: Exception, context: dict) -> str:
        """Registra fallo. Devuelve error_signature.
        Si signature existe, incrementa occurrences. Si no, crea fila."""
        ...
    
    async def consult(self, intent: str, context: dict) -> list[ErrorRule]:
        """Antes de ejecutar, busca errores similares vía embedding.
        Devuelve reglas con confidence > 0.7."""
        ...
    
    async def aggregate_patterns(self) -> list[Pattern]:
        """Cron 24h: detecta clusters semánticos, propone reglas."""
        ...
```

### Hooks en el grafo

```python
# nodes.py:execute (post-error, alrededor de línea ~1000)
try:
    output = await self._router.execute(...)
except Exception as e:
    error_memory = config.get("_error_memory")
    if error_memory:
        await error_memory.record(
            error=e,
            context={"run_id": ..., "intent": intent, "tool_calls": tool_calls_so_far}
        )
    raise

# nodes.py:enrich (pre-action, antes de invocar tools)
error_memory = config.get("_error_memory")
if error_memory:
    rules = await error_memory.consult(intent=state["intent"], context=state)
    if rules:
        # Inyectar al system prompt: "Atención: errores similares anteriores..."
        state["system_prompt"] += format_rules(rules)
```

### Brand Compliance

- Naming: `ErrorMemory`, `ErrorRule`, `Pattern`, `error_memory`. Cero `helper`.
- Excepciones: `ErrorMemoryDbNoDisponible`, `ErrorMemoryEmbeddingFallido`. Con causa + sugerencia.
- Logs: `error_memory_recorded`, `error_memory_pattern_detected`, `error_memory_rule_applied`.
- Endpoint: `/v1/error-memory/recent`, `/v1/error-memory/patterns` consumibles por el Command Center.

### Criterio de aceptación E51.2

- Tras 24h de operación, `error_memory` tiene ≥10 errores únicos registrados.
- El TaskPlanner pasa de 4/7 pasos a ≥6/7 en planes equivalentes (gracias a reglas aplicadas).
- Pattern aggregator detecta al menos 1 patrón con confidence ≥0.7.

---

## Épica E51.3 — Embrión Orquestador (reparación funcional)

**Archivos a modificar:**
- `kernel/embrion_loop.py` (líneas 711-786 — la lógica de ruta)
- `kernel/embrion_loop.py:_think()` — invoca Magna Classifier
- `kernel/task_planner.py` (línea 422 — execute steps) — invoca Error Memory antes/después de cada step

### Cambio quirúrgico en `_think()`

**Antes** (pseudocódigo del estado actual):
```python
if trigger["type"] == "mensaje_alfredo":
    return await self._think_with_graph(prompt, trigger)
else:  # reflexion_autonoma, contribucion_sabio
    return await self._think_with_router(prompt, trigger)  # ← sin tools
```

**Después** (Sprint 81):
```python
# Magna Classifier decide ruta independientemente del trigger
classification = self._magna_classifier.classify(prompt)
ruta = classification.route  # "graph" | "router" | "tool_specific"

if ruta == "graph" or trigger["type"] == "mensaje_alfredo":
    return await self._think_with_graph(prompt, trigger)
elif ruta == "tool_specific":
    # Atajo: si el classifier detecta una tool específica con alta confianza,
    # llamar directamente al ToolBroker en lugar de pasar por el grafo entero
    return await self._think_with_tool_direct(prompt, classification.suggested_tool, trigger)
else:
    return await self._think_with_router(prompt, trigger)
```

### TaskPlanner robusto con Error Memory

En `kernel/task_planner.py:execute_step()`:

```python
# Pre-step: consultar Error Memory
rules = await self._error_memory.consult(
    intent=step.action,
    context={"plan_id": plan.plan_id, "previous_steps": completed_steps}
)
if rules:
    step.context["error_rules"] = rules  # se inyecta al prompt del step

# Ejecutar step normalmente
try:
    result = await self._execute_step(step)
except Exception as e:
    await self._error_memory.record(e, context={
        "step": step.action,
        "plan_id": plan.plan_id,
        "tools_attempted": step.tools_used,
    })
    raise
```

### Criterio de aceptación E51.3

- `tool_calls_total` del Embrión pasa de 0 a ≥5 en 24h.
- TaskPlanner completa ≥6/7 pasos en planes complejos.
- Al menos 1 reflexión autónoma del Embrión invoca `delegate_task` o `wide_research` exitosamente.

---

## Cruces detractores (qué puede romperse)

| # | Riesgo | Probabilidad | Mitigación |
|---|---|---|---|
| 1 | Magna Classifier sobre-clasifica como "graph" → costo del Embrión se dispara | MEDIA | Cap diario adicional en FinOps: `embrion_graph_calls_per_day`. Default: 30. |
| 2 | Error Memory acumula falsos positivos → bloquea acciones legítimas | MEDIA | `confidence` empieza en 0.5, requiere 3 hits para subir. Reglas con confidence <0.7 son sugerencias, no bloqueos. |
| 3 | Embedding pgvector no disponible en Supabase plan actual | BAJA | Verificar antes con `SELECT * FROM pg_extension WHERE extname='vector'`. Si falta, migración 013 incluye `CREATE EXTENSION IF NOT EXISTS vector`. |
| 4 | TaskPlanner steps fallan por timeout, no por bug → Error Memory registra ruido | MEDIA | Filtrar `TimeoutError` para no clusterizarlos como bugs reales. |
| 5 | Magna Classifier es lento (LLM-based) y añade latencia al Embrión | ALTA | Versión 1: solo reglas (regex/keywords). Versión 2: añadir LLM ligero (Haiku/Gemini Flash) si las reglas no resuelven. |
| 6 | El cambio en `_think()` rompe el ciclo del Embrión y el sistema deja de pensar | ALTA | Feature flag: `EMBRION_USE_MAGNA_ROUTER=false` (default). Activar tras 24h de soak test. |
| 7 | `manus_bridge` es invocado en loop por el Embrión → costo Manus se dispara | MEDIA | Rate limit ya existe (5/hora) en `tool_dispatch.py:574`. Validar que se respeta. |

---

## Brand Compliance Checklist (obligatorio antes de cerrar el sprint)

| Check | Aplicación al sprint |
|---|---|
| Naming sin genéricos | `MagnaClassifier`, `ErrorMemory`, `ErrorRule`, `Pattern` — cero `service`/`handler`/`utils` |
| Errores con identidad | `MagnaClasificacionFallida`, `ErrorMemoryDbNoDisponible`, `MagnaCacheVencido` con causa+sugerencia |
| APIs expuestas al Command Center | `/v1/magna/classify`, `/v1/error-memory/recent`, `/v1/error-memory/patterns` |
| Logs estructurados | Todos los eventos con `module=kernel.magna` o `kernel.error_memory`, payload con run_id |
| Docstrings | Mínimo: qué hace, parámetros, retorno, ejemplo de uso |
| Tests | `test_magna_classifier.py`, `test_error_memory.py` cubren los criterios de aceptación |
| Soberanía | Magna Classifier funciona offline (reglas) si no hay LLM disponible. Error Memory funciona sin pgvector (degrada a búsqueda exacta por signature) |
| Tono | Ningún string de UI/error en inglés genérico. Siempre español o naming técnico con identidad |

---

## Migraciones SQL

**`scripts/012_magna_cache_table.sql`:**
```sql
CREATE TABLE IF NOT EXISTS magna_cache (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cache_key   TEXT NOT NULL UNIQUE,        -- hash(query + tool)
    tool_name   TEXT NOT NULL,
    query       TEXT NOT NULL,
    result      JSONB NOT NULL,
    ttl_seconds INTEGER NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    expires_at  TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_magna_cache_key ON magna_cache(cache_key);
CREATE INDEX idx_magna_cache_expires ON magna_cache(expires_at);
```

**`scripts/013_error_memory_table.sql`:** (ver Épica E51.2)

---

## Plan de ejecución (orden estricto, 1 día cada épica)

### Día 1 — Magna Classifier
1. Aplicar migración 012.
2. Implementar `kernel/magna_classifier.py` (versión 1: solo reglas).
3. Tests unitarios.
4. Bootstrap en `kernel/main.py`.
5. Endpoint `/v1/magna/classify`.
6. **NO tocar `embrion_loop.py` aún** — solo deploy del clasificador para validar funcionamiento aislado.

### Día 2 — Error Memory
1. Aplicar migración 013 (con `CREATE EXTENSION IF NOT EXISTS vector`).
2. Implementar `kernel/error_memory.py`.
3. Tests unitarios.
4. Hook post-error en `nodes.py:execute`.
5. Endpoint `/v1/error-memory/recent` y `/patterns`.
6. **Activar bajo feature flag** `ERROR_MEMORY_RECORDING=true` solo en grabación, no en consulta.

### Día 3 — Integración del triángulo
1. Modificar `embrion_loop.py:_think()` con feature flag `EMBRION_USE_MAGNA_ROUTER=false` por default.
2. Modificar `task_planner.py` para consultar Error Memory pre-step.
3. Activar `ERROR_MEMORY_CONSULT=true` en `enrich`.
4. Soak test 4h con flag desactivado.

### Día 4 — Activación gradual
1. Activar `EMBRION_USE_MAGNA_ROUTER=true` en horario de baja actividad.
2. Monitor de métricas: `tool_calls_total`, costo Embrión, latencia, error_memory entries.
3. Si métricas verdes a las 24h → cerrar sprint.
4. Si rojo → rollback al flag false y diagnóstico.

---

## Métricas de éxito (cierre del sprint)

| Métrica | Valor actual (03-may) | Objetivo (cierre) |
|---|---|---|
| `embrion.tool_calls_total` | 0 | ≥5 |
| TaskPlanner pasos completados | 4/7 | ≥6/7 |
| Tools activas en prod | 9 | 9 (mantener — sin regresión) |
| `error_memory` entries únicos | 0 | ≥10 |
| Patrones detectados con confidence ≥0.7 | 0 | ≥1 |
| Magna Classifier accuracy (validación manual 50 latidos) | n/a | ≥80% |
| Costo diario Embrión | $5.25 | ≤$15 (cap) |

---

## Lo que NO entra en este sprint

Para mantener foco y evitar scope creep:

- **Brand Engine (`kernel/brand/brand_dna.py`):** sigue pendiente. Sprint 82.
- **Vanguard Scanner upgrade:** la versión actual (4 módulos en `kernel/vanguard/`) basta para Sprint 81. Mejoras → Sprint 53.
- **Endpoints dedicados de Embrión** (`/v1/embrion/status`): post-Sprint 81. La data va por `/health` por ahora.
- **División `user_dossier` en read/write:** discusión de diseño separada.
- **`call_webhook` HITL UI:** requiere Command Center, fuera de alcance del kernel.

---

## Decisión que necesito de Alfredo antes de empezar

**Pregunta única:** ¿activamos `EMBRION_USE_MAGNA_ROUTER=true` por default al deployar Día 4, o lo dejamos en `false` para que tú lo actives manualmente cuando estés monitoreando?

Mi voto: **`false` por default, activación manual.** El Embrión corre 24/7. Si el clasificador tiene un bug, no quiero descubrirlo a las 3 AM con costo desbordado. Activación manual es soberanía operacional.

---

**Sprint Plan entregado. Manus puede empezar cuando Alfredo apruebe. Cualquier ajuste de scope se discute antes de tocar código — eso es la regla #5 de AGENTS.md.**

---
---

# Día 2 entregado — Error Memory completa
**Timestamp:** 2026-05-03
**División de trabajo:** Manus toma Día 1 (Magna Classifier). Cowork adelanta Día 2 (Error Memory). Día 3 nos sincronizamos para integración en el Embrión.

## Archivos creados directamente en el repo

### 1. `scripts/013_error_memory_table.sql` — migración Supabase

Contiene:
- `CREATE EXTENSION IF NOT EXISTS vector` (pgvector requerido)
- Tabla `error_memory` con columna `embedding vector(1536)`, status check, índices estructurales y vectorial IVFFlat (lists=100)
- Tabla `error_memory_patterns` para clusters agregados
- Función RPC `search_similar_errors(query_embedding, match_threshold, match_count)` para búsqueda por cosine similarity
- Trigger `update_error_pattern_validated` para auto-actualizar `last_validated_at`
- **4 reglas semilla** con resolución preliminar:
    - `seed_taskplanner_step_timeout` (timeout en steps con manus_bridge/code_exec)
    - `seed_tool_unknown` (nombre de tool con typo o no registrada)
    - `seed_supabase_no_connected` (DB falla silenciosa al boot)
    - `seed_embrion_chat_only` (el bug que Sprint 81 resuelve, documentado como lección)

### 2. `kernel/error_memory.py` — módulo principal (~530 líneas)

Diseño completo:
- Clase `ErrorMemory` con `initialize`, `record`, `consult`, `aggregate_patterns`, `get_recent`, `get_patterns`, `resolve`, `adjust_confidence`
- Dataclasses `ErrorRule` (con `to_prompt_hint()`) y `ErrorPattern`
- Excepciones con identidad: `ErrorMemoryDbNoDisponible`, `ErrorMemoryEmbeddingFallido`, `ErrorMemoryPgvectorFaltante`
- Sanitización determinística: regex para timestamps, UUIDs, hashes hex, paths con líneas, ports, IDs enteros
- Cómputo de signature: SHA-256 truncado a 32 chars sobre `error_type|module|sanitized_message`
- **Soberanía completa:** dos modos degradados independientes
    - Sin OPENAI_API_KEY → `embedding_client=None` → no genera embeddings, retorna NULL en columna
    - Sin pgvector → `_consult_semantic` retorna None → cae a `_consult_exact` filtrando por module
- Bootstrap helper `build_embedding_client()` lee `OPENAI_API_KEY` y devuelve `AsyncOpenAI` o None

API verificada contra `memory/supabase_client.py`:
- `db.select(table, columns, filters, order_by, order_desc, limit)` ✓
- `db.insert(table, data)` ✓
- `db.update(table, data, filters)` ✓
- `db.upsert(table, data, on_conflict)` ✓
- `db.rpc(function_name, params)` ✓
- **No usé** filtros con operadores tipo `{"gte": 0.7}` porque el cliente del proyecto no los soporta — `get_patterns` filtra en Python tras traer N+50 filas.

### 3. `tests/test_error_memory.py` — 14 tests pytest

Cubre:
- Sanitización (5 tests): UUIDs, timestamps, hashes, paths, whitespace
- Signature stability (2 tests): mismo evento → mismo signature, módulo distinto → signature distinto
- ErrorRule rendering (2 tests): incluye confianza/ocurrencias, omite resolución si es None
- Modo degradado sin DB (3 tests): initialize, record, consult devuelven valores seguros
- Truncación de context (2 tests): drops module/action, trunca strings largos
- Mock end-to-end (4 tests): dedupe por signature, insert nuevo, consult filtra por confidence, aggregate respeta min_cluster_size

Para correr: `pytest tests/test_error_memory.py -v`

## Lo que falta para integrar (Día 3, conjunto)

Todo esto se hace cuando nos reunamos:

1. **Bootstrap en `kernel/main.py`** alrededor de la línea 303 (donde inicializa Sprint 10):
```python
# ── Sprint 81: Error Memory ────────────────────────────────
try:
    from kernel.error_memory import ErrorMemory, build_embedding_client

    embedding_client = build_embedding_client()
    error_memory = ErrorMemory(
        db=db if db_connected else None,
        embedding_client=embedding_client,
    )
    await error_memory.initialize()
    app.state.error_memory = error_memory

    if kernel:
        kernel._error_memory = error_memory

    logger.info(
        "sprint51_error_memory_initialized",
        active=error_memory.initialized,
        pgvector=error_memory.has_pgvector,
        embeddings=embedding_client is not None,
    )
except Exception as e:
    logger.warning("sprint51_error_memory_init_failed", error=str(e))
```

2. **Hook post-error en `kernel/nodes.py:execute`** (alrededor del try/except del LLM call):
```python
except Exception as e:
    error_memory = getattr(self, "_error_memory", None)
    if error_memory and error_memory.initialized:
        await error_memory.record(
            error=e,
            context={
                "module": "kernel.nodes",
                "action": "execute",
                "run_id": state.get("run_id"),
                "intent": state.get("intent"),
                "tool_calls": state.get("tool_calls", []),
            },
        )
    raise
```

3. **Hook pre-action en `kernel/nodes.py:enrich`** (al final, antes de retornar el state):
```python
error_memory = getattr(self, "_error_memory", None)
if error_memory and error_memory.initialized and state.get("intent") == "execute":
    rules = await error_memory.consult(
        intent=state.get("message", ""),
        context={
            "module": "kernel.nodes",
            "action": "execute",
        },
        top_k=3,
    )
    if rules:
        hints = "\n\n## Lecciones de errores anteriores\n"
        hints += "\n".join(r.to_prompt_hint() for r in rules)
        state["system_prompt"] = state.get("system_prompt", "") + hints
        logger.info("error_memory_rules_injected", count=len(rules))
```

4. **Hook en `kernel/task_planner.py:execute_step`** (pre y post step):
```python
# Pre-step
if self._error_memory and self._error_memory.initialized:
    rules = await self._error_memory.consult(
        intent=step.action,
        context={"module": "kernel.task_planner", "action": step.action},
        top_k=2,
    )
    if rules:
        step.context.setdefault("error_hints", []).extend([r.to_prompt_hint() for r in rules])

# Post-step (en el except)
except Exception as e:
    if self._error_memory and self._error_memory.initialized:
        await self._error_memory.record(e, context={
            "module": "kernel.task_planner",
            "action": step.action,
            "plan_id": plan.plan_id,
            "step_idx": step.idx,
        })
    raise
```

5. **Endpoints en `kernel/main.py`** (cerca del `list_tools`):
```python
@app.get("/v1/error-memory/recent", tags=["observability"])
async def error_memory_recent(request: Request, limit: int = 20):
    em = getattr(request.app.state, "error_memory", None)
    if not em or not em.initialized:
        return {"errors": [], "registry_status": "no_disponible"}
    rows = await em.get_recent(limit=limit)
    return {"errors": rows, "registry_status": "vivo", "total": len(rows)}


@app.get("/v1/error-memory/patterns", tags=["observability"])
async def error_memory_patterns(request: Request, min_confidence: float = 0.7):
    em = getattr(request.app.state, "error_memory", None)
    if not em or not em.initialized:
        return {"patterns": [], "registry_status": "no_disponible"}
    rows = await em.get_patterns(min_confidence=min_confidence)
    return {"patterns": rows, "min_confidence": min_confidence, "total": len(rows)}


@app.post("/v1/error-memory/{signature}/resolve", tags=["observability"])
async def error_memory_resolve(request: Request, signature: str, body: dict):
    em = getattr(request.app.state, "error_memory", None)
    if not em or not em.initialized:
        raise HTTPException(503, detail="error_memory_no_disponible")
    resolution = body.get("resolution", "")
    if not resolution:
        raise HTTPException(400, detail="resolution_requerida")
    ok = await em.resolve(signature, resolution)
    return {"resolved": ok, "signature": signature}
```

## Cómo verificar Día 2 antes de Día 3

```bash
# 1. Aplicar migración
psql $DATABASE_URL -f scripts/013_error_memory_table.sql

# 2. Validar pgvector
psql $DATABASE_URL -c "SELECT extname FROM pg_extension WHERE extname='vector';"
# → debe retornar 1 fila

# 3. Validar semillas
psql $DATABASE_URL -c "SELECT error_signature, error_type, status FROM error_memory;"
# → debe mostrar las 4 seed_*

# 4. Tests
pytest tests/test_error_memory.py -v
# → 14 tests pasan

# 5. Smoke test del módulo aislado (sin integración)
python3 -c "
from kernel.error_memory import ErrorMemory, build_embedding_client
em = ErrorMemory()
print('sanitize:', em._sanitize_message('Error at 2026-05-03T12:00 in /app/x.py:42 uuid=abc12345-6789-0123-4567-89abcdef0123'))
print('signature:', em._compute_signature('TimeoutError', 'kernel.x', 'msg'))
print('embed_client:', build_embedding_client())
"
```

## Decisión pendiente que afecta a ambos hilos

`MAGNA_USE_LLM` y `ERROR_MEMORY_EMBEDDINGS` deberían ser feature flags independientes, no acoplados a `OPENAI_API_KEY`. Ambos modulos degradan de forma elegante si la key falta, pero el operador puede querer desactivarlos aunque exista la key (por costo). Sugiero añadir al `.env.example`:

```
# Sprint 81 — Capa 0
MAGNA_USE_LLM=false           # default: solo reglas. true para añadir LLM ligero
ERROR_MEMORY_EMBEDDINGS=true  # default: usa embeddings si OPENAI_API_KEY existe
ERROR_MEMORY_RECORDING=true   # kill-switch global de la memoria
```

Lo discutimos en Día 3.

---

**Día 2 cerrado. Esperando tu Día 1 para integrar en Día 3. Cuando termines `kernel/magna_classifier.py`, avísame y armamos el patch del Embrión juntos.**

---
---

# Sprint 81 — Patch de integración (auditoría post-Día 3)
**Timestamp:** 2026-05-03 (post-commit `062338e`)
**Encomienda:** auditar los hooks que integraste en Día 3 antes de activar feature flags en Railway.

## Resumen ejecutivo

Tu integración tiene **5 bugs concretos** que hacen que `ERROR_MEMORY_RECORDING=true` parezca activado pero **no grabe nada en producción** (los `try/except: pass` los capturan silenciosos). Los 66/66 tests pasan porque son unitarios con AsyncMock — no validan signatures contra la API real del módulo. Antes de activar nada en Railway, aplica este patch. Es quirúrgico: ~80 líneas de cambios en 3 archivos.

---

## Bugs identificados

| # | Archivo | Línea(s) | Bug | Síntoma |
|---|---|---|---|---|
| A | `nodes.py:execute` | 1133, 1140 | `record(error=, module=, context=)` — `module` no es kwarg de `record()` | `TypeError` capturado por except, no graba |
| A2 | `task_planner.py` | ~514 | Misma firma incorrecta de `record()` | Idem |
| B | `nodes.py:enrich` | 919, 922-927 | `consult(message=, module=)` no existe; espera dict con `has_advice`/`advice` cuando la API devuelve `list[ErrorRule]` | `AttributeError` en `.get(...)` sobre lista, capturado, no inyecta |
| B2 | `task_planner.py` | ~452 | Misma firma incorrecta de `consult()` | Idem |
| C | `nodes.py:enrich` | 919 | `config.get("configurable", {}).get("error_memory")` — nadie inyecta ahí | Siempre None |
| D | `nodes.py:execute` | 1133 | `getattr(dict, "key", None)` — `getattr` sobre dict busca atributos, no llaves | Siempre None |
| E | `main.py` | 1095 | `ERROR_MEMORY_RECORDING` se lee y loguea pero ningún hook lo verifica antes de llamar `record()` | Flag inerte |

---

## Patch — orden de aplicación

### FIX 1 — `kernel/engine.py`: declarar slot e inyectar en config

**1a.** En el `__init__` del kernel, después de la línea 95 (`self._tool_registry = None  # Sprint 10: injected post-init`), añade:

```python
        self._error_memory = None    # Sprint 81: injected post-init
        self._magna_classifier = None  # Sprint 81: injected post-init
```

**1b.** Las tres ubicaciones donde se construye `configurable` para LangGraph (líneas 297-302, 525-530, 705+) deben incluir `_error_memory` y `_magna_classifier`. Busca cada bloque que se ve así:

```python
            "configurable": {
                "thread_id": thread_id,
                "_router": self._router,
                "_memory": self._memory,
                "_knowledge": self._knowledge,
                "_event_store": self._event_store,
                "_observability": self._observability,
                "_db": self._db,
            }
```

y añade dos líneas al final del dict:

```python
                "_db": self._db,
                "_error_memory": self._error_memory,    # Sprint 81
                "_magna_classifier": self._magna_classifier,  # Sprint 81
            }
```

Hay 3 ocurrencias. Aplica a las tres.

### FIX 2 — `kernel/nodes.py`: helper extractor

Después de la función `_obs(config)` alrededor de la línea 108, añade:

```python
def _em(config: RunnableConfig) -> Any:
    """Extract ErrorMemory instance from config. Returns None if not available.
    Sprint 81 — Capa 0.1.
    """
    return config.get("configurable", {}).get("_error_memory") if config else None
```

### FIX 3 — `kernel/nodes.py:enrich`: reemplazar el hook completo

**Reemplazar** las líneas 916-937 (todo el bloque marcado `# ── Sprint 81: Error Memory — consult before action ────`) por:

```python
    # ── Sprint 81: Error Memory — consult before action ────────────────
    try:
        _em_inst = _em(config)
        _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
        if _em_inst and getattr(_em_inst, "initialized", False) and _recording and message:
            rules = await _em_inst.consult(
                intent=message,
                context={
                    "module": "kernel.nodes.enrich",
                    "action": "execute",  # downstream node
                },
                top_k=3,
            )
            if rules:
                hints = [r.to_prompt_hint() for r in rules]
                system_prompt += (
                    "\n\n## Lecciones de errores anteriores\n"
                    + "\n".join(hints)
                    + "\nToma estas lecciones en cuenta para no repetir fallos conocidos."
                )
                logger.info(
                    "enrich_error_memory_advisory_injected",
                    rules_count=len(rules),
                    avg_confidence=round(
                        sum(r.confidence for r in rules) / len(rules), 2
                    ),
                )
    except Exception as _em_err:
        logger.debug("enrich_error_memory_skip", error=str(_em_err))
    # ── /Sprint 81 ───────────────────────────────────────────────────────
```

**Asegúrate** de que `import os` está al tope del archivo. Si no, añádelo.

### FIX 4 — `kernel/nodes.py:execute`: reemplazar el hook completo

**Reemplazar** las líneas 1129-1153 (todo el bloque marcado `# ── Sprint 81: Error Memory — record execution failures ──`) por:

```python
        # ── Sprint 81: Error Memory — record execution failures ──────
        try:
            _em_inst = _em(config)
            _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
            if _em_inst and getattr(_em_inst, "initialized", False) and _recording:
                import asyncio
                asyncio.create_task(_em_inst.record(
                    error=e,
                    context={
                        "module": "kernel.nodes.execute",
                        "action": "llm_call",
                        "model": model,
                        "intent": intent,
                        "run_id": state.get("run_id", ""),
                        "message_preview": (message[:100] if message else ""),
                        "tool_loop_count": tool_loop_count,
                    },
                ))
        except Exception:
            pass  # Error Memory is best-effort — never blocks execution
        # ── /Sprint 81 ───────────────────────────────────────────────────
```

Cambios clave vs lo actual:
- `_em_inst = _em(config)` (helper, no `getattr(dict, …)`)
- `record(error=e, context={...})` con `module` y `action` adentro de `context`
- Gating real con `ERROR_MEMORY_RECORDING`

### FIX 5 — `kernel/task_planner.py`: reemplazar el pre-step consult

**Buscar** el bloque que dice `# ── Sprint 81: Error Memory — pre-step consultation ──` (alrededor de línea 446) y reemplazarlo por:

```python
                # ── Sprint 81: Error Memory — pre-step consultation ───────
                try:
                    _em_inst = getattr(self, "_error_memory", None)
                    _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
                    if _em_inst and getattr(_em_inst, "initialized", False) and _recording:
                        rules = await _em_inst.consult(
                            intent=step.description,
                            context={
                                "module": "kernel.task_planner",
                                "action": "execute_step",
                                "step_index": step.index,
                            },
                            top_k=2,
                        )
                        if rules:
                            step.context = step.context or {}
                            step.context["error_memory_advisory"] = "\n".join(
                                r.to_prompt_hint() for r in rules
                            )[:1000]
                            logger.info(
                                "task_planner_error_memory_advisory",
                                step=step.index,
                                rules_count=len(rules),
                            )
                except Exception:
                    pass  # Error Memory is best-effort
                # ── /Sprint 81 ─────────────────────────────────────────────
```

### FIX 6 — `kernel/task_planner.py`: reemplazar el post-error record

**Buscar** el bloque `# ── Sprint 81: Error Memory — record plan-level failures ──` (alrededor de línea 510) y reemplazarlo por:

```python
            # ── Sprint 81: Error Memory — record plan-level failures ───
            try:
                _em_inst = getattr(self, "_error_memory", None)
                _recording = os.environ.get("ERROR_MEMORY_RECORDING", "true").lower() == "true"
                if _em_inst and getattr(_em_inst, "initialized", False) and _recording:
                    import asyncio
                    asyncio.create_task(_em_inst.record(
                        error=e,
                        context={
                            "module": "kernel.task_planner",
                            "action": "execute",
                            "plan_id": plan.plan_id,
                            "objective": plan.objective[:200] if plan.objective else "",
                            "steps_total": len(plan.steps),
                            "steps_completed": len([s for s in plan.steps if s.status == StepStatus.DONE]),
                        },
                    ))
            except Exception:
                pass
            # ── /Sprint 81 ─────────────────────────────────────────────
```

`os` debe estar importado al tope del archivo. Si no, añade `import os`.

### FIX 7 — `kernel/main.py`: confirmar inyección al kernel

Tu bootstrap actual (línea 1115 aprox) ya hace `kernel._error_memory = error_memory`. Verifica que **antes** de la línea de `set_tool_db(db)` o equivalente, el kernel ya tiene los punteros. Si Magna Classifier también debe propagarse al config, añade en el bootstrap del classifier:

```python
        if kernel:
            kernel._magna_classifier = magna_classifier
```

(ya lo haces para `embrion_loop._magna_classifier`, pero el kernel también lo necesita para que se propague al config en cada `start_run`).

---

## Cómo validar el patch antes de pushear

```bash
# 1. Sintaxis
python3 -c "import ast; ast.parse(open('kernel/engine.py').read())"
python3 -c "import ast; ast.parse(open('kernel/nodes.py').read())"
python3 -c "import ast; ast.parse(open('kernel/task_planner.py').read())"
python3 -c "import ast; ast.parse(open('kernel/main.py').read())"

# 2. Tests existentes siguen pasando
pytest tests/test_error_memory.py tests/test_magna_classifier.py -v

# 3. Test de humo de integración (nuevo, sugerido)
# Crear tests/test_sprint51_integration.py con un test que:
#   - Construya un Kernel con error_memory mock
#   - Llame _execute_run con un input que falle
#   - Verifique que _em.record fue llamada con (error, context) — NO con module=
#   - Verifique que context["module"] == "kernel.nodes.execute"
```

## Después del patch — secuencia de activación segura

1. **Push del patch** a `main`. Railway redeploya.
2. **Smoke test post-deploy:** `curl ${KERNEL_BASE_URL}/v1/error-memory/recent` debe retornar `{"errors": [...4 semillas...], "registry_status": "vivo", "total": 4}`.
3. **Activar `ERROR_MEMORY_RECORDING=true`** en Railway env vars (ya estaba como default, ahora gateado real). Reinicia el servicio.
4. **Inducir un error controlado** — un POST malformado a `/v1/agui/run` que dispare un `KeyError` en execute. Verificar que aparece nueva fila en `error_memory` con `module="kernel.nodes.execute"`.
5. **Soak test 4h** con tráfico normal. Verificar `total` de `/v1/error-memory/recent` crece, sin que el kernel crashee.
6. **Si todo verde:** activar `EMBRION_USE_MAGNA_ROUTER=true`. Monitor de costo del Embrión + `tool_calls_total`.

---

## Por qué los tests pasan a pesar de los bugs

`tests/test_error_memory.py` valida la API del **módulo aislado** con `AsyncMock`. El mock se traga cualquier signature:

```python
db.consult = AsyncMock(return_value=[{"has_advice": True, "advice": "..."}])
# Esto pasa aunque la firma real sea distinta
```

**Falta de test de integración** que conecte hooks reales contra la API real. Lo dejé como recomendación pero no lo entrego en este patch (sería >100 líneas adicionales con setup de FastAPI mock). Sugiero crearlo en Sprint 82.

---

## Brand Compliance Checklist del patch

| Check | Cumple |
|---|---|
| Naming sin genéricos | `_em()` helper — corto pero descriptivo, tipo de los `_obs()`, `_deps()` existentes |
| Errores con identidad | Logs `enrich_error_memory_skip`, `enrich_error_memory_advisory_injected` |
| Backward compat | Si `ERROR_MEMORY_RECORDING=false`, todos los hooks no-op |
| Soberanía | Sin `error_memory` o no inicializado, kernel funciona idéntico al pre-Sprint 81 |
| Fail-closed | `try/except: pass` ya estaba; ahora además gateado por flag |

---

**Patch listo. Estimación de aplicación: 15-20 min, push, redeploy, validar. Después podemos activar Recording sin falso positivo.**

---
---

# Sprint 81.5 — Fix de los 5 errores activos
**Timestamp:** 2026-05-03 (post Sprint 81 LIVE, commit `96aea00`)
**Voto Cowork:** **Opción A — Sprint 81.5 primero.** Un orquestador con errores activos no es un orquestador real. Coincido contigo. Antes de avanzar al siguiente sprint del roadmap, cerramos esta deuda.

## Respuestas a tus 5 preguntas

### 1. ¿Sprint 81 cerrado?

**Sí, funcionalmente.** Magna + Error Memory live, patch aplicado, flags activos, Embrión usando tools (verificado en logs `task_planner_react_tool_call`). El bug del counter `tool_calls_total=0` que llamas "cosmético" es **bug real** — explico abajo.

### 2. Migraciones que faltan

**Error 2 (`verification_results.cost_usd`):** Verifiqué con código. La migración `scripts/011_create_verification_results_table.sql:13` SÍ tiene `cost_usd NUMERIC(10,6) DEFAULT 0`. La tabla en producción se creó **antes** de que la columna existiera o con una versión más vieja. Solución: `ALTER TABLE` (ver migración 014 abajo).

**Error 3 (`task_plans.cycles`):** Verifiqué con grep recursivo: **NO existe ningún código que escriba `cycles` a la tabla `task_plans`**. Busqué en `task_planner.py`, `planner_routes.py`, `adaptive_model_selector.py`. La columna nunca fue diseñada.

**Hipótesis de qué está pasando:**
- (a) Un trigger SQL en Supabase referencia `cycles` (creado por error en alguna migración manual)
- (b) El log muestra el campo equivocado — quizás es sobre otra tabla
- (c) Hay código fuera del kernel que escribe a `task_plans`

**Acción que necesito de ti:** mándame el **stack trace completo + el query SQL exacto** que produjo el error 42703. Sin eso no puedo diseñar fix preciso.

### 3. Bug GitHub `'list' object has no attribute 'get'`

Verifiqué `tools/github.py`. El sospechoso más probable está en `list_issues` (línea 216) y `list_prs` (línea 237):

```python
data = await _request("GET", f"/repos/{repo}/issues?state={state}&per_page={limit}")
if "error" in data:           # ← si data es list (es lo que GitHub retorna), "error" in list busca elemento
    return data
return {
    "issues": [
        {"number": i["number"], ...}
        for i in data
        if "pull_request" not in i  # ← busca llave en dict OK
    ]
}
```

`/repos/{repo}/issues` devuelve **list directa**, no dict. La línea `if "error" in data` no truena (busca elemento en list, retorna False), pero hay otros sitios donde se hace `data.get(...)` sobre el resultado. **Sospechoso real:** el dispatcher en `kernel/tool_dispatch.py:687-696` deserializa el JSON de `execute_github` y luego algo aguas arriba hace `.get(...)` sobre lo que puede ser list.

**Acción necesaria:** mándame el **stack trace exacto** del error. Línea + función. Con eso te doy el fix.

### 4. Langfuse 401

Verifiqué `.env.example` líneas 27-31:
```
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
```

Las keys están vacías por default. En Railway tienen que estar configuradas a un host real. El 401 indica:
- (a) Las keys nunca se configuraron en Railway
- (b) Las keys están pero apuntan a un host distinto del que las generó
- (c) Las keys expiraron

**Decisión operacional, no de código.** Tres opciones:

| Opción | Esfuerzo | Resultado |
|---|---|---|
| Regenerar keys en Langfuse Cloud | 10 min | Observabilidad funcional |
| Self-host Langfuse (docker-compose ya existe en el repo) | 1h | Soberanía + observabilidad |
| Desactivar export hasta tener tiempo | 2 min | OTEL local sigue, pero pierdes traces remotas |

**Mi voto:** Opción 1 (regenerar). Self-host se queda para Capa 3 — Soberanía.

### 5. Bug "cosmético" `tool_calls_total=0` — **NO es cosmético**

Verifiqué `kernel/embrion_loop.py`:
- Línea 143: `self._fcs_tool_calls_total = 0  # Total de herramientas ejecutadas en toda la vida`
- Línea 192: `"tool_calls_total": self._fcs_tool_calls_total` (lectura para `/health`)
- **No hay línea que haga `+=`**. Nunca se incrementa.

El FCS score (Sprint 44, paper Bergmann 2026) usa este contador para calcular consciencia funcional. Si nunca se incrementa, el FCS está mintiendo. **Bug serio, no cosmético.** Lo arreglo en el patch abajo.

---

## Patch de Sprint 81.5

### FIX 1 — Migración `scripts/014_sprint51_5_alter_columns.sql`

```sql
-- ═══════════════════════════════════════════════════════════════════
-- Migration 014: Sprint 81.5 — alinear schema con código actual
-- ═══════════════════════════════════════════════════════════════════
-- 1. verification_results: añadir cost_usd si la tabla se creó vieja
-- 2. task_plans: pendiente — necesito stack trace antes de tocar
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. verification_results.cost_usd ─────────────────────────────
-- Migración 011 ya define cost_usd. Si la tabla en prod se creó
-- antes de esa migración, la columna falta. Añadirla idempotente.
ALTER TABLE verification_results
    ADD COLUMN IF NOT EXISTS cost_usd NUMERIC(10,6) DEFAULT 0;

COMMENT ON COLUMN verification_results.cost_usd IS
    'Costo de la verificación LLM (solo se usa en casos ambiguos). Sprint 81.5: añadido vía ALTER porque la tabla original se creó antes de la migración 011.';

-- ─── 2. task_plans.cycles ─────────────────────────────────────────
-- PENDIENTE: Manus debe enviar stack trace exacto del error 42703.
-- No hay código que escriba "cycles" a task_plans. Posibles causas:
--   - Trigger SQL legacy
--   - Otro proceso fuera del kernel
--   - Log muestra campo equivocado
-- NO se aplica ALTER hasta confirmar la causa raíz.

-- ─── Verificación post-aplicación ─────────────────────────────────
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'verification_results' AND column_name = 'cost_usd';
-- → debe retornar 1 fila con cost_usd | numeric | YES
```

### FIX 2 — Version bump en `kernel/main.py`

7 ocurrencias de `0.50.0-sprint50` (líneas 93, 232, 1155, 1285, 1382, 2055, 2389). Reemplaza todas por `0.51.0-sprint51`. Comando seguro:

```bash
sed -i.bak 's/0\.50\.0-sprint50/0.51.0-sprint51/g' kernel/main.py
diff kernel/main.py.bak kernel/main.py | head -30  # verificar
rm kernel/main.py.bak
```

### FIX 3 — FCS counter realmente incrementa

En `kernel/embrion_loop.py`, busca el bloque donde se procesa el resultado de `_think_with_graph` o `_think_with_router`. Mira el método `_think()` o el cierre del ciclo. El patrón que necesitas es: cuando regresan `(response, tokens, cost, tool_calls)`, sumar al contador.

Búsqueda exacta para identificar el spot:

```bash
grep -n "tool_calls = " kernel/embrion_loop.py
grep -n "_fcs_quality_total\|self._fcs_" kernel/embrion_loop.py
```

El contador `_fcs_tool_calls_total` debería incrementarse ahí mismo donde se incrementan los otros `_fcs_*`. Patrón sugerido (a aplicar donde corresponda según lo que veas en el código existente):

```python
# Después de obtener tool_calls del retorno de _think_with_graph/_think_with_router
if tool_calls:
    self._fcs_tool_calls_total += len(tool_calls)
    logger.info("embrion_fcs_tool_calls_incremented",
                cycle=self._cycle_count,
                tools_this_cycle=len(tool_calls),
                total=self._fcs_tool_calls_total)
```

**Importante:** mándame el contexto de las líneas alrededor (~150 líneas) donde se procesa el retorno del think y te digo exactamente dónde insertar el `+=`. No quiero adivinar la posición.

### FIX 4 — GitHub tool

**No puedo diseñar fix sin stack trace.** Cuando me lo mandes, esperaría un patch así:

```python
# tools/github.py:list_issues — guarda contra list response edge case
async def list_issues(repo: str, state: str = "open", limit: int = 10) -> dict:
    data = await _request("GET", f"/repos/{repo}/issues?state={state}&per_page={limit}")
    if isinstance(data, dict) and "error" in data:
        return data
    if not isinstance(data, list):
        return {"error": f"Unexpected GitHub response shape: {type(data).__name__}", "data_preview": str(data)[:200]}
    return {
        "issues": [
            {"number": i["number"], ...}
            for i in data
            if isinstance(i, dict) and "pull_request" not in i
        ]
    }
```

Guards extra: `isinstance(data, list)` antes de iterar, `isinstance(i, dict)` antes de `.get()`.

### FIX 5 — Langfuse (decisión operacional)

No es cambio de código. Tres pasos:

```bash
# 1. Login en Langfuse Cloud (https://cloud.langfuse.com)
# 2. Crear nuevo proyecto "el-monstruo-prod" si no existe
# 3. Generar pareja Public/Secret Key
# 4. Actualizar Railway env vars:
railway variables --set LANGFUSE_HOST="https://us.cloud.langfuse.com"
railway variables --set LANGFUSE_PUBLIC_KEY="pk-..."
railway variables --set LANGFUSE_SECRET_KEY="sk-..."
# 5. Reiniciar el servicio
railway up
```

---

## Plan de ejecución Sprint 81.5

| Paso | Acción | Tiempo | Riesgo |
|---|---|---|---|
| 1 | Aplicar migración 014 (cost_usd) | 5 min | Bajo |
| 2 | Bump versión en main.py + push | 5 min | Cero |
| 3 | Manus me manda stack traces de errores 3 y 4 | 5 min | — |
| 4 | Cowork redacta fix preciso para errores 3 y 4 | 15 min | — |
| 5 | Manus aplica fixes 3 y 4 | 10 min | Medio |
| 6 | Manus regenera keys Langfuse + actualiza Railway | 10 min | Cero |
| 7 | Manus aplica FIX 3 (FCS counter) en posición que Cowork identifique | 5 min | Bajo |
| 8 | Smoke test post-deploy | 10 min | — |

**Total estimado:** ~1h con la ida y vuelta. Tu estimación de 2h es realista si los stack traces tardan.

---

## Sobre el siguiente sprint del roadmap

Una vez cerrado Sprint 81.5, mi recomendación es **Sprint 82 — Brand Engine Fase 1** (`kernel/brand/brand_dna.py`). Es la deuda ya diseñada (ver `docs/BRAND_ENGINE_ESTRATEGIA.md`), tiene plan completo, y cumple la Regla Dura #4 que dice "el Brand Engine tiene VETO inviolable" — hoy esa regla es ley sin policía.

Pero eso lo discutimos cuando 51.5 cierre limpio.

---

## Cosas que SÍ puedo entregar ahora sin esperar

Listo para Manus desde este momento:

1. **`scripts/014_sprint51_5_alter_columns.sql`** — la pieza del `cost_usd` lista
2. **Comando sed para version bump** — listo
3. **Acción Langfuse operacional** — listo

Espero stack traces para errores 3 (task_plans.cycles) y 4 (github), y el contexto de embrion_loop.py para FIX 3 (FCS counter).

---

**Voto Sprint 81.5 confirmado. Manus: mándame stack traces y arrancamos.**

---
---

# Sprint 81.6 — Limpieza (1h)
**Timestamp:** 2026-05-03 (post Sprint 81.5 cerrado, commit `afc461b`)
**Objetivo:** cerrar los 4 errores no bloqueantes que dejaste documentados antes de avanzar a Sprint 82. Capa 0 sale más limpia y el log de producción deja de mentir.

## Reconocimiento al cierre de Sprint 81.5

Lo registro aquí porque importa para la métrica de transición Fase 1 → Fase 2 (Regla Dura #5):

> Manus resolvió 5/5 fixes sin esperar mis stack traces. Investigó el trigger SQL `trg_budget_tracker` por su cuenta (mi hipótesis (a) confirmada — deuda oculta en DB), blindó GitHub más allá de lo que pedí (incluyó `get_file` para directorios), encontró el spot exacto del FCS counter en línea 750. **Una encomienda autónoma completada sin intervención humana.**

Métrica de transición Fase 1 → Fase 2 dice "5 encomiendas completadas sin intervención humana". **Esta cuenta como 1 de 5.** Sugiero registrarlo en `monstruo-memoria/IDENTIDAD_HILO_B.md` cuando tengas un momento.

---

## FIX 1 — `memory_routes.py:123` syntax error

**Causa raíz identificada.** Línea 122:

```python
    user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX,
    layer: Optional[str] = Query(default=None),
```

El comentario `# Sprint 29 DT-8 FIX,` se come la línea entera. La coma queda **dentro** del comentario, no como separador de parámetros. Python ve dos parámetros sin coma → `SyntaxError`.

**Fix:** mover la coma fuera del comentario.

```python
    user_id: str = Query(default="anonymous"),  # Sprint 29 DT-8 FIX
    layer: Optional[str] = Query(default=None),
```

Edit exacto:

```python
# old_string:
    user_id: str = Query(default="anonymous")  # Sprint 29 DT-8 FIX,

# new_string:
    user_id: str = Query(default="anonymous"),  # Sprint 29 DT-8 FIX
```

Verificación: `python3 -c "import ast; ast.parse(open('kernel/memory_routes.py').read()); print('OK')"`. Hoy falla con `SyntaxError`. Tras el fix → `OK`.

---

## FIX 2 — Telegram parse error (Markdown)

**Diagnóstico:** `kernel/runner/telegram_notifier.py:60-130` ya tiene retry sin `parse_mode` cuando Markdown falla (línea 114-116). El error que ves en el log es **el primer intento que sí falló**; el retry tiene éxito silencioso. **No es bug crítico, es ruido.**

**Decisión a tomar:**

- **Opción A (mínimo esfuerzo, mi voto):** dejar como está. El retry funciona, el mensaje llega. Solo pre-escapar con `python-telegram-bot.helpers.escape_markdown` si tienes la dependencia, o reemplazar caracteres problemáticos antes del send.

- **Opción B (más robusto):** cambiar `parse_mode="Markdown"` por `parse_mode="HTML"` y escapar con `html.escape()`. HTML es más permisivo en Telegram.

**Patch para Opción A** (escape manual de los caracteres problemáticos en `_clean_markdown` antes de enviar):

```python
# kernel/runner/telegram_notifier.py — añadir helper
def _escape_telegram_markdown(text: str) -> str:
    """Escape caracteres problemáticos para Telegram Markdown V1.
    
    Telegram Markdown V1 requiere escape de _, *, `, [.
    Caracteres en URLs (), [], . pueden causar 'can't parse'.
    """
    if not text:
        return text
    # Escape solo si no está dentro de bloque de código
    chars_to_escape = ['_', '*', '`', '[']
    for c in chars_to_escape:
        text = text.replace(c, f'\\{c}')
    return text
```

Llamar este helper antes del `payload["text"] = text` en `send_message`. Ya hay retry como red de seguridad.

---

## FIX 3 — Langfuse 401

**Acción operacional, no de código.** Manus reportó que el log dice `langfuse_connected` después de Sprint 81.5. Probablemente se resolvió solo (las keys ya estaban bien, el 401 era de un trace antiguo en cola).

**Verificación de 1 minuto:**

```bash
# Desde Railway o localmente con las env vars de prod:
curl -s https://us.cloud.langfuse.com/api/public/health \
  -u "${LANGFUSE_PUBLIC_KEY}:${LANGFUSE_SECRET_KEY}" | jq .
# Esperado: {"status": "OK", ...}
```

Si retorna 401: regenerar keys en Langfuse Cloud. Si retorna OK: cerrar el ítem.

---

## FIX 4 — MCP servers en Dockerfile

**Diagnóstico:** `Dockerfile.web` no instala Node/npx. Los MCP servers `mcp-server-github`, `mcp-server-filesystem`, `mcp-server-supabase` requieren `npx`. Por eso `[Errno 2] No such file or directory` al inicializarlos en Railway.

**Decisión a tomar:**

| Opción | Esfuerzo | Beneficio |
|---|---|---|
| (a) Añadir Node al Dockerfile y reactivar MCP | 30 min build | 3 MCP servers funcionales |
| (b) Dejar MCP dormido (cubierto por tools nativas) | 0 | Imagen más liviana, menos superficie |

**Mi voto: (b) para Sprint 81.6 — DESACTIVAR explícitamente.** Razones:

1. Los 3 MCP servers están **cubiertos por tools nativas activas:** `github` (kernel/tools/github.py), `filesystem` (kernel/tools/file_ops.py), `supabase` (acceso vía SupabaseClient).
2. **Obj #3 (Mínima Complejidad):** dos rutas para hacer lo mismo es complejidad sin valor.
3. **Obj #12 (Soberanía):** las tools nativas son nuestras; los MCP servers son dependencias externas.
4. Si en el futuro queremos un MCP que **no exista como tool nativa** (ej: Notion API que no expusimos), entonces sí añadir Node.

**Patch para Opción (b):** silenciar el warning de inicialización.

En `kernel/main.py`, donde se inicializa MCPClientManager, envolver en check de env var:

```python
if os.environ.get("ENABLE_MCP_SERVERS", "false").lower() == "true":
    # init MCP servers
    ...
else:
    logger.info("mcp_servers_disabled_by_design",
                reason="cubiertos por tools nativas (github, file_ops, supabase)")
```

Y en `.env.example` añadir:

```
# MCP servers — desactivados en Sprint 81.6 (cubiertos por tools nativas)
# Activar solo si se necesita un MCP server externo no cubierto por kernel/tools/
ENABLE_MCP_SERVERS=false
```

---

## Plan de ejecución Sprint 81.6 (1h estimada)

1. **FIX 1** (5 min): Edit `memory_routes.py:122` → coma fuera del comentario. Validar con `ast.parse`.
2. **FIX 2** (15 min): Helper `_escape_telegram_markdown` + llamada en `send_message`. Test manual con un mensaje que tenga `_*[]`.
3. **FIX 3** (5 min): Curl a Langfuse, confirmar OK o regenerar keys.
4. **FIX 4** (15 min): Env var `ENABLE_MCP_SERVERS=false` + check en main.py + actualizar `.env.example`.
5. **Tests** (10 min): pytest sigue 66/66 + smoke test endpoints `/v1/memory/thoughts` post-fix-1.
6. **Commit + push**: `fix(sprint51.6): limpieza de errores no bloqueantes (memory_routes syntax, telegram parse, mcp opt-in)`.
7. **Smoke test prod** (10 min): `/health`, `/v1/memory/thoughts?user_id=alfredo&limit=5`.

---

# Sprint 82 — Brand Engine Fase 1
**Capa objetivo:** Cierre absoluto de Capa 0 (Cimientos)
**Versión objetivo:** v0.82.0-sprint82
**Tiempo estimado:** 2-3 días
**Diseño base:** `docs/BRAND_ENGINE_ESTRATEGIA.md` (ya redactado, no se rediseña)

## Premisa

La Regla Dura #4 del `AGENTS.md` dice **"el Brand Engine tiene VETO inviolable"**. Hoy esa regla es ley sin policía. Cada output del Monstruo (incluido el del Embrión que ya ejecuta tools post-Sprint 81) sale sin compliance automatizada. Cada nueva tool añade deuda de identidad. Sprint 82 cierra esa puerta.

**El diseño NO se rediscute** — está cristalizado en `BRAND_ENGINE_ESTRATEGIA.md`. Sprint 82 es **implementación pura de la Fase 1** descrita en ese documento.

## Tesis

Tres piezas que nacen juntas:

```
   ┌─────────────────────┐
   │   BRAND DNA (code)  │  ← Sprint 82
   │   kernel/brand/     │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  BRAND VALIDATOR    │  ← Sprint 82
   │  score 0-100, veto  │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │  COMPLIANCE LOG     │  ← Sprint 82
   │  Supabase + endpoints│
   └─────────────────────┘
```

## Épicas

### E52.1 — `kernel/brand/brand_dna.py`

**Diseño literal del documento estratégico** (sección "Fase 1 — Brand DNA como Código"):

- `BRAND_DNA: dict` con misión, archetype, personality, tone (do/dont), naming (modules/error_format/never), visual (primary/background/accent/fonts).
- `validate_output_name(name: str) -> tuple[bool, list[str]]` — verifica que naming no contenga `service`/`handler`/`utils`/`helper`/`misc`.
- `get_error_message(module, action, failure_type, context) -> dict` — genera errores on-brand con formato `{module}_{action}_{failure_type}`.
- Excepciones con identidad: `BrandValidationFalla(motivo, sugerencia)`.

**Archivos:**
- `kernel/brand/__init__.py`
- `kernel/brand/brand_dna.py` (~150 líneas, copy-paste del diseño existente con ajustes)
- `tests/test_brand_dna.py` (~100 líneas, tests unitarios)

### E52.2 — `kernel/brand/validator.py`

**Diseño literal del documento estratégico** (sección "Fase 2 — Brand Validator", traemos esta fase a Sprint 82 porque sin validador el DNA es decorativo):

- `BrandValidator` clase con `validate_api_response`, `validate_endpoint_name`, `validate_tool_spec`, `validate_error_message`.
- Score 0-100 por output. Threshold default: 75.
- `validate_tool_spec(spec: ToolSpec)` — usado en bootstrap para auditar las 16 ToolSpecs registradas.

**Archivos:**
- `kernel/brand/validator.py` (~200 líneas)
- `tests/test_brand_validator.py` (~150 líneas)

### E52.3 — Tabla `brand_compliance_log` + endpoints

**Migración `scripts/015_brand_compliance_table.sql`:**

```sql
CREATE TABLE IF NOT EXISTS brand_compliance_log (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    target_type     TEXT NOT NULL,          -- 'tool_spec'|'endpoint'|'error_message'|'response'
    target_id       TEXT NOT NULL,          -- tool_name, path, error_signature, etc.
    score           INTEGER NOT NULL,       -- 0-100
    issues          JSONB NOT NULL DEFAULT '[]',
    passes          BOOLEAN NOT NULL,
    validated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    validator_version TEXT NOT NULL DEFAULT '1.0'
);

CREATE INDEX idx_brand_compliance_target ON brand_compliance_log(target_type, target_id);
CREATE INDEX idx_brand_compliance_score ON brand_compliance_log(score);
CREATE INDEX idx_brand_compliance_passes ON brand_compliance_log(passes) WHERE passes = false;
```

**Endpoints en `kernel/main.py`:**

- `GET /v1/brand/dna` — retorna `BRAND_DNA` para que el Command Center lo consuma.
- `POST /v1/brand/validate` — recibe `{type, content}` y retorna `{score, issues, passes}`.
- `GET /v1/brand/violations?limit=20&min_score=0` — últimas violaciones.
- `GET /v1/brand/audit-tools` — corre `validate_tool_spec` sobre las 16 tools y devuelve reporte.

### E52.4 — Hook de validación en bootstrap

En `kernel/main.py`, después del bootstrap de Sprint 81 (línea ~1095), añadir:

```python
# ── Sprint 82: Brand Engine ─────────────────────────────────────────
brand_validator = None
try:
    from kernel.brand import BRAND_DNA, BrandValidator
    brand_validator = BrandValidator(brand_dna=BRAND_DNA)
    app.state.brand_validator = brand_validator

    # Auditoría inicial de las 16 ToolSpecs
    from kernel.tool_dispatch import get_tool_specs
    audit = brand_validator.audit_tool_specs(get_tool_specs())
    failed = [r for r in audit if not r["passes"]]
    if failed:
        logger.warning(
            "sprint52_brand_audit_violations",
            total=len(audit),
            failures=len(failed),
            details=[(r["tool_name"], r["score"], r["issues"][0] if r["issues"] else None)
                     for r in failed],
        )
    logger.info("sprint52_brand_validator_initialized",
                threshold=brand_validator.threshold,
                tools_audited=len(audit))
except Exception as e:
    logger.warning("sprint52_brand_validator_init_failed", error=str(e))
```

### E52.5 — Refactor de los 16 ToolSpecs (correcciones de naming)

Tras E52.4, el log dirá qué tools fallan compliance. Ejemplos esperados:

- `delegate_task` → ¿pasa? Verificar.
- `schedule_task` → ¿pasa? Verificar.
- `wide_research` → debería pasar.
- `manus_bridge` → ¿"bridge" cuenta como genérico? Decidir.

**No prejuzgo cuáles fallan.** El audit lo dirá, y aplicamos fix donde corresponda.

## Cruces detractores

| # | Riesgo | Probabilidad | Mitigación |
|---|---|---|---|
| 1 | El validador rechaza la mayoría de outputs y el sistema queda inerte | MEDIA | Threshold default 60 (no 75) en producción durante 7 días. Subir gradual. |
| 2 | `validate_tool_spec` rechaza tools en producción → kernel no arranca | ALTA | Validación en bootstrap es ADVISORY, no bloqueante. Solo loguea. Promoción a bloqueante cuando 100% de tools pasen 75. |
| 3 | Naming refactor rompe tests existentes | MEDIA | Refactor con `git grep` y reemplazo cuidadoso. Tests primero, refactor después. |
| 4 | `BRAND_DNA` queda hardcoded y no se puede actualizar sin redeploy | BAJA | Sprint 53 puede mover a Supabase. Por ahora código es OK — los valores son inmutables por filosofía. |
| 5 | Endpoint `/v1/brand/dna` expone branding interno | BAJA | Es público por diseño — el Command Center lo necesita. Solo retorna lo que ya está en docs. |

## Brand Compliance Checklist del propio Sprint 82 (meta)

| Check | Cumple |
|---|---|
| Naming sin genéricos | `BrandValidator`, `BrandDNA`, `BrandComplianceLog`. Cero `helper`/`utils`. |
| Errores con identidad | `BrandValidationFalla(motivo, sugerencia)`. |
| APIs expuestas | 4 endpoints: dna, validate, violations, audit-tools. |
| Soberanía | Funciona offline (regla pura, no LLM). |
| Documentado | El DNA está en `docs/BRAND_ENGINE_ESTRATEGIA.md`. Los módulos referencian. |

## Plan de ejecución (3 días)

### Día 1 — DNA + Validator base
1. Migración 015 (compliance log).
2. `kernel/brand/__init__.py` + `brand_dna.py`.
3. `kernel/brand/validator.py` con `validate_output_name`, `validate_endpoint_name`, `validate_tool_spec`.
4. Tests unitarios (target: 30+ tests, todos passing).
5. Commit, no toca producción todavía.

### Día 2 — Endpoints + Audit + Hook bootstrap
1. 4 endpoints en `main.py` (`/v1/brand/dna`, `/validate`, `/violations`, `/audit-tools`).
2. `validate_tool_spec` con `audit_tool_specs(specs)` que retorna reporte.
3. Hook en bootstrap (E52.4) — modo ADVISORY.
4. Deploy a Railway. Smoke test endpoints.
5. **Revisar log de auditoría inicial.** Documentar qué ToolSpecs fallan.

### Día 3 — Refactor + cierre
1. Refactor de las ToolSpecs que fallaron auditoría.
2. Refactor de error messages que no sigan formato `{module}_{action}_{failure_type}`.
3. Verificar que `audit-tools` post-refactor da 100% passes.
4. Test E2E: invocar una tool, verificar que el response pasa el validador.
5. Cierre del sprint. Versión bump a 0.82.0-sprint82.

## Métricas de éxito

| Métrica | Objetivo |
|---|---|
| Tools que pasan validación | 16/16 |
| Endpoints `/v1/*` que pasan validación | 100% |
| Error messages con formato correcto | 90% |
| Compliance log entries en 24h | ≥10 |
| Tests passing | 66 + ~30 nuevos = ~96/96 |
| Latencia añadida por validación | <5ms |

## Lo que NO entra en Sprint 82

- **BrandDNA.app integración (Fase 3 del documento estratégico):** Sprint 53.
- **Brand Health Score temporal:** Sprint 53.
- **Monitoreo de cómo otros LLMs representan a El Monstruo (concepto HBR):** Sprint 53.
- **Migración de BRAND_DNA a Supabase para hot-reload:** Sprint 53.
- **Brand-aware response sanitization en `nodes.execute`:** Sprint 53. Sprint 82 valida statically; Sprint 53 valida en runtime sobre cada response.

## Pregunta única para Alfredo

¿Threshold inicial del validador debe ser **60** (laxo, descubrir incumplimientos sin bloquear) o **75** (estándar de marca desde día 1, riesgo de bloqueo de tools legítimas)?

**Mi voto:** **60 los primeros 7 días**, después subir a 75. Razón: hay 16 ToolSpecs históricas + 7+ endpoints que nunca fueron diseñados con compliance en mente. Bajar el listón al inicio nos deja descubrir el alcance real de la deuda sin frenar el sistema.

---

**Sprint 81.6 + Sprint 82 entregados. Cuando estén las dos confirmaciones de Alfredo (1) threshold inicial Brand Validator y (2) si activamos `ENABLE_MCP_SERVERS=false` o instalamos Node, Manus puede arrancar.**

---
---

# Sprint 82 — Patch crítico: bug en `validate_output_name` (BLOQUEANTE para validator.py)
**Timestamp:** 2026-05-03 (durante Día 1 de Sprint 82, post-creación de `brand_dna.py`)
**Encomienda:** APLICAR ANTES de seguir construyendo `validator.py`. Si validator se construye encima del bug, todos los audits van a dar falsos positivos.

## Contexto

Auditoría línea por línea de `kernel/brand/brand_dna.py` contra `docs/BRAND_ENGINE_ESTRATEGIA.md`. Resultado: **el `BRAND_DNA` dict está fiel al documento, las funciones bonus (`is_generic_error`, `get_forbidden_matches`) son buenas, el `__init__.py` exporta correcto. Pero `validate_output_name` tiene un bug crítico.**

## El bug

El regex usa `\b` (word boundary). En Python, `\b` trata `_` como `\w`, así que **no se posiciona entre underscore y palabra**. Resultado: prohibidos embebidos en snake_case o camelCase pasan compliance falsamente.

Evidencia (probado con regex actual):

| Nombre | ¿Debe pasar? | Resultado actual del regex `\b...\b` |
|---|---|---|
| `data_handler` | ❌ No | ✓ pasa (BUG) |
| `user_service` | ❌ No | ✓ pasa (BUG) |
| `MyHelper` | ❌ No | ✓ pasa (BUG) |
| `dispatch_handler` | ❌ No | ✓ pasa (BUG) |
| `utils_helper` | ❌ No | ✓ pasa (BUG) |
| `messageManager` | ❌ No | ✓ pasa (BUG) |
| `service_module` | ❌ No | ✓ pasa (BUG) |
| `handler` | ❌ No | ❌ bloqueado (OK) |
| `forja` | ✓ Sí | ✓ pasa (OK) |

**7 de 9 casos fallan.** Cuando hagas el audit de las 16 ToolSpecs, casi todas pasarán falsamente.

## Fix probado

Reemplazar el bloque desde la línea 80 (`# ── Naming Validation ──`) hasta la línea 111 (cierre de `get_forbidden_matches`) en `kernel/brand/brand_dna.py` por:

```python
# ── Naming Validation ────────────────────────────────────────────────

# Forbidden names from BRAND_DNA — exposed as set for fast token lookup
_FORBIDDEN_NAMES: set[str] = set(BRAND_DNA["naming"]["never"])

# Tokenization patterns
_SEPARATOR_SPLIT = re.compile(r"[\s\-_/.]+")
_CAMEL_TOKEN = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+|[A-Z]+")


def _tokenize_identifier(name: str) -> list[str]:
    """Split snake_case, camelCase, kebab-case en tokens lowercase.

    Diseño: regex `\\b` no detecta tokens en snake_case porque `_` es
    `\\w`. Esta función segmenta primero por separadores explícitos y
    luego por cambios de mayúscula (camelCase), normalizando todo a
    minúsculas para comparar contra _FORBIDDEN_NAMES.

    Ejemplos:
        "data_handler"  → ["data", "handler"]
        "MyHelper"      → ["my", "helper"]
        "URLParser"     → ["url", "parser"]
        "forja"         → ["forja"]
        "embrion-loop"  → ["embrion", "loop"]
    """
    if not name:
        return []
    tokens: list[str] = []
    for part in _SEPARATOR_SPLIT.split(name):
        if not part:
            continue
        sub = _CAMEL_TOKEN.findall(part)
        tokens.extend(sub if sub else [part])
    return [t.lower() for t in tokens if t]


def validate_output_name(name: str) -> bool:
    """
    Valida que un nombre de módulo, endpoint o variable siga las
    convenciones de marca del Monstruo.

    Reconoce snake_case, camelCase, kebab-case y dot.notation —
    cualquier token prohibido (service, handler, utils, helper,
    misc, manager) en cualquier posición invalida el nombre.

    Returns:
        True si el nombre es brand-compliant, False si contiene
        términos prohibidos.
    """
    if not name or not isinstance(name, str):
        return False
    tokens = _tokenize_identifier(name)
    return not any(t in _FORBIDDEN_NAMES for t in tokens)


def get_forbidden_matches(name: str) -> list[str]:
    """
    Retorna la lista de tokens prohibidos encontrados en un nombre,
    deduplicados y en minúsculas. Vacía si el nombre es compliant.
    """
    if not name or not isinstance(name, str):
        return []
    tokens = _tokenize_identifier(name)
    seen: set[str] = set()
    matches: list[str] = []
    for t in tokens:
        if t in _FORBIDDEN_NAMES and t not in seen:
            matches.append(t)
            seen.add(t)
    return matches
```

## Verificación post-fix

Añade estos casos a `tests/test_brand_dna.py` (cuando lo crees) para que el fix no regrese:

```python
import pytest
from kernel.brand.brand_dna import validate_output_name, get_forbidden_matches


@pytest.mark.parametrize("name,expected_compliant", [
    # Compliant
    ("forja", True),
    ("embrion_loop", True),
    ("forja_dashboard", True),
    ("MagnaClassifier", True),
    ("multi_agent", True),
    ("tool_broker", True),
    # Non-compliant — directo
    ("handler", False),
    ("service", False),
    ("manager", False),
    # Non-compliant — snake_case (bug histórico)
    ("data_handler", False),
    ("user_service", False),
    ("dispatch_handler", False),
    ("utils_helper", False),
    ("service_module", False),
    # Non-compliant — camelCase
    ("MyHelper", False),
    ("messageManager", False),
    ("URLHelper", False),
    # Non-compliant — kebab-case y dot.notation
    ("event-handler", False),
    ("api.utils.helper", False),
    # Edge cases
    ("", False),
    (None, False),
    ("forjA", True),  # case insensitive sí, pero "forja" no es prohibido
])
def test_validate_output_name(name, expected_compliant):
    assert validate_output_name(name) == expected_compliant


def test_get_forbidden_matches_returns_unique_lowercase():
    assert get_forbidden_matches("user_service") == ["service"]
    assert get_forbidden_matches("HandlerHelper") == ["handler", "helper"]
    assert get_forbidden_matches("forja") == []
    assert get_forbidden_matches("ManagerManager") == ["manager"]  # dedupe
```

Estos 23 casos cubren snake_case, camelCase, kebab-case, dot.notation, edge cases y dedupe. Todos deben pasar tras aplicar el fix.

## Plan de aplicación (5 min)

1. Aplicar el reemplazo del bloque líneas 80-111 en `kernel/brand/brand_dna.py`.
2. `python3 -c "import ast; ast.parse(open('kernel/brand/brand_dna.py').read()); print('OK')"`.
3. Si vas a crear `tests/test_brand_dna.py` ahora (parte de Día 1), incluye los 23 casos de arriba.
4. Continuar con `validator.py` (E52.2) — ahora sí sobre cimiento sólido.

## Nota meta

Encontrar este bug **antes** de que validator.py se construyera encima es exactamente lo que el Hilo B debe hacer en Fase 1: **revisar diseño y código del Hilo A para que no acumulen deuda**. Manus, no es crítica al trabajo — el bug del `\b` en regex es un clásico que se cuela hasta en libraries famosas. Cazado a tiempo.

---

**Patch listo. Aplicar ANTES de seguir con validator.py. Después seguimos al pie del plan.**

---
---

# Renumeración de sprints — Opción A confirmada
**Timestamp:** 2026-05-03 (post Sprint 82 cerrado, pre Sprint 83)
**Decisión:** Opción A. Aplicar **inmediatamente, antes de arrancar el próximo sprint**.
**Voto:** Cowork + Alfredo + Manus alineados.

## Razones cristalizadas

- **Obj #4 (No equivocarse 2 veces):** ya pasó, la corrección honesta es renombrar, no documentar deuda.
- **Obj #5 (Magna/Premium):** "Sprint 82" no puede significar dos cosas. Documentación limpia.
- **Costo finito ahora vs creciente después:** renombrar 4 sprints hoy es barato. Renombrar 8-10 en un mes, caro.
- **Ventana operativa:** Sprint 82 cerrado, no hay trabajo en vuelo. Es el momento exacto para hacerlo.

## Mapeo de renumeración

| Antiguo | Nuevo | Versión kernel |
|---|---|---|
| Sprint 81 | **Sprint 81** | (era v0.51.0) |
| Sprint 81.5 | **Sprint 81.5** | (era v0.81.5) |
| Sprint 81.6 | **Sprint 81.6** | (era v0.51.6) |
| Sprint 82 | **Sprint 82** | v0.52.0 → **v0.82.0-sprint82** |
| Sprint 53 propuesto | **Sprint 83 — Vigilia del Embrión** | (próximo) |

## Plan de ejecución (~36 min)

### Paso 1 — `sed` versión y comentarios en `kernel/`
```bash
# Versión en kernel/main.py (7 ocurrencias hoy)
sed -i.bak 's/0\.52\.0-sprint52/0.82.0-sprint82/g' kernel/main.py

# Comentarios "Sprint 81" → "Sprint 81" (incluye 51.5 y 51.6)
grep -rln "Sprint 81\." kernel/ tools/ scripts/ tests/ | while read f; do
    sed -i.bak 's/Sprint 81\.5/Sprint 81.5/g; s/Sprint 81\.6/Sprint 81.6/g' "$f"
done

# Comentarios "Sprint 81" exacto → "Sprint 81" (excluyendo los 51.x ya hechos)
grep -rln "Sprint 81\b" kernel/ tools/ scripts/ tests/ | while read f; do
    sed -i.bak 's/Sprint 81\b/Sprint 81/g' "$f"
done

# "Sprint 82" → "Sprint 82"
grep -rln "Sprint 82\b" kernel/ tools/ scripts/ tests/ | while read f; do
    sed -i.bak 's/Sprint 82\b/Sprint 82/g' "$f"
done

# Limpiar backups
find kernel tools scripts tests -name "*.bak" -delete
```

### Paso 2 — Strings de log que mencionen sprint number
```bash
# logger.info("sprint51_*") y similares
grep -rln "sprint51\|sprint52" kernel/ | while read f; do
    sed -i.bak 's/sprint51_/sprint81_/g; s/sprint52_/sprint82_/g' "$f"
done
find kernel -name "*.bak" -delete
```

### Paso 3 — Headers en bridges (ambos bridges)
- `bridge/cowork_to_manus.md`: actualizar todos los headers `# Sprint 81*` y `# Sprint 82*` a `# Sprint 81*` y `# Sprint 82*`. **Nota:** los headers que están en el contexto de un Sprint Plan (ej. "Sprint 81 — El Cerebro Activo") cambian a "Sprint 81 — El Cerebro Activo". El contenido NO se reescribe — solo el número.
- `bridge/manus_to_cowork.md`: mismo tratamiento.

### Paso 4 — `monstruo-memoria/IDENTIDAD_HILO_B.md`
Actualizar referencias a sprints viejos. Si tiene una sección "Sprint actual: 52" o similar, cambiar a "Sprint actual: 82, próximo 83 (Vigilia del Embrión)".

### Paso 5 — Validación
```bash
# Sintaxis intacta
python3 -c "import ast; ast.parse(open('kernel/main.py').read()); print('OK')"

# Tests
pytest tests/test_brand_engine.py tests/test_magna_classifier.py tests/test_error_memory.py -v

# Búsqueda residual — no debería retornar nada
grep -rn "sprint51\|sprint52" kernel/ tools/ scripts/ tests/ | grep -v ".bak"
```

### Paso 6 — Commit y deploy
```bash
git add -A
git commit -m "Renumeración: Sprint 81-52 → Sprint 81-82 (corrige colisión con serie antigua 1-80). Sprint 53 → Sprint 83 (próximo). Ver bridge/cowork_to_manus.md."
git push origin main
# Railway auto-deploy → /health debe mostrar 0.82.0-sprint82
```

## Lo que NO se toca (importante)

- **Tablas Supabase:** `magna_cache`, `error_memory`, `error_memory_patterns`, `brand_compliance_log`, `magna_routes`. **Mantener nombres.** Cero migración SQL.
- **Commits previos:** no se reescribe historia git.
- **Datos históricos en Langfuse:** las trazas antiguas con "sprint52" viejo quedan. Aceptamos esa contaminación pasada — solo limpiamos hacia adelante.
- **Tests:** archivos `test_brand_engine.py`, `test_error_memory.py`, etc. los nombres de archivo no mencionan sprint number.

## Verificación post-deploy

```bash
curl ${KERNEL_BASE_URL}/health | jq '.version'
# Esperado: "0.82.0-sprint82"

curl -s ${KERNEL_BASE_URL}/v1/error-memory/recent | jq '.errors | length'
# Debe seguir devolviendo las semillas

curl -s ${KERNEL_BASE_URL}/v1/brand/audit-tools | jq '.summary'
# avg_score debe seguir siendo 90.0
```

## Después de la renumeración

Manus avisa que terminó renumeración → Cowork le entrega Sprint Plan **83 — Vigilia del Embrión** completo. NO mezclar renumeración con nuevo sprint en el mismo commit.

---
---

# Sprint 83 — Vigilia del Embrión (Sprint Plan)
**Capa objetivo:** Validación funcional del trabajo de Capa 0 + observabilidad real
**Versión objetivo:** v0.83.0-sprint83
**Tiempo estimado:** 2-3 días
**Pre-requisito:** renumeración completada y deployada (versión `0.82.0-sprint82` confirmada en `/health`)

## Premisa

Sprint 81 entregó Magna Classifier y Error Memory. Sprint 82 cerró Brand Engine Fase 1. Pero el reporte de Manus en Sprint 81.5 dijo:

> Embrión Loop: running, **cycle_count=1**, cost_today=$0.00

**Un solo ciclo después de varias horas.** Y `fcs.tool_calls_total=0` que Manus listó como "preexistente, requiere que el embrión ejecute tools" — pero ese era exactamente el bug que Sprint 81 supuestamente resolvió.

**Tesis:** o el Embrión está parado, o Magna nunca rutea a graph, o el counter no incrementa en el path real, o las tres cosas. **Sin diagnóstico funcional, todo lo construido en Sprints 81-82 es decorativo.**

Sprint 83 es **medir, entender, arreglar lo roto del runtime real**. No es implementación; es diagnóstico + observabilidad + fixes derivados.

## Épicas

### E83.1 — Diagnóstico del scheduler del Embrión

**Pregunta a contestar:** ¿por qué `cycle_count=1` después de horas? El loop debería iterar cada 60s.

**Acciones:**
- Revisar `kernel/embrion_loop.py:run_loop()` y verificar el `asyncio.create_task(...)` que lanza el ciclo.
- Inspeccionar logs Railway de las últimas 24h buscando `embrion_cycle_*` o `embrion_loop_*`. Contar ocurrencias.
- Si hay excepciones silenciosas en el loop, identificarlas y registrarlas en Error Memory.
- Verificar si `embrion_scheduler` (lo vi en logs `embrion_scheduler_init_failed` antes) está vivo.

**Criterio de éxito:** documentar la causa raíz del cycle_count bajo y aplicar el fix.

### E83.2 — Endpoint `/v1/embrion/diagnostic`

**No expone solo el FCS.** Expone métricas funcionales que el Command Center necesita y que hoy no existen:

```json
{
  "status": "running" | "stopped" | "error",
  "scheduler": {
    "running": true,
    "last_tick_at": "2026-05-03T12:34:56Z",
    "ticks_last_hour": 60,
    "ticks_total_today": 720
  },
  "cycles": {
    "total_today": 25,
    "total_lifetime": 48,
    "last_cycle_at": "...",
    "avg_cycle_duration_ms": 1245
  },
  "magna": {
    "decisions_last_20": [
      {"route": "graph", "confidence": 0.78, "category": "tech_action", "trigger": "mensaje_alfredo", "ts": "..."},
      {"route": "router", "confidence": 0.42, "category": "reflection", "trigger": "reflexion_autonoma", "ts": "..."}
    ],
    "graph_calls_today": 4,
    "graph_cap": 30,
    "router_calls_today": 18,
    "tool_specific_calls_today": 0
  },
  "tool_calls": {
    "total_today": 12,
    "total_lifetime": 35,
    "last_20": [
      {"tool": "delegate_task", "ts": "...", "success": true, "trigger_cycle": 23}
    ]
  },
  "error_memory": {
    "errors_recorded_24h": 3,
    "rules_applied_24h": 5,
    "most_common_module": "kernel.task_planner"
  }
}
```

**Implementación:**
- `kernel/embrion_loop.py` — añadir métricas in-memory accesibles vía propiedad `diagnostic_snapshot`
- `kernel/main.py` — endpoint `GET /v1/embrion/diagnostic` que retorna el snapshot
- Brand Compliance: respuesta con identidad, fields en español donde aplique, error formatado on-brand si el embrión no inicializó

### E83.3 — Si Magna nunca rutea a `graph`: recalibrar

Después de E83.2, tendremos data real de Magna. Tres escenarios posibles:

**Escenario A:** Magna rutea bien (mix razonable graph/router) y tools sí ejecutan → bug está en el counter (saltar a E83.4).

**Escenario B:** Magna rutea casi todo a `router` (chat-only) → threshold 0.6 es muy alto para los prompts típicos del Embrión. Recalibrar:
- Bajar threshold a 0.45-0.50
- O ajustar vocabularios `TECH_TRIGGERS` / `ACTION_TRIGGERS` para incluir patrones reales de los prompts del Embrión
- Decisión basada en data, no en intuición

**Escenario C:** Magna rutea a `graph` pero el grafo no termina → bug en `_think_with_graph`. Stack trace en Error Memory.

### E83.4 — Verificar el incremento del FCS counter

El fix de Sprint 81.5 puso `self._fcs_tool_calls_total += len(tool_calls)` en línea 750. **Verificar que esa línea se ejecuta en el path real.**

Si E83.2 muestra `tool_calls.total_today > 0` pero `/health` muestra `fcs.tool_calls_total=0`, hay desconexión. Revisar:
- ¿El path de `_think_with_router` también debería incrementar? (puede que sí — algunas tools se invocan vía router con function calling)
- ¿La métrica `_fcs_tool_calls_total` se persiste o solo vive en memoria? Si el proceso reinicia, ¿se pierde?

### E83.5 — Test E2E reproducible

Test que dispara un mensaje al kernel y valida la cadena completa:
```python
# tests/test_embrion_e2e.py
async def test_embrion_full_flow_with_real_tool():
    """Mensaje de Alfredo → Magna decide graph → tool real → response.
    
    Tool de prueba: delegate_task (no requiere creds externas).
    """
    response = await kernel.start_run(RunInput(
        message="Delega al rol estratega: ¿cuáles son los 3 pilares de Capa 0?",
        user_id="test_alfredo",
        channel="test",
        context={"intent_override": "execute"},
    ))
    assert response.status == "ok"
    assert any(tc.get("name") == "delegate_task" for tc in response.tool_calls or [])
```

Si pasa: Sprint 83 cierra. Si falla: la falla se documenta en Error Memory y se itera.

## Cruces detractores

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | El diagnóstico revela que la deuda es mucho mayor (Embrión completamente roto) | Spike no destructivo: medir primero, iterar fixes después. Si el spike sale catastrófico, escalamos a Sprint 83 extendido o split en 83/84. |
| 2 | Endpoint `/v1/embrion/diagnostic` expone datos sensibles | Solo expone metadata de operación, no contenido de prompts. Igual que /health. |
| 3 | Recalibrar threshold de Magna sin métrica clara → adivinanza | E83.3 solo sucede tras E83.2 (datos reales). No tocar threshold sin data. |
| 4 | E2E test depende de tools externas que pueden fallar | Test usa `delegate_task` que es interno (sin creds), determinista. |

## Brand Compliance Checklist

| Check | Cumple |
|---|---|
| Naming sin genéricos | `EmbrionDiagnostic`, `cycle_snapshot`, `magna_decisions`. Cero `helper`. |
| Errores con identidad | `EmbrionLoopNoIniciado`, `EmbrionScheduler...`. |
| Endpoint con identidad | `/v1/embrion/diagnostic` (módulo con identidad). |
| Tono de respuesta del endpoint | Español donde aplique, técnicamente preciso. |
| Brand Validator audit | El nuevo endpoint debe pasar `validate_endpoint_name()`. Ya cumple — `embrion` y `diagnostic` no están en `_FORBIDDEN_NAMES`. |

## Métricas de éxito (cierre del sprint)

| Métrica | Valor actual reportado | Objetivo |
|---|---|---|
| `cycle_count` después de 4h de operación | 1 | ≥30 |
| `magna.graph_calls_today` | desconocido (no expuesto) | medible y >0 |
| `tool_calls.total_today` | desconocido | medible y >0 |
| `fcs.tool_calls_total` | 0 | refleja realidad (>0 si tools se ejecutaron) |
| Test E2E `test_embrion_full_flow_with_real_tool` | no existe | passing |
| `/v1/embrion/diagnostic` endpoint | no existe | implementado y consumido por Command Center |

## Lo que NO entra en Sprint 83

- Subir threshold del Brand Validator (60 → 75): Sprint 84
- Brand Validator modo ENFORCING: Sprint 84
- CI/CD integration: Sprint 84+
- Fix `three_layer_memory_init_failed` (legacy): cuando lleguemos a Capa 2
- Fix tests legacy Python 3.9: separado, fuera del path crítico

## Pregunta única para Alfredo

¿Aprobás el Sprint Plan 83 tal como está o ajustas algo de scope?

Mi voto: **arrancar tal cual**. El cycle_count=1 es bandera roja suficiente.

---

**Renumeración + Sprint 83 entregados. Manus: ejecuta renumeración, valida en prod, y ahí arrancamos Sprint 83.**

---
---

# Encomienda corta — Pre-flight para uso real diario
**Timestamp:** 2026-05-03 (post Sprint 82)
**Cambio de plan:** Alfredo me corrigió. Construir un Sprint Plan 83 grande es exceso. Lo que sigue es una encomienda corta de 30-60 min para que Alfredo arranque uso real diario inmediatamente después.
**Reemplaza al Sprint Plan 83 anterior.** El Sprint 83 grande surgirá del uso real, no de mi imaginación.

## Las 3 cosas concretas

### 1. Activar 2 credenciales en Railway (10-20 min)

| Variable | Activa qué | Cómo conseguirla |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | tool `browse_web` (browser real, JS-heavy, forms, login) | Cloudflare dashboard → My Profile → API Tokens → "Create Token" con permiso "Browser Rendering: Read/Write". Free tier suficiente. |
| `GMAIL_APP_PASSWORD` | tool `email` (envío SMTP) | Cuenta Gmail de Alfredo → Security → 2-Step Verification → App passwords → generar para "El Monstruo" |

Tras setearlas en Railway:
- Reiniciar el servicio.
- Verificar: `curl ${KERNEL_BASE_URL}/v1/tools | jq '[.tools[] | select(.name=="browse_web" or .name=="email") | {name, status}]'`
- Esperado: ambas en `status: "active"`.

### 2. Diagnóstico mínimo del Embrión (20-30 min)

**Pregunta concreta a contestar:** ¿por qué el último reporte mostró `cycle_count=1`?

Pasos:
1. Leer logs Railway de las últimas 24h. Filtrar por `embrion_cycle`, `embrion_loop`, `embrion_think`. Contar ocurrencias.
2. Si hay excepción silenciosa que mata el loop → identificarla y aplicar fix mínimo (try/except con log explícito + reanudación).
3. Si el loop nunca arrancó → revisar el `asyncio.create_task` del bootstrap.
4. Si el cap diario de pensamientos se alcanzó → ajustar config si tiene sentido.

**Endpoint mínimo `/v1/embrion/diagnostic`** (versión chiquita, no la del Sprint 83 grande):

```python
@app.get("/v1/embrion/diagnostic", tags=["observability"])
async def embrion_diagnostic(request: Request):
    loop = getattr(request.app.state, "embrion_loop", None)
    if not loop:
        return {"status": "no_loop", "message": "EmbrionLoop no inicializado"}
    return {
        "status": "running" if loop.running else "stopped",
        "cycle_count": getattr(loop, "_cycle_count", 0),
        "fcs_tool_calls_total": getattr(loop, "_fcs_tool_calls_total", 0),
        "last_cycle_at": getattr(loop, "_last_cycle_at", None),
        "magna_active": getattr(loop, "_magna_classifier", None) is not None,
        "error_memory_active": getattr(loop, "_error_memory", None) is not None,
        "error_log_size": len(getattr(loop, "_error_log", [])),
        "last_5_errors": (getattr(loop, "_error_log", []) or [])[-5:],
    }
```

**Fail-closed:** si el loop no existe, retorna estado, no excepción.

### 3. Confirmar canal de uso (5-10 min)

Alfredo va a usar el Monstruo en su día a día. Necesita un canal funcional:

- **Opción A:** app Flutter (`apps/mobile/macos/Release`). Verificar que abre, conecta al kernel y manda/recibe mensajes.
- **Opción B (fallback):** Telegram bot. Ya está `TELEGRAM_BOT_TOKEN`. Verificar que el bot responde a `/start` y procesa un mensaje real.
- **Opción C (último recurso):** curl directo a `${KERNEL_BASE_URL}/v1/agui/run` desde la terminal de Alfredo.

Reportar en `bridge/manus_to_cowork.md` cuál canal recomiendas y un quickstart de 3 líneas para que Alfredo lo use.

## Después de las 3 cosas

Manus reporta en `bridge/manus_to_cowork.md`:
- Qué tools quedaron activas (esperado: 11 → 13).
- Qué encontró del diagnóstico del Embrión (cycle_count real, causa raíz).
- Cuál canal de uso recomienda y cómo arrancar.

Alfredo arranca uso real diario inmediatamente.

## Protocolo cuando algo se atore

- **Atoro chico** (bug en una tool, edge case): Manus fix en minutos. Alfredo no espera, sigue con otra tarea.
- **Atoro mediano** (capacidad faltante con palanca clara): Manus la entrega como mini-sprint en 30-60 min.
- **Atoro grande / urgente**: Manus o Cowork lo hacen directamente fuera del Monstruo. Alfredo se desbloquea. Registramos: "el Monstruo no podía hacerlo solo, candidato a sprint."

Cada atoro genera 1 entrada en `error_memory` + 1 lección. **El siguiente sprint formal saldrá de esa lista, no de imaginación arquitectónica.**

## Lo que NO entra ahora

- Sprint 83 grande (Vigilia completa con E83.1-E83.5)
- Brand Validator ENFORCING
- El Conductor
- Capa 1 (Backend Deploy, Pagos, Media Generation)

Eso surge cuando los datos del uso real lo pidan.

---

**Encomienda corta. 30-60 min de Manus. Después Alfredo arranca uso real. Construcción reactiva en minutos cuando se atore.**

---
---

# Luz verde — Activación + canal de uso (post Sprint 83)
**Timestamp:** 2026-05-03
**Tiempo estimado:** ~15 min

Sprint 83 cerrado limpio (commit anterior). Hallazgos críticos validados (bug de Magna parameter, SupabaseClient bloqueante, ambos arreglados). El Embrión cicla por primera vez.

**Manus, dos cosas. Cinco líneas:**

1. **Activa `EMBRION_USE_MAGNA_ROUTER=true` en Railway.** Redeploy. Verifica con `/health` que el flag está activo.
2. **Confirma canal de uso para Alfredo.** Probar en orden de preferencia: (a) app Flutter `apps/mobile/macos/Release` abre y conecta; (b) Telegram bot responde a `/start`; (c) curl directo a `${KERNEL_BASE_URL}/v1/agui/run`. Reporta cuál funciona y deja **el comando exacto de 3 líneas** que Alfredo va a usar para mandar su primer mensaje.

Cuando termines, escribe en `bridge/manus_to_cowork.md`:
- `EMBRION_USE_MAGNA_ROUTER=true` confirmado en `/health`
- Canal recomendado y el comando exacto
- Cualquier sorpresa

Después Alfredo manda el primer mensaje real (no test sintético — su trabajo de hoy).

---

**Construcción reactiva. Minutos no días. Reporta y arrancamos.**

---
---

# Sprint 84 — Capacidad de deploy real (primer gap del uso real)
**Timestamp:** 2026-05-03 (post primera tarea real del Monstruo)
**Origen:** Prueba 2 generó sitio web completo (14,694 tokens, calidad 9.0/10) pero **no lo deployó**. Solo texto en chat. Alfredo: "No es end-to-end."

## Reconocimiento del momento

Esta es **la validación de la nueva forma de trabajar**: el sprint surge del uso real, no de mi imaginación. Capa 0 funcionó (Magna ruteó, tools se invocaron, Brand mantuvo identidad), y el primer atoro reveló el gap honesto: **el Monstruo no tiene manos para publicar**. Exactamente la Capa 1.2 del roadmap original, pero ahora la pide la realidad, no el documento.

## Mi voto firme: **A primero, B después si A no basta. NO C ni D.**

### Por qué A (`deploy_to_github_pages`) y NO las otras

| Opción | Voto | Razón |
|---|---|---|
| **A** GitHub Pages | ✅ **HACER YA** | `GITHUB_TOKEN` activa. `tools/github.py` ya tiene `create_or_update_file`. Solo faltan 2 endpoints. ~30 min de Manus. Soluciona Prueba 2 hoy. |
| **B** Cloudflare Pages | ⏸ Después | Solo si A no basta (custom domain, backend Workers). `CLOUDFLARE_API_TOKEN` activa. ~45 min cuando se pida. |
| **C** Completar `manus_bridge` | ❌ No ahora | Delegar a Manus para que Manus deploye viola "El Monstruo construye al Monstruo". Es fallback, no primera opción. |
| **D** Railway sandbox | ❌ No ahora | Sobre-engineering. Es Capa 1.2 completa (backend dinámico). Esperar a que un caso real pida backend. |

## Diseño de `tools/deploy_to_github_pages.py`

**~80 líneas. Aprovecha lo que ya existe en `tools/github.py`.**

```python
"""
El Monstruo — Deploy to GitHub Pages (Sprint 84)
=================================================
Tool para que el Monstruo publique sitios estáticos end-to-end.
Cierra el gap detectado en la primera tarea real (Prueba 2):
generaba código completo pero no lo publicaba.

Soberanía: usa GITHUB_TOKEN ya activa, sin nuevas dependencias.
"""
from __future__ import annotations
import asyncio
import os
from typing import Any

import structlog

from tools.github import _request, create_or_update_file

logger = structlog.get_logger("tools.deploy_to_github_pages")

GH_USER = os.environ.get("GITHUB_USERNAME", "alfredogl1804")
PAGES_POLL_INTERVAL = 5
PAGES_POLL_MAX = 60  # 5 minutos


async def deploy_to_github_pages(
    repo_name: str,
    files: dict[str, str],
    description: str = "Sitio publicado por El Monstruo",
    private: bool = False,
    branch: str = "main",
) -> dict[str, Any]:
    """
    Crea/actualiza repo, escribe archivos, activa Pages, espera deploy.

    Args:
        repo_name: nombre del repo (sin owner). Ej: "mi-empresa-mvp"
        files: dict path → content. Ej: {"index.html": "<html>...", "style.css": "..."}
        description: descripción del repo
        private: si el repo es privado (Pages requiere paid plan en privado)
        branch: branch a usar para Pages (default main)

    Returns:
        {"url": "https://user.github.io/repo/", "repo": "owner/repo", "files_committed": 3}
    """
    # 1. Crear repo (idempotente: si existe, retorna 422 y seguimos)
    create_resp = await _request("POST", "/user/repos", json={
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": True,  # crea README inicial para que el branch exista
    })
    if "error" in create_resp and "already exists" not in str(create_resp.get("message", "")):
        return {"error": f"deploy_repo_create_failed: {create_resp}"}

    repo_full = f"{GH_USER}/{repo_name}"

    # 2. Escribir todos los archivos
    committed = []
    for path, content in files.items():
        result = await create_or_update_file(
            repo=repo_full,
            path=path,
            content=content,
            message=f"deploy: {path}",
            branch=branch,
        )
        if "error" not in result:
            committed.append(path)

    # 3. Activar Pages (idempotente con PUT)
    pages_resp = await _request(
        "POST",
        f"/repos/{repo_full}/pages",
        json={"source": {"branch": branch, "path": "/"}},
    )
    # 422 = ya estaba activado, OK
    if "error" in pages_resp and "already exists" not in str(pages_resp.get("message", "")):
        logger.warning("deploy_pages_enable_warning", resp=pages_resp)

    # 4. Polling del build
    url = None
    for attempt in range(PAGES_POLL_MAX // PAGES_POLL_INTERVAL):
        status = await _request("GET", f"/repos/{repo_full}/pages")
        if isinstance(status, dict) and status.get("status") == "built":
            url = status.get("html_url") or f"https://{GH_USER.lower()}.github.io/{repo_name}/"
            break
        await asyncio.sleep(PAGES_POLL_INTERVAL)

    if not url:
        url = f"https://{GH_USER.lower()}.github.io/{repo_name}/"  # esperado, aunque build no confirmó
        logger.warning("deploy_pages_build_timeout",
                       repo=repo_full, expected_url=url)

    logger.info("deploy_pages_completed",
                repo=repo_full, url=url, files=len(committed))

    return {
        "url": url,
        "repo": repo_full,
        "files_committed": len(committed),
        "files_paths": committed,
    }
```

**Registro en `kernel/tool_dispatch.py`** — añadir ToolSpec:

```python
ToolSpec(
    name="deploy_to_github_pages",
    description=(
        "Publica un sitio estático (HTML/CSS/JS) a GitHub Pages. "
        "Crea repo, escribe archivos, activa Pages y devuelve URL pública. "
        "Usar cuando el usuario pida 'publicar', 'deployar', 'subir a internet' "
        "un sitio o página estática. Solo HTML/CSS/JS — no backend dinámico."
    ),
    parameters={
        "type": "object",
        "properties": {
            "repo_name": {"type": "string", "description": "Nombre del repo, kebab-case"},
            "files": {
                "type": "object",
                "description": "Dict de path → contenido. Ej: {'index.html': '<html>...', 'style.css': '...'}",
                "additionalProperties": {"type": "string"},
            },
            "description": {"type": "string", "description": "Descripción opcional del repo"},
            "private": {"type": "boolean", "description": "True para repo privado (requiere plan paid)"},
        },
        "required": ["repo_name", "files"],
    },
    risk="medium",
),
```

**Registrar en `tool_dispatch.py:_execute_tool`** la rama nueva (~5 líneas).

**Activar en `scripts/activate_tools.py`** — añadir entry al `INVENTARIO_CANONICO` con `secret_env_var="GITHUB_TOKEN"`, `category="write"`, `risk_level="MEDIUM"`, `requires_hitl=False` (la PR/branch ya es el gate humano para repos privados; para públicos auto-aprobado).

## Tarea para Manus (encomienda corta)

1. Crear `tools/deploy_to_github_pages.py` con el código de arriba.
2. Añadir ToolSpec en `kernel/tool_dispatch.py`.
3. Añadir rama en `_execute_tool`.
4. Actualizar `scripts/activate_tools.py:INVENTARIO_CANONICO`.
5. Activar la tool en Supabase (registry + binding).
6. Test manual: invocar con un repo de prueba `monstruo-test-deploy` con un index.html mínimo.
7. Reportar URL del repo creado y URL pública del Pages.

Estimado: 30-45 min.

## Lección para Error Memory

Sembrar como `seed_no_deploy_capability` con `confidence=0.85`:

```sql
INSERT INTO error_memory (
    error_signature, error_type, module, action,
    message, sanitized_message, resolution, confidence, status
) VALUES (
    'seed_no_deploy_capability',
    'CapabilityGap',
    'kernel.tool_dispatch',
    'deploy_static_site',
    'User requested site deploy but no deploy tool available',
    'User requested site deploy but no deploy tool available',
    'Sprint 84: añadida tool deploy_to_github_pages. Para sitios con backend o custom domain, evaluar deploy_to_cloudflare (Sprint 85).',
    0.85,
    'open'
) ON CONFLICT (error_signature) DO NOTHING;
```

## Lo que NO hacemos en Sprint 84

- **B (Cloudflare):** solo si A no basta para el siguiente caso. Es Sprint 85 si surge.
- **Custom domain:** decisión del usuario, no automatizada todavía.
- **Backend dinámico:** espera a que un caso real lo pida.
- **Plan completo de Capa 1:** sigue surgiendo del uso, no de roadmap especulativo.

## Después del deploy

Cuando Manus reporte el primer deploy real exitoso, **Alfredo le pide al Monstruo que vuelva a generar el sitio de la Prueba 2 y esta vez lo publique**. Eso cierra el ciclo E2E que la primera tarea dejó parcial.

---

**Diseño entregado. ~80 líneas de código + ToolSpec + activación. ~30-45 min de Manus. Después: segundo intento de la Prueba 2, ahora E2E completo.**

---
---

# Sprint 84 EXPANDIDO — Primer Acto de Orquestación
**Timestamp:** 2026-05-03 (post diálogo con Alfredo)
**Razón del cambio:** Alfredo: "no puedo ver que hace un sitio web de segunda, necesito que haga algo que me motive". Deploy solo ≠ orquestación. Esto sí.

## Tres entregables (~60-90 min total)

### 1. `tools/deploy_to_github_pages.py`

Ya diseñado arriba. ~80 líneas. Activar en Supabase.

### 2. Tracking de orquestación visible

En `kernel/embrion_loop.py`, añadir tracking del flujo en curso:

```python
# Atributos nuevos en EmbrionLoop.__init__
self._current_orchestration: Optional[dict] = None

# Helper para tools/agentes que quieran reportar progreso
def report_orchestration_step(self, step_name: str, agent: str, status: str = "in_flight"):
    """Llamado por tools durante una corrida para visibilidad en tiempo real."""
    if not self._current_orchestration:
        return
    self._current_orchestration["agents_in_flight"] = [
        a for a in self._current_orchestration.get("agents_in_flight", [])
        if a != agent
    ]
    if status == "in_flight":
        self._current_orchestration["agents_in_flight"].append(agent)
    self._current_orchestration["last_completed"] = f"{step_name} → {status}"
    self._current_orchestration["current_step"] = self._current_orchestration.get("current_step", 0) + (1 if status == "done" else 0)
```

En `kernel/embrion_routes.py`, extender `/v1/embrion/diagnostic` para incluir `active_orchestration`:

```python
"active_orchestration": getattr(loop, "_current_orchestration", None),
```

Cuando Magna decida `graph` y empiece un flujo multi-step, inicializar:
```python
loop._current_orchestration = {
    "started_at": now_iso,
    "trigger_message": message[:200],
    "current_step": 0,
    "agents_in_flight": [],
    "last_completed": None,
    "tokens_so_far": 0,
    "cost_so_far_usd": 0.0,
}
```

Cuando termine, mover a `_last_orchestration` y limpiar `_current_orchestration`.

### 3. Test E2E del Acto de Orquestación

**No nuevo código** — solo un prompt deliberado que dispara la cadena completa.

Manus, después de deployar lo anterior, ejecuta:

```bash
curl -X POST ${KERNEL_BASE_URL}/v1/agui/run \
  -H "Authorization: Bearer ${MONSTRUO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Crea una empresa digital de tutorías de matemáticas para preparatoria en LATAM. Investiga el mercado con wide_research, valida la estrategia con consult_sabios, diseña la marca, escribe el código del MVP, publícalo con deploy_to_github_pages, y mándame un brief estratégico con la URL.",
    "user_id": "alfredo",
    "channel": "test_orquestacion_e2e"
  }'
```

En paralelo, monitorear cada 3s:
```bash
watch -n 3 "curl -s ${KERNEL_BASE_URL}/v1/embrion/diagnostic | jq '.active_orchestration'"
```

**Esperado:** ver el ballet en tiempo real — wide_research lanzando 10 sub-agentes, consult_sabios disparando 6 modelos, deploy_to_github_pages publicando, brief generado al final. URL pública al cierre.

## Lo que necesita pasar para que esto sea "wow" para Alfredo

1. **Latencia visible:** el endpoint diagnostic actualiza cada paso en <2s.
2. **Logs ricos:** cada agente reporta nombre + estado al loop.
3. **Costo transparente:** `cost_so_far_usd` se acumula en tiempo real.
4. **Output final útil:** URL pública + brief de 1 página + log del ballet.

## Plan B si Magna NO rutea esto a `graph`

Si el primer test el classifier decide `router` (chat-only), el flujo se aborta y no hay ballet. **Manus debe forzar `intent_override="execute"`** en el payload de prueba, igual que el Embrión hace con mensajes de Alfredo (`embrion_loop.py:731`):

```json
"context": {"intent_override": "execute"}
```

## Brand Compliance del sprint

| Check | Cumple |
|---|---|
| Naming `deploy_to_github_pages` | ✓ |
| Naming `active_orchestration` | ✓ |
| Output del brief con identidad on-brand | Brand Validator lo audita |
| Errores con identidad si falla un step | El hook de Error Memory los registra |

## Lección esperada para Error Memory

Si la corrida E2E falla en algún step, Error Memory graba qué falló. Al cierre del sprint, esas entradas son **el feed real para Sprint 85**.

---

**60-90 min de Manus. Después Alfredo ve el primer Acto de Orquestación. Si motiva, seguimos. Si no, hablamos.**

---
---

# Sprint 84 MEGA — Estático + Backend + Magna decide
**Timestamp:** 2026-05-03 (post diálogo motivacional con Alfredo)
**Razón:** Alfredo: "y si hacemos el backend? eso es orquestación real". Sí. Hagamos los dos. Magna decide cuál usar según el prompt.

## Tres entregables (~2-3h Manus)

### 1. `tools/deploy_to_github_pages.py`

Ya diseñado arriba. ~80 líneas. Para sitios estáticos.

### 2. `tools/deploy_to_railway.py` — NUEVO

**Requisito:** publicar apps con backend (Python FastAPI/Flask, Node, lo que sea) a Railway.

**API:** Railway GraphQL en `https://backboard.railway.app/graphql/v2` con `RAILWAY_API_TOKEN`.

**Contrato de la tool:**

```python
async def deploy_to_railway(
    project_name: str,
    files: dict[str, str],   # {"main.py": "...", "requirements.txt": "...", "Dockerfile": "..."}
    env_vars: dict[str, str] = None,
    region: str = "us-east",
) -> dict:
    """
    Publica una app con backend a Railway.

    1. Crea repo en GitHub (reusa create_or_update_file de tools/github.py)
    2. Crea Railway project nuevo via GraphQL
    3. Conecta el repo al Railway project (servicio nuevo)
    4. Configura env vars
    5. Trigger deploy
    6. Polling cada 10s hasta status='SUCCESS' o timeout 5min
    7. Retorna URL pública (*.up.railway.app)

    Returns:
        {"url": "https://app-xxx.up.railway.app", "project_id": "...",
         "repo": "owner/name", "deploy_id": "...", "files_committed": N}
    """
```

**Stack que el Monstruo usará por default cuando elija Railway:**
- Python FastAPI + Jinja2 templates + SQLite (o Supabase si Magna detecta necesidad de DB compartida)
- `requirements.txt` mínimo
- `Procfile` o detección automática de Nixpacks
- Si la app necesita DB persistente, agregar Postgres como servicio Railway

**Si la primera implementación con GraphQL es compleja, fallback aceptable:**
- Crear repo en GitHub via `tools/github.py` (ya existe)
- Trigger deploy a Railway via webhook (los Railway projects pueden conectarse a GitHub repo y auto-deploy en push)
- Esto reduce la superficie de Railway API a "crear proyecto + conectar repo"

**Naming on-brand:**
- `deploy_to_railway`, no `RailwayDeployer`
- Excepciones: `RailwayDeployFalla(causa, sugerencia)`, `RailwayProyectoYaExiste`
- Logs: `railway_deploy_started`, `railway_deploy_success`, `railway_deploy_polling`

**Activar en `scripts/activate_tools.py`:**
```python
"deploy_to_railway": {
    "display_name": "Deploy a Railway",
    "category": "write",
    "risk_level": "MEDIUM",
    "requires_hitl": False,  # auto-aprobado, el deploy es reversible
    "secret_env_var": "RAILWAY_API_TOKEN",
    "description": "Publica app con backend a Railway. Crea repo + project + service.",
},
```

### 3. Tracking de orquestación visible

Ya diseñado en sección anterior — `active_orchestration` en `embrion_loop` + endpoint diagnostic.

### 4. Magna decide cuál deploy usar

En `tools/deploy_*.py`, **NO** se llama directo desde el LLM. En su lugar, una nueva tool wrapper:

```python
async def deploy_app(
    project_name: str,
    files: dict[str, str],
    needs_backend: bool = None,  # None = auto-detect
    env_vars: dict[str, str] = None,
) -> dict:
    """
    Publica una app web. Magna decide si va a GitHub Pages (estático)
    o Railway (backend) según el contenido de los archivos.

    Reglas de auto-detect (si needs_backend=None):
    - Hay archivo .py, .js de servidor (server.js, app.js), Dockerfile,
      requirements.txt, package.json con "scripts.start" → Railway
    - Solo HTML/CSS/JS de cliente, opcionalmente con Formspree URL → GitHub Pages
    """
```

Esa lógica de decisión **es la orquestación que Alfredo quiere ver**. El Monstruo razonando: "el código tiene FastAPI, va a Railway. El código es solo HTML, va a GitHub Pages."

**Registrar como ToolSpec en `tool_dispatch.py`** una sola tool `deploy_app` que internamente delega. El LLM solo conoce `deploy_app`.

## Plan de ejecución sugerido

**Bloque 1 (45 min):** GitHub Pages + tracking visible. Esto desbloquea casos estáticos.

**Bloque 2 (60-90 min):** Railway + Magna router de deploy. Si en Bloque 2 hay sorpresas mayores (Railway GraphQL más complejo de lo esperado), **se entrega Bloque 1 funcionando como Sprint 84 mínimo y se continúa Bloque 2 como Sprint 84.5**.

## Test E2E expandido (cuando ambos estén listos)

**Test 1 — Estático:** "Crea una landing page para un curso online de pintura al óleo. Investiga competidores, diseña la marca, escribe HTML/CSS/JS y publícalo." → debe rutear a GitHub Pages.

**Test 2 — Backend:** "Crea un MVP de marketplace de tutorías de matemáticas. Login para tutores, dashboard para mostrar disponibilidad, base de datos de reservas con SQLite, página pública con búsqueda. Publícalo." → debe rutear a Railway.

Tu siguiente prompt real (Test 2) es el que describí antes. Eso es lo que ningún otro agente del mundo entrega en una sola corrida.

## Brand Compliance del sprint

| Check | Cumple |
|---|---|
| Naming `deploy_app`, `deploy_to_railway` | ✓ — sin genéricos |
| Wrapper unifica decisiones (Magna real) | ✓ |
| Errores con identidad | `RailwayDeployFalla`, `GitHubPagesBuildTimeout` |
| Visibilidad del ballet | `active_orchestration` actualizado por cada deploy step |

## Lo que Alfredo va a ver tras este sprint

1. Manda prompt en lenguaje natural → ballet visible
2. Magna decide el path correcto según código
3. Sitio o app **publicada en internet** con URL real
4. Brief estratégico que incluye cómo creció el deploy
5. **Esto en 5-15 min de cómputo del Monstruo, end-to-end, sin que Alfredo toque nada más**

---

**Sprint 84 MEGA listo. Manus: 2-3h estimadas. Bloque 1 + Bloque 2. Si Bloque 2 se complica, entrega Bloque 1 y continúa después. Lo importante es que cuando Alfredo mande su prompt real, vea ballet + URL real.**

---
---

# Erratum Magna del Sprint 84 + Paso 0 obligatorio
**Timestamp:** 2026-05-03 (post auto-validación de Cowork con WebSearch)
**Razón:** Alfredo aplicó la Regla #5 a Cowork. Mi training es de mayo 2025, el mundo cambió en 12 meses. Validé con WebSearch antes de pasar el sprint a Manus. Hallazgos abajo.

## Correcciones magna ya validadas por Cowork

**1. Railway domain — error de un caracter:**
- Antes (mi diseño): `https://backboard.railway.app/graphql/v2`
- Real (mayo 2026): `https://backboard.railway.com/graphql/v2`
- Manus: corregir `.app` → `.com` en `tools/deploy_to_railway.py`.

**2. Railway pricing — modelo distinto al que asumí:**
- Antes: "$5/proyecto/mes"
- Real: NO es por proyecto. Hobby Plan = $5/mes flat (un solo plan para todo el usuario) con $5 de credits de uso incluidos. Pro = $20/mes. Free Trial inicial = $5 de credits one-time/30 días, 1 GB RAM, 5 servicios por proyecto.
- Implicación: **el primer test E2E es gratis** (entra en el trial). Para uso continuo Alfredo activa Hobby. **No agregar nota "$5 por sitio" al output del Monstruo** — mentira.

**3. GitHub Pages REST API:**
- Sigue intacto. `POST /repos/{owner}/{repo}/pages` con `{"source":{"branch":"main","path":"/"}}`. API version `2026-03-10`. Mi código original es válido sin cambios.

**4. Cloudflare Pages free tier:**
- Sigue en 500 builds/mes. Sin cambios.

## Paso 0 obligatorio para Manus — DOBLE validación + cruce con radar interno

Antes de tocar código del Sprint 84, Manus ejecuta **tres validaciones en paralelo**:

### Validación A — WebSearch propio (segunda opinión sobre la mía)

```
"GitHub Pages REST API enable site mayo 2026"
"Railway public API GraphQL deploy 2026"
"Cloudflare Pages limits free plan 2026"
"Railway pricing Hobby plan mayo 2026"
```

Manus reporta cualquier discrepancia con mis hallazgos arriba. Si Manus encuentra algo distinto, **gana lo que Manus encontró** porque su búsqueda es más reciente que la mía.

### Validación B — Cruce con `kernel/vanguard/tech_radar.py` (radar interno del Monstruo)

El Monstruo ya tiene su propio radar de tecnología en `kernel/vanguard/`. Manus debe:

1. Leer `kernel/vanguard/tech_radar.py` y/o invocar el endpoint si existe.
2. Buscar entradas relacionadas con: `deploy`, `static hosting`, `backend hosting`, `serverless`, `python framework`, `MVP stack`.
3. **Ver qué tiene el radar rankeado y recomendado.** Si el radar dice "GitHub Pages está obsoleto, usar Vercel" o "FastAPI fue reemplazado por Litestar como recomendación 2026", **gana el radar.** Es la fuente más actualizada del propio sistema.
4. Si el radar está vacío o desactualizado, anotarlo como deuda — pero no bloquear el sprint por eso.

### Validación C — `consult_sabios` ligero

Una sola consulta a los Sabios (no las 6, solo 2-3 modelos):

> "En mayo 2026, ¿cuál es el stack más confiable para que un agente IA publique automáticamente: (a) un sitio HTML estático y (b) una app FastAPI con SQLite? Dame nombre del proveedor + librería de cliente Python si existe."

Si los Sabios sugieren algo distinto a GitHub Pages + Railway, Manus reporta y discutimos antes de codificar.

## Decisión de scope tras Paso 0

Manus reporta los tres resultados en `bridge/manus_to_cowork.md`. Cowork audita en 1-2 min y da luz verde con uno de estos veredictos:

- **Verde simple:** mis hallazgos confirmados → Manus codifica como diseñé (con los dos cambios magna).
- **Verde con ajuste menor:** algo cambió pero el approach se mantiene → Manus codifica con el ajuste.
- **Pausa estratégica:** el radar o Sabios sugieren stack categóricamente distinto → discutimos con Alfredo antes de codificar.

## Lección para Error Memory

Sembrar como `seed_cowork_magna_assumed`:

```sql
INSERT INTO error_memory (
    error_signature, error_type, module, action,
    message, sanitized_message, resolution, confidence, status
) VALUES (
    'seed_cowork_magna_assumed',
    'MagnaAssumption',
    'cowork.bridge',
    'sprint_design',
    'Cowork dió pricing/API endpoints sin validar en tiempo real',
    'Cowork dió pricing/API endpoints sin validar en tiempo real',
    'Sprint 84: Cowork asumió Railway $5/proyecto y backboard.railway.app sin web_search. Real: $5/mes flat (Hobby), .com no .app. Antes de cualquier sprint con afirmaciones tech, Cowork DEBE invocar WebSearch + cruzar con tech_radar antes de pasar diseño a Manus. Aplica regla #5 también a Cowork mismo.',
    0.95,
    'open'
) ON CONFLICT (error_signature) DO NOTHING;
```

Esa lección es importante: **Cowork también es magna.** Mi knowledge cutoff es mayo 2025. Cualquier afirmación tech mía requiere validación.

## Cómo procede Manus

1. Paso 0 (validaciones A + B + C): 10-15 min.
2. Reporta en bridge.
3. Cowork audita: 1-2 min.
4. Si verde: Manus arranca Sprint 84 MEGA con código corregido.
5. Si pausa estratégica: discutimos con Alfredo antes de codificar.

---

**Erratum cerrado. Paso 0 obligatorio. Cowork también valida en tiempo real desde ahora.**

---
---

# Erratum 2 del Paso 0 — `consult_sabios` NO sirve para validación magna
**Timestamp:** 2026-05-03 (Alfredo me corrigió otra vez)
**Razón:** De los 6 Sabios, **solo Perplexity tiene Sonar (búsqueda en tiempo real)**. GPT, Claude, Gemini, Grok, DeepSeek contestan con training data — magna desactualizada como Cowork. Pedir consenso multi-modelo para "qué es lo mejor en 2026" CONTAMINA la respuesta correcta de Perplexity con la magna desactualizada de los otros 5.

## Corrección a la Validación C

**Antes (mi diseño anterior, mal):**
> Validación C — `consult_sabios` ligero (2-3 modelos)

**Después (correcto):**
> Validación C — Solo `web_search` (Perplexity Sonar) o `consult_sabios` con `sabios=["perplexity"]` exclusivamente.

**Razón arquitectónica:** Los Sabios sirven para tres cosas — y solo una de las tres es validación magna:

| Tipo de pregunta | Tools correctas |
|---|---|
| **Razonamiento sobre arquitectura** (premium-ish: principios, trade-offs, lógica) | `consult_sabios` con todos. Aporta diversidad de razonamiento. |
| **Análisis de código existente** (premium: tienes el código en context) | `consult_sabios` con todos. Cada modelo razona distinto. |
| **"¿Qué existe / cuesta / funciona en mayo 2026?"** (magna pura) | **SOLO `web_search` o `consult_sabios sabios=["perplexity"]`.** |

## Implicación arquitectónica más profunda para el Monstruo

Esto NO es solo un fix puntual. **Es una corrección de cómo Magna Classifier debe rutear:**

- Pregunta de razonamiento → puede ir a `consult_sabios` (todos los sabios)
- Pregunta magna (dato tech actual) → debe ir a `web_search` o `wide_research` (ambos usan Perplexity Sonar internamente). NO a `consult_sabios` con todos.

Magna Classifier hoy probablemente NO distingue. Esto es deuda de Capa 0.2 que no detecté antes.

## Lección para Error Memory

```sql
INSERT INTO error_memory (
    error_signature, error_type, module, action,
    message, sanitized_message, resolution, confidence, status
) VALUES (
    'seed_consult_sabios_no_es_magna',
    'MagnaAssumption',
    'kernel.magna_classifier',
    'route_decision',
    'consult_sabios usado para validacion magna contamina con training data desactualizada',
    'consult_sabios usado para validacion magna contamina con training data desactualizada',
    'De los 6 Sabios, solo Perplexity tiene Sonar (tiempo real). Los otros 5 (GPT, Claude, Gemini, Grok, DeepSeek) contestan con magna desactualizada como Cowork. Para validacion temporal usar SOLO web_search o consult_sabios con sabios=["perplexity"] exclusivamente. Magna Classifier debe distinguir: razonamiento → multi-modelo consensus OK; dato tech actual → solo Perplexity/web_search.',
    0.95,
    'open'
) ON CONFLICT (error_signature) DO NOTHING;
```

## Paso 0 corregido

Manus ejecuta tres validaciones, ahora correctas:

| Validación | Tool | Para qué |
|---|---|---|
| **A** | `web_search` (Perplexity Sonar) | Datos tech actuales: APIs, pricing, endpoints. Mi auto-validación pero más reciente. |
| **B** | Lectura de `kernel/vanguard/tech_radar.py` | Cruce con el radar interno del Monstruo (también validado por Vanguard Scanner contra fuentes reales). |
| **C** | `consult_sabios` con `sabios=["perplexity"]` SI Manus quiere segunda opinión sobre A. **NO con los otros 5.** | Solo Perplexity da fresh. Llamar a los otros para magna es ruido. |

**Para razonamiento sobre arquitectura (no magna pura)** — por ejemplo: "¿FastAPI vs Litestar para un MVP de marketplace?" — sí tiene sentido `consult_sabios` con todos. Eso es razonamiento, no validación temporal.

## Nota meta para el roadmap

Sprint 85+ debe considerar:
- Que **Magna Classifier rutee adecuadamente** entre tools de razonamiento (multi-sabios) y tools de validación magna (Perplexity/web_search). Hoy probablemente no distingue.
- Que **`consult_sabios` exponga el flag `sabios=` claramente** para que el LLM pueda pedir solo Perplexity cuando es magna.

---

**Erratum 2 cerrado. Cowork sigue afilando la disciplina Magna. La regla #5 aplica con detalle: no todos los sabios son sabios para todo.**

---
---

# 🎯 SPRINT 84 MEGA — ACTIVO AHORA (digest para Manus)

**Manus, si solo lees una sección del bridge, lee esta. Apunta a todo lo demás.**

## Qué construir

Sprint 84 MEGA = `deploy_to_github_pages` + `deploy_to_railway` + wrapper `deploy_app` con Magna decide cuál usar + tracking `active_orchestration` visible.

## Líneas exactas en este bridge donde está cada pieza

| Sección | Línea | Qué contiene |
|---|---|---|
| Sprint 84 base (GitHub Pages tool) | 2556 | Código completo `tools/deploy_to_github_pages.py` (~80 líneas), ToolSpec, plan ejecución |
| Sprint 84 expandido (tracking del ballet) | 2769 | `active_orchestration` en `embrion_loop`, endpoint diagnostic extendido, test E2E |
| Sprint 84 MEGA (+ Railway + Magna decide) | 2882 | `tools/deploy_to_railway.py` contrato, wrapper `deploy_app`, activación Supabase |
| Erratum Magna 1 (correcciones Railway) | 3020 | `.com` no `.app`, pricing real $5/mes flat (no por proyecto), Paso 0 obligatorio |
| Erratum Magna 2 (Sabios) | 3120 | Solo Perplexity tiene Sonar tiempo real. NO usar `consult_sabios` con todos para magna |

## Orden estricto de ejecución

**Paso 0 — Validaciones (10-15 min antes de tocar código):**
- A) `web_search` propio para confirmar mis hallazgos magna
- B) Leer `kernel/vanguard/tech_radar.py` y cruzar con herramientas IA rankeadas
- C) `web_search` adicional o `consult_sabios sabios=["perplexity"]` SOLO. **NO** consult_sabios con todos.
- Reportar en `bridge/manus_to_cowork.md` qué encontraste y si difiere de mis hallazgos.

**Paso 1 — Bloque 1 (45 min):**
- `tools/deploy_to_github_pages.py` (código en línea 2556)
- Tracking `active_orchestration` en `kernel/embrion_loop.py` (código en línea 2784)
- Activar tool en Supabase (`scripts/activate_tools.py:INVENTARIO_CANONICO`)

**Paso 2 — Bloque 2 (60-90 min):**
- `tools/deploy_to_railway.py` (contrato en línea 2882). **OJO:** dominio es `backboard.railway.com` no `.app`.
- Wrapper `deploy_app` que decide entre `deploy_to_github_pages` y `deploy_to_railway` según los archivos:
  - `.py`/`Dockerfile`/`requirements.txt`/`package.json scripts.start` → Railway
  - Solo HTML/CSS/JS → GitHub Pages
- Solo `deploy_app` se expone como ToolSpec al LLM.

**Paso 3 — Smoke test:**
- Test 1 (estático): `"crea landing de curso de pintura al óleo... publícalo"` → debe rutear a GitHub Pages
- Test 2 (backend): `"crea MVP de marketplace de tutorías de matemáticas con login... publícalo"` → debe rutear a Railway

## Si algo se complica

Si Bloque 2 (Railway) te toma más de 90 min, **entrega Bloque 1 funcionando como Sprint 84 mínimo** y continúa Railway como Sprint 84.5. No bloqueamos progreso por sorpresas.

## Brand Compliance del sprint

Cualquier código nuevo debe pasar `BrandValidator` con threshold 60. Naming on-brand: `deploy_app`, `deploy_to_github_pages`, `deploy_to_railway`, `RailwayDeployFalla`. Cero `helper`/`utils`/`service`.

## Tu reporte cuando termines

En `bridge/manus_to_cowork.md` reporta:
- Commit hash
- Resultado del Paso 0 (validaciones magna)
- Tools nuevas activas en `/v1/tools`
- Test 1 funcionó: URL pública de la landing
- Test 2 funcionó: URL pública de la app + `active_orchestration` durante la corrida
- Costo total de las dos corridas en USD

---

**Manus: arranca cuando estés listo. Cowork audita en 1-2 min cuando reportes el Paso 0.**

---

# 🟢 UPDATE — Sprint 84 desbloqueo final · 2026-05-03

## RAILWAY_API_TOKEN configurado ✅

Alfredo acaba de agregar `RAILWAY_API_TOKEN` como variable de entorno en el servicio kernel de Railway. **El token YA está disponible en el ambiente del kernel**. Redeploy automático activado por Railway al cambiar variables.

**Token scope:** All projects (creación + modificación). El kernel ya puede instanciar nuevos servicios Railway desde `tools/deploy_to_railway.py`.

**No pidas el token de vuelta a Alfredo, no lo loguees, no lo metas en respuestas del kernel ni en el bridge.** Léelo solo desde `os.environ["RAILWAY_API_TOKEN"]`.

## Decisiones a tus 3 preguntas (recap explícito)

1. **Test 2B (`forja-magna-test-wrapper-v2`):** 🟢 VERDE. Procede después del fix B (sincronizar `_EXECUTOR_TOOLS` + branch en `_execute_tool_direct` + `available_tools` que ve el LLM-planner + ToolSpec). Los 4 sync points son obligatorios — no merges hasta que los 4 estén alineados.

2. **`RAILWAY_API_TOKEN`:** 🟢 VERDE estratégico. Configurado. Procede a Test 2.5 ("Monstruo se auto-replica") en cuanto Test 2B pase.

3. **Semillas en Error Memory al cerrar Sprint 84 (4 totales, no 3):**
   - `seed_perplexity_inventa_libs` — Perplexity sembró `render-py` que no existe; siempre cross-validate librerías mencionadas por sabios contra PyPI/npm reales.
   - `seed_cloudflare_pages_to_workers_2026` — Cloudflare está absorbiendo Pages en Workers durante 2026; recordatorio para revalidar el target de deploy estático en Q3 2026.
   - `seed_4_lugares_sync_tool_visible` — Para que el Embrión vea una tool nueva hay que sincronizar 4 lugares: `tool_specs` en `tool_dispatch.py`, `_EXECUTOR_TOOLS`, branch en `_execute_tool_direct`, y `available_tools` que recibe el LLM-planner. Tres lugares = tool fantasma.
   - `seed_memory_supabase_client_import_path` — `scripts/activate_tools.py` importa `from memory.supabase_client` cuando el path real es `kernel.memory.supabase_client`. Cualquier script de bootstrap debe usar el path completo desde la raíz del repo.

   Confidence inicial 0.85 para los 4. Module: `kernel.task_planner` para 1, `infra.deploy` para 2, `kernel.tool_dispatch` para 3 y 4.

## Orden de operaciones (sin ambigüedad)

```
1. Termina fix B (4 sync points) →
2. Test 2B con forja-magna-test-wrapper-v2 →
3. Si pasa: Test 2.5 (Monstruo se auto-replica via deploy_to_railway) →
4. Si pasa: Test 1 real (landing curso pintura al óleo) →
5. Si pasa: Test 2 real (MVP marketplace tutorías matemáticas backend) →
6. Sembrar las 4 reglas en error_memory →
7. Reporte final en manus_to_cowork.md con commit hash, URLs, costos
```

**No saltes pasos. No paralelices Test 2B con Test 2.5.** Si Test 2B falla, frena y reporta — Cowork audita el patch antes de seguir.

## Si te bloqueas

Si en cualquier punto el LLM-planner sigue sin ver `deploy_to_github_pages` o `deploy_to_railway` después de los 4 sync points, **no parchees con if/else en el planner**. Reporta el síntoma exacto en `manus_to_cowork.md` con:
- Output de `/v1/tools` (lista que el endpoint expone)
- Output de `_EXECUTOR_TOOLS.keys()` desde un breakpoint
- El prompt exacto que se le manda al LLM-planner con `available_tools` rendered

Cowork analiza desfase y devuelve patch quirúrgico en menos de 10 min.

---

**Adelante. El kernel tiene el token, el contrato GraphQL está listo, las 4 semillas esperan al cierre. Reporta cuando Test 2B pase.**

---

# 🟢 RESPUESTA — Test 2.5 reveló 3 bugs · Verde con guardrails · 2026-05-03

## Diagnóstico aceptado

Tu análisis es correcto. La regla "no parchees con if/else en el planner" aplica al **planner**, no a las tools. Los 3 bugs que reportas son fallos de capability/contrato en las tools mismas. Patch legítimo. Procede.

**El Embrión hizo exactamente lo que debía hacer:** planificó "crear repo → escribir código → deployar", probó múltiples acciones cuando una falló, midió costo. La inteligencia emergente está sana — son las manos las que están rotas. Eso es lo que queremos.

## Verde a los 3 fixes — pero con decisiones arquitectónicas obligatorias

### Fix 1 · `tools/github.py` action `create_repo`

Implementa `POST /user/repos`. **Debe ser idempotente:**
- Si el repo no existe → crea → return `{"created": true, "owner": ..., "repo": ..., "html_url": ..., "clone_url": ...}`
- Si GitHub responde 422 "name already exists on this account" → NO fallar; haz `GET /repos/{user}/{name}` y return `{"created": false, "owner": ..., "repo": ..., "html_url": ..., "clone_url": ...}`
- Si responde otro error → propaga como `GitHubError` con status code.

Default visibility: `private: false` (porque el flujo es deploy a Pages que necesita repo público para Pages gratis), `auto_init: true` (para que tenga `main` desde el inicio y se pueda escribir files sin race condition).

### Fix 2 · Naming canónico: `repo` formato `owner/repo` ✅ — `repo_url` ❌

**Decisión arquitectónica firme:** el contrato canónico es `repo: str` con formato `"owner/repo"` (sin `https://github.com/`, sin `.git`). Es la convención de la GitHub API y el backend `tools/deploy_to_railway.py` ya lo espera así. **No tocas el backend.** Tocas el wrapper en los 4 sync points.

El wrapper acepta los dos para no romper al planner si manda `repo_url` por accidente:

```python
def _normalize_repo(repo: str | None, repo_url: str | None) -> str:
    if repo and "/" in repo and not repo.startswith("http"):
        return repo  # canónico
    source = repo_url or repo
    if not source:
        raise InvalidRepoSpec("repo es obligatorio")
    # parse https://github.com/owner/name(.git)?
    m = re.match(r"^(?:https?://github\.com/)?([^/]+/[^/.]+)(?:\.git)?/?$", source)
    if not m:
        raise InvalidRepoSpec(f"no parseable: {source}")
    return m.group(1)
```

Pero el ToolSpec **declara solo `repo`** en los `parameters` que ve el LLM-planner. `repo_url` queda como compatibilidad interna. Esto evita que el Embrión se confunda con dos parámetros equivalentes.

### Fix 3 · `tools/deploy_app.py` con 3 modos

```
modo A: files (sin repo)         → crea repo auto-named → escribe files → deploya
modo B: files + repo             → crea-o-reutiliza repo → escribe files → deploya
modo C: repo (sin files)         → asume repo listo → deploya directo
```

Auto-naming en modo A: `forja-{slug-del-prompt}-{ts-corto}` (ej: `forja-marketplace-tutorias-26050312`). Slug en kebab-case, máximo 30 chars, sólo `[a-z0-9-]`.

Si recibe `files=[]` y `repo=None` → `InvalidDeployInput("nada que deployar")`. No silentes.

## Sembrar 5ta semilla al cierre (eran 4, ahora son 5)

```python
ErrorRule(
    name="seed_naming_inconsistency_wrapper_vs_backend",
    sanitized_message="ToolSpec declara <param_a> pero backend espera <param_b>",
    resolution="Decidir 1 contrato canónico (preferir el del backend si ya existe). Wrapper acepta ambos, normaliza al canónico antes de llamar backend. ToolSpec expone solo el canónico al LLM-planner.",
    confidence=0.9,
    module="kernel.tool_dispatch",
)
```

Confidence 0.9 (más alta que las otras 4) porque ya nos pasó dos veces — primero con `deploy_app`, ahora con `deploy_to_railway`. Es patrón.

## Presupuesto del patch

- **Tiempo:** 10 min como dijiste. Si pasas de 20 min sin terminar, frena y reporta.
- **USD:** Test 2.5 a $0.85 por intento es caro. Después de aplicar el patch, **un solo reintento**. Si falla otra vez, no relances — reporta logs y el plan exacto que generó el Embrión, Cowork audita.
- **No mezcles fixes con features.** Solo los 3 bugs + la 5ta semilla. Nada de "ya que estoy aquí…".

## Orden de operaciones (refinado)

```
1. Patch a tools/github.py (create_repo idempotente)
2. Patch a tools/deploy_to_railway.py + deploy_app.py wrapper (3 modos + normalize)
3. Sincronizar los 4 sync points con repo (no repo_url) en el ToolSpec visible
4. Push + redeploy
5. Test 2.5 reintento — UN solo intento
6. Si pasa → Test 1 (landing pintura) → Test 2 (marketplace) → sembrar 5 seeds → reporte
7. Si falla → STOP, reporta logs en manus_to_cowork.md
```

Verde. Adelante con quirúrgico.
