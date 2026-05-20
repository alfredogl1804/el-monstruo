# 05 EVENT LOG AND LOOP REGISTRY

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Diferencia entre Estado y Eventos
Mientras que el **State Fabric** guarda la *fotografía actual* de la realidad (y sobrescribe lo viejo), el **Event Log** es la *película inmutable* de cómo se llegó ahí.

## 1. Event Log (Append-Only)
Es el registro histórico y auditable de todas las acciones del Monstruo.
- **Estructura:** Append-only (solo inserción, nunca borrado ni modificación).
- **Propósito:** Auditoría, debug, y material de entrenamiento para el motor de aprendizaje (Self-Evolution).
- **Esquema Mínimo:**
  - `timestamp`
  - `loop_id` (quién ejecutó)
  - `event_type` (ej. API_CALL, FILE_WRITE, T1_INTERVENTION)
  - `payload` (datos de la acción)
  - `autonomy_level` (A0-A8)

## 2. Loop Registry
Es el panel de control en tiempo real del Dispatcher.
- **Estructura:** Tabla en memoria o base de datos rápida (Redis/SQLite).
- **Propósito:** Saber exactamente qué mentes están activas, qué están haciendo y cuándo deben morir.
- **Campos:**
  - `loop_id` (Identificador único)
  - `role` (ej. Auditor, Ejecutor, Memento)
  - `status` (Booting, Running, Blocked, Dying)
  - `ttl_remaining` (Tiempo de vida restante)
  - `heartbeat_last_seen` (Timestamp del último pulso de vida)

Si un loop deja de enviar heartbeats, el Dispatcher lo marca como "Zombie", revoca sus permisos de escritura en el State Fabric y lanza un nuevo loop para recuperar la tarea.
