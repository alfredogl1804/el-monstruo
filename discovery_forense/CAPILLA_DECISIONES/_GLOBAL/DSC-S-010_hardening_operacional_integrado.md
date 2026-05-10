# DSC-S-010: Hardening operacional integrado

**Tipo**: Decisión Soberana Canonizada (Seguridad / Meta)
**Estado**: FIRMADO
**Sprint origen**: S-003.A
**Fecha**: 2026-05-10
**Autor ejecutor**: Hilo B (Manus)
**Orquestador**: Cowork (Claude)
**Referencias cruzadas**: DSC-S-001, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005, DSC-S-006, DSC-S-007, DSC-S-008

---

## Contexto

Los sprints S-002.5 (RLS P0+P1), S-002.6 (RLS universal + naming canónico), y S-003.A (rotación + supply chain) cristalizaron una doctrina operativa de seguridad sustentada en tres planos: **plano de datos** (RLS por defecto, DSC-S-006), **plano de identidad** (rotación automatizada, DSC-S-008), y **plano de cadena de suministro** (Dependabot + SBOM + CVE scan, sin DSC dedicado hasta este). Sin embargo, estos planos hasta ahora vivían como reglas dispersas en AGENTS.md y DSCs individuales sin un meta-contrato que articulara su interdependencia, sus SLAs operativos, y la disciplina de mantenimiento perpetuo. DSC-S-010 cierra esa brecha como contrato meta-operacional.

## Decisión

El hardening del Monstruo opera bajo **tres planos canónicos** que se vigilan continuamente y se mejoran por sprint. Cada plano tiene policy enforcement (linter pre-commit, workflow CI), audit periódico, y SLA de respuesta a incidentes. Ningún plano puede cerrarse: la seguridad es ciclo perpetuo, no estado terminal. Los hallazgos de cada sprint deben sembrarse como deuda en los siguientes sprints.

## Los 3 planos y sus contratos

### Plano de datos

Toda tabla y vista materializada del schema `public` de Supabase nace bajo policy explícita firmada en migración versionada. La doctrina es: **ningún dato es accesible sin policy explícita**. Enforcement vía linter pre-commit `_check_rls_default.py` (rechaza commits) y workflow CI `rls-audit-weekly.yml` (lunes 06:00 UTC, audita producción y abre issue auto). Policy mínima: `service_role` puede todo, anon/authenticated nada (a menos que la tabla justifique acceso público con DSC dedicado). Vistas materializadas no soportan RLS nativo; protegerlas con `REVOKE ALL FROM PUBLIC, anon, authenticated`. SLA de remediación: deuda detectada en audit semanal debe cerrarse antes del cierre del próximo sprint que toque la tabla afectada.

### Plano de identidad

Toda credencial activa del proyecto está inventariada en `bridge/credentials_inventory.md` con tipo, storage primario, fechas conocidas, frecuencia objetivo, responsable y runbook. La doctrina es: **ninguna credencial existe sin trazabilidad**. Enforcement vía workflow CI `credentials-rotation-reminder.yml` (lunes 10:00 UTC, lee inventario y abre issue cuando alguna credencial supera 80% de su frecuencia objetivo). Frecuencias canónicas: LLM keys 30 días, service-role 90 días, PATs 90 días, master passwords 90 días, service tokens limitados 180 días, webhook secrets 180 días. SLA de remediación: rotación inmediata al detectar exposure, rotación programada en <14 días al recibir alerta del workflow.

### Plano de cadena de suministro

Toda dependencia externa del Monstruo está sujeta a escaneo continuo. La doctrina es: **la cadena de suministro es tan crítica como el código propio**. Enforcement vía workflow CI `cve-scan.yml` (Grype contra SBOM generado por Syft, falla si CRITICAL/HIGH, abre issue auto), workflow `sast.yml` (Semgrep en cada PR), workflow `license-audit.yml` (validación de licencias en cada push a main). Updates automáticos de dependencias vía `.github/dependabot.yml` (PRs semanales agrupados, lunes 09:00-11:00 UTC). SLA de respuesta: CRITICAL en <72h, HIGH en <7d, MEDIUM en próximo sprint, LOW documentar y diferir si justificado.

## Disciplina perpetua

Los tres planos se vigilan como sistema, no como checklist. Cada sprint que toca infraestructura, código, dependencias, credenciales o datos debe responder en el reporte final: ¿qué deuda nueva introdujo este sprint en cada plano? ¿qué deuda heredada redujo? La métrica de éxito no es "sin deuda" (utopía) sino "deuda monotónicamente decreciente con visibilidad total". El workflow CI semanal funciona como sensor; los runbooks operativos como protocolo de respuesta; los DSCs como memoria institucional irrevocable. Bypass de cualquiera de los tres mecanismos de enforcement (linters, workflows, DSCs) requiere DSC firmado en el mismo PR con justificación documentada y plazo de remediación.

## Métricas trackeable por sprint

| Métrica | Baseline 2026-05-10 (post S-002.6 + S-003.A) | Objetivo S-003.B |
|---|---|---|
| Tablas con RLS habilitado en `public` | 117/117 (100%) | 100% sostenido |
| Tablas con RLS sin policy (deuda) | 0 | 0 |
| Matviews protegidas | 2/2 | 100% sostenido |
| Credenciales en inventario | 42/42 (100%) | 100% sostenido |
| Credenciales con `created_at: unknown` | 41/42 | reducir según se rote |
| Runbooks documentados | 3/42 (7%) | 10/42 (24%) |
| Workflows CI de seguridad activos | 7 (sast, sbom, license-audit, secret-scan, ai-infra-guard, rls-audit-weekly, credentials-rotation-reminder, cve-scan) | mantener |
| GitHub Actions pinned by SHA | parcial (sprint 17 + nuevos no migrados) | 100% (sprint mantenimiento) |
| Audit trail de requests al kernel | 0% (no implementado) | 100% (sprint S-003.B) |
| Release signing | no implementado | implementado (sprint S-003.B) |

## Implicaciones operativas

Cualquier sprint futuro que viole alguno de los tres planos debe declarar la violación explícitamente y asumir responsabilidad de remediación en el sprint siguiente. Los hallazgos de tipo "deuda detectada" durante audits no bloquean cierres de sprint, pero deben quedar documentados en el postmortem del sprint en curso y aceptados explícitamente por Cowork. La auditoría externa (futura, no en este sprint) puede consultar este DSC como contrato vivo del estado de seguridad del Monstruo.

## Cruces explícitos

DSC-S-001 a DSC-S-005 establecen los principios fundacionales (no-secrets-in-code, pre-commit hooks, TTLs, anti-patterns, archive-first cleanup); DSC-S-010 los integra como sistema operativo coherente. DSC-S-006 y DSC-S-007 cubren el plano de datos; DSC-S-008 cubre el plano de identidad; DSC-S-010 añade el plano de supply chain como tercera columna. DSC-S-009 (release signing, pendiente del sprint S-003.B) extenderá el plano de supply chain con verificación de integridad de artefactos desplegados.

---

**Firmado**: 2026-05-10 — Sprint S-003.A
