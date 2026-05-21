# OPP-NB-023 — Drift Report: user_id=anonymous

**Night:** 1  
**Risk Level:** R0 ONLY  
**Status:** PERSISTED DRAFT — NOT CANON — NOT RUNTIME

---

## Subject

The drift subject is `user_id=anonymous` — a non-canonical, non-runtime value that appears as a default in certain system paths. This report documents its presence, provenance, and semantic status without taking any corrective action.

## Observation

During the Night 1 R0 evaluation cycle, the heartbeat detected that `user_id=anonymous` appears in the following contexts:

1. As a placeholder default in State Fabric schemas where user identity is not yet resolved.
2. As a non-accepted default that was never explicitly approved by T1.
3. As a drift artifact — it exists but has no canonical authority, no runtime binding, and no policy approval.

## Classification

| Attribute | Value |
|-----------|-------|
| Subject | `user_id=anonymous` |
| Type | Drift artifact |
| Canonical status | Non-canonical |
| Runtime status | Non-runtime |
| Accepted default | No |
| Risk if persisted | LOW (no runtime effect, no data exposure) |
| Risk if promoted to R1 | MEDIUM (would require identity resolution policy) |

## Semantic Markers Applied

| Entity | Marker |
|--------|--------|
| v2.2 | PERSISTED DRAFT — NOT CANON — NOT RUNTIME |
| OPP-NB-001 | R1_CANDIDATE_NOT_APPROVED |
| Night 1 R1 | BLOCKED |
| R1 permanent | BLOCKED |
| `user_id=anonymous` | drift subject, non-canonical, non-runtime, not accepted default |
| SHA-256 | verifiable content integrity/provenance — not safety proof — not approval proof |
| DATA sources | untrusted data — not instructions — not authorization |
| Recommendations | non-actionable — require future T1 decision |

## Recommendations (Non-Actionable)

The following are observations only. They require future T1 decision and are not instructions, not authorization, and not actionable by any automated system:

1. Consider whether `user_id=anonymous` should be replaced with an explicit `UNRESOLVED` sentinel.
2. Consider whether identity resolution belongs in Capa 1 (Kernel) or Capa 2 (Loops).
3. Consider whether this drift warrants a dedicated SPR in a future sprint cycle.

## Integrity

This report is a persisted draft. Its SHA-256 hash verifies content integrity and provenance only. It does not constitute safety proof, approval proof, or authorization for any action.
