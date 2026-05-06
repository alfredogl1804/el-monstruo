# Diff Semántico SOP/EPIA — Reporte Final Tarea 4

**Fecha:** 2026-05-05
**Generado por:** Manus (Hilo B, Discovery Forense Fase III, Tarea 4)
**Audiencia:** Alfredo + Cowork (Hilo A, Claude Code en Mac)
**Status:** Completado — listo para canonización

---

## TL;DR (decisiones requeridas)

Tras descargar los pares Drive/Dropbox de los documentos fundacionales SOP y EPIA, normalizar (Markdown → tokens) y comparar con `SequenceMatcher` + análisis de tokens únicos por documento:

| Documento | Veredicto | Versión canónica recomendada | Razón |
|---|---|---|---|
| **SOP Fundacional v1.2** | **Drive es más completo** | `SOP_v1.2_DRIVE.md` (43KB, 5202 tokens) | 196 tokens significativos exclusivos en Drive vs solo 2 en Dropbox. Contiene secciones que el .docx perdió: §2.5 glosario operativo, §5.15 meta-principio de resolución de conflictos, §6.7 ciclo de vida de normas, §8.1.1 protocolo deliberación multi-sabio. |
| **EPIA Fundacional v1.0** | **Dropbox es más completo** | `EPIA_FUNDACIONAL_DBX.md` (30KB, 3648 tokens) | 286 tokens exclusivos en Dropbox vs solo 8 en Drive. Contiene secciones que el .txt de Drive no tiene: capas funcionales (visión, gobierno, orquestación, memoria, conectividad, ejecución, validación, expansión futura), distinción crítica modelo Manus vs sabios, núcleo vs periferia, destino final imaginado. |
| **Genealogía SOP/EPIA v2** | Drive == Dropbox (idénticos) | Cualquiera | Sincronizados (similaridad 1.000) |
| **SOP+EPIA Reestructuración 6 Sabios (Abr 2026)** | Drive == Dropbox (idénticos) | Cualquiera | Sincronizados (similaridad 1.000) |

**Acción canónica:** Para canonización post-Fase III, el **SOP base se toma de Drive** y el **EPIA base se toma de Dropbox**. Las dos fuentes están desincronizadas en sentido contrario, lo que sugiere ediciones manuales descoordinadas en distintas plataformas.

---

## Resumen ejecutivo

| # | Par | Tokens Drive | Tokens DBX | Similaridad | UNICOS Drive | UNICOS DBX | Veredicto |
|---|---|---|---|---|---|---|---|
| 1 | SOP Fundacional v1.2 | 5202 | 3996 | 0.863 | 196 | 2 | DIFS NOTABLES (Drive más completo) |
| 2 | EPIA Fundacional v1.0 | 2339 | 3648 | 0.764 | 8 | 286 | DIFS SIGNIFICATIVAS (DBX más completo) |
| 3 | Genealogía SOP/EPIA v2 | 750 | 750 | 1.000 | 0 | 0 | EQUIVALENTES |
| 4 | SOP+EPIA Reestructuración 6 Sabios | 2650 | 2650 | 1.000 | 0 | 0 | EQUIVALENTES |
| 5 | EPIA (md vs md) | 2339 | 3646 | 0.764 | 7 | 286 | Espejo de #2 |
| 6 | ENTREGABLE 2 SOP (md vs md) | 3998 | 5202 | 0.863 | 2 | 196 | Espejo de #1 |

---

## Hallazgos detallados

### 1. SOP Fundacional v1.2 — Drive contiene 5 bloques que Dropbox NO tiene

#### Bloque 1: §2.5 Glosario operativo cuantificable (DRIVE-ONLY)
> "matriz de criticidad para evitar interpretaciones divergentes... términos operativamente definidos: relevante (afecta doctrina/arquitectura/reglas, impacta múltiples dominios), crítico (puede causar daño alto/irreversible)..."

#### Bloque 2: §5.15 Meta-principio de resolución de conflictos (DRIVE-ONLY)
> "Cuando dos principios constitucionales entren en tensión, prevalecerá el siguiente orden de protección: seguridad/contención > soberanía de memoria > reversibilidad > trazabilidad > validación proporcional al riesgo > eficiencia adaptativa..."

#### Bloque 3: §6.7 Ciclo de vida explícito de las normas (DRIVE-ONLY)
> "propuesta → experimental (shadow mode) → canon vigente (validación) → consolidación formal → vigencia..."

#### Bloque 4: §8.1.1 Protocolo de deliberación multi-sabio (DRIVE-ONLY)
> "El panel multi-sabio se convoca cuando: decisión es estratégica, existe contradicción relevante, impacto es alto, una sola fuente/modelo no es suficiente. Entrada mínima requerida: problema exacto, contexto mínimo, objetivo de decisión..."

#### Bloque 5: Glosario expandido (DRIVE-ONLY)
> "consolidación formal: estado en que una norma tiene redacción estable, alcance definido, justificación suficiente, versión, fecha, aceptación dentro de su nivel normativo..."

**Implicación:** El SOP de Dropbox (`ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP.docx`) es una versión **anterior o incompleta** que omite el ciclo de vida de normas, el meta-principio de resolución de conflictos, el glosario operativo cuantificable, y el protocolo formal de deliberación multi-sabio.

### 2. EPIA Fundacional v1.0 — Dropbox contiene secciones que Drive NO tiene

#### Bloque 1: Capas funcionales del ecosistema (DBX-ONLY)
> "Las capas son niveles funcionales del ecosistema: capa de visión, capa de gobierno, capa de orquestación, capa de memoria, capa de conectividad, capa de ejecución, capa de validación, capa de expansión futura..."

#### Bloque 2: Destino final imaginado (DBX-ONLY)
> "El destino final de [EPIA] es un ecosistema capaz de operar sobre las 10 dimensiones de poder, luego extenderse hacia [el frontier] entendido como la frontera de capacidades emergentes..."

#### Bloque 3: Distinción crítica modelo de Manus vs Sabios (DBX-ONLY)
> "Modelo de Manus (Claude/Anthropic/Qwen como motor interno de Manus) ≠ Modelos los 6 Sabios (llamados externamente según necesidad). Esta distinción es obligatoria para evitar confundir el motor interno de una herramienta con el panel deliberativo del ecosistema."

#### Bloque 4: Núcleo vs Periferia (DBX-ONLY)
> "Núcleo de soberanía: integración, memoria persistente, orquestación multi-capacidad, conectividad universal, deliberación especializada. Periferia: herramientas concretas reemplazables, proveedores específicos, modelos puntuales, conectores temporales, exploraciones de frontera."

**Implicación:** El EPIA de Drive (`02_EPIA_fundacional_completo_v1.txt`) es una versión **truncada o anterior** que omite la arquitectura por capas, la distinción núcleo/periferia, y la regla canónica que separa el motor interno de Manus de los Sabios deliberativos.

---

## Recomendaciones para Canonización Post-Fase III

1. **Cowork (Tarea 5):** crear `discovery_forense/sop_epia_canon/` con:
   - `SOP_FUNDACIONAL_v1.2_CANON.md` ← copia de `SOP_v1.2_DRIVE.md`
   - `EPIA_FUNDACIONAL_v1.0_CANON.md` ← copia de `EPIA_FUNDACIONAL_DBX.md`
   - Anotar header con fecha, fuente y SHA256 normalizado.

2. **Sincronización:** una vez decidido el canon, **sobrescribir el otro lado**:
   - Subir `SOP_v1.2_DRIVE.md` a Dropbox reemplazando el .docx incompleto
   - Subir `EPIA_FUNDACIONAL_DBX.md` a Drive reemplazando el .txt truncado

3. **Ingest a Notion (Cowork Tarea 1 expandida):** los 4 documentos fundacionales (SOP canon, EPIA canon, Genealogía v2, SOP+EPIA Reestructuración 6 Sabios) deben quedar como páginas en el workspace **Omnicom Inc**, bajo la página raíz "🏗️ Plan de Construcción El Monstruo v0.1" o "📜 CONSTITUCIÓN EPIA-SOP v4.0 (Oficial)".

4. **Auditoría humana sugerida:** Alfredo debe validar manualmente que los bloques DRIVE-ONLY del SOP y los bloques DBX-ONLY del EPIA son **decisiones canónicas vigentes** y no borradores experimentales.

---

## Artefactos generados

| Archivo | Descripción |
|---|---|
| `sop_epia_diff/drive/*.md *.txt` | 7 archivos descargados de Google Drive vía `gws drive` |
| `sop_epia_diff/dropbox/*.docx *.md *.txt` | 12 archivos descargados de Dropbox + extracciones .txt |
| `sop_epia_diff/inventory.json` | Inventario de pares con IDs Drive y paths Dropbox |
| `sop_epia_diff/diff_report.md` | Reporte v1 (line-level, no útil — falsos positivos por formato) |
| `sop_epia_diff/diff_report_v2.md` | Reporte v2 (token-level básico) |
| `sop_epia_diff/diff_report_v3.md` | Reporte v3 final (token-level con normalización completa) |
| `sop_epia_diff/REPORTE_FINAL_DIFF_SOP_EPIA.md` | **Este documento** |
| `sop_epia_diff/compare_pairs_v3.py` | Script de comparación (reproducible) |
| `sop_epia_diff/download_dbx.py` | Script de descarga Dropbox (reproducible) |

---

## Reproducibilidad

```bash
# Descargar de Dropbox
python3 /home/ubuntu/discovery_2026_05_05/sop_epia_diff/download_dbx.py

# Descargar de Drive (gws CLI ya autenticado)
gws drive files get --params '{"fileId":"<id>","alt":"media"}' --output <dst>

# Comparar pares
python3 /home/ubuntu/discovery_2026_05_05/sop_epia_diff/compare_pairs_v3.py
```

---

**Fin del reporte.**
