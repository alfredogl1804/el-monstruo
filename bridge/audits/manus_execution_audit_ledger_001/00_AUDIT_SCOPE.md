# 00 — AUDIT SCOPE

## Sprint
SPR-MANUS-EXECUTION-AUDIT-LEDGER-001-v2

## Alcance
Auditar todas las ejecuciones de Manus en el frente Reactor / Embriones / R0+ y pericia asociada, desde la branch `monstruo-reality-atlas-001`.

## Frentes incluidos
- Scheduler R0
- Heartbeat R0
- Scheduler activation
- M2 readiness
- M2 one-shot
- M2 stabilization
- LIMITED_ACTIVE_R0
- Epoch 002
- Epoch 003
- Epoch 004 (si existe)
- Oracle autonomous embryo
- Scheduler-driven Oracle embryo
- Oracle auditor embryo
- Oracle pair bicefalo
- Grounding
- Epoch 005 first autonomous R0+ artifact
- Epoch 006 Memory Palace
- Epoch 007 T1 Feedback Loop
- Epoch 008 (OUT_OF_SCOPE_IF_NOT_YET_REPORTED_BY_T1 — pero detectado en repo)
- Pericia kit global95 coverage patch
- Pericia recalibration v1.2

## Reglas duras
- NO modificar codigo productivo
- NO tocar scheduler policy
- NO cambiar kill-switch
- NO ejecutar ciclos
- NO llamar providers
- NO tocar Supabase
- NO tocar DB
- NO tocar secrets
- NO memory/Memento/Anti-Dory writes
- NO APP_VISION
- NO canon
- NO PRE-IA close
- NO main
- NO PR
- NO deploy
- NO R1
- NO Self-Evolution
- NO Perplexity
- NO DeepSeek
- NO provider auto-replacement
- NO runtime
- NO SHELL runtime

## Que NO se audita
- Branches distintas a monstruo-reality-atlas-001 (salvo cross-reference)
- Commits en main (solo se verifica si algun commit IN_SCOPE toco main)
- Codigo de kernel/ que no fue tocado por commits del frente
- Infraestructura CI/CD (auditada en otro sprint)

## Declaraciones obligatorias
- "Accepted by ChatGPT-0" NO es equivalente a "Fully Audited"
- "Tests PASS reportados" NO es equivalente a "Tests verificados"
- No se toca piloto vivo
- No se cambia kill-switch
- No se ejecutan ciclos
- No se justifica a Manus
- No se defiende el trabajo
- No se inflan resultados

## Metodologia
1. Commit Universe via git log (no solo lista manual)
2. Diff-tree por commit
3. Hard rules scan por paths y contenido
4. Test/cost/provider extraction de reports
5. Event log / state scan
6. Claims vs evidence cross-reference
7. Classification final
8. Anomalies / risks / verdict

## Fecha
2026-05-21

## Agente ejecutor
Manus B (celula SPR-MANUS-EXECUTION-AUDIT-LEDGER-001-v2)

## Branch auditada
origin/monstruo-reality-atlas-001 HEAD: d41d14c
