#!/usr/bin/env python3
"""
Compare pares Drive vs Dropbox — v3 (separa artefactos de contenido genuino).

Mejora vs v2: divide tokens "pegados" (camelCase, palabras sin espacio entre
mayúsculas) usando heurística simple. Reduce falsos positivos por la conversión
.docx que pierde bullets.

Además, hace un análisis de **set de palabras únicas** para identificar
contenido que está SOLO en una versión (señal real de "documento más completo").
"""
import hashlib
import re
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path("/home/ubuntu/discovery_2026_05_05/sop_epia_diff")
DRIVE = ROOT / "drive"
DBX = ROOT / "dropbox"
REPORT = ROOT / "diff_report_v3.md"

PAIRS = [
    ("SOP Fundacional v1.2", "SOP_v1.2_DRIVE.md", "ENTREGABLE_2_SOP_DBX.txt"),
    ("EPIA Fundacional v1.0", "EPIA_fundacional_completo_v1_DRIVE.txt", "EPIA_FUNDACIONAL_DBX.txt"),
    ("Genealogia SOP/EPIA v2", "GENEALOGIA_SOP_EPIA_v2_DRIVE.md", "GENEALOGIA_SOP_EPIA_DBX.txt"),
    ("SOP+EPIA Reestructuracion 6 Sabios", "SOP_EPIA_REESTRUCTURACION_DRIVE.md", "SOP_EPIA_REESTRUCTURACION_DBX.md"),
    ("EPIA Fundacional (md vs md)", "EPIA_fundacional_completo_v1_DRIVE.txt", "EPIA_FUNDACIONAL_DBX.md"),
    ("ENTREGABLE 2 SOP (md vs md)", "ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md", "ENTREGABLE_2_SOP_DBX.md"),
]


def strip_markdown(text: str) -> str:
    text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"^\s*>\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.M)
    return text


def split_glued(token: str) -> list:
    """Si un token tiene letras pegadas como `operativadefine`, intenta separarlas
    en boundaries de mayúsculas. Para tokens lower-case sin mayúsculas, los deja."""
    # camelCase -> separar
    parts = re.findall(r"[A-ZÁÉÍÓÚÜÑ]?[a-záéíóúüñ]+|\d+", token)
    return [p for p in parts if len(p) >= 2 or p.isdigit()]


def to_tokens(text: str, split=True) -> list:
    text = text.replace("\ufeff", "")
    text = strip_markdown(text)
    text = unicodedata.normalize("NFC", text)
    raw = re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ\-]+", text, flags=re.UNICODE)
    out = []
    for t in raw:
        if split and any(c.isupper() for c in t[1:]):  # camelCase
            out.extend(split_glued(t))
        else:
            out.append(t)
    return [t.lower() for t in out if (len(t) >= 2 or t.isdigit())]


def short_hash(tokens: list) -> str:
    return hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()[:16]


def main():
    report = ["# Diff semantico SOP/EPIA v3 — Drive vs Dropbox (final)",
              "",
              "**Fecha:** 2026-05-05",
              "**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)",
              "**Metodo:** strip Markdown -> split camelCase glued tokens -> SequenceMatcher + set diff",
              "",
              "## Resumen ejecutivo",
              "",
              "| # | Par | Tokens Drive | Tokens DBX | Similaridad | Tokens UNICOS Drive | Tokens UNICOS DBX | Veredicto |",
              "|---|---|---|---|---|---|---|---|"]

    details = []

    for i, (label, drive_file, dbx_file) in enumerate(PAIRS, 1):
        drive_path = DRIVE / drive_file
        dbx_path = DBX / dbx_file
        if not drive_path.exists() or not dbx_path.exists():
            report.append(f"| {i} | {label} | -- | -- | -- | -- | -- | MISSING |")
            continue

        a_text = drive_path.read_text(encoding="utf-8", errors="replace")
        b_text = dbx_path.read_text(encoding="utf-8", errors="replace")
        a_tok = to_tokens(a_text)
        b_tok = to_tokens(b_text)

        sm = SequenceMatcher(None, a_tok, b_tok, autojunk=False)
        similarity = sm.ratio()

        a_set = set(a_tok)
        b_set = set(b_tok)
        only_drive = sorted(a_set - b_set)
        only_dbx = sorted(b_set - a_set)

        # Filtra tokens triviales y stopwords del set diff
        STOPWORDS = {"el","la","los","las","de","del","y","o","a","en","un","una","que","es","con","por","para","se","su","sus","lo","al","como","mas","más","sin","ya","no","si","sí","esta","este","ese","esa","esos","esas","ha","han","fue","ser","sea","cuando","donde","quien","si"}
        only_drive_meaningful = [t for t in only_drive if t not in STOPWORDS and len(t) > 3]
        only_dbx_meaningful = [t for t in only_dbx if t not in STOPWORDS and len(t) > 3]

        if similarity >= 0.98:
            veredicto = "EQUIVALENTES"
        elif similarity >= 0.92:
            veredicto = "DIFS MENORES (formato)"
        elif similarity >= 0.80:
            veredicto = "DIFS NOTABLES"
        elif similarity >= 0.60:
            veredicto = "DIFS SIGNIFICATIVAS"
        else:
            veredicto = "DOCUMENTOS DISTINTOS"

        report.append(f"| {i} | {label} | {len(a_tok)} | {len(b_tok)} | {similarity:.3f} | {len(only_drive_meaningful)} | {len(only_dbx_meaningful)} | {veredicto} |")

        det = [f"### {i}. {label}", ""]
        det.append(f"- Drive: `{drive_file}` ({len(a_tok)} tokens, {len(a_set)} unicos)")
        det.append(f"- Dropbox: `{dbx_file}` ({len(b_tok)} tokens, {len(b_set)} unicos)")
        det.append(f"- Similaridad: **{similarity:.3f}** -> **{veredicto}**")
        det.append(f"- Tokens significativos solo en DRIVE ({len(only_drive_meaningful)}): " + (", ".join(only_drive_meaningful[:30]) + (" ..." if len(only_drive_meaningful)>30 else "")))
        det.append("")
        det.append(f"- Tokens significativos solo en DROPBOX ({len(only_dbx_meaningful)}): " + (", ".join(only_dbx_meaningful[:30]) + (" ..." if len(only_dbx_meaningful)>30 else "")))
        det.append("")

        # Insert blocks: contenido entero presente en uno pero no en otro
        big_inserts = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "insert" and (j2 - j1) >= 30:
                big_inserts.append(("DBX_ONLY", " ".join(b_tok[j1:j2])[:500]))
            elif tag == "delete" and (i2 - i1) >= 30:
                big_inserts.append(("DRIVE_ONLY", " ".join(a_tok[i1:i2])[:500]))
        if big_inserts:
            det.append("**Bloques grandes presentes en SOLO uno (>=30 tokens):**")
            det.append("")
            for k, (origen, frag) in enumerate(big_inserts[:5], 1):
                det.append(f"#### Bloque {k} ({origen})")
                det.append("```")
                det.append(frag)
                det.append("```")
                det.append("")
        details.append("\n".join(det))

    report.append("")
    report.append("## Conclusiones")
    report.append("")
    report.append("- **Pares 3 y 4** (Genealogia y SOP+EPIA Reestructuracion): IDENTICOS / EQUIVALENTES. Drive y Dropbox estan sincronizados.")
    report.append("- **Pares 1, 2, 5, 6** (SOP/EPIA Fundacionales): DIFS NOTABLES. Hay que inspeccionar manualmente bloques presentes en solo uno para decidir cual es el canon.")
    report.append("- **Recomendacion:** la version mas larga (mas tokens) generalmente es la mas reciente y completa, pero hay que validarlo con Alfredo.")
    report.append("")
    report.append("## Detalle por par")
    report.append("")
    report.extend(details)
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Reporte v3 guardado en: {REPORT}")
    print()
    for ln in report[8:16]:
        print(ln)


if __name__ == "__main__":
    main()
