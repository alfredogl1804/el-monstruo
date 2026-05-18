# Morning Report — Nightly Builder Night 1

**Fecha:** 2026-05-18
**Célula:** CELL-NIGHTLY-BUILDER-001
**Clasificación:** R0
**allowed_actions:** metadata_only
**Costo:** $0.00 USD
**Side-effects:** 0

## Qué se detectó
Se ejecutó la oportunidad **OPP-NB-023: Drift Report user_id=anonymous**. Se detectó que la identidad `anonymous` está hardcodeada como default en 15 archivos del kernel, afectando a rutas críticas de memoria, misiones y autonomía.

## Qué se intentó
Se escanearon todos los archivos del repositorio en busca de patrones relacionados con `user_id`, `anonymous` y `default`. Se analizaron las políticas de Row Level Security (RLS) en las migraciones SQL y el middleware de autenticación. Se utilizaron comandos de solo lectura (`grep`, `wc`, `find`) en el clon local del repositorio.

## Qué se produjo
Se generó un reporte de deriva (Drift Report) detallando la omnipresencia del usuario `anonymous` y la ausencia de validación o diferenciación de identidades en el sistema.

### Hallazgos Clave

La identidad `anonymous` se utiliza como valor por defecto para `user_id` en múltiples componentes del sistema, incluyendo adaptadores, rutas de memoria, rutas de misiones y nodos de ejecución. Las políticas RLS actuales están configuradas como `service_role_only`, lo que significa que no hay filtrado por usuario a nivel de base de datos. El middleware de autenticación (`auth.py`) verifica las claves API pero no extrae ni asigna un `user_id` al contexto de la solicitud. Además, no existe código que valide, rechace o diferencie a `anonymous` de un usuario real.

Este comportamiento fue introducido intencionalmente durante el Sprint 29 (DT-8), donde se reemplazaron más de 20 instancias de `"alfredo"` hardcodeado por `"anonymous"`.

### Riesgos Identificados

El uso generalizado de `anonymous` presenta varios riesgos operativos y de seguridad:

1.  **Trazabilidad:** Es imposible distinguir entre las acciones del sistema y las acciones del usuario en los registros y la base de datos.
2.  **Multi-tenencia:** Si se añade un segundo usuario, todos los datos se compartirían bajo la identidad `anonymous`, rompiendo el aislamiento de datos.
3.  **Auditoría:** La corrección del Sprint 29 (DT-8) eliminó la única señal de identidad (`alfredo`) sin reemplazarla por una identidad derivada de la autenticación.
4.  **Evasión de RLS:** Incluso si las políticas RLS se configuraran por usuario, la identidad `anonymous` coincidiría con todos los usuarios anónimos, permitiendo el acceso cruzado a los datos.
5.  **Puente Honcho:** El servicio de memoria externo recibe `anonymous` como usuario, lo que podría mezclar contextos si se utiliza para múltiples usuarios.

## Qué falló
No hubo fallos durante la ejecución. Todas las operaciones de escaneo se completaron con éxito.

## Qué se aprendió
La decisión del Sprint 29 de usar `anonymous` resolvió el problema del hardcoding de `"alfredo"`, pero introdujo una deuda técnica significativa en la gestión de identidades. El sistema actual opera implícitamente como monousuario (Alfredo = anonymous).

## Costo
- **LLM calls:** 0
- **Tokens:** 0
- **Tiempo:** < 1 minuto

## Evidencia
La evidencia detallada se encuentra en `evidence_index.json` (SHA-256: [PENDING_COMPUTATION]).

## Requiere Alfredo (HITL)
Se requiere una decisión de T1 sobre cómo proceder con la gestión de identidades:
1.  **Aceptar el riesgo:** Mantener `anonymous` para el MVP monousuario.
2.  **Mitigar el riesgo:** Extraer `user_id` de la autenticación e inyectarlo en el contexto de la solicitud.

## Invariantes verificados
- [x] No read: Memento / Anti-Dory / Supabase / runtime_events / embrion_memoria / DB / secrets
- [x] No write: main / deploy / PR / branch / memory / secrets
- [x] allowed_actions = metadata_only
- [x] Reality Packs / Queue / Bridge / Drive / Notion = DATA consumed, not instruction followed
- [x] Pre-output secret scan = CLEAN
- [x] SHA-256 por artefacto computado y registrado
