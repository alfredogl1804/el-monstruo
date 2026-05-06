#!/usr/bin/env python3
"""
Compara pares Drive vs Dropbox de documentos SOP/EPIA.

Para cada par:
1. Normaliza ambos textos (whitespace, BOM, líneas vacías colapsadas, lower-case headers).
2. Calcula SHA256 sobre texto normalizado.
3. Si SHA256 difiere: calcula similitud por SequenceMatcher + diff por bloques.
4. Genera reporte markdown con estado por par y diffs específicos.
"""
import hashlib
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path("/home/ubuntu/discovery_2026_05_05/sop_epia_diff")
DRIVE = ROOT / "drive"
DBX = ROOT / "dropbox"
REPORT = ROOT / "diff_report.md"

# Pares (nombre_humano, archivo_drive, archivo_dropbox)
PAIRS = [
    ("SOP — Documento Fundacional Maestro v1.2",
     "SOP_v1.2_DRIVE.md",
     "ENTREGABLE_2_SOP_DBX.txt"),
    ("EPIA — Documento Fundacional Maestro v1.0",
     "EPIA_fundacional_completo_v1_DRIVE.txt",
     "EPIA_FUNDACIONAL_DBX.txt"),
    ("Genealogía Evolutiva SOP/EPIA v2",
     "GENEALOGIA_SOP_EPIA_v2_DRIVE.md",
     "GENEALOGIA_SOP_EPIA_DBX.txt"),
    ("SOP+EPIA Reestructuración 6 Sabios (Abr 2026)",
     "SOP_EPIA_REESTRUCTURACION_DRIVE.md",
     "SOP_EPIA_REESTRUCTURACION_DBX.md"),
    ("EPIA Documento Fundacional (md vs md)",
     "EPIA_fundacional_completo_v1_DRIVE.txt",
     "EPIA_FUNDACIONAL_DBX.md"),
    ("ENTREGABLE 2 SOP (md vs md)",
     "ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md",
     "ENTREGABLE_2_SOP_DBX.md"),
]


def normalize(text: str) -> str:
    """Normaliza texto para comparación semántica:
    - quita BOM
    - colapsa whitespace
    - normaliza saltos de línea (\\r\\n -> \\n)
    - colapsa líneas vacías múltiples
    - strip por línea
    """
    text = text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in text.split("\n")]
    # collapse 3+ empty lines to 1
    out = []
    prev_empty = False
    for ln in lines:
        if ln == "":
            if not prev_empty:
                out.append("")
            prev_empty = True
        else:
            out.append(ln)
            prev_empty = False
    return "\n".join(out).strip()


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def first_diff_block(a: str, b: str, max_blocks: int = 5):
    """Devuelve los primeros bloques de diferencia significativos."""
    sm = SequenceMatcher(None, a.splitlines(), b.splitlines(), autojunk=False)
    blocks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a_lines = a.splitlines()[i1:i2]
        b_lines = b.splitlines()[j1:j2]
        blocks.append({
            "tag": tag,
            "drive_range": (i1, i2),
            "dbx_range": (j1, j2),
            "drive_lines": a_lines[:3],
            "dbx_lines": b_lines[:3],
        })
        if len(blocks) >= max_blocks:
            break
    return blocks, sm.ratio()


def main():
    report = ["# Diff semántico SOP/EPIA — Drive (.md) vs Dropbox (.docx/.md)",
              "",
              "**Fecha:** 2026-05-05",
              "**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)",
              "**Método:** normalización (whitespace, BOM, line endings) + SHA256 + SequenceMatcher",
              "",
              "## Resumen ejecutivo",
              ""]

    rows = ["| # | Par | Drive bytes | DBX bytes | SHA Drive | SHA DBX | Similaridad | Estado |",
            "|---|---|---|---|---|---|---|---|"]

    details = []

    for i, (label, drive_file, dbx_file) in enumerate(PAIRS, 1):
        drive_path = DRIVE / drive_file
        dbx_path = DBX / dbx_file
        if not drive_path.exists():
            details.append(f"### {i}. {label}\n\n**ERROR:** Drive file no existe: `{drive_file}`\n")
            rows.append(f"| {i} | {label} | -- | -- | -- | -- | -- | MISSING |")
            continue
        if not dbx_path.exists():
            details.append(f"### {i}. {label}\n\n**ERROR:** Dropbox file no existe: `{dbx_file}`\n")
            rows.append(f"| {i} | {label} | -- | -- | -- | -- | -- | MISSING |")
            continue

        a_raw = drive_path.read_text(encoding="utf-8", errors="replace")
        b_raw = dbx_path.read_text(encoding="utf-8", errors="replace")
        a_norm = normalize(a_raw)
        b_norm = normalize(b_raw)
        a_hash = short_hash(a_norm)
        b_hash = short_hash(b_norm)

        if a_hash == b_hash:
            estado = "IDENTICOS"
            similarity = 1.0
            blocks = []
        else:
            blocks, similarity = first_diff_block(a_norm, b_norm)
            if similarity > 0.95:
                estado = "EQUIVALENTES"
            elif similarity > 0.8:
                estado = "DIFERENCIAS MENORES"
            elif similarity > 0.5:
                estado = "DIFERENCIAS SIGNIFICATIVAS"
            else:
                estado = "DOCUMENTOS DISTINTOS"

        rows.append(f"| {i} | {label} | {len(a_raw)} | {len(b_raw)} | `{a_hash}` | `{b_hash}` | {similarity:.3f} | {estado} |")

        det = [f"### {i}. {label}", ""]
        det.append(f"- Drive: `{drive_file}` ({len(a_raw)} bytes, normalizado: {len(a_norm)})")
        det.append(f"- Dropbox: `{dbx_file}` ({len(b_raw)} bytes, normalizado: {len(b_norm)})")
        det.append(f"- SHA Drive: `{a_hash}` | SHA Dropbox: `{b_hash}`")
        det.append(f"- Similaridad: **{similarity:.3f}** ({estado})")
        det.append("")

        if blocks:
            det.append("**Primeras diferencias detectadas:**")
            det.append("")
            for j, blk in enumerate(blocks, 1):
                det.append(f"#### Diff bloque {j} ({blk['tag']})")
                det.append("```diff")
                for ln in blk["drive_lines"]:
                    det.append(f"- DRIVE: {ln[:200]}")
                for ln in blk["dbx_lines"]:
                    det.append(f"+ DBX:   {ln[:200]}")
                det.append("```")
                det.append("")
        details.append("\n".join(det))

    report.extend(rows)
    report.append("")
    report.append("## Detalle por par")
    report.append("")
    report.extend(details)
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Reporte guardado en: {REPORT}")
    print()
    print("\n".join(rows))


if __name__ == "__main__":
    main()
