# DTA Automatizaciones — Forja Omega Tramo 1

Pipeline de resguardo automático para la bitácora viva (`bitacora.jsonl`).

## Qué resuelve

La captura en JSONL es autónoma. Pero sin estas automatizaciones, el resguardo depende de intervención manual. Este pipeline cierra ese gap con 4 piezas:

| # | Automatización | Trigger | Estado |
|---|----------------|---------|--------|
| 1 | Commit + Push | ≥5 líneas nuevas o cierre de bloque | Operativa |
| 2 | Index regenerado | Pre-commit (encadenado a #1) | Operativa |
| 3 | Guardian memoria | Post-push exitoso | Operativa (con KERNEL_API_KEY) |
| 4 | Genome Vivo | Post-push exitoso | Placeholder (sin endpoint PATCH) |

## Instalación

```bash
bash forja_omega_tramo_1/scripts/install.sh
```

Eso instala un git hook `post-commit` que dispara el pipeline cuando se modifica `bitacora.jsonl`. Opcionalmente instala un cron job cada 15 min como fallback.

## Uso manual

```bash
# Pipeline completo
python3 forja_omega_tramo_1/scripts/dta_sync.py

# Dry-run (muestra qué haría)
python3 forja_omega_tramo_1/scripts/dta_sync.py --dry-run

# Forzar sin umbral
python3 forja_omega_tramo_1/scripts/dta_sync.py --force

# Solo regenerar index
python3 forja_omega_tramo_1/scripts/dta_sync.py --index-only
```

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `KERNEL_API_KEY` o `MONSTRUO_API_KEY` | Para Auto 3 | API key del kernel Railway |
| `KERNEL_BASE_URL` | No | Override del URL base (default: producción) |

Si `KERNEL_API_KEY` no está disponible, el payload de Guardian se guarda en `_guardian_pending.jsonl` para envío manual posterior.

## Archivos generados

| Archivo | Propósito |
|---------|-----------|
| `bitacora_index.md` | Index auto-regenerado (versionado) |
| `_guardian_pending.jsonl` | Payloads pendientes de envío (no versionado) |
| `scripts/.dta_sync.log` | Log de ejecuciones (no versionado) |

## Requisitos

- Python 3.9+ (stdlib only, zero dependencies externas)
- git en PATH
- Acceso push al branch actual

## Diseño

- **1 script, 4 automatizaciones**: `dta_sync.py` es el orquestador único
- **Zero dependencies**: solo stdlib de Python (json, subprocess, pathlib, urllib)
- **Fail-safe**: si Guardian o Genome fallan, el pipeline no se detiene — guarda en pending log
- **Idempotente**: ejecutar múltiples veces no duplica commits ni payloads
- **Universal**: funciona para cualquier bitácora JSONL futura (cambiar constantes al inicio)

## Notas sobre Genome Vivo

El endpoint `GET /v1/genome/now` es solo lectura. No existe `PATCH` ni `POST` para actualizar campos arbitrarios. Por eso la Automatización 4 opera como placeholder:

1. Construye el payload correcto
2. Lo guarda en `_guardian_pending.jsonl`
3. Cuando exista un endpoint de escritura, se conecta sin cambiar la lógica

## Sprint

- Branch: `feat/dta-automatizaciones`
- PR target: `tramo-1-bitacora-y-dta`
- Autoría: Hilo B (Manus), 2026-05-29
