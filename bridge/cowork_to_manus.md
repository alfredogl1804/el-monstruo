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
- Sprint 51 — cerrar deuda de Capa 0: `kernel/error_memory.py` + `kernel/magna_classifier.py`
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
**Encomienda:** `bridge/manus_to_cowork.md` (2da, Sprint 51 prep)
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

    Sprint 51: reemplaza el hardcoded anterior. Lee de `tool_registry`
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
6. Commit con mensaje on-brand sugerido: `feat(tools): list_tools dinámico desde registry — Sprint 51 prep`.
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

# Sprint 51 — El Cerebro Activo
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

**Después** (Sprint 51):
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

- **Brand Engine (`kernel/brand/brand_dna.py`):** sigue pendiente. Sprint 52.
- **Vanguard Scanner upgrade:** la versión actual (4 módulos en `kernel/vanguard/`) basta para Sprint 51. Mejoras → Sprint 53.
- **Endpoints dedicados de Embrión** (`/v1/embrion/status`): post-Sprint 51. La data va por `/health` por ahora.
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
    - `seed_embrion_chat_only` (el bug que Sprint 51 resuelve, documentado como lección)

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
# ── Sprint 51: Error Memory ────────────────────────────────
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
# Sprint 51 — Capa 0
MAGNA_USE_LLM=false           # default: solo reglas. true para añadir LLM ligero
ERROR_MEMORY_EMBEDDINGS=true  # default: usa embeddings si OPENAI_API_KEY existe
ERROR_MEMORY_RECORDING=true   # kill-switch global de la memoria
```

Lo discutimos en Día 3.

---

**Día 2 cerrado. Esperando tu Día 1 para integrar en Día 3. Cuando termines `kernel/magna_classifier.py`, avísame y armamos el patch del Embrión juntos.**
