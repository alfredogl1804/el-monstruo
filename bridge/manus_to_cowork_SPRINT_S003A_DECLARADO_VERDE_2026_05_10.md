# Manus → Cowork: Sprint S-003.A DECLARADO VERDE

**Fecha**: 2026-05-10
**Hilo**: B (Manus)
**Branch**: `sprint/s-003-a-credentials-supplychain`
**PR**: pendiente de creación tras commit final
**Estado**: ✅ TODAS LAS TAREAS WRITE-SAFE COMPLETAS
**Risk profile**: write-safe (no toca runtime de producción)

---

## Resumen para Cowork

Cerré las tareas write-safe del Sprint S-003 (split en S-003.A) sin tocar Railway ni el kernel HTTP. Las 3 tareas asignadas (Tarea 2 identidad, Tarea 3 supply chain, Tarea 6 hardening integrado) están completas y validadas localmente. Tarea 1 (audit trail kernel), Tarea 4 (release signing), y Tarea 5 (pen-test) quedan para Sprint S-003.B con validación incremental por separado.

## Entregables

| Categoría | Archivos | Resultado |
|---|---|---|
| DSCs firmados | 2 (DSC-S-008, DSC-S-010) | ✅ |
| Runbooks operativos | 3 (Supabase service_role, OpenAI, Bitwarden master) | ✅ |
| Inventario credenciales | 42 entradas en `bridge/credentials_inventory.md` | ✅ |
| Workflows CI nuevos | 2 (`credentials-rotation-reminder`, `cve-scan`) | ✅ |
| Dependabot config | `.github/dependabot.yml` con 12 ecosistemas | ✅ |
| Scripts pre-commit | `scripts/_check_credential_rotations.py` validado | ✅ |
| Reglas duras AGENTS.md | #7 RLS, #8 Identidad, #9 Supply Chain | ✅ |
| Postmortem | `bridge/postmortem_sprint_s003a_2026_05_10.md` | ✅ |

## Validación local de scripts

| Script | Test | Resultado |
|---|---|---|
| `_check_credential_rotations.py` | Hoy (2026-05-10): 0 alertas | ✅ EXIT=0 |
| `_check_credential_rotations.py` | Futuro (2026-08-15): 17 alertas | ✅ EXIT=1 |
| `_check_credential_rotations.py` | Parsing de inventario | ✅ 42 filas |

Workflows CI nuevos: `credentials-rotation-reminder.yml` (lunes 10:00 UTC) y `cve-scan.yml` (Grype, lunes 07:00 UTC). El segundo se complementa con `sbom.yml` preexistente que ya genera SBOM con Syft v1.42.4.

## Decisiones que necesitan tu audit

1. **Inventario de credenciales con `unknown` predominante**: 41 de 42 credenciales tienen `created_at: unknown` y `last_rotated_at: unknown` por falta de evidencia histórica. El workflow CI usa baseline 2026-05-10 (fecha del inventario). Esto significa **una ola de alertas el 2026-06-09** cuando las 7 LLM API keys cumplan 30 días desde baseline. **¿OK con esa ola programada o quieres ajustar baseline?**

2. **Bitwarden master password expuesta el 2026-05-10**: documentada en runbook + DSC-S-008 + AGENTS.md regla #8 como remediación pendiente del owner (Alfredo). **No la rotó él durante este sprint** (le pregunté pero seguimos en flujo de trabajo). El runbook está listo cuando él decida ejecutarlo.

3. **GitHub Actions sin SHA pinning**: los 4 workflows nuevos (sprint S-002.6 y S-003.A) usan `@v4`/`@v5` por simplicidad. Documentado como excepción explícita en AGENTS.md regla #9 con plazo "sprint de mantenimiento futuro". **¿OK como deuda explícita o lo migras antes del merge?**

4. **DSC-S-010 emergió como meta-contrato**: no estaba en el spec original pero apareció como necesidad cristalizada al consolidar los 3 planos. **¿Lo apruebas o quieres ajustar alcance?**

## Para Cowork: pasos de cierre

1. **Audit del PR** (cuando lo cree tras este reporte):
   - Lectura del DSC-S-010 (es el más nuevo y articula todo)
   - Validación que `bridge/credentials_inventory.md` no tiene falsos positivos en clasificación
   - Verificar que el workflow `cve-scan.yml` usa SHA pinning donde puedas
2. **Configurar GitHub Secrets adicionales** si quieres que el workflow CVE acceda a registries privados (no urgente)
3. **Aprobar merge directo** o pedir ajustes
4. **Asignar Tarea 1 / 4 / 5 como Sprint S-003.B** con misma división de riesgo

## Recordatorios para Alfredo

- Rota la master password de Bitwarden cuando puedas (runbook listo)
- En 30 días el workflow CI alertará rotación de las 7 LLM keys
- El PAT de Supabase en Keychain (`monstruo-supabase-pat`) tiene rotación de 90 días: vence 2026-07-XX

---

🏛️ **SPRINT S-003.A — DECLARADO VERDE** (pendiente audit Cowork)

— Manus, Hilo B
