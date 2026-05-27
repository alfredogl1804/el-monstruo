# Cabina Dual — Clase Mundial Binario — 2026-05-27

Goal: usuario abre iPhone, dice "audita Sprint 91 y abre PR de cierre", suelta el teléfono, vuelve a los 10 min con PR real abierto en GitHub.

## Criterio binario de aceptación final

Test e2e en iPhone físico:
- Prompt: "Audita el último sprint y abre PR de cierre"
- Resultado esperado: tarjeta final con URL de PR REAL en `github.com/alfredogl1804/...`, hash de commit verificable con `git show <sha>`, links tap-ables a artifacts.
- Sin manual intervention después del prompt inicial.

## Sprints

- [x] **S1** — Fix catálogo de modelos del Embrión-loop (kimi-k2-6 → activo)
  - Resolución: env var `EMBRION_CATASTRO_ENABLED=false` en Railway. Embrión vuelve al fallback `gpt-5.5`.
  - Verificado: `errors_count: 0`, ciclos 1-3 con multi-agente real (sonar-pro + claude-opus-4-7 + gemini-3.1-pro-preview + gpt-5).
  - Thoughts auto-disciplinados por el `SelfVerifier` (importancia_too_low) — comportamiento intencional (Doctrina del Silencio Inteligente). Para autonomía visible necesita trigger `mensaje_alfredo` desde el Hilo (bypass del verifier).
- [x] **S2** — Activar MCP real con WRITE actions sobre fastmcp
  - Resolución: extender `kernel/fastmcp_server.py:github_ops` con 4 write actions: `create_branch`, `commit_file`, `create_pr`, `create_issue`. Verificado GITHUB_TOKEN scope `repo, workflow`.
- [ ] **S3** — Forja v4 enforce L0-L3 PR a tablero-campana
  - Criterio: una acción L1 produce `evidence_receipt.merkle_root` validable
- [ ] **S4** — Planning recursivo multi-step en kernel
  - Criterio: prompt "audita+PR" produce ≥4 steps con ≥2 tool_calls reales
- [ ] **S5** — Artifact panel Flutter (links accionables)
  - Criterio: al finalizar hilo, bloque con PR URL / commit hash / row id tap-ables
- [ ] **S6** — Continuidad multi-turn (persist thread_id)
  - Criterio: cerrar app + reabrir + "continuar último hilo" reanuda contexto
- [ ] **E2E** — Test final iPhone físico + commit + push + entrega

## Política de honestidad

- Si un sprint se atora >2 ciclos sin resolver → aviso al usuario sin marketing.
- Cada sprint termina con verificación contra endpoint real, no contra hipótesis.
- Cualquier alucinación detectada → corrijo inmediatamente, no la arrastro.
