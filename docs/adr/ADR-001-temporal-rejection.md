# ADR-001: Rechazo Permanente de TemporalIO

## Estado
**ACEPTADO** — Sprint 28 (25 abril 2026)

## Contexto
El radar automatizado de GitHub (24 abril 2026) recomendó adoptar `temporalio/temporal` (19.8K stars)
para durable execution. Esta recomendación se basa en popularidad, no en compatibilidad arquitectónica.

## Decisión
**TemporalIO queda DESCARTADO PERMANENTEMENTE** para El Monstruo.

## Razones
1. **Incompatibilidad fundamental:** Temporal usa journal replay que requiere determinismo.
   Los LLMs son inherentemente no-determinísticos. Cada replay produciría resultados diferentes.
2. **LangGraph PostgresSaver** ya resuelve el problema de durabilidad con checkpoint caching,
   sin requerir determinismo.
3. **Hatchet** (MIT, PostgreSQL-only) queda como Plan B si se necesita durable execution
   más allá de lo que LangGraph ofrece.

## Consecuencias
- Cualquier radar futuro que recomiende Temporal debe ser rechazado automáticamente.
- Esta decisión fue ratificada por el Motor Determinista de Cruce (24 abril 2026)
  y por 4/5 Sabios consultados.

## Alternativas Evaluadas
| Plataforma | Licencia | Veredicto | Razón |
|---|---|---|---|
| LangGraph PostgresSaver | MIT/Apache | **GANADOR** | Nativo, 0 infra extra |
| Hatchet | MIT | Plan B | Solo PostgreSQL, diseñado para AI |
| Temporal | MIT | **DESCARTADO** | Journal replay incompatible con LLMs |
| Restate | BSL 1.1 | Descartado | Licencia no open source |
| Windmill | AGPL | Descartado | 3 CVEs graves abril 2026 |
