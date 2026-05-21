# NEXT DECISIONS T1: Post-Heartbeat R0

Tras la ejecución exitosa del primer latido one-shot, Alfredo (T1) debe tomar las siguientes decisiones para definir el futuro del runtime del Monstruo:

## Decisiones Críticas sobre el Runtime

1. **Autorizar SPR-REACTOR-SCHEDULER-R0-001**
   - ¿Autorizas la creación de un scheduler persistente (cron/daemon) que ejecute este latido automáticamente?
   - [ ] SÍ
   - [ ] NO

2. **Frecuencia Candidata**
   - Si se aprueba el scheduler, ¿cuál debe ser la frecuencia base del latido?
   - [ ] Cada 6 horas
   - [ ] Cada 12 horas
   - [ ] Diario (24h)
   - [ ] Manual Only (no automatizar aún)

3. **Alcance del Heartbeat Automatizado**
   - Cuando el latido corra en background, ¿debe limitarse a reportar (`RUN_AUDIT_ONLY_R0`) o puede ejecutar cadenas locales (`RUN_ORACLE_CHAIN_R0`)?
   - [ ] Solo reportar anomalías
   - [ ] Ejecutar cadenas R0 completas

4. **Budget Recurrente**
   - ¿Cuál es el límite de gasto (USD) permitido por ciclo de latido automatizado (para cuando se autorice R1+)?
   - [ ] $1.00 / ciclo
   - [ ] $5.00 / ciclo
   - [ ] Otro: _______

5. **Integración con Cockpit**
   - ¿El reporte del latido debe enviarse a una interfaz visual (Cockpit) o basta con archivos Markdown en el repo?
   - [ ] Markdown en repo es suficiente
   - [ ] Requiere UI (Cockpit)

6. **Destino de los Outputs (Catastro)**
   - ¿Los reportes y el State Fabric deben migrarse a Supabase para persistencia a largo plazo, o se mantienen como JSON/MD locales?
   - [ ] Mantener local (JSON/MD)
   - [ ] Iniciar migración a Supabase
