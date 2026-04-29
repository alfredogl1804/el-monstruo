---
name: el-monstruo
description: Context absorption system for El Monstruo ecosystem (SOP, EPIA, MAOC, architecture, governance). Use when any task involves El Monstruo, SOP, EPIA, MAOC, Absorción Soberana, Alfredo's AI ecosystem, operational decisions, or any query requiring knowledge of the Monstruo corpus. Provides hierarchical context loading from Genoma (core), Tejidos (domains), and Supabase semantic search.
---

# El Monstruo — Sistema de Contexto Soberano

Activate on ANY task related to El Monstruo, SOP, EPIA, MAOC, Absorción Soberana, or Alfredo's AI ecosystem.

## Protocol

### Step 1: Load Genoma

Read `context_packets/genoma_core.yaml` in this skill directory. Contains: system identity, domain map, core rules, keywords. Always load first (~9K chars).

### Step 2: Identify Relevant Domains

Map the current task to 1-5 domains using the Genoma's `domains` field:

| Domain | Code | Focus |
|--------|------|-------|
| Architecture | ARQ | Technical stack, Supabase, LangGraph, deployment |
| SOP | SOP | Governance, rules, validation, operating procedures |
| Investigation | INV | Research, benchmarks, tool comparisons |
| Audits | AUD | Evaluations, 6 Sabios outputs, gap analysis |
| Biblias | BIB | MCPs, tool guides, integration docs |
| MAOC | MAOC | Memory, proactivity, Notion knowledge core |
| History | HIS | Thread logs, evolution, decisions over time |
| General | GEN | Cross-cutting, foundational documents |

### Step 3: Load Relevant Tejidos

Read `context_packets/tejido_<code>.yaml` for each relevant domain. Max 5 per session (~5-7K chars each).

### Step 4: Semantic Search (if detail needed)

For specific facts, run Supabase pgvector search via the retrieve pipeline:

```bash
python3 /home/ubuntu/el_monstruo/pipelines/retrieve.py search "<query>"
```

### Step 5: Oracle Escalation (complex synthesis only)

Only for multi-document synthesis or reasoning over 15+ heterogeneous chunks:

```bash
python3 /home/ubuntu/el_monstruo/pipelines/retrieve.py oracle "<question>" --max-context 60000
```

## Critical Rules

- NEVER answer about El Monstruo without loading at least the Genoma
- NEVER invent information — if not in corpus, say so
- ALWAYS cite sources (doc_id, file, domain)
- NEVER send full corpus to external LLM — always curated packages under 80K chars

## Data Sources

- **Supabase** (xsumzuhwmivjgftsneov): 578 docs, 25,573 chunks, 23,473 embeddings
- **Notion Dashboard**: https://www.notion.so/33a14c6f8bba813d998dcbb1bf88bdd9
- **Drive**: MONSTRUO_CORE_CANON/ folder
