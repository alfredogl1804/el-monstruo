# Epoch 006 Declaration — Memory Palace R0+

**Sprint:** SPR-EPOCH006-MEMORY-PALACE-R0PLUS-001
**Branch:** monstruo-reality-atlas-001
**Epoch:** 006
**Codename:** MEMORY_PALACE_PRODUCTION
**Timestamp:** 2026-05-21T04:50:00Z

---

## What Epoch 006 Adds

1. **Memory Palace v0.1** — Local JSON-based persistent memory for embryos
2. **Oracle v0.3** — Memory-guided task selection + memory write-back
3. **Auditor v0.3** — Memory-guided audit + memory write-back
4. **Cross-embryo memory** — Both embryos read/write to shared Memory Palace
5. **Second R0+ Artifact** — Autonomously produced from memory-guided cycle

## Key Upgrade: Memory-Guided Decision Making

Before Epoch 006, embryos had no persistent memory between cycles. Each cycle started fresh.

After Epoch 006:
- Embryos read lessons from previous cycles
- Task selection is influenced by memory (repetition penalty, boost for unexplored)
- Each cycle writes back what it learned
- Auditor can reference Oracle's memory entries for context

## Constraints (unchanged)

- Kill-switch supreme
- 0 Supabase
- 0 DB writes
- 0 secrets exposed
- 0 R1 operations
- Budget cap: $0.05/day
- Memory Palace is LOCAL JSON only (no external persistence)

## Predecessor

Epoch 005 (Grounded Oracle Production R0+)
