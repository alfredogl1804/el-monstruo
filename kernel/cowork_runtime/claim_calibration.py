"""
kernel/cowork_runtime/claim_calibration.py — Sprint COWORK-MEMENTO-001 T2

Claim calibration retrospectiva — pieza 1 anti-Dory (D2 + D3) cross-sesión.

Registra cada afirmación factual de Cowork con `verification_status` binario,
exponiendo dataset retrospectivo (`public.cowork_claims_calibration`) para
iterar el harness anti-Dory con evidencia (Opus 4.7 Dirección 4 verbatim) no
hipótesis.

Doctrina:
- DSC-V-001  : validación claims estado-del-mundo (subset del decorator)
- DSC-S-006 v1.1 : tabla con RLS habilitado + policy explícita (migration 0033)
- DSC-S-016 : anti-fabricación causalidad sin grep (extractor regex deterministas)
- DSC-G-008 v3 §4 : deducción consecuencias materiales (limitaciones declaradas)
- DSC-MO-006 v1.1 : PBA permanente (dataset alimenta decisiones Sabios)
- F26 (anti) : este módulo ES código ejecutable, no doctrina markdown

Estatus binario por claim:
    verified_pre              → register_tool_call() pre-emit con claim verbatim
    verified_post_match       → claim matchea exacto contra tool result en history
    verified_post_mismatch    → tool call existe pero strings divergen (F21 latente)
    unverified                → no hay tool call relacionado (F21 candidato)

Uso programático:

    from kernel.cowork_runtime.claim_calibration import (
        ClaimExtractor, ClaimLogger, ClaimType, VerificationStatus
    )
    extractor = ClaimExtractor()
    candidates = extractor.extract_claims(cowork_output_text)
    logger = ClaimLogger(supabase_client=client, session_id=session_uuid)
    logger.log_batch(records_with_status)

Spec firmado T1: bridge/sprints_propuestos/sprint_COWORK_MEMENTO_001.md commit 78d1fb00
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Iterable, List, Optional
from uuid import UUID


# ============================================================================
# Enums (claim taxonomy — 12 tipos canónicos firmados T1)
# ============================================================================

class ClaimType(str, Enum):
    """12 categorías de claim factual extraíbles del output Cowork."""
    FILE_PATH = "file_path"
    TABLE_NAME = "table_name"
    COLUMN_NAME = "column_name"
    MIGRATION_NUMBER = "migration_number"
    PR_NUMBER = "pr_number"
    COMMIT_HASH = "commit_hash"
    BRANCH_NAME = "branch_name"
    SPRINT_NAME = "sprint_name"
    LOC_COUNT = "loc_count"
    TEST_COUNT = "test_count"
    FECHA_ISO = "fecha_iso"
    VERSION_STRING = "version_string"


class VerificationStatus(str, Enum):
    """4 estados binarios de verificación post-hoc."""
    VERIFIED_PRE = "verified_pre"
    VERIFIED_POST_MATCH = "verified_post_match"
    VERIFIED_POST_MISMATCH = "verified_post_mismatch"
    UNVERIFIED = "unverified"


# ============================================================================
# Dataclasses
# ============================================================================

@dataclass(frozen=True)
class ClaimCandidate:
    """Claim extraído de output_text por ClaimExtractor (sin verificar aún)."""
    claim_type: ClaimType
    claim_value: str
    detected_in_output: str       # snippet contextual ±50 chars
    extraction_regex_id: str      # id interno del regex que lo capturó


@dataclass
class ClaimRecord:
    """Registro listo para INSERT a public.cowork_claims_calibration."""
    claim_type: ClaimType
    claim_value: str
    verification_status: VerificationStatus
    turn_index: int
    detected_in_output: Optional[str] = None
    extraction_regex_id: Optional[str] = None
    tool_call_evidence: Optional[str] = None
    session_uuid: Optional[UUID] = None
    metadata: dict = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def to_db_row(self) -> dict:
        """Serialización para insert via Supabase client."""
        return {
            "session_uuid": str(self.session_uuid) if self.session_uuid else None,
            "turn_index": int(self.turn_index),
            "claim_type": self.claim_type.value,
            "claim_value": self.claim_value,
            "verification_status": self.verification_status.value,
            "tool_call_evidence": self.tool_call_evidence,
            "detected_in_output": self.detected_in_output,
            "extraction_regex_id": self.extraction_regex_id,
            "metadata": self.metadata or {},
        }


# ============================================================================
# ClaimExtractor (regex deterministas, anti-F21)
# ============================================================================

# Regex con id explícito para trazabilidad (extraction_regex_id en tabla)
_EXTRACTORS: list[tuple[ClaimType, str, re.Pattern]] = [
    (
        ClaimType.MIGRATION_NUMBER,
        "regex_migration_v1",
        re.compile(r"\b(\d{4})_[\w]+\.sql\b"),
    ),
    (
        ClaimType.FILE_PATH,
        "regex_file_path_v1",
        re.compile(r"(?:^|[\s`(])((?:[a-zA-Z0-9_.\-]+/)+[a-zA-Z0-9_.\-]+\.[a-zA-Z0-9]{1,6})\b"),
    ),
    (
        ClaimType.PR_NUMBER,
        "regex_pr_number_v1",
        re.compile(r"\bPR\s*#(\d{1,6})\b", re.IGNORECASE),
    ),
    (
        ClaimType.COMMIT_HASH,
        "regex_commit_hash_v1",
        re.compile(r"\b(?:commit\s+)?([0-9a-f]{7,40})\b"),
    ),
    (
        ClaimType.TABLE_NAME,
        "regex_table_name_v1",
        re.compile(
            r"\b(?:FROM|INTO|UPDATE|JOIN)\s+([a-z][a-z0-9_]{2,63})\b",
            re.IGNORECASE,
        ),
    ),
    (
        ClaimType.BRANCH_NAME,
        "regex_branch_name_v1",
        re.compile(r"\b((?:feat|fix|chore|sprint|revert|hotfix)/[a-zA-Z0-9_\-/.]+)\b"),
    ),
    (
        ClaimType.SPRINT_NAME,
        "regex_sprint_name_v1",
        re.compile(r"\b([A-Z][A-Z\-]+-\d{3})\b"),
    ),
    (
        ClaimType.LOC_COUNT,
        "regex_loc_count_v1",
        re.compile(r"\b(\d{1,6})\s*(?:LOC|loc|lines?\s+of\s+code)\b"),
    ),
    (
        ClaimType.TEST_COUNT,
        "regex_test_count_v1",
        re.compile(r"\b(\d{1,4})\s*(?:tests?|passed|PASSED)\b"),
    ),
    (
        ClaimType.FECHA_ISO,
        "regex_fecha_iso_v1",
        re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b"),
    ),
    (
        ClaimType.VERSION_STRING,
        "regex_version_string_v1",
        re.compile(r"\b(v\d+\.\d+(?:\.\d+)?)\b"),
    ),
    # COLUMN_NAME se detecta solo en contexto sql COLUMN ... — heurística conservadora
    (
        ClaimType.COLUMN_NAME,
        "regex_column_name_v1",
        re.compile(r"\bCOLUMN\s+([a-z][a-z0-9_]{1,63})\b", re.IGNORECASE),
    ),
]


class ClaimExtractor:
    """Extrae claims factuales de un output_text Cowork vía regex deterministas."""

    SNIPPET_RADIUS = 50  # chars antes/después del match para contexto

    def extract_claims(self, output_text: str) -> List[ClaimCandidate]:
        """Itera regex registrados sobre output_text y devuelve candidates deduplicados."""
        if not output_text:
            return []

        seen: set[tuple[str, str]] = set()
        out: list[ClaimCandidate] = []

        for claim_type, regex_id, pattern in _EXTRACTORS:
            for match in pattern.finditer(output_text):
                value = match.group(1).strip()
                key = (claim_type.value, value)
                if key in seen:
                    continue
                seen.add(key)
                start = max(0, match.start() - self.SNIPPET_RADIUS)
                end = min(len(output_text), match.end() + self.SNIPPET_RADIUS)
                snippet = output_text[start:end]
                out.append(
                    ClaimCandidate(
                        claim_type=claim_type,
                        claim_value=value,
                        detected_in_output=snippet,
                        extraction_regex_id=regex_id,
                    )
                )
        return out


# ============================================================================
# Verification status inference (post-hoc heurístico, L_A3 declarada)
# ============================================================================

def infer_verification_status(
    claim: ClaimCandidate,
    tool_call_history: Iterable[str],
    pre_registered_claims: Optional[Iterable[str]] = None,
) -> tuple[VerificationStatus, Optional[str]]:
    """
    Infiere verification_status del claim contra el tool_call_history reciente.

    Returns:
        (status, evidence_string_or_None)

    Lógica:
        1. Si claim.claim_value ∈ pre_registered_claims → verified_pre
        2. Si claim.claim_value ⊂ algún tool result → verified_post_match
        3. Si claim_type-prefix existe en history pero value no matchea → verified_post_mismatch
        4. Sino → unverified
    """
    value = claim.claim_value
    if pre_registered_claims and value in set(pre_registered_claims):
        return VerificationStatus.VERIFIED_PRE, f"pre-registered:{value}"

    history_concat = "\n".join(tool_call_history) if tool_call_history else ""

    if not history_concat:
        return VerificationStatus.UNVERIFIED, None

    if value in history_concat:
        # Match exacto del string en algún tool result
        return VerificationStatus.VERIFIED_POST_MATCH, _extract_evidence_window(history_concat, value)

    # Heurística post_mismatch: si claim_type-keyword aparece en history pero value no
    type_keyword = _type_keyword_for_mismatch(claim.claim_type)
    if type_keyword and type_keyword.lower() in history_concat.lower():
        return VerificationStatus.VERIFIED_POST_MISMATCH, type_keyword

    return VerificationStatus.UNVERIFIED, None


def _type_keyword_for_mismatch(claim_type: ClaimType) -> Optional[str]:
    """Keyword heurístico por tipo para detectar mismatch (tool call existe pero value diverge)."""
    return {
        ClaimType.MIGRATION_NUMBER: ".sql",
        ClaimType.FILE_PATH: "/",
        ClaimType.PR_NUMBER: "PR #",
        ClaimType.COMMIT_HASH: "commit",
        ClaimType.TABLE_NAME: "FROM ",
        ClaimType.BRANCH_NAME: "feat/",
        ClaimType.SPRINT_NAME: "sprint",
        ClaimType.LOC_COUNT: "LOC",
        ClaimType.TEST_COUNT: "passed",
        ClaimType.FECHA_ISO: "20",
        ClaimType.VERSION_STRING: "v",
        ClaimType.COLUMN_NAME: "COLUMN ",
    }.get(claim_type)


def _extract_evidence_window(text: str, value: str, radius: int = 40) -> str:
    """Devuelve snippet ±radius chars alrededor de la primera ocurrencia de value en text."""
    idx = text.find(value)
    if idx == -1:
        return value
    start = max(0, idx - radius)
    end = min(len(text), idx + len(value) + radius)
    return text[start:end]


# ============================================================================
# ClaimLogger (INSERT a public.cowork_claims_calibration via Supabase client)
# ============================================================================

class ClaimLogger:
    """Persiste ClaimRecords a public.cowork_claims_calibration.

    Diseñado fire-and-forget: log_claim/log_batch nunca bloquean el hook ni
    levantan excepciones a quien lo llama (DSC-G-008 v3 §4 dedu consecuencias:
    si el logger falla, NO debe romper el flujo Cowork; cuenta como L_A6).

    Args:
        supabase_client: cliente Supabase con .table().insert() o callable
            compatible. Para tests pasar mock con interfaz mínima.
        session_id: UUID de la sesión Cowork activa, o None para CLI standalone.
        on_error: callback opcional que recibe excepción si ocurre (default: silent).
    """

    TABLE_NAME = "cowork_claims_calibration"

    def __init__(
        self,
        supabase_client: Any,
        session_id: Optional[UUID] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        self.client = supabase_client
        self.session_id = session_id
        self.on_error = on_error
        self._insert_count = 0
        self._error_count = 0

    def log_claim(self, claim: ClaimRecord) -> bool:
        """Insert un único claim. Retorna True si OK, False si error (silent)."""
        if claim.session_uuid is None and self.session_id is not None:
            claim.session_uuid = self.session_id
        try:
            row = claim.to_db_row()
            self._insert_row(row)
            self._insert_count += 1
            return True
        except Exception as exc:  # pragma: no cover (defensive)
            self._error_count += 1
            if self.on_error:
                self.on_error(exc)
            return False

    def log_batch(self, claims: List[ClaimRecord]) -> int:
        """Insert múltiples claims en una sola operación. Retorna cantidad de OKs."""
        ok = 0
        rows: list[dict] = []
        for claim in claims:
            if claim.session_uuid is None and self.session_id is not None:
                claim.session_uuid = self.session_id
            rows.append(claim.to_db_row())
        try:
            self._insert_rows(rows)
            self._insert_count += len(rows)
            ok = len(rows)
        except Exception as exc:
            self._error_count += 1
            if self.on_error:
                self.on_error(exc)
        return ok

    def aggregate_daily(
        self,
        days: int = 1,
        claim_type: Optional[str] = None,
    ) -> dict:
        """SELECT GROUP BY claim_type, verification_status sobre últimos N días.

        Retorna dict shape:
            {
                "days": N,
                "total_claims": M,
                "by_type": {
                    "<claim_type>": {
                        "verified_pre": int,
                        "verified_post_match": int,
                        "verified_post_mismatch": int,
                        "unverified": int,
                    }
                },
                "f21_rate": float,         # (mismatch + unverified) / total
                "generated_at": ISO timestamp,
            }
        """
        rows = self._query_aggregate(days=days, claim_type=claim_type)
        by_type: dict[str, dict[str, int]] = {}
        total = 0
        f21 = 0
        for r in rows:
            ct = r.get("claim_type", "unknown")
            vs = r.get("verification_status", "unverified")
            n = int(r.get("n") or r.get("count") or 0)
            by_type.setdefault(ct, {
                "verified_pre": 0,
                "verified_post_match": 0,
                "verified_post_mismatch": 0,
                "unverified": 0,
            })
            by_type[ct][vs] = by_type[ct].get(vs, 0) + n
            total += n
            if vs in ("unverified", "verified_post_mismatch"):
                f21 += n
        return {
            "days": days,
            "total_claims": total,
            "by_type": by_type,
            "f21_rate": (f21 / total) if total else 0.0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internals (abstracción sobre el cliente Supabase concreto)
    # ------------------------------------------------------------------

    def _insert_row(self, row: dict) -> None:
        """Hook tests-friendly: aislamos el cliente real."""
        if hasattr(self.client, "table"):
            self.client.table(self.TABLE_NAME).insert(row).execute()
        elif callable(self.client):
            self.client({"action": "insert", "table": self.TABLE_NAME, "row": row})
        else:
            # Fallback: cliente con insert directo (mocks de test)
            self.client.insert(self.TABLE_NAME, row)

    def _insert_rows(self, rows: list[dict]) -> None:
        if not rows:
            return
        if hasattr(self.client, "table"):
            self.client.table(self.TABLE_NAME).insert(rows).execute()
        elif callable(self.client):
            self.client({"action": "insert_batch", "table": self.TABLE_NAME, "rows": rows})
        else:
            self.client.insert_batch(self.TABLE_NAME, rows)

    def _query_aggregate(self, days: int, claim_type: Optional[str]) -> List[dict]:
        """Ejecuta query agregada vía cliente. Tests-friendly via duck-typing."""
        if hasattr(self.client, "aggregate_claims"):
            return list(self.client.aggregate_claims(days=days, claim_type=claim_type))
        if callable(self.client):
            return list(self.client({
                "action": "aggregate",
                "table": self.TABLE_NAME,
                "days": days,
                "claim_type": claim_type,
            }) or [])
        return []

    @property
    def insert_count(self) -> int:
        return self._insert_count

    @property
    def error_count(self) -> int:
        return self._error_count


# ============================================================================
# Públicas
# ============================================================================

__all__ = [
    "ClaimType",
    "VerificationStatus",
    "ClaimCandidate",
    "ClaimRecord",
    "ClaimExtractor",
    "ClaimLogger",
    "infer_verification_status",
]
