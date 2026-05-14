# Propuesta de Arquitectura: MANUS-ANTI-DORY-002 (v0)

**Objetivo:** Erradicar el "Síndrome Dory" (pérdida de contexto en hilos nuevos) de Manus AI usando infraestructura existente en El Monstruo, asegurando que un hilo virgen pueda retomar el trabajo exacto donde lo dejó el hilo anterior sin reexplicación humana.

## Los 5 Componentes de la Solución

### 1. `thread_snapshots` (Supabase)
Nueva tabla en Supabase para almacenar el estado canónico al cierre de cada sesión.
- **Columnas:** `id` (uuid), `thread_id` (text), `cuenta_manus` (text), `timestamp` (timestamptz), `sprint_activo` (text), `frente_activo` (text), `fase_actual` (text), `decisiones_t1` (jsonb), `ultimos_artefactos` (jsonb), `proximo_paso_esperado` (text).
- **RLS:** Habilitado, accesible vía `SUPABASE_SERVICE_KEY`.

### 2. `manus-snapshot-write` (Skill/Utility)
Script utilitario que el agente debe invocar obligatoriamente antes de enviar el mensaje final (`result`) de una sesión.
- Extrae el estado actual del contexto del agente.
- Escribe el registro en `thread_snapshots`.

### 3. `monstruo-auto-attach` (Skill)
Skill que se ejecuta al inicio de un hilo virgen.
- Hace query a Supabase: `SELECT * FROM thread_snapshots WHERE cuenta_manus = 'current' ORDER BY timestamp DESC LIMIT 1`.
- Carga el estado en el prompt del sistema o como primer mensaje de contexto.
- Verifica la vigencia de los artefactos (ej. si el PR mencionado sigue abierto).

### 4. Pre-hook en `guardian.py`
Extensión del script `~/.monstruo/guardian.py` (que ya se ejecuta por regla en `AGENTS.md`).
- Llama a `monstruo-auto-attach`.
- Si falla la recuperación del snapshot, emite un `HALT` y pide intervención humana.

### 5. ID de Proyecto Canónico (`project_id`)
Uso consistente del `project_id` de Manus API al crear tareas, para que los snapshots se agrupen correctamente bajo el paraguas de "El Monstruo" y no se mezclen con otros proyectos del usuario (ej. ticketlike).

## Flujo Operativo Propuesto
1. **Cierre de Hilo A:** Agente invoca `manus-snapshot-write` -> Guarda estado en Supabase -> Envía mensaje de despedida.
2. **Inicio de Hilo B (Virgen):** Usuario envía "continuar".
3. **Arranque Hilo B:** Regla `AGENTS.md` obliga a ejecutar `guardian.py`.
4. **Recuperación:** `guardian.py` ejecuta `monstruo-auto-attach` -> Lee Supabase -> Inyecta contexto.
5. **Ejecución:** Agente B responde: *"Contexto recuperado del Hilo A. Retomando fase X del sprint Y."*
