# Sprint COMMAND_CENTER_THEME_001 — Migración theme a Apple/Tesla

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFT para firma T1
**Paradigma:** D (sin SMP — es solo theme, sin data sensible). **Owner:** Manus E1 (repo `el-monstruo-command-center`, Next.js). **Lane:** frontend theme.
**Objetivo:** Migrar el theme del Command Center de cyan/púrpura genericos a la paleta canónica Apple/Tesla firmada T1 (DSC-MO-002 v3).

## Objetivo
Corregir el drift de theme del Command Center. Hoy (matriz §2.14) usa cyan `#00E5FF` + púrpura `#BB86FC` (inspired ChatGPT/Claude/Gemini) — drift binario contra el Brand DNA. Migrar a la paleta canónica Apple/Tesla firmada T1 (DSC-MO-002 v3).

## Paleta destino (DSC-MO-002 v3, firmada T1 2026-05-27)
- Base neutra: `#F5F5F7` off-white Apple, `#1D1D1F` near-black Apple, `#171A20` dark Tesla, `#FFFFFF`/`#000000`, grises Apple.
- Acento primario: rojo Tesla `#E82127`. Acento secundario: azul Apple `#0071E3`.
- DEPRECADO: cyan/púrpura actuales + forja-graphite-acero.

## Alcance
- ✅ Reemplazar tokens de color cyan/púrpura por la paleta Apple/Tesla en las 7 superficies (chat, finops, fleet, memory, runs, security, settings).
- ✅ Minimalismo Apple/Tesla (restraint, neutral, contenido sobre cromo).
- Repo separado (`el-monstruo-command-center`) — NO es el kernel ni la app Flutter.

## Tareas
- T1: localizar el sistema de tokens/theme del Command Center (Tailwind config / CSS vars).
- T2: reemplazar paleta cyan/púrpura → Apple/Tesla (base neutra + rojo Tesla primario + azul Apple secundario).
- T3: pasada de las 7 superficies para consistencia (sin hardcodes de color viejo).
- T4: screenshot binario antes/después para audit visual.

## Reglas duras
- Cero secrets. Solo theme (sin lógica de data).
- Coherencia con DSC-MO-002 v3 (fuente única de la paleta). Si hay duda de hex, DSC-MO-002 manda.

## Criterios de Cierre
PR sin auto-merge en el repo command-center, audit Cowork (screenshot antes/después). Verde = 7 superficies en paleta Apple/Tesla, cero cyan/púrpura residual. **Comando reproducible:** `pnpm test` + `grep -rE '#00E5FF|#BB86FC' src/` devuelve 0 ocurrencias. **Artifact:** screenshot antes/después de las 7 superficies en `bridge/artifacts/command_center_theme_2026_05_27/`. **Verificación hex:** archivo de tokens contiene exactamente `#E82127` + `#0071E3`.

## Nota
Depende de que DSC-MO-002 v3 esté sincronizado al repo (hoy pendiente por caída de API GitHub). Ejecutar tras sync de v3.

— Cowork T2-A, DRAFT (local; push pendiente API GitHub)
