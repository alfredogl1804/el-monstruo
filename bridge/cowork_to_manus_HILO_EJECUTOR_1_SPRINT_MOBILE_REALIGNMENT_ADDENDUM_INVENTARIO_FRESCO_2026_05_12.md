---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_ADDENDUM_INVENTARIO_FRESCO_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1
tipo: addendum_pre_T1_obligatorio
prioridad: P0 (bloquea arranque de T1 hasta cumplir)
referencia_kickoff: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_MOBILE_REALIGNMENT_KICKOFF_2026_05_12.md (commit 74f301f)
referencia_spec: bridge/sprints_propuestos/sprint_mobile_REALIGNMENT_001.md (commit 4f477be)
autoridad_T1: Alfredo 2026-05-12 ("si mejor hace inventario fresco antes el ejecutor uno")
---

# Addendum obligatorio — Inventario fresco apps/mobile/ ANTES de T1

## §1 ¿Por qué este addendum existe?

Alfredo T1 aplicó V25 (anti-alucinación) sobre el spec MOBILE-REALIGNMENT-001: *"es posible que ya este hecho? y no lo sepas?"*

Cowork verificó binariamente con 9 checks contra filesystem actual y confirmó que el **Realignment NO está hecho**. Pero la verificación también detectó algo que el spec NO contemplaba:

**Entre 2026-05-05 y 2026-05-12 hubo 7 commits A2UI mergeados a `apps/mobile/`:**

```
a25c330 feat(mobile/a2ui): T7 integración A2UIMessageView en chat bubble
52bc52d test(mobile/a2ui): T6 suite widgets + end-to-end parser y renderer
6fd4f10 feat(mobile/a2ui): T5 action channel WebSocket + buffered fake
80b17fb feat(mobile/a2ui): T4 3 widgets especializados Monstruo
f1842cb feat(mobile/a2ui): T3 16 widgets whitelist + renderer dispatcher
22aa2e1 feat(mobile/a2ui): T2 parser A2UI v1.0 con fallback Markdown
291dd64 feat(mobile/a2ui): T1 estructura base y tipos A2UI v1.0
```

Estos commits son del Sprint MOBILE_1B A2UI (PR #92) que se mergeó posteriormente al `REPORTE_BINARIO_APP_FLUTTER_2026_05_11.md` en que se basa el spec MOBILE-REALIGNMENT-001.

**Implicación binaria:** el spec asume scope basado en filesystem del 11-may, pero filesystem del 12-may tiene drift. **Antes de tocar nada, necesitás inventario fresco real.**

## §2 Pre-T1 obligatorio (15-20 min) — ANTES de aplicar T1 del spec

### Paso 1 — Inventario filesystem fresco

```bash
cd ~/el-monstruo

# Contar archivos .dart actuales por directorio
find apps/mobile/lib -type f -name '*.dart' | wc -l
# Esperado: número >31 (mi reporte del 11-may decía 31; los 7 commits A2UI seguramente agregaron archivos)

# Estructura nivel 1 + 2
find apps/mobile/lib -maxdepth 2 -type d | sort

# Inventario por feature (LOC)
for dir in apps/mobile/lib/features/*/; do
  echo "=== $dir ==="
  wc -l "$dir"*.dart 2>/dev/null
  ls -la "$dir"widgets/ 2>/dev/null
done

# Específico genui (lo que el spec mueve a core/a2ui/)
wc -l apps/mobile/lib/features/genui/*.dart 2>&1
ls apps/mobile/lib/features/genui/widgets/ 2>&1  # ¿existe ahora?
ls apps/mobile/lib/features/genui/parsers/ 2>&1  # ¿existe ahora?

# Específico chat (lo que el spec wrappea en modes/daily/)
wc -l apps/mobile/lib/features/chat/*.dart 2>&1
ls apps/mobile/lib/features/chat/widgets/ 2>&1

# core/ actual (lo que el spec extiende)
find apps/mobile/lib/core -type f -name '*.dart' | xargs wc -l 2>&1
```

### Paso 2 — Búsqueda de paradigma A2UI nuevo

Los 7 commits A2UI agregaron **16 widgets whitelist + 3 widgets especializados Monstruo + parser + WebSocket channel**. Probablemente vive en:

```bash
# Buscar dónde quedó el código nuevo
find apps/mobile/lib -name '*a2ui*' 2>&1
find apps/mobile/lib -name '*A2UI*' 2>&1
grep -rln "A2UIMessageView\|A2UIParser\|A2UIRenderer" apps/mobile/lib 2>&1 | head -20
```

### Paso 3 — Verificación de impacto sobre spec original

Por cada path canonizado en el spec §1 tabla "Path canonizado vs Estado real", **re-verificá binariamente**:

| Path canonizado spec | Comando verificación |
|---|---|
| `core/transport/kernel_websocket.dart` | `find apps/mobile/lib -name 'kernel_websocket*' -o -name 'kernel_messenger*'` |
| `core/a2ui/renderer.dart` | `find apps/mobile/lib -name 'a2ui_renderer*' -o -name 'genui_renderer*'` |
| `core/mensajeros/` | `ls apps/mobile/lib/core/mensajeros/ 2>&1` |
| `modes/daily/` | `ls apps/mobile/lib/modes/daily/ 2>&1` |
| `modes/cockpit/` | `ls apps/mobile/lib/modes/cockpit/ 2>&1` |
| `core/state/mode_provider.dart` | `find apps/mobile/lib -name 'mode_provider*'` |
| `routing/mode_router.dart` | `find apps/mobile/lib -name 'mode_router*'` |

**Si CUALQUIERA de estos paths YA existe en el filesystem actual (porque alguien lo hizo en los 7 commits A2UI o después), el spec de Realignment tiene drift y vos NO ejecutás T1-T6 ciegamente.**

### Paso 4 — Reporte de inventario al bridge

Producí `bridge/manus_to_cowork_MOBILE_REALIGNMENT_INVENTARIO_FRESCO_2026_05_12.md`:

```
§1 Conteo de archivos .dart actual vs reporte 11-may (31 archivos)
§2 Estructura de directorios actual nivel 1+2
§3 Inventario por feature con LOC
§4 Búsqueda paradigma A2UI: dónde quedó el código nuevo de los 7 commits
§5 Re-verificación binaria 7 paths canonizados (estado fresh por cada uno)
§6 Hallazgos de drift respecto al spec original:
   - Paths del spec que ya existen (no necesitan T1-T6)
   - Paths del spec que siguen ausentes (T1-T6 sigue válido para ellos)
   - Archivos NUEVOS no contemplados por el spec (cómo encajarlos en el realignment)
§7 Recomendación a Cowork:
   - ¿El spec sigue válido tal cual? → arrancá T1
   - ¿El spec necesita ajuste menor? → propone ajustes y esperá firma
   - ¿El spec necesita reescritura? → reportá y Cowork redacta v2
```

## §3 Después del inventario

**Caso A — Spec sigue 100% válido:** arrancá T1 del kickoff original (`74f301f`) inmediato. Reportá decisión en §7 del inventario fresco.

**Caso B — Spec necesita ajuste menor (renames distintos, paths con archivos nuevos):** proponé ajustes en el reporte de inventario + esperá firma Cowork antes de codear. ETA Cowork audit: 10-15 min.

**Caso C — Spec tiene drift mayor (ej: alguien ya creó `core/mensajeros/`, o A2UI vive en `features/genui/` pero con scope expandido):** reportá honesto y Cowork redacta spec v2. ETA Cowork: 30-45 min.

**NO ejecutés T1 del kickoff original hasta:**
- Inventario fresco reportado al bridge
- Decisión binaria del Caso A/B/C clara
- Si B o C: firma Cowork aplicada al ajuste

## §4 Regla anti-autoboicot reforzada

Este addendum aplica exactamente la lección que vos canonizaste en S89 v1: cuando hubo drift entre spec firmado y realidad de prod, parar y reportar fue lo correcto, no arrancar ciegamente.

La diferencia esta vez: yo Cowork ya detecté el drift potencial (7 commits A2UI). Vos solo verificás binariamente y reportás. No tenés que "descubrirlo solo" en pre-flight rojo — ya tenés señal.

## §5 ETA actualizado

- **Pre-T1 inventario fresco:** 15-20 min (este addendum)
- **Sprint MOBILE-REALIGNMENT-001 (T1-T7):** 4-6h reales (per kickoff original — puede ajustar a la baja si Caso A confirma menos scope)
- **Total con inventario:** 4-6h 15-20 min

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:40 UTC

**Addendum bajo orden T1 Alfredo "si mejor hace inventario fresco antes el ejecutor uno". Aplica V25 anti-alucinación al propio spec MOBILE-REALIGNMENT-001: el reporte fuente del 11-may pre-data 7 commits A2UI mergeados, por lo tanto el inventario binario fresco es pre-requisito obligatorio.**
