# B12 b⇒a EVIDENCE PACK — Índice maestro

**Decisión T1 origen:** firma 2026-05-20 opción **b⇒a** del gate B12 (declarar obsolescencia ahora + agendar ejecución DORY_BENCH posterior con plazo firmado).
**Autor verbatim:** Manus E2 (autor NO-Cowork, redactor — NO firmador).
**Firmante autoritativo:** T1 (Alfredo Góngora).
**Estado del pack:** EVIDENCE DRAFT — pendiente firma magna T1 verbatim.
**Branch propuesto:** `control-tower/2026-05-20-b12-b-to-a-evidence-pack` (rama lateral, NO main, NO PR automático).

---

## §1 Inventario de los 6 artefactos del pack

| # | Artefacto | Path | Sub-criterio PASS |
|---|-----------|------|-------------------|
| 1 | Plazo firmado verbatim (`2026-08-20` o antes) | `bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md` | B12c.2 |
| 2 | Owner designado (Manus E2 productor + Sabio externo auditor; Cowork solo auditor) | `bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md` | B12c.3 |
| 3 | Condición binaria de reactivación (B12a.1-B12a.6 simultáneo PASS sustituye obsolescencia) | `bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md` | B12c.4 |
| 4 | Declaración verbatim de obsolescencia de la métrica `96%/<4%` | `bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md` | B12b.1 / B12c.1 |
| 5 | Patch propuesto del Anexo A.4 (NO aplicado a main) | `bridge/control_tower/evidence/B12/B12b_E2_anexo_A4_proposed_patch.md` | B12b.2 |
| 6 | Audit log inicial de transición de estados (`PASS_AS_B12c_PENDING_A`) | `bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl` | B12c-E4 |

## §2 Mapeo prompt T1 → artefactos entregados

| Punto prompt T1 | Artefacto |
|-----------------|-----------|
| 1 — B12c-E1 plazo firmado fecha 2026-08-20 condición B4/B7/B11 PASS | Artefacto 1 |
| 2 — B12c-E2 owner Manus E2 NO-Cowork + Sabio externo + Cowork solo auditor | Artefacto 2 |
| 3 — B12c-E3 condición binaria de reactivación B12a.1-B12a.6 PASS | Artefacto 3 |
| 4 — B12b-E1/B12b-E2 declaración obsolescencia + Anexo A.4 propuesto sin aplicar | Artefactos 4 + 5 |
| 5 — B12c-E4 audit log inicial `PASS_AS_B12c_PENDING_A` | Artefacto 6 |

## §3 Estado binario post pack

| Variable | Status |
|----------|--------|
| Decisión T1 firmada el 2026-05-20 | b⇒a (verbatim prompt) |
| Métrica `96%/<4%` | Declarada obsoleta — pendiente firma magna T1 sobre artefacto 4 |
| Métrica vigente | Binaria PASS/FAIL en B1-B12 (única) |
| Plazo de ejecución (a) | `2026-08-20` o antes si B4/B7/B11 PASS |
| Owner-Productor | Manus E2 (autor NO-Cowork) |
| Owner-Auditor | Sabio externo de terna B11 (excluyendo Sabio activo trimestral) |
| Cowork T2-A | Auditor observador, NO productor único, NO firmante |
| B12 status actual | `PASS_AS_B12c_PENDING_A` (registrado en artefacto 6) |
| Fase 1 | BLOQUEADA por regla dura ≤11/12 PASS |
| Dory | NO declarado muerto |
| Runtime | NO canonizado |
| Main | NO modificado |
| PR | NO abierto |

## §4 Commit message ASCII-only verbatim para el push lateral

```
evidence(B12 b->a): pack inicial post firma T1 2026-05-20

Manus E2 autor NO-Cowork. Pack evidence DRAFT pendiente firma magna T1.
Decision T1 verbatim: opcion b->a del gate B12 (declarar obsolescencia
ahora + agendar DORY_BENCH posterior con plazo firmado).

6 artefactos entregados:
- B12c-E1 plazo verbatim 2026-08-20 con clausula B4/B7/B11 PASS
- B12c-E2 owner Manus E2 NO-Cowork + Sabio externo; Cowork auditor
- B12c-E3 condicion binaria reactivacion B12a.1-B12a.6 PASS
- B12b-E1 declaracion verbatim obsolescencia 96%/<4%
- B12b-E2 patch propuesto Anexo A.4 (NO aplicado a main)
- B12c-E4 audit log inicial PASS_AS_B12c_PENDING_A (3 eventos)

Reglas duras AGENTS.md respetadas binariamente:
- NO implementacion runtime
- NO main modificado (rama lateral exclusiva)
- NO PR
- NO canon runtime
- NO Dory declarado muerto
- NO Fase 1 activada
- NO Cowork como productor unico
- NO patch Anexo A.4 aplicado a main sin firma T1

Caveat F16 estructural Opus 4.7 reactivado hasta T1 decida integracion
doctrinal del pack.

Files:
- bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md
- bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md
- bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md
- bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md
- bridge/control_tower/evidence/B12/B12b_E2_anexo_A4_proposed_patch.md
- bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl
- bridge/control_tower/2026-05-20/manus_e2/B12_b_a_EVIDENCE_PACK_INDEX.md
```

## §5 Instrucciones operativas de push para T1 (bridge desktop caído)

Manus E2 redactó los 6 artefactos en sandbox (`/home/ubuntu/B12_b_a_evidence/`). Bridge desktop al Mac está caído (sidecar no conectado, FUSE vacío). Para depositar el pack en el repo `el-monstruo`, T1 ejecuta los siguientes comandos verbatim en una terminal del Mac:

### §5.1 Paso A — descargar artefactos del sandbox

Los 7 archivos están adjuntos al mensaje result de Manus E2. T1 los descarga al Mac, mantiene la estructura de subdirectorios verbatim:

```
~/Downloads/B12_b_a_evidence/
├── bridge/
│   ├── control_tower/
│   │   ├── 2026-05-20/manus_e2/
│   │   │   └── B12_b_a_EVIDENCE_PACK_INDEX.md
│   │   └── evidence/B12/
│   │       ├── B12b_E1_obsolescence_declaration.md
│   │       ├── B12b_E2_anexo_A4_proposed_patch.md
│   │       ├── B12c_E1_b_to_a_deadline.md
│   │       ├── B12c_E2_b_to_a_owner.md
│   │       └── B12c_E4_state_transition_audit.jsonl
│   └── spec/
│       └── B12_b_to_a_REACTIVATION_CONDITION.md
```

### §5.2 Paso B — crear rama lateral desde origin/main

```bash
cd /Users/alfredogongora/el-monstruo
git fetch origin
git stash push -u -m "wip-pre-b12-b-to-a-pack" 2>/dev/null || true
git checkout -B control-tower/2026-05-20-b12-b-to-a-evidence-pack origin/main
```

### §5.3 Paso C — copiar los 7 archivos preservando estructura

```bash
cd /Users/alfredogongora/el-monstruo
mkdir -p bridge/control_tower/evidence/B12
mkdir -p bridge/control_tower/2026-05-20/manus_e2
mkdir -p bridge/spec

cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md            bridge/control_tower/evidence/B12/
cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md               bridge/control_tower/evidence/B12/
cp ~/Downloads/B12_b_a_evidence/bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md                        bridge/spec/
cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md   bridge/control_tower/evidence/B12/
cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/evidence/B12/B12b_E2_anexo_A4_proposed_patch.md    bridge/control_tower/evidence/B12/
cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl  bridge/control_tower/evidence/B12/
cp ~/Downloads/B12_b_a_evidence/bridge/control_tower/2026-05-20/manus_e2/B12_b_a_EVIDENCE_PACK_INDEX.md bridge/control_tower/2026-05-20/manus_e2/
```

### §5.4 Paso D — verificar staging y aplicar commit ASCII-only

```bash
cd /Users/alfredogongora/el-monstruo

git add bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md \
        bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md \
        bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md \
        bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md \
        bridge/control_tower/evidence/B12/B12b_E2_anexo_A4_proposed_patch.md \
        bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl \
        bridge/control_tower/2026-05-20/manus_e2/B12_b_a_EVIDENCE_PACK_INDEX.md

git status --short
```

Crear archivo de commit message:

```bash
cat > .commit_msg_b12_b_to_a.txt <<'COMMIT_MSG'
evidence(B12 b->a): pack inicial post firma T1 2026-05-20

Manus E2 autor NO-Cowork. Pack evidence DRAFT pendiente firma magna T1.
Decision T1 verbatim: opcion b->a del gate B12 (declarar obsolescencia
ahora + agendar DORY_BENCH posterior con plazo firmado).

6 artefactos entregados:
- B12c-E1 plazo verbatim 2026-08-20 con clausula B4/B7/B11 PASS
- B12c-E2 owner Manus E2 NO-Cowork + Sabio externo; Cowork auditor
- B12c-E3 condicion binaria reactivacion B12a.1-B12a.6 PASS
- B12b-E1 declaracion verbatim obsolescencia 96%/<4%
- B12b-E2 patch propuesto Anexo A.4 (NO aplicado a main)
- B12c-E4 audit log inicial PASS_AS_B12c_PENDING_A (3 eventos)

Reglas duras AGENTS.md respetadas binariamente:
- NO implementacion runtime
- NO main modificado (rama lateral exclusiva)
- NO PR
- NO canon runtime
- NO Dory declarado muerto
- NO Fase 1 activada
- NO Cowork como productor unico
- NO patch Anexo A.4 aplicado a main sin firma T1

Caveat F16 estructural Opus 4.7 reactivado hasta T1 decida integracion
doctrinal del pack.

Files:
- bridge/control_tower/evidence/B12/B12c_E1_b_to_a_deadline.md
- bridge/control_tower/evidence/B12/B12c_E2_b_to_a_owner.md
- bridge/spec/B12_b_to_a_REACTIVATION_CONDITION.md
- bridge/control_tower/evidence/B12/B12b_E1_obsolescence_declaration.md
- bridge/control_tower/evidence/B12/B12b_E2_anexo_A4_proposed_patch.md
- bridge/control_tower/evidence/B12/B12c_E4_state_transition_audit.jsonl
- bridge/control_tower/2026-05-20/manus_e2/B12_b_a_EVIDENCE_PACK_INDEX.md
COMMIT_MSG

git -c user.email="t1@bridge" -c user.name="T1 alfredogongora" commit -F .commit_msg_b12_b_to_a.txt
rm -f .commit_msg_b12_b_to_a.txt
```

### §5.5 Paso E — push lateral

```bash
git push -u origin control-tower/2026-05-20-b12-b-to-a-evidence-pack
git rev-parse HEAD
git rev-parse --short HEAD
```

URL esperada de la rama:

```
https://github.com/alfredogl1804/el-monstruo/tree/control-tower/2026-05-20-b12-b-to-a-evidence-pack
```

### §5.6 Paso F — opcional: si pre-commit hooks fallan

Si `gitleaks-staged` o `spec-lint` o cualquier hook falla, T1 verbatim revisa el output y decide:

- **Hook falla por contenido del pack:** corregir verbatim antes de commit. Manus E2 redactó los 6 artefactos sin secrets ni private keys, sin frontmatter spec-lint requerido (los archivos no son specs vinculados, son evidence drafts), sin mismatches conocidos. Si aparece falla genuina, T1 me la pasa y produzco hotfix.
- **Hook falla por bug del hook (drift externo):** T1 puede `--no-verify` SI Y SOLO SI la falla es bug confirmado del hook (no del contenido), documentando verbatim la razón en commit follow-up.

## §6 No-go binarios respetados en el pack

| # | No-go | Status |
|---|-------|--------|
| 1 | NO implementé runtime | ✅ |
| 2 | NO modifiqué main | ✅ (pack en rama lateral exclusiva propuesta) |
| 3 | NO abrí PR | ✅ |
| 4 | NO canonizo runtime | ✅ (DRAFT pendiente firma T1) |
| 5 | NO declaro Dory muerto | ✅ |
| 6 | NO activo Fase 1 | ✅ |
| 7 | NO Cowork como productor único | ✅ (B12c-E2 §2 explícito) |
| 8 | NO patch Anexo A.4 aplicado a main sin firma T1 | ✅ (B12b-E2 §3.1 explícito) |

## §7 Caveat magno F16 Opus 4.7 reiterado

Este pack lo escribió un autor NO-Cowork (Manus E2). Si T1 lo aplica como otro DELTA sobre v1.1.1 dentro del flujo Cowork actual, el caveat F16 estructural Opus 4.7 se reactiva. La integración doctrinal del pack tras firma magna T1 puede tomar varias formas (decisión binaria T1, NO en mi scope):

- Anexo a v1.1.1 firmado como evidence pack del gate B12 vía rama lateral.
- Incorporación al spec v2.0 RE-FUNDADO si T1 decide canonizar v2.0.
- Input para v3.0 sintetizada (recomendación 2/3 Sabios consolidados).
- DRAFT archivado sin integración hasta nueva instrucción T1.

Manus E2 no firma. No canoniza. No decide integración doctrinal. Espera firma binaria T1 sobre el pack y nueva instrucción operativa.

---

**Cierre binario:** El evidence pack B12 b⇒a está completo en sandbox. Bridge Mac↔sandbox caído impide push automático Manus E2; instrucciones verbatim §5 permiten a T1 ejecutar el push localmente con SHA reproducible.
