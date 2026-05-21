# BATCH 006 — CÉLULA D: ROLLBACK PLAN

## Objetivo
Proporcionar un mecanismo determinístico para revertir el sistema a su estado original (pre-Anti-Dory) en caso de que la Fase 1 Canary detecte una falla catastrófica o degradación inaceptable.

## 1. Rollback de Supabase (SQL)
Si las tablas de Anti-Dory causan problemas de rendimiento o interfieren con operaciones existentes, ejecutar este script:

```sql
-- 1. Eliminar tabla Plan Ledger y registro de migración
DROP TABLE IF EXISTS anti_dory_plan_ledger CASCADE;
DELETE FROM supabase_migrations.schema_migrations WHERE version = '0051';

-- 2. Eliminar tabla Anchor Store y registro de migración
DROP TABLE IF EXISTS anti_dory_anchor_store CASCADE;
DELETE FROM supabase_migrations.schema_migrations WHERE version = '0050';
```
*Nota: Este rollback asume que no hay dependencias externas (foreign keys) hacia estas tablas desde módulos legacy.*

## 2. Rollback de Código (Git)
Si el código en `main` causa fallos, revertir el Mega-PR de integración:

```bash
# Identificar el commit de merge del PR de Anti-Dory Batch 005
git log --oneline
# Revertir el merge commit (asumiendo que es el HEAD actual)
git revert -m 1 HEAD
git push origin main
```

## 3. Desactivación Rápida (Sin Rollback de Git)
Si se prefiere no revertir el código, pero se necesita apagar Anti-Dory:

1. **Feature Flags:** Asegurar que `b10_guardian_cron.py` tenga `FEATURE_FLAG_GUARDIAN_AUTONOMO = False`.
2. **Fase 1 Flag:** Asegurar que cualquier verificación de `FASE_1_CANARY_ACTIVE` devuelva `False`.
3. **Mocks:** Si `b4_memento.py` o `b2_claim_vg.py` están interceptando tráfico real, cambiar sus routers para que hagan bypass (passthrough) al comportamiento legacy.

## 4. Confirmación de Guardian OFF
Verificar que el Guardian Autónomo (Cron) no esté corriendo en background:
```bash
# Revisar logs del worker en Railway (si aplica)
railway logs | grep "guardian_cron"
# Confirmar que no hay ejecuciones recientes
```

## Confirmación
- **NO EJECUCIÓN:** Este documento es solo el plan de rollback preventivo.
- Diseñado para ser ejecutado por T1 o un agente autorizado en caso de emergencia.
