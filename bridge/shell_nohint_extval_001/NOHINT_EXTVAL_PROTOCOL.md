# SHELL No-Hint External Validation Protocol

**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001 — Carril D

## Objetivo
Validar que el encoding No-Hint de SHELL transporta significado operativo robusto sin pistas textuales, utilizando 4 providers verificados como decodificadores ciegos.

## Protocolo
Cada provider recibe exclusivamente:
1. El payload JSON opaco (`nohint_encoding_attempt_001.json`).
2. El axis registry dimensional (`shell_axis_registry_v0.yaml` resumido).
3. El decoder prompt (instrucciones de decodificación pura).

No se proporciona: contexto previo, decoded understanding report, explicación de respuesta esperada, ni summary.

## Providers
- OpenAI `gpt-4o-mini`
- Anthropic `claude-sonnet-4-20250514`
- Google `gemini-2.0-flash`
- xAI `grok-3-mini-fast`

## Budget
- Max total: $1.00 USD
- Max calls per provider: 1
- Retries: 0

## Invariantes Evaluados (10)
1. T1_IDENTIFIED
2. DISPATCHER_IDENTIFIED
3. STATE_FABRIC_IDENTIFIED
4. SINGLE_WRITER_DEDUCED
5. NO_FREE_MESH_DEDUCED
6. NO_R1_DETECTED
7. T1_AUTHORITY_CONFIRMED
8. RISK_ANALYSIS_PRESENT
9. LOOPS_IDENTIFIED
10. GUARDRAILS_NOTED

## Criterio
- STRONG_PASS: 4/4 providers >= 9/10
- PASS: 3/4 providers >= 8/10
- WEAK_PASS: 2/4 providers >= 8/10
- FAIL: 2+ providers pierden T1/NO_R1/NO_RUNTIME
