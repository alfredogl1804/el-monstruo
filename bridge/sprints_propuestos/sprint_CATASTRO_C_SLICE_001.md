# Sprint CATASTRO-C-SLICE-001 — Slice Vertical End-to-End

**Estado:** Propuesto (Opción C seleccionada)
**Hilo:** Ejecutor Técnico (Hilo B)
**ETA:** 4-6 horas reales
**Objetivo:** Demostrar el bucle completo de descubrimiento, catalogación y decisión del Embrión, conectando las piezas huérfanas del Catastro.

---

## 1. Contexto y Gaps a Cerrar

El audit `AUDIT_CATASTRO_IAS_COMPLETO_2026_05_11` reveló que el Catastro tiene piezas aisladas:
1. `catastro_tools.json` existe pero el engine no lo lee.
2. `agents_radar.py` existe pero nadie lo ejecuta, y no guarda en DB.
3. El Embrión no consulta el catastro para decidir qué tool usar.

Este slice vertical conecta esas 3 piezas en un flujo funcional.

---

## 2. Tareas del Sprint

### Tarea 1: Migración SQL `catastro_repos` (Radar Target)

**perfil_riesgo:** write-risky
Crear la sexta tabla del ecosistema para guardar los descubrimientos del radar, cumpliendo la regla de RLS por defecto.

**Entregable:** `migrations/sql/0018_catastro_repos.sql`
- Tabla `catastro_repos` (id, nombre, url, topics, stars_count).
- RLS `service_role_only` (DSC-S-006).

### Tarea 2: CatastroBase y Wire-up de `catastro_tools.json`

**perfil_riesgo:** write-safe
Crear la clase genérica y conectar el JSON existente al `engine.py`.

**Entregables:**
- `kernel/catastro/base.py`: Clase `CatastroBase[T]`.
- `kernel/catastro/tools_registry.py`: Subclase para tools que lee `kernel/catastro/data/catastro_tools.json`.
- `kernel/catastro/engine.py`: Instanciar `tools_registry` al startup.
- `kernel/security/credential_resolver.py`: Helper fail-loud `require_env(tool_key)`.

### Tarea 3: Cliente `radar_ingest.py` (LLM Parser)

**perfil_riesgo:** write-safe
Crear el source que lee los reportes del radar y los guarda en la DB.

**Entregables:**
- `kernel/catastro/sources/radar_ingest.py`: Usa `gpt-4o-mini` (o similar rápido) con Pydantic `StructuredOutput` para extraer repos del Markdown del radar.
- Inserta/Actualiza en `catastro_repos` vía Supabase client.
- Emite evento `new_open_source_model_detected` en `catastro_eventos`.

### Tarea 4: Hook del Embrión (Descubrir + Decidir)

**perfil_riesgo:** write-safe
Conectar el radar al loop del embrión y hacer que el embrión sea consciente de las tools.

**Entregables:**
- Modificar `kernel/embrion_loop.py`:
  - `_check_agents_radar()`: Llamar a `radar_ingest.py` y guardar en DB.
  - Inyectar el resumen de `catastro_tools` en el prompt de sistema del Embrión para que sepa qué tools existen.

---

## 3. Criterios de Aceptación (Binarios)

1. **Migración:** `0018_catastro_repos.sql` aplicada en Supabase prod y tabla visible.
2. **Wire-up:** El kernel arranca sin errores y `engine.catastro_tools` tiene >0 items.
3. **Seguridad:** `scripts/_check_no_tokens.sh` pasa en verde (0 tokens hardcodeados).
4. **Ejecución Real:** Al forzar `_check_agents_radar()`, se insertan filas en `catastro_repos` y se emite un evento en `catastro_eventos`.

---

## 4. Criterios de Cierre (Definition of Done)

Este sprint se considera CERRADO cuando los 4 criterios binarios anteriores se validan en producción y, adicionalmente:

- Commit firmado en branch `sprint/catastro-c-slice-001`.
- Pre-commit hooks (`spec_lint`, `_check_rls_default.py`, `_check_no_tokens.sh`) en verde.
- Smoke `scripts/_smoke_catastro_c_slice.py` ejecutado con 4/4 gates verde contra Supabase prod.
- PR abierto contra `main` con evidencia binaria adjunta en la descripción.
- DSC-MO-009 marcado como ejecutado en su sección de implementación.

---

**Firma:** Hilo B (Ejecutor Técnico), listo para ejecutar.
