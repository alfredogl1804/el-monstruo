# [ARCHIVED] DSC-G-013 v1 — pre-Sabios DRAFT

**Status:** 🗃️ ARCHIVED 2026-05-18 (preservación forensics anti-Memento)
**Razón archivado:** GPT-5.5 Pro adversarial detectó sesgo confirmatorio en hipótesis "3 capas estructurales" (F#15 es síntoma operativo, no evidencia estructural equivalente a H12/H13). Spec degradado a v0.1 con hipótesis reformulada como "familia de drift pre-acción".

**Veredicto Sabios verbatim:**
- Opus 4.7 → 🟡 CON CAVEAT — 3 ajustes técnicos (L_C3, §4.1 DROP/ALTER, §10 métricas)
- Perplexity Sonar T2-B → 🟡 CON CAVEAT — Atlas/Flyway/Liquibase como referencia industria
- GPT-5.5 Pro → 🟡 DEGRADADO — re-hipótesis + recorte editorial + 2 limitaciones nuevas + Nivel B → experimento T+14d

**Reemplazado por:** [`DSC-G-013_db_repo_coherence_gate.md`](../DSC-G-013_db_repo_coherence_gate.md) (v0.1 firmable)
**Nivel B movido a:** [`EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md`](../../../EXPERIMENTOS_T14D/DSC-G-013_nivel_B_experimento.md)

**Veredictos Sabios verbatim conservados:**
- [Opus 4.7](../../../../bridge/veredictos_dsc_g_013/opus_4_7_veredicto_2026_05_18.md)
- [Perplexity Sonar](../../../../bridge/veredictos_dsc_g_013/perplexity_sonar_veredicto_2026_05_18.md)
- [GPT-5.5 Pro](../../../../bridge/veredictos_dsc_g_013/gpt55_pro_veredicto_2026_05_18.md)

---

## Contenido v1 verbatim (preservado para forensics)

---

dsc_id: DSC-G-013
titulo: DB↔Repo Coherence Gate
estado: 🟡 DRAFT — espera convergencia 3 Sabios Tier 1 (Perplexity + GPT-5.5 Pro + Claude Opus 4.7)
autor_spec: Cowork T2-A
fecha_draft: 2026-05-18
ambito: _GLOBAL
hermanos: DSC-S-012 (anti-deriva migration numbering), DSC-S-016 (anti-fabricación), DSC-G-008 v4 (audit doctrine)
evidencia_magna: 3 manifestaciones del mismo patrón en 1 sesión Cowork (HOY 2026-05-17/18)
proximos_pasos: convergencia 3 Sabios + firma T1 + integración pre-flight audit_middleware

---

# DSC-G-013 — DB↔Repo Coherence Gate (v1 pre-Sabios)

> **Hipótesis doctrinal v1 (degradada en v0.1):** El estado canónico de El Monstruo se distribuye en al menos **3 fuentes paralelas** — código en repo, schema_migrations en Supabase, modelo mental del agente actuante. Sin un gate binario que verifique coherencia entre las 3 antes de cada acción magna, el sistema acumula drift silente que se manifiesta como F-pattern reincidentes.

**Contenido completo v1 disponible en Git history:**
```
git show e12046af15fecfef90553ffa7d46627f6a97748d
```

O directamente desde commit `cb5a4f43` que introdujo el v1 original (12.4KB, 10 secciones).

**Razón no-duplicación bytes:** el contenido vive en Git inmortal. Este archivo es puntero + contexto del archivado, no duplicado de 12KB.

---

**Archivado por:** Cowork T2-A bajo autorización T1 "procede x" verbatim 2026-05-18.
