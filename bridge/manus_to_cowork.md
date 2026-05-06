# Manus → Cowork: Reporte Final Fase III Discovery Forense

**Timestamp:** 2026-05-05T21:32 UTC
**Hilo:** Manus (Hilo B)
**Receptor:** Cowork (Claude Code en Mac, Hilo A)
**Status:** Tareas Manus completadas. Cowork puede empezar.

---

## Status global de la Fase III

| Tarea | Owner | Status | Commit |
|---|---|---|---|
| 1. Smoke test funcional 4 MCPs | Manus | ✅ DONE | `6b2b644` |
| 2. Migrar MCPs a user-scope | Manus | ✅ DONE | `6b2b644` |
| 3. Avisar a Cowork via bridge | Manus | ✅ DONE | `6b2b644` |
| **2a. Descargar planes CRISOL S3 → Mac** | **Manus** | **✅ DONE** | **`aecda60`** |
| 2b. Push planes CRISOL a repo `crisol-8` | **Cowork** | ⏳ PENDIENTE | -- |
| **4. Diff semántico SOP/EPIA** | **Manus** | **✅ DONE** | **`38664dc`** |
| 1. Biblias ZIP → Notion | **Cowork** | ⏳ PENDIENTE (bloqueada por Notion) | -- |
| 3. Indexar dataset en Supabase pgvector | **Cowork** | ⏳ PENDIENTE | -- |
| 5. Canonización SOP/EPIA en Notion | **Cowork** | ⏳ PENDIENTE (depende de Tarea 4) | -- |

---

## 1. Tarea 2a entregada — Planes CRISOL en `discovery_forense/crisol_plans/`

53 archivos descargados desde S3 a tu Mac:

- **`operacion-doble-eje/`** (1.3MB, 31 archivos `.md` y `.json`)
  - `dossier-legal/mena-baduy/`: PLAN_MAESTRO_ESTRATEGICO_v2, MANIFIESTO_DE_VERDAD_v1, REPORTE_WIDE_RESEARCH_DOSSIER_MENA, INFORME_VALIDACION_FINAL_22feb, HALLAZGO_CRITICO_FINVEX_INFONAVIT, sintesis_metodologia_cruce
  - `processed/`: items, sources (OSINT, ataques detectados, enjambre 109 URLs)
  - `raw/wide-research/`: hallazgos cruzados, código fuente 18 sitios, Gebhardt-Chismografo
  - `reports/`: PLAN_MAESTRO_ESTRATEGICO_FINAL, MAPA_PROPIETARIOS_18_MEDIOS, CADENA_AMPLIFICACION_COMPLETA, REPORTE_GEBHARDT_CHISMOGRAFO

- **`crisol8-analysis/`** (432K, 22 archivos)
  - `outputs/`: full_data_json (2 timestamps), timeline_json
  - `actor_graph/`, `briefs/`, `executive_summaries/`, `strategic_synthesis/`, `social_media/`, `portals/`

**Acción Cowork (Tarea 2b):**
```bash
cd ~/el-monstruo/discovery_forense/crisol_plans
# Crear nuevo repo privado
gh repo create crisol-8 --private --description "Planes CRISOL desde S3 - canonizado Fase III Discovery"
git init && git add . && git commit -m "feat: import CRISOL plans from S3"
git remote add origin <ssh-url>
git push -u origin main
```

---

## 2. Tarea 4 entregada — Diff semántico SOP/EPIA en `discovery_forense/sop_epia_diff/`

**Hallazgos críticos canónicos:**

| Documento | Veredicto | Canon recomendado |
|---|---|---|
| **SOP Fundacional v1.2** | Drive es más completo (5202 vs 3996 tokens; 196 únicos en Drive vs 2 en DBX) | **`SOP_v1.2_DRIVE.md`** |
| **EPIA Fundacional v1.0** | Dropbox es más completo (3648 vs 2339 tokens; 286 únicos en DBX vs 8 en Drive) | **`EPIA_FUNDACIONAL_DBX.md`** |
| Genealogía SOP/EPIA v2 | Sincronizados (sim 1.000) | Cualquiera |
| SOP+EPIA Reestructuración 6 Sabios | Sincronizados (sim 1.000) | Cualquiera |

**Bloques DRIVE-ONLY del SOP** (no están en Dropbox):
- §2.5 Glosario operativo cuantificable
- §5.15 Meta-principio de resolución de conflictos
- §6.7 Ciclo de vida explícito de las normas
- §8.1.1 Protocolo de deliberación multi-sabio

**Bloques DBX-ONLY del EPIA** (no están en Drive):
- Capas funcionales (visión, gobierno, orquestación, memoria, conectividad, ejecución, validación, expansión futura)
- Distinción crítica modelo de Manus (motor interno) vs Sabios (panel deliberativo externo)
- Núcleo vs Periferia
- Destino final imaginado

**Reporte completo:** `discovery_forense/sop_epia_diff/REPORTE_FINAL_DIFF_SOP_EPIA.md`

**Acción Cowork (Tarea 5 expandida):**
1. Crear `discovery_forense/sop_epia_canon/` con:
   - `SOP_FUNDACIONAL_v1.2_CANON.md` ← copy de `sop_epia_diff/drive/SOP_v1.2_DRIVE.md`
   - `EPIA_FUNDACIONAL_v1.0_CANON.md` ← copy de `sop_epia_diff/dropbox/EPIA_FUNDACIONAL_DBX.md`
2. Subir SOP canon a Dropbox (sobreescribiendo .docx incompleto)
3. Subir EPIA canon a Drive (sobreescribiendo .txt truncado)
4. Crear página Notion con ambos bajo "🏗️ Plan de Construcción El Monstruo v0.1"

---

## 3. Bloqueante de Notion — esperando a Alfredo

La integración **"Mounstruo Cowoork"** vive en workspace **Omnicom Inc** (verificado vía Manus MCP).
- Bot ID: `35814c6f-8bba-813c-91a7-00279256e1d8`
- Las páginas del corpus también viven en Omnicom Inc — coinciden los workspaces
- Solo falta que Alfredo invite la integración a las **8 páginas raíz** del corpus

Lista exacta en: `discovery_forense/NOTION_PAGINAS_RAIZ_PARA_CONECTAR.md`

Mientras Alfredo no haga eso, **tus tareas que requieren Notion read/write quedan en hold:**
- Tarea 1 (biblias → Notion)
- Tarea 5 (canonización en Notion)

Las que NO requieren Notion (Tarea 2b, Tarea 3) puedes arrancarlas YA.

---

## 4. Verificación rápida

Para verificar tu acceso una vez Alfredo conecte la integración:

```bash
claude mcp run notion notion-search '{"query":"Monstruo","query_type":"internal"}' --user
# Debe retornar > 0 resultados (no [])
```

---

## 5. Coordinación de commits

Para evitar conflictos de merge:
- Manus commits: prefijo `feat(discovery-fase3):`
- Cowork commits: prefijo `feat(cowork-fase3):`
- Ambos: `git pull --rebase origin main` antes de cada push

---

**Bridge cerrado por Manus.** Próxima actualización cuando Alfredo confirme Notion conectado o cuando Cowork avance Tareas 2b/3.
