#!/usr/bin/env python3
# scripts/audit_visual_diff.py
"""
Auditor visual cuantitativo de diferenciacion per vertical (DSC-V-002).

Contrato ejecutable de DSC-V-002. Es el script que el gate
`output_diferenciado_per_vertical` en kernel/milestones/gates.yaml invoca.
Sin este script, declarar PRODUCTO COMERCIALIZABLE es bloqueado.

Detecta el problema cascaron: paginas que parecen distintas pero son template
copy/paste con solo el termino vertical cambiado. Computa similitud lexica,
estructural (headings) y de call-to-action (botones, CTAs) entre todas las
parejas de paginas, y devuelve un differentiation_score 0-100. Score bajo =
template; score alto = paginas genuinamente diferenciadas per vertical.

Sin dependencias externas: solo stdlib. Sin Playwright (HTML server-rendered
solamente). Para sitios JS-pesados, sumar Playwright en una segunda iteracion.

CLI:
    python scripts/audit_visual_diff.py \\
        --urls reports/landing_urls_per_vertical.json \\
        --min-score 75

Input JSON shape (reports/landing_urls_per_vertical.json):
    {
      "verticals": [
        {"vertical": "interiorismo", "url": "https://..."},
        {"vertical": "bioguard",     "url": "https://..."},
        ...
      ]
    }

Output JSON (reports/visual_audit_diff.json):
    {
      "evaluated_at": "ISO8601",
      "min_score_required": 75,
      "differentiation_score": 42.3,
      "passed": false,
      "metrics": {...},
      "per_pair": [...],
      "fetch_errors": [...]
    }

Exit code:
    0  = score >= min_score (paginas diferenciadas)
    1  = score < min_score  (template detectado, declaracion rechazada)
    2  = error de configuracion / fetch (mas de 50% paginas inalcanzables)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html.parser
import itertools
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Stopwords minimas ES + EN. No exhaustivo a proposito — el objetivo es
# evitar que palabras funcionales hinflen artificialmente la similitud,
# no hacer NLP perfecto.
STOPWORDS = {
    # ES
    "a", "al", "ante", "bajo", "con", "como", "contra", "de", "del", "desde",
    "el", "en", "entre", "es", "ese", "esa", "eso", "esta", "este", "esto",
    "hacia", "hasta", "la", "las", "le", "les", "lo", "los", "más", "mas", "mi",
    "ni", "no", "nos", "nuestra", "nuestro", "o", "para", "pero", "por",
    "porque", "que", "se", "si", "sí", "sin", "sobre", "su", "sus", "te", "ti",
    "tu", "tus", "un", "una", "unas", "uno", "unos", "y", "ya", "yo",
    # EN
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "he", "her", "his", "i", "if", "in", "is", "it", "its", "of",
    "on", "or", "she", "that", "the", "this", "to", "was", "we", "were", "with",
    "you", "your", "our", "their", "them",
}

# Tags de los que extraemos texto para vocabulario general
TEXT_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "span", "div",
             "a", "button", "label", "title"}
HEADING_TAGS = {"h1", "h2", "h3"}
CTA_TAGS = {"button", "a"}  # Para CTAs filtramos por texto corto despues
CTA_MAX_WORDS = 8  # Un CTA real es corto


@dataclass
class PageExtract:
    vertical: str
    url: str
    fetched: bool
    status: int | None
    raw_bytes: int
    vocabulary: set[str] = field(default_factory=set)
    headings: list[str] = field(default_factory=list)
    ctas: list[str] = field(default_factory=list)
    error: str | None = None


class _LandingHTMLParser(html.parser.HTMLParser):
    """Extractor minimo: vocabulario general, headings, CTAs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._tag_stack: list[str] = []
        self.text_chunks: list[str] = []
        self.heading_chunks: list[tuple[str, list[str]]] = []  # (tag, [texts])
        self.cta_chunks: list[tuple[str, list[str]]] = []
        # current accumulator
        self._in_text = False
        self._in_heading: str | None = None
        self._in_cta: str | None = None
        self._cur_text: list[str] = []
        self._cur_heading: list[str] = []
        self._cur_cta: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        if tag in TEXT_TAGS:
            self._in_text = True
        if tag in HEADING_TAGS and self._in_heading is None:
            self._in_heading = tag
            self._cur_heading = []
        if tag in CTA_TAGS and self._in_cta is None:
            self._in_cta = tag
            self._cur_cta = []

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        if tag in TEXT_TAGS:
            self._in_text = False
        if tag == self._in_heading:
            text = " ".join(self._cur_heading).strip()
            if text:
                self.heading_chunks.append((tag, [text]))
            self._in_heading = None
            self._cur_heading = []
        if tag == self._in_cta:
            text = " ".join(self._cur_cta).strip()
            if text and len(text.split()) <= CTA_MAX_WORDS:
                self.cta_chunks.append((tag, [text]))
            self._in_cta = None
            self._cur_cta = []

    def handle_data(self, data: str) -> None:
        if self._in_text:
            self._cur_text.append(data)
            self.text_chunks.append(data)
        if self._in_heading:
            self._cur_heading.append(data)
        if self._in_cta:
            self._cur_cta.append(data)


def _tokenize(text: str) -> set[str]:
    """Tokeniza a set de palabras lowercase sin stopwords ni numeros sueltos."""
    text = text.lower()
    # Replace any non-alphanum with space
    text = re.sub(r"[^\w\sñáéíóúü]", " ", text, flags=re.UNICODE)
    tokens = text.split()
    return {
        t
        for t in tokens
        if len(t) >= 3 and t not in STOPWORDS and not t.isdigit()
    }


def _normalize(text: str) -> str:
    """Para comparar headings/CTAs: lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def _fetch(url: str, timeout: int = 30) -> tuple[bool, int | None, bytes, str | None]:
    """Fetch URL via urllib. Returns (ok, status, body_bytes, error)."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; "
                    "ElMonstruo-VisualAudit/1.0; +https://el-monstruo.dev)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return True, resp.status, body, None
    except urllib.error.HTTPError as e:
        return False, e.code, b"", f"http_error: {e.code} {e.reason}"
    except urllib.error.URLError as e:
        return False, None, b"", f"url_error: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return False, None, b"", f"error: {type(e).__name__}: {e}"


def extract_page(vertical: str, url: str) -> PageExtract:
    ok, status, body, err = _fetch(url)
    if not ok:
        return PageExtract(
            vertical=vertical,
            url=url,
            fetched=False,
            status=status,
            raw_bytes=0,
            error=err,
        )
    try:
        text = body.decode("utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        return PageExtract(
            vertical=vertical,
            url=url,
            fetched=False,
            status=status,
            raw_bytes=len(body),
            error=f"decode_error: {e}",
        )

    parser = _LandingHTMLParser()
    try:
        parser.feed(text)
    except Exception as e:  # noqa: BLE001
        return PageExtract(
            vertical=vertical,
            url=url,
            fetched=False,
            status=status,
            raw_bytes=len(body),
            error=f"parse_error: {e}",
        )

    full_text = " ".join(parser.text_chunks)
    vocab = _tokenize(full_text)
    headings = [_normalize(h) for _, chunks in parser.heading_chunks for h in chunks]
    ctas = [_normalize(c) for _, chunks in parser.cta_chunks for c in chunks]

    return PageExtract(
        vertical=vertical,
        url=url,
        fetched=True,
        status=status,
        raw_bytes=len(body),
        vocabulary=vocab,
        headings=headings,
        ctas=ctas,
    )


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _seq_jaccard(a: list[str], b: list[str]) -> float:
    return _jaccard(set(a), set(b))


def compute_metrics(pages: list[PageExtract]) -> dict[str, Any]:
    valid = [p for p in pages if p.fetched]
    n = len(valid)
    if n < 2:
        return {
            "n_pages_total": len(pages),
            "n_pages_valid": n,
            "differentiation_score": 0.0,
            "mean_pairwise_jaccard_text": 0.0,
            "mean_pairwise_jaccard_headings": 0.0,
            "mean_pairwise_jaccard_ctas": 0.0,
            "template_ratio": 0.0,
            "per_pair": [],
            "note": "n<2 paginas validas — no comparable",
        }

    pair_results = []
    js_text, js_head, js_cta = [], [], []
    for a, b in itertools.combinations(valid, 2):
        jt = _jaccard(a.vocabulary, b.vocabulary)
        jh = _seq_jaccard(a.headings, b.headings)
        jc = _seq_jaccard(a.ctas, b.ctas)
        js_text.append(jt)
        js_head.append(jh)
        js_cta.append(jc)
        pair_results.append({
            "a": a.vertical,
            "b": b.vertical,
            "jaccard_text": round(jt, 4),
            "jaccard_headings": round(jh, 4),
            "jaccard_ctas": round(jc, 4),
        })

    mean_jt = sum(js_text) / len(js_text)
    mean_jh = sum(js_head) / len(js_head) if js_head else 0.0
    mean_jc = sum(js_cta) / len(js_cta) if js_cta else 0.0

    # Template ratio: cuanto del vocabulario es comun a TODAS las paginas
    if all(p.vocabulary for p in valid):
        common = set.intersection(*(p.vocabulary for p in valid))
        union = set.union(*(p.vocabulary for p in valid))
        template_ratio = len(common) / len(union) if union else 0.0
    else:
        template_ratio = 0.0

    # Score combinado:
    #   60% texto (lo mas indicativo de cascaron),
    #   25% headings (estructura),
    #   15% CTAs.
    # Differentiation = 100 * (1 - similitud_combinada)
    combined_similarity = 0.60 * mean_jt + 0.25 * mean_jh + 0.15 * mean_jc
    differentiation_score = round(100.0 * (1.0 - combined_similarity), 2)

    # Penalty extra si template_ratio es muy alto
    if template_ratio > 0.5:
        differentiation_score = round(
            differentiation_score * (1.0 - (template_ratio - 0.5)),
            2,
        )

    return {
        "n_pages_total": len(pages),
        "n_pages_valid": n,
        "differentiation_score": max(0.0, differentiation_score),
        "mean_pairwise_jaccard_text": round(mean_jt, 4),
        "mean_pairwise_jaccard_headings": round(mean_jh, 4),
        "mean_pairwise_jaccard_ctas": round(mean_jc, 4),
        "template_ratio": round(template_ratio, 4),
        "per_pair": pair_results,
    }


def audit(urls_file: Path, min_score: float, output_file: Path) -> tuple[bool, dict[str, Any]]:
    payload_in = json.loads(urls_file.read_text())
    verticals = payload_in.get("verticals") or []
    if not verticals:
        raise ValueError(
            f"{urls_file} no contiene campo 'verticals' o esta vacio. "
            "Shape esperado: {\"verticals\": [{\"vertical\": ..., \"url\": ...}, ...]}"
        )

    pages: list[PageExtract] = []
    for entry in verticals:
        v = entry["vertical"]
        u = entry["url"]
        pages.append(extract_page(v, u))

    metrics = compute_metrics(pages)
    fetch_errors = [
        {"vertical": p.vertical, "url": p.url, "error": p.error, "status": p.status}
        for p in pages
        if not p.fetched
    ]

    # Si mas de 50% paginas no se pudieron fetchar, exit 2 (config error)
    if pages and len(fetch_errors) / len(pages) > 0.5:
        result = {
            "evaluated_at": _dt.datetime.utcnow().isoformat() + "Z",
            "min_score_required": min_score,
            "differentiation_score": 0.0,
            "passed": False,
            "config_error": True,
            "metrics": metrics,
            "fetch_errors": fetch_errors,
            "note": "Mas del 50% de paginas inalcanzables. Audit no comparable.",
        }
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        return False, result

    score = metrics["differentiation_score"]
    passed = score >= min_score

    result = {
        "evaluated_at": _dt.datetime.utcnow().isoformat() + "Z",
        "min_score_required": min_score,
        "differentiation_score": score,
        "passed": passed,
        "config_error": False,
        "metrics": metrics,
        "fetch_errors": fetch_errors,
        "interpretacion": _interpret(score, metrics),
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return passed, result


def _interpret(score: float, metrics: dict[str, Any]) -> str:
    tr = metrics.get("template_ratio", 0.0)
    if score >= 80:
        return "Diferenciacion alta. Paginas distintas per vertical en lexico, headings y CTAs."
    if score >= 60:
        return "Diferenciacion moderada. Hay diferencias pero comparten estructura significativa."
    if tr > 0.5:
        return (
            f"Template detectado: {tr:.0%} del vocabulario es comun a todas las paginas. "
            "Cumple el patron 'cascaron' (DSC-G-014)."
        )
    return (
        "Diferenciacion baja. Paginas demasiado similares; revisar copy y CTAs per vertical."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit cuantitativo de diferenciacion de landings per vertical (DSC-V-002). "
            "Contrato ejecutable invocado por kernel/milestones/gates.yaml."
        )
    )
    parser.add_argument(
        "--urls",
        required=True,
        type=Path,
        help="JSON con shape {\"verticals\": [{\"vertical\": ..., \"url\": ...}, ...]}",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=75.0,
        help="Score minimo para pasar (default 75).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/visual_audit_diff.json"),
        help="Path del JSON de evidencia (default reports/visual_audit_diff.json).",
    )
    args = parser.parse_args()

    if not args.urls.exists():
        print(f"ERROR: archivo de URLs no existe: {args.urls}", file=sys.stderr)
        return 2

    try:
        passed, result = audit(args.urls, args.min_score, args.output)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR de configuracion: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"ERROR inesperado: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if result.get("config_error"):
        print(f"\n[config_error] {result['note']}", file=sys.stderr)
        for fe in result["fetch_errors"]:
            print(f"  - {fe['vertical']} ({fe['url']}): {fe['error']}", file=sys.stderr)
        return 2

    score = result["differentiation_score"]
    if passed:
        print(
            f"[ok] differentiation_score={score} >= {args.min_score}. "
            f"Audit visual VERDE. Evidencia: {args.output}"
        )
        print(f"     {result['interpretacion']}")
        return 0

    print(
        f"[fail] differentiation_score={score} < {args.min_score}. "
        f"Audit visual ROJO (DSC-V-002 + DSC-G-014).",
        file=sys.stderr,
    )
    print(f"       {result['interpretacion']}", file=sys.stderr)
    print(f"       metricas: {json.dumps(result['metrics'], indent=2, ensure_ascii=False)}", file=sys.stderr)
    print(f"       evidencia: {args.output}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
