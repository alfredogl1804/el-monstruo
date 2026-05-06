#!/usr/bin/env python3
"""
Compara pares Drive vs Dropbox de documentos SOP/EPIA — versión 2.

Diferencia clave vs v1: hace **comparación a nivel de tokens**, no de líneas.
Esto neutraliza los artefactos de formato (Markdown `#`, `**bold**`, vs texto plano
del .docx que pierde estructura). Si el contenido textual es equivalente, similarity
debe ser >0.95 incluso si Markdown vs plain difieren.

Estrategia:
1. Strip Markdown markers: `#`, `**`, `*`, `_`, `>`, ``` etc.
2. Tokenizar a palabras (alfa-num + acentos), lower-case.
3. Comparar listas de tokens con SequenceMatcher.
4. Para diff visualmente útil, también guardar diffs por párrafo equivalente.
"""
import hashlib
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path("/home/ubuntu/discovery_2026_05_05/sop_epia_diff")
DRIVE = ROOT / "drive"
DBX = ROOT / "dropbox"
REPORT = ROOT / "diff_report_v2.md"

PAIRS = [
    ("SOP Fundacional v1.2",
     "SOP_v1.2_DRIVE.md",
     "ENTREGABLE_2_SOP_DBX.txt"),
    ("EPIA Fundacional v1.0",
     "EPIA_fundacional_completo_v1_DRIVE.txt",
     "EPIA_FUNDACIONAL_DBX.txt"),
    ("Genealogia SOP/EPIA v2",
     "GENEALOGIA_SOP_EPIA_v2_DRIVE.md",
     "GENEALOGIA_SOP_EPIA_DBX.txt"),
    ("SOP+EPIA Reestructuracion 6 Sabios Abr2026",
     "SOP_EPIA_REESTRUCTURACION_DRIVE.md",
     "SOP_EPIA_REESTRUCTURACION_DBX.md"),
    ("EPIA Fundacional (md vs md)",
     "EPIA_fundacional_completo_v1_DRIVE.txt",
     "EPIA_FUNDACIONAL_DBX.md"),
    ("ENTREGABLE 2 SOP (md vs md)",
     "ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md",
     "ENTREGABLE_2_SOP_DBX.md"),
]


def strip_markdown(text: str) -> str:
    """Remueve sintaxis Markdown sin perder contenido textual."""
    # Code blocks
    text = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Headers
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    # Bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # Blockquotes
    text = re.sub(r"^\s*>\s*", "", text, flags=re.M)
    # List markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    # Links: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Horizontal rules
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.M)
    return text


def to_tokens(text: str) -> list:
    """Tokeniza a palabras alfa-num+acentos, lower-case, ignora puntuación leve."""
    text = text.replace("\ufeff", "")
    text = strip_markdown(text)
    text = text.lower()
    # Normaliza Unicode (NFC) para que los acentos comparen igual
    text = unicodedata.normalize("NFC", text)
    # Tokens: secuencias de letras/números/guiones, ignora puntuación suelta
    tokens = re.findall(r"[\wáéíóúüñ\-]+", text, flags=re.UNICODE)
    # Filtra tokens muy cortos sin valor (artefactos)
    tokens = [t for t in tokens if len(t) >= 2 or t.isdigit()]
    return tokens


def short_hash(tokens: list) -> str:
    return hashlib.sha256(" ".join(tokens).encode("utf-8")).hexdigest()[:16]


def diff_tokens(a: list, b: list, max_blocks: int = 5):
    sm = SequenceMatcher(None, a, b, autojunk=False)
    blocks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        blocks.append({
            "tag": tag,
            "drive": a[i1:i2][:30],
            "dbx": b[j1:j2][:30],
            "drive_count": i2 - i1,
            "dbx_count": j2 - j1,
        })
        if len(blocks) >= max_blocks:
            break
    return blocks, sm.ratio()


def main():
    report = ["# Diff semantico SOP/EPIA v2 — Drive vs Dropbox (token-level)",
              "",
              "**Fecha:** 2026-05-05",
              "**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)",
              "**Metodo:** strip_markdown -> tokenize -> SequenceMatcher sobre tokens (neutraliza formato)",
              "",
              "## Resumen ejecutivo",
              "",
              "| # | Par | Tokens Drive | Tokens DBX | Hash Drive | Hash DBX | Similaridad | Veredicto |",
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
        a_hash = short_hash(a_tok)
        b_hash = short_hash(b_tok)

        if a_hash == b_hash:
            veredicto = "IDENTICOS (token-level)"
            similarity = 1.0
            blocks = []
        else:
            blocks, similarity = diff_tokens(a_tok, b_tok)
            if similarity >= 0.98:
                veredicto = "EQUIVALENTES"
            elif similarity >= 0.90:
                veredicto = "DIFERENCIAS MENORES"
            elif similarity >= 0.70:
                veredicto = "DIFERENCIAS NOTABLES"
            else:
                veredicto = "DOCUMENTOS DISTINTOS"

        report.append(f"| {i} | {label} | {len(a_tok)} | {len(b_tok)} | `{a_hash}` | `{b_hash}` | {similarity:.3f} | {veredicto} |")

        det = [f"### {i}. {label}", ""]
        det.append(f"- Drive: `{drive_file}` ({len(a_tok)} tokens)")
        det.append(f"- Dropbox: `{dbx_file}` ({len(b_tok)} tokens)")
        det.append(f"- Similaridad token-level: **{similarity:.3f}** -> **{veredicto}**")
        det.append("")

        if similarity >= 0.98:
            det.append("Sin diferencias semanticas significativas. Solo formato.")
        elif blocks:
            det.append("**Bloques de diferencia (token-level):**")
            det.append("")
            for j, blk in enumerate(blocks, 1):
                det.append(f"#### Bloque {j} ({blk['tag']}, drive={blk['drive_count']} tokens, dbx={blk['dbx_count']} tokens)")
                det.append("```")
                drive_str = " ".join(blk["drive"])[:300]
                dbx_str = " ".join(blk["dbx"])[:300]
                det.append(f"DRIVE: {drive_str}")
                det.append(f"DBX:   {dbx_str}")
                det.append("```")
                det.append("")
        details.append("\n".join(det))

    report.append("")
    report.append("## Detalle por par")
    report.append("")
    report.extend(details)
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"Reporte guardado en: {REPORT}")
    print()
    for ln in report[8:16]:
        print(ln)


if __name__ == "__main__":
    main()
