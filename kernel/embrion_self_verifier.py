"""
kernel/embrion_self_verifier.py — Self-Verifier de 3 decisiones para el Embrión

Sprint EMBRION-NEEDS-001, Tarea 2.
Origen: bridge/sprints_propuestos/sprint_EMBRION_NEEDS_001.md (Tarea 2)

Misión:
  Romper el patrón de eco activo del embrión (cycles 76-216 del 10-may
  con 30+ respuestas idénticas, ~$0.40 acumulados de gpt-5.5) y prevenir
  el bucle del 30 abr → 1 may (10 ciclos similares, $155 USD en 48h).

  Capa adicional ANTES de `_should_speak()` y antes de cualquier acción.
  Si 2 de 3 decisiones dicen NO, el cycle se aborta y se registra en
  `loop_detection_log` con telemetría completa para auditoría.

Las 3 Decisiones:

  D1. PURPOSE
      ¿Este pensamiento contribuye al PURPOSE declarado del embrión?
      Heurística simple basada en keywords del PURPOSE (línea 80-83 del loop):
        construir, monstruo, soberano, alfredo, investigar, código, kernel,
        aprender, anticipar, ayudar.
      Si el pensamiento NO contiene NINGUNA palabra del PURPOSE → NO.
      También se rechaza si contiene anti-purpose (gastar sin propósito,
      repetir, actuar sin reportar).

  D2. NOVELTY
      ¿Es nuevo o repite uno anterior de las últimas 24h?
      Hashing simple primero (recomendación del spec): sha256 del texto
      normalizado (lower, strip whitespace excesivo, sin puntuación trivial).
      Buscar en `embrion_memoria` las últimas 24h con tipo en
      ['respuesta_embrion','pensamiento'] y comparar hashes.
      Si match exacto o jaccard de bigramas >= 0.85 → NO (repetido).

  D3. VERIFIABLE
      ¿Produce output verificable (PR, archivo, commit, decisión registrada)
      o es eco puro? Heurística: detectar marcadores de acción concreta:
        "creé", "hice commit", "abrí PR", "escribí archivo", "modifiqué",
        "decidí que", "ejecuté", "envié", "actualicé tabla", "inserté",
        URL a PR/commit, mención de path/archivo, llamada a tool/fn.
      Si NO hay ningún marcador → NO (eco puro).

API pública:
  - `verify(thought, *, trigger_type, cycle_id, supabase_client=None) -> SelfVerifyDecision`
  - `_normalize_thought(t) -> str`             (testeable, puro)
  - `_thought_hash(t) -> str`                  (testeable, puro)
  - `_jaccard_bigrams(a, b) -> float`          (testeable, puro)

Configuración:
  - EMBRION_VERIFIER_NOVELTY_WINDOW_HOURS  default 24
  - EMBRION_VERIFIER_JACCARD_THRESHOLD     default 0.85
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    import structlog
    logger = structlog.get_logger("embrion.self_verifier")
except ImportError:  # pragma: no cover
    import logging
    logger = logging.getLogger("embrion.self_verifier")


# ── Config

NOVELTY_WINDOW_HOURS = int(os.environ.get("EMBRION_VERIFIER_NOVELTY_WINDOW_HOURS", "24"))
JACCARD_THRESHOLD = float(os.environ.get("EMBRION_VERIFIER_JACCARD_THRESHOLD", "0.85"))


# ── Heurísticas: keywords del PURPOSE y antikeywords

# Stems del PURPOSE — buscamos como prefijo dentro de palabras tokenizadas.
# Esto cubre formas conjugadas: "aprender" -> "aprendi", "aprendiendo", etc.
# El stem mínimo de 4 chars evita falsos positivos absurdos.
PURPOSE_KEYWORDS = (
    "constru",   # construir, construyendo, construye
    "monstr",    # monstruo
    "soberan",   # soberano, soberania
    "alfredo",
    "investig",  # investigar, investigando, investigue
    "codig",     # código, codigo, códigos
    "kernel",
    "aprend",    # aprender, aprendi, aprendiendo, aprende
    "anticip",   # anticipar, anticipando, anticipa
    "necesi",    # necesidad, necesito, necesita
    "mejor",     # mejorar, mejora, mejorando
    "implem",    # implementar, implementando
    "disen",     # diseñar (sin acento) -> disen, disenar
    "valid",     # validar, valido, validacion
    "asisten",   # asistente, asistencia
    "doctrin",   # doctrina
    "engran",    # engranaje
    "sprint",
    "supabase",
    "embrion",   # embrion, embrión (post-normalize accent)
    "telegram",
    "escrib",    # escribir, escribi, escribiendo
    "crear",     # crear, creando
    "propos",    # proposito, proposita
    "util",      # util, utilizar (cubre "algo util" que pidió Cowork)
)

ANTI_PURPOSE_PHRASES = (
    "gastar recursos sin",
    "actuar sin reportar",
    # Frases de eco puro detectadas en producción:
    "recibido y entendido",
    "estoy aquí escuchando",
    "estoy aqui escuchando",
)

VERIFIABLE_MARKERS = (
    # Acciones concretas en pasado (output ya producido)
    r"\bcre[éo]\b", r"\bhice commit\b", r"\babri[oó] pr\b", r"\babri pr\b",
    r"\bescribi[oó]?\b", r"\bmodifiqu[éo]\b", r"\bdecid[íi]\b",
    r"\bejecut[éo]\b", r"\benvi[éo]\b", r"\bactualic[éo]\b",
    r"\binsert[éo]\b", r"\bcomite[éo]\b", r"\bpushe[éo]\b",
    r"\bcorri[óo]\b", r"\bgenere\b", r"\bdesplegu[ée]\b",
    # Acciones en pasado del embrión hacia su mundo (incluye auto-referencia)
    r"\b(yo )?escrib[íi]\b", r"\b(yo )?cre[éo]\b", r"\b(yo )?guard[éo]\b",
    # Marcadores futuros con compromiso ejecutable
    r"\bvoy a (escribir|crear|abrir|implementar|hacer|ejecutar|enviar|insertar)\b",
    r"\b(siguiente acci[óo]n|propuesta concreta|decisi[óo]n registrada)\b",
    # URLs a artefactos
    r"https?://[^\s)]+/(pull|commit|blob|issues|releases)/",
    # Paths a archivos del repo
    r"\b(kernel|tests|migrations|scripts|bridge|docs|tools)/[\w/_.-]+\.(py|sql|md|sh|ts|tsx|json|yaml|yml)\b",
    # Llamadas a tools/funciones
    r"\b\w+\([^)]{0,200}\)",
    # Referencias a tablas de supabase
    r"\b(embrion_memoria|embrion_budget_state|loop_detection_log|embrion_write_proposals|validation_log)\b",
)
_VERIFIABLE_RE = re.compile("|".join(VERIFIABLE_MARKERS), re.IGNORECASE)


# ── DTOs

@dataclass
class SelfVerifyDecision:
    """Resultado del verifier. Determinístico para inputs iguales."""
    abort: bool                      # True si hay que abortar el cycle
    decision_purpose: bool           # D1: contribuye al PURPOSE
    decision_novelty: bool           # D2: es nuevo
    decision_verifiable: bool        # D3: produce output verificable
    votes_no: int                    # cuántas decisiones dieron NO
    reasons: list[str] = field(default_factory=list)
    similarity_match_id: Optional[str] = None
    similarity_score: Optional[float] = None
    thought_hash: Optional[str] = None

    def __bool__(self) -> bool:
        return not self.abort  # `if decision: proceed` semantics


# ── Funciones puras

_PUNCT_RE = re.compile(r"[^\w\sáéíóúñü]+", re.IGNORECASE | re.UNICODE)
_WS_RE = re.compile(r"\s+")


def _strip_accents(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize_thought(text: str) -> str:
    """Normaliza el texto para hashing y comparación de similitud.

    Pasos:
      1. lowercase
      2. strip accents
      3. drop punctuation
      4. collapse whitespace
    """
    if not text:
        return ""
    t = text.lower()
    t = _strip_accents(t)
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def _thought_hash(text: str) -> str:
    """sha256 hex del texto normalizado. Determinístico."""
    norm = _normalize_thought(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def _bigrams(text: str) -> set[str]:
    norm = _normalize_thought(text)
    tokens = norm.split()
    if len(tokens) < 2:
        return set(tokens)
    return {f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)}


def _jaccard_bigrams(a: str, b: str) -> float:
    """Similitud Jaccard entre bigramas de dos strings. 0..1."""
    A, B = _bigrams(a), _bigrams(b)
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0
    inter = len(A & B)
    union = len(A | B)
    return inter / union if union else 0.0


# ── Decisiones individuales

def evaluate_purpose(thought: str) -> tuple[bool, str]:
    """D1: ¿contribuye al PURPOSE?"""
    if not thought or not thought.strip():
        return False, "thought_empty"

    norm = _normalize_thought(thought)
    # Anti-purpose phrases — match directo (también normalizadas)
    for anti in ANTI_PURPOSE_PHRASES:
        if _normalize_thought(anti) in norm:
            return False, f"anti_purpose_match: {anti!r}"

    # Purpose stems — cualquier token del thought que empiece con el stem cuenta
    tokens = norm.split()
    for kw in PURPOSE_KEYWORDS:
        kw_norm = _normalize_thought(kw)
        for tok in tokens:
            if tok.startswith(kw_norm):
                return True, f"purpose_stem: {kw!r} matches token {tok!r}"

    return False, "no_purpose_keywords_found"


def evaluate_verifiable(thought: str) -> tuple[bool, str]:
    """D3: ¿produce output verificable o es eco puro?"""
    if not thought or not thought.strip():
        return False, "thought_empty"

    m = _VERIFIABLE_RE.search(thought)
    if m:
        return True, f"verifiable_marker: {m.group(0)[:60]!r}"

    return False, "no_verifiable_markers_found"


def evaluate_novelty(
    thought: str,
    *,
    supabase_client,
    window_hours: int = NOVELTY_WINDOW_HOURS,
    jaccard_threshold: float = JACCARD_THRESHOLD,
) -> tuple[bool, str, Optional[str], Optional[float]]:
    """D2: ¿es nuevo o repite uno anterior 24h?

    Returns:
        (es_nuevo, razón, match_id, similarity_score)
    """
    if not thought or not thought.strip():
        return False, "thought_empty", None, None

    if supabase_client is None:
        # Fail-open conservador: si no podemos consultar, asumimos nuevo
        # PERO logueamos. Esto evita matar al embrión en outage de Supabase.
        return True, "supabase_unavailable_fail_open", None, None

    h = _thought_hash(thought)
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()

    try:
        rows, _ = supabase_client.select(
            "embrion_memoria",
            params={
                "select": "id,contenido,created_at,tipo",
                "tipo": "in.(respuesta_embrion,pensamiento)",
                "created_at": f"gte.{cutoff}",
                "order": "created_at.desc",
                "limit": "200",
            },
        )
    except Exception as e:
        logger.warning("embrion_self_verifier_query_failed", error=str(e))
        return True, f"query_failed_fail_open: {e}", None, None

    # 1) Match exacto por hash
    for r in rows:
        contenido = r.get("contenido") or ""
        if _thought_hash(contenido) == h:
            return False, "exact_hash_match_24h", r.get("id"), 1.0

    # 2) Match por jaccard de bigramas (solo top 50 más recientes para perf)
    best_id = None
    best_score = 0.0
    for r in rows[:50]:
        contenido = r.get("contenido") or ""
        score = _jaccard_bigrams(thought, contenido)
        if score > best_score:
            best_score = score
            best_id = r.get("id")

    if best_score >= jaccard_threshold:
        return False, f"jaccard_match_{best_score:.3f}", best_id, best_score

    return True, f"no_match_best_jaccard={best_score:.3f}", best_id, best_score


# ── API principal

def verify(
    thought: str,
    *,
    trigger_type: str,
    cycle_id: int,
    supabase_client=None,
    persist: bool = True,
) -> SelfVerifyDecision:
    """Self-Verifier completo: ejecuta las 3 decisiones y registra resultado.

    Args:
        thought: el contenido del pensamiento generado por el modelo
        trigger_type: tipo de trigger que disparó el cycle
        cycle_id: id numérico del cycle del embrión
        supabase_client: opcional, para tests sin red
        persist: si True, escribe row en loop_detection_log

    Returns:
        SelfVerifyDecision con `abort=True` si 2 de 3 dieron NO.
    """
    if supabase_client is None and persist:
        try:
            from kernel.embrion_budget import _get_supabase_client
            supabase_client = _get_supabase_client()
        except Exception as e:
            logger.warning("embrion_self_verifier_no_client", error=str(e))
            persist = False

    reasons: list[str] = []

    # D1
    d1, r1 = evaluate_purpose(thought)
    reasons.append(f"D1 purpose={d1}: {r1}")

    # D2
    d2, r2, match_id, sim_score = evaluate_novelty(
        thought, supabase_client=supabase_client,
    )
    reasons.append(f"D2 novelty={d2}: {r2}")

    # D3
    d3, r3 = evaluate_verifiable(thought)
    reasons.append(f"D3 verifiable={d3}: {r3}")

    votes_no = sum(1 for d in (d1, d2, d3) if not d)
    abort = votes_no >= 2

    h = _thought_hash(thought)

    decision = SelfVerifyDecision(
        abort=abort,
        decision_purpose=d1,
        decision_novelty=d2,
        decision_verifiable=d3,
        votes_no=votes_no,
        reasons=reasons,
        similarity_match_id=match_id if not d2 else None,
        similarity_score=sim_score,
        thought_hash=h,
    )

    if persist and supabase_client is not None:
        try:
            payload = {
                "detected_pattern": (
                    "self_verifier_abort" if abort else "self_verifier_pass"
                ),
                "severity": "high" if abort else "low",
                "auto_action_taken": "abort_cycle" if abort else None,
                "resolved": (not abort),
                "cycle_id": int(cycle_id),
                "decision_purpose": d1,
                "decision_novelty": d2,
                "decision_verifiable": d3,
                "votes_no": votes_no,
                "aborted": abort,
                "embrion_thought": (thought or "")[:4000],
                "embrion_thought_hash": h,
                "similarity_match_id": match_id if not d2 else None,
                "trigger_type": trigger_type,
                "reasoning": {"reasons": reasons, "similarity_score": sim_score},
            }
            supabase_client.insert("loop_detection_log", payload)
        except Exception as e:
            logger.warning("embrion_self_verifier_persist_failed", error=str(e))

    logger.info(
        "embrion_self_verifier_evaluated",
        cycle_id=cycle_id,
        abort=abort,
        votes_no=votes_no,
        d1=d1, d2=d2, d3=d3,
    )

    return decision


def daily_metrics(*, supabase_client=None) -> dict:
    """Métrica registrada (requerida por el spec):
       ratio de aborts por self-verifier vs cycles totales evaluados hoy."""
    if supabase_client is None:
        from kernel.embrion_budget import _get_supabase_client
        supabase_client = _get_supabase_client()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows, _ = supabase_client.select(
        "loop_detection_log",
        params={
            "select": "aborted,decision_purpose,decision_novelty,decision_verifiable",
            "created_at": f"gte.{today}T00:00:00+00:00",
            "detected_pattern": "in.(self_verifier_abort,self_verifier_pass)",
        },
    )
    total = len(rows)
    aborts = sum(1 for r in rows if r.get("aborted"))
    failed_d1 = sum(1 for r in rows if r.get("decision_purpose") is False)
    failed_d2 = sum(1 for r in rows if r.get("decision_novelty") is False)
    failed_d3 = sum(1 for r in rows if r.get("decision_verifiable") is False)
    return {
        "date": today,
        "evaluated_total": total,
        "aborts": aborts,
        "abort_ratio": (aborts / total) if total else 0.0,
        "failed_purpose": failed_d1,
        "failed_novelty": failed_d2,
        "failed_verifiable": failed_d3,
    }
