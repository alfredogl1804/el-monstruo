# Capilla de Decisiones — LA-FORJA

Decisiones canonizadas (Decision Sealed in Capilla, DSC) del proyecto **La Forja** — la herramienta personal de IA para Alfredo Góngora Sr.

Carpeta creada al cierre del Sprint LA-FORJA-001 D3.2 el 2026-05-16. Los DSC-LF-001 a DSC-LF-004 fueron canonizados retroactivamente en esa misma fecha porque vivían como referencias verbales en bridges y `_DOCTRINA_D3.md`. DSC-LF-005 nació firmado formalmente.

## Índice local

| ID | Título | Estado | Firma T1 |
|---|---|---|---|
| [DSC-LF-001](DSC-LF-001_cinco_puertas_inviolables.md) | Las 5 puertas inviolables (LF-FIVE-DOORS-001) | enforced | 2026-05-16 (retroactivo) |
| [DSC-LF-002](DSC-LF-002_budget_pre_call_check.md) | preCallCheck obligatorio antes de `next()` con HTTP 429 | enforced | 2026-05-16 (retroactivo) |
| [DSC-LF-003](DSC-LF-003_cap_budget_usuario_mes.md) | Cap $50 USD/mes con `postCallCommit` y rollback negativo | enforced | 2026-05-16 (retroactivo) |
| [DSC-LF-004](DSC-LF-004_magna_validation_perplexity_sonar.md) | Magna validation con Perplexity Sonar Reasoning Pro | enforced | 2026-05-16 (retroactivo) |
| [DSC-LF-005](DSC-LF-005_sse_obligatorio_endpoints_llm.md) | SSE obligatorio para endpoints LLM (Vercel AI SDK 6) | enforced | 2026-05-16 (firma original) |

## Cruces con DSCs globales

- **DSC-G-005** (validación tiempo real) — cruzado por DSC-LF-004 (magna usa Perplexity como capa de validación con citations).
- **DSC-G-008 v4** (validar codebase antes de specs) — cruzado por DSC-LF-005 (Cowork audit D3.2 verificó codebase con `git show beebff8 a53cca6 e13d669`).
- **DSC-G-017** (DSC as contract) — cruzado por todos: cada DSC-LF tiene paths ejecutables en `apps/la-forja/`.

## Estado actual del sprint LA-FORJA-001 al cierre D3.2

- **Commits cerrados:** `beebff8` (D3.2 inicial) → `a53cca6` (D3.2.1 Perplexity pase 1) → `e13d669` (D3.2.2 Perplexity pase 2) → `2ac7f81` (Cowork audit VERDE 14/14).
- **PR #133:** OPEN/READY/MERGEABLE. Merge manual T1 cuando decida.
- **D3.3 autorizado:** UI toggles `requireValidation` + `streamdown` + tests Chat.tsx con happy-dom + MSW.
- **Items diferidos:** D5 (RLS Supabase universal), D6 (provider layer unification + logging diferenciado abort/error).

## Siguientes DSCs probables

A medida que el sprint avance, los siguientes DSCs probables son:

- **DSC-LF-006:** Provider layer unification (D6) — migrar `invokeTutor` legacy de `@anthropic-ai/sdk@0.96.0` a `@ai-sdk/anthropic` v3.
- **DSC-LF-007:** RLS Supabase per-userId para `forja_budget_usage` (D5) — habilitar el contrato real del `BudgetClient` que actualmente usa mock.
- **DSC-LF-008:** Markdown rendering canónico para Chat.tsx (D3.3) — adoptar `streamdown` con cap de tokens visualizados y sanitización XSS.
