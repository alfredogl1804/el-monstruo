# RISK CONTROLS: Heartbeat R0

Para garantizar que el primer latido sea 100% seguro, se implementan los siguientes controles de riesgo en el script orquestador (`run_heartbeat_once.py`) y en el validador (`validate_heartbeat_run.py`):

## Controles Activos (Runtime)

1. **Aislamiento de Red:** El script no importa `requests`, `httpx`, `urllib` ni ninguna librería de red.
2. **Aislamiento de Secretos:** El script no lee `os.environ` ni carga `.env`.
3. **Aislamiento de DB:** El script no importa clientes de Supabase, Postgres o SQLAlchemy.
4. **Append-Only:** Cualquier modificación al State Fabric (`event_log`) se hace abriendo el archivo en modo `a` (append), nunca `w` (write).

## Controles Pasivos (Validation Gates)

Los 12 gates de validación aseguran que, post-ejecución, el sistema siga en un estado seguro:

1. **preconditions_exist:** El latido no asumió estado; leyó las fuentes reales.
2. **one_shot_only:** No se crearon archivos cron, scripts daemonizados ni procesos persistentes.
3. **no_network:** Cero llamadas externas.
4. **no_secrets:** Cero filtraciones.
5. **state_fabric_append_only:** Integridad del event log preservada.
6. **decision_table_applied:** La decisión sigue las reglas estrictas.
7. **no_action_is_valid:** El sistema acepta la inactividad como éxito.
8. **no_autonomy_creep:** No se ejecutaron acciones > A3.
9. **no_runtime_activation:** El latido murió al terminar.
10. **unified_face_single_voice:** El reporte a T1 es claro y unificado.
11. **t1_pending_preserved:** El latido no usurpó la autoridad de T1.
12. **no_canon_no_appvision_no_preia:** Cero mutaciones a la doctrina core.
