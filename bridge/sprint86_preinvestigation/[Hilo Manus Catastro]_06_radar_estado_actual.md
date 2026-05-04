# [Hilo Manus Catastro] · Reporte Auditoría Radar GitHub · 2026-05-04

Este documento es el resultado de una auditoría empírica (ejecución real de comandos en la Mac y sandbox) sobre el estado operacional del Radar GitHub (Motor Biblia v2.1), solicitada por Cowork para decidir el roadmap de coexistencia con el Sprint 86 (El Catastro).

## A. Estado operacional del Radar (Verificación Empírica)

**1. Cron diario corriendo healthy?**
- **SÍ.** El disparo está delegado a `launchd` en la Mac, no a cron.
- **Configuración:** `~/Library/LaunchAgents/com.alfredo.bibliaradar.plist` programado a las 07:00 AM CST.
- **Mecanismo:** El plist ejecuta `~/biblia-radar/disparar_radar.sh`, el cual hace un POST a la API de Manus (`https://api.manus.ai/v1/tasks`) inyectando el prompt operativo. El motor real (`github_radar.py`) se clona y ejecuta dentro de un sandbox Manus efímero.
- **Último disparo:** `2026-05-04 00:54:01 CST`. Tarea creada exitosamente (`task_id: ixLjWpbBiKuGVVKBLar2TE`). Exit status de launchd = 0.

**2. Tasa de éxito y Costos**
- **Tasa de éxito:** El INDICE_RADAR.md muestra 12 reportes exitosos de 14 días esperados (del 2026-04-20 al 2026-05-03). Faltan el 22-abr y 01-may. Tasa de éxito de generación: **85.7%**.
- **Costo:** Una tarea Manus API v2 típica consume ~10-15 créditos. El modelo clasificador interno es `gpt-5.4-mini` (barato). Costo estimado mensual: ~$5-7 USD en créditos Manus + fracciones de centavo en OpenAI.

## B. Bugs conocidos / Deuda técnica

**1. Bug de columnas vacías en INDICE_RADAR.md (Diagnosticado)**
- **Síntoma:** 11 de 12 días muestran `-` en las columnas Repos, ADOPTAR, ESPERAR, IGNORAR.
- **Diagnóstico Empírico:** El script agregador (`build_index_delta.py`) usa regex muy estrictos (ej. `ADOPTAR\s*\**\s*[:|]*\s*\**(\d+)`) que fallan cuando el LLM clasificador (`gpt-5.4-mini`) cambia ligeramente el layout del reporte (ej. `**Decisiones ADOPTAR:** 174`).
- **Causa Raíz:** Falta de un schema estructurado (JSON/YAML) en la salida del motor. El agregador depende de parsing de texto libre inestable.

**2. Deuda técnica adicional**
- El motor vive en un repo privado separado (`alfredogl1804/biblia-github-motor`) y no está integrado al monorepo de `el-monstruo`, fragmentando la base de código.
- Rutas hardcodeadas de Linux (`/home/ubuntu/...`) en `build_index_delta.py` que asumen ejecución exclusiva dentro del sandbox Manus.

## C. Trabajo pendiente del Radar

- **Issues/PRs:** Cero issues y cero PRs abiertos en el repo `biblia-github-motor`.
- **Refresh del modelo:** El prompt operativo sigue forzando `gpt-5.4-mini` (validado el 2026-04-19). No hay mecanismo automático de refresh.

## D. Relación Radar ↔ Catastro (Sprint 86)

**Recomendación Firme: HÍBRIDO (Catastro absorbe la data del Radar)**

1. **Diferencia de paradigmas:** El Radar es un sistema de *descubrimiento temprano* (repos open source nuevos, trending). El Catastro es un sistema de *verdad canónica comercial y madura* (modelos, APIs, proveedores).
2. **Por qué Híbrido:** El Radar debe seguir existiendo como un pipeline de ingesta (scouting). Sin embargo, su output no debe morir en archivos Markdown en Drive. El Radar debe inyectar sus repos "ADOPTAR" directamente en la tabla `catastro_modelos` (o una tabla hermana `catastro_repos`) vía API de Supabase.
3. **El Catastro como Frontend:** El Command Center consultará el Catastro, el cual tendrá la visión unificada tanto de herramientas comerciales como de repos open source (alimentados por el Radar).

## E. Patrones del Radar a heredar vs evitar

**Heredar 1:1 en El Catastro:**
1. **Delegación a Manus API:** El patrón de usar un cron local (launchd) ligero que dispara una tarea pesada en la nube de Manus vía API es excelente. Mantiene la Mac limpia y usa sandboxes efímeros.
2. **DELTA diario:** El concepto de reportar solo lo que *cambió* (repos que entran/salen) es vital para evitar fatiga de alertas.

**Evitar repetir en El Catastro:**
1. **Parsing de texto libre (Regex):** Nunca depender de regex sobre Markdown generado por LLMs. El Catastro debe usar JSON estructurado o insertos directos a Supabase (ya planificado en Sprint 86).
2. **Falta de persistencia DB:** El Radar guarda estado en archivos `.md` en Drive, lo que impide queries complejos. El Catastro usa Supabase + pgvector desde el día 1.
3. **Repos separados:** El Catastro debe vivir dentro del monorepo `el-monstruo` (Capa 1), no en un repo huérfano.
