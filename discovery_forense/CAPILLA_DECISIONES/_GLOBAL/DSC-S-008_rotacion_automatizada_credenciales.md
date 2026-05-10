# DSC-S-008: Rotación automatizada de credenciales

**Tipo**: Decisión Soberana Canonizada (Seguridad)
**Estado**: FIRMADO
**Sprint origen**: S-003.A
**Fecha**: 2026-05-10
**Autor ejecutor**: Hilo B (Manus)
**Orquestador**: Cowork (Claude)
**Referencias cruzadas**: DSC-S-001, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005, DSC-S-006, DSC-S-007, DSC-G-008 v2

---

## Contexto

El proyecto El Monstruo posee **38 credenciales** desplegadas en Railway env vars del servicio kernel (verificadas el 2026-05-10), más credenciales adicionales almacenadas en macOS Keychain, Bitwarden y dashboards de proveedores. Hasta este sprint, no existía política unificada de rotación, ni inventario centralizado, ni proceso de recordatorio. El incidente del 2026-05-06 (credenciales en repo público) y el incidente del 2026-05-10 (master password de Bitwarden expuesta accidentalmente en chat) demostraron que la confianza en la memoria del owner no es estrategia de seguridad sostenible.

## Decisión

Toda credencial del proyecto debe estar inventariada en `bridge/credentials_inventory.md` con: tipo, storage primario, fecha de creación documentada, fecha de última rotación, frecuencia objetivo de rotación, y responsable. La rotación es obligatoria cuando ocurre cualquiera de tres condiciones: la credencial supera su frecuencia objetivo, hay sospecha confirmada de exposición, o un colaborador con acceso deja el proyecto. El proceso de rotación de cada credencial debe estar documentado en un runbook canónico bajo `bridge/runbooks/runbook_rotacion_<credencial>.md` con pasos exactos: generar nueva credencial, actualizar storage, verificar funcionamiento, revocar la antigua, documentar la rotación. Un workflow CI semanal lee el inventario, calcula tiempo desde última rotación, y abre issue automático cuando alguna credencial supera el 80% de su frecuencia objetivo.

## Inventario inicial

El inventario completo vive en `bridge/credentials_inventory.md`. Contiene las **38 credenciales** detectadas en Railway más las credenciales auxiliares en Keychain, Bitwarden y dashboards externos. Cada entrada documenta tipo, storage, fechas conocidas, frecuencia objetivo y responsable.

## Frecuencias objetivo (canónicas)

| Categoría | Frecuencia objetivo | Justificación |
|---|---|---|
| Service-role/admin keys (Supabase service, Stripe secret, GitHub PAT con `repo`+`workflow`) | 90 días | Acceso amplio, alta superficie de daño |
| LLM API keys (OpenAI, Anthropic, Gemini, Grok, etc.) | 30 días | Costo por token alto, abuso detectable solo post-facto |
| Service tokens limitados (Telegram bot, Notion, Dropbox app) | 180 días | Scope acotado, menor superficie |
| Webhook secrets (Telegram webhook, Stripe webhook) | 180 días | Solo verificación de origen, no acceso directo |
| Personal Access Tokens (Supabase PAT, Railway token) | 180 días | Identidad ampliada, riesgo medio |
| Master passwords (Bitwarden, Apple ID) | 90 días | Llave de bóveda, riesgo crítico |
| DB passwords (Postgres) | 90 días | Acceso directo a datos |

## Runbooks priorizados (3 críticos primero)

El sprint S-003.A entrega runbooks operativos para las 3 credenciales de mayor riesgo y frecuencia: `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`, y `BITWARDEN_MASTER_PASSWORD`. Los 35 runbooks restantes quedan diferidos a sprints S-003.1 y posteriores, con prioridad asignada según frecuencia objetivo.

## Workflow CI

`.github/workflows/credentials-rotation-reminder.yml` corre semanalmente (`cron: '0 10 * * 1'`, lunes 10:00 UTC) y ejecuta `scripts/_check_credential_rotations.py`. El script lee `bridge/credentials_inventory.md`, calcula días transcurridos desde `last_rotated_at` para cada credencial, y abre issue automático cuando supera el 80% de la frecuencia objetivo. El issue lleva labels `security`, `rotation-reminder`, `auto-generated` y un cuerpo con la lista de credenciales por rotar y el runbook correspondiente.

## Cumplimiento e implicaciones

Sprints futuros que introduzcan nuevas credenciales deben actualizar `credentials_inventory.md` en el mismo PR donde se introduce la credencial. El linter pre-commit del Sprint S-002.6 (`_check_rls_default.py`) cubre el patrón anti-DSC-S-004 (defaults sospechosos). La política de rotación se valida vía workflow CI; ninguna rotación manual es válida sin documentación posterior en el inventario. La doctrina canónica es: ninguna credencial activa del proyecto puede existir sin entrada en el inventario.

## Cruces explícitos

DSC-S-001 establece que tokens nunca van en código; DSC-S-008 garantiza que estos tokens reciban rotación periódica. DSC-S-002 enforza pre-commit hooks; DSC-S-008 añade audit semanal complementario. DSC-S-003 fija TTL máximos; DSC-S-008 los formaliza con frecuencias objetivo automatizadas. DSC-S-004 prohíbe defaults sospechosos en código; DSC-S-008 cierra el loop con runbooks que sustituyen valores hardcodeados con `require_env()`. DSC-S-005 establece archive-first para cleanup; DSC-S-008 aplica este principio a credenciales legacy (revocadas pero documentadas). DSC-S-006 y DSC-S-007 protegen el plano de datos; DSC-S-008 protege el plano de identidad.

---

**Firmado**: 2026-05-10 — Sprint S-003.A
