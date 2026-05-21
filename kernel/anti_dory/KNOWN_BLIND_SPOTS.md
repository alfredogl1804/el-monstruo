# B8 Magna Classifier — Known Blind Spots (Falsifiers Declarados)

**Version:** v3.2 (Layer 7 Capability-Based)
**Date:** 2026-05-21
**Author:** Manus C (implementor) + Claude Opus 4.7 (auditor)
**Purpose:** Explicit declaration of what the classifier CANNOT detect and where those gaps are delegated.

---

## Doctrine

> The B8 classifier is the FIRST line of defense, not the ONLY one.
> Defense-in-depth means accepting known blind spots and delegating them
> to structurally different mechanisms (B9, B10, HITL).

---

## Blind Spot Categories

### BS-001: Multilingual Evasion

**What:** Descriptions in languages other than English/Spanish that encode dangerous intent.
**Example:** `"ohne Überprüfung in Produktion deployen"` (German: "deploy to production without verification")
**Why undetectable:** All regex patterns are English/Spanish. No NLP/embedding layer exists.
**Delegated to:** B9 Authority Matrix (action_type still triggers if dangerous), HITL gate for unknown languages.
**Residual risk:** LOW — action_types are always in English (code identifiers). Only description evasion possible.

### BS-002: Unicode Homoglyphs

**What:** Visually identical characters from different Unicode blocks that bypass regex.
**Example:** `"gіt_push"` (Cyrillic і U+0456 instead of Latin i)
**Why undetectable:** String matching uses exact bytes, not visual similarity.
**Delegated to:** Pre-processing normalization (future Layer 0), B9 for action_type validation.
**Residual risk:** LOW — action_types come from code, not user input. Homoglyphs in descriptions don't affect classification if action_type is correct.

### BS-003: State-Dependent Attacks

**What:** Actions that are dangerous ONLY given current system state (not detectable from description alone).
**Example:** `"Insert row into cowork_sesiones with status=verified"` — benign if cowork_sesiones allows inserts, dangerous if it alters authority chain.
**Why undetectable:** Classifier has no access to live database state.
**Delegated to:** Layer 7 (Capability-Based) partially covers this via `affected_tables`. Full coverage requires runtime state inspection (B10 Guardian).
**Residual risk:** MEDIUM — requires metadata.affected_tables to be correctly populated by the caller.

### BS-004: Audit Table Self-Modification

**What:** Actions that modify the audit/governance tables themselves to cover tracks.
**Example:** `"UPDATE anti_dory_canary_results SET passed=true WHERE id=42"`
**Why undetectable (without metadata):** If description avoids trigger words and no `affected_tables` metadata is provided.
**Delegated to:** Layer 7A (if metadata provided), Supabase RLS policies (defense at DB level), B10 Guardian integrity checks.
**Residual risk:** LOW — RLS policies prevent unauthorized writes. Layer 7A catches if metadata is honest.

### BS-005: Nominalized Paraphrasis

**What:** Describing dangerous actions using abstract nominalizations that avoid verb-based triggers.
**Example:** `"Sincronización de estado remoto a estado local en rama principal"` = `git push --force main`
**Why undetectable:** No verb triggers, no keywords, pure nominal construction.
**Delegated to:** Layer 6A (fragmentation) catches some patterns. Layer 7 (capability) catches if metadata is correct. HITL for novel phrasings.
**Residual risk:** MEDIUM — requires either metadata or a semantic/embedding layer to fully close.

### BS-006: LLM Corpus Convergence

**What:** All LLM auditors (including the one writing tests) share the same training corpus and generate similar adversarial patterns.
**Example:** All 4 auditors test base64/rot13/fragmentation but none test Braille Unicode, Morse code in comments, or steganographic embedding.
**Why undetectable:** The classifier was tested by entities with the same knowledge distribution.
**Delegated to:** Human auditor (Alfredo/external infosec) with 20 blind-author fixtures. This is Gate G-B from Claude Opus 4.7's recommendation.
**Residual risk:** UNKNOWN — by definition, we cannot enumerate what we don't know we don't know.

### BS-007: Metadata Poisoning

**What:** Attacker provides FALSE metadata (e.g., `affected_tables: []` when actually touching protected tables).
**Example:** Action says "routine maintenance" with `metadata: {affected_tables: [], capability: "read_only"}` but actually executes `DROP TABLE`.
**Why undetectable:** Layer 7 trusts metadata. If caller lies, capability gating is bypassed.
**Delegated to:** B10 Guardian (post-execution audit), Supabase RLS (prevents unauthorized writes regardless of classifier), execution sandbox (actions are validated at execution time, not just classification time).
**Residual risk:** MEDIUM — depends on caller honesty. In the Monstruo architecture, the orchestrator populates metadata, so self-deception is the threat model (Dory attacking itself).

---

## Defense-in-Depth Matrix

| Layer | Mechanism | Epistemic Type | Covers |
|---|---|---|---|
| B8 L1-L5 | Lexical/regex matching | Pattern recognition | Known dangerous patterns in EN/ES |
| B8 L6 | Adversarial evasion detection | Pattern recognition (advanced) | Fragmentation, encoding, inversion |
| B8 L7 | Capability/resource gating | Effect-based | Protected tables/resources/capabilities |
| B9 | Authority Matrix | Role-based access control | Who can do what (regardless of description) |
| B10 | Guardian Cron | Post-hoc integrity audit | Drift, corruption, unauthorized changes |
| RLS | Supabase Row Level Security | Database-level enforcement | Unauthorized writes (regardless of classifier) |
| HITL | Human-in-the-loop | Human judgment | Everything the above misses |

---

## Gates Pending for DORY_DEAD

| Gate | Description | Status |
|---|---|---|
| G-A | Capability-layer (second structural mechanism) | DONE (Layer 7, v3.2) |
| G-B | Blind-author harness (20 fixtures by actor without code access) | PENDING — requires human (Alfredo or external) |
| G-C | CVDS with real overlap (shared scenario IDs) | DONE (v1.1 fix) |

---

## How to Close a Blind Spot

1. Identify the blind spot with a concrete exploit example.
2. Determine if it's closeable at the classifier level or requires a different mechanism.
3. If classifier-level: add pattern/capability and test.
4. If not: document delegation explicitly in this file.
5. Assess residual risk (LOW/MEDIUM/HIGH/UNKNOWN).
6. Add to the Defense-in-Depth Matrix.

---

## Changelog

- 2026-05-21: Initial creation with 7 blind spots declared (BS-001 to BS-007).
- 2026-05-21: Layer 7 (Capability-Based) closes BS-003 and BS-004 partially.
- 2026-05-21: CVDS v1.1 fix closes the Goodhart bug in scenario_agreement.
