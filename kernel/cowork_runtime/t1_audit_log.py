"""
kernel/cowork_runtime/t1_audit_log.py — Audit log para fase T1 OBSERVE-ONLY.

Cada interception del hook (con sus claims clasificados) se persiste en
JSONL para auditoria manual posterior. La auditoria a 24h debe poder
clasificar cada claim como:

  classification:
    "true_block"      claim sin tag que efectivamente debia bloquear
    "false_positive"  claim sin tag que NO debia ser claim factual
    "false_negative"  claim con tag erroneo o claim ignorado por el detector
    "verified_after"  claim que post-hoc se verifico fuera de sesion
    "pending"         aun no revisado

  severity: P0 | P1 | P2  (heredada del detector, ajustable por auditor)
  fuente_requerida: string (que fuente verificaria el claim)

NO se borra ningun registro. NO se mutan in-place: la auditoria agrega
un nuevo evento `claim_reviewed` con el audit_id correspondiente.

Esto permite reconstruir la decision de ENFORCE: las 50 claims se sacan
de aqui (`load_for_audit(limit=50)`) y luego `tag_claim_review` registra
cada decision.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from kernel.cowork_runtime.t1_output_contract import ContractReport, Claim
from kernel.cowork_runtime.tool_call_audit import (
    ToolCallContext,
    evaluate_claim_tool_call,
)


DEFAULT_AUDIT_LOG_PATH = Path("bridge/t1_audit_log.jsonl")


@dataclass
class AuditEntry:
    """Una interception completa del hook con sus claims y contexto."""
    audit_id: str
    timestamp_utc: str
    session_id: str
    mode: str                  # off|observe_only|enforce
    user_message: str
    output_preview: str        # primeros 400 chars del output
    output_chars: int
    blocked: bool              # si en ENFORCE se hubiera/fue bloqueado
    would_block: bool          # lo que habria bloqueado en ENFORCE (en obs)
    claims: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    legacy_guardian_violations: list[str] = field(default_factory=list)

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


@dataclass
class ClaimReview:
    """Una revision manual de un claim previamente registrado."""
    audit_id: str
    claim_index: int           # indice del claim dentro de entry.claims
    classification: str        # true_block|false_positive|false_negative|verified_after|pending
    severity_corrected: Optional[str] = None  # P0|P1|P2 o None
    fuente_requerida: str = ""
    reviewer: str = "alfredo"
    reviewed_at_utc: str = ""

    def to_jsonl(self) -> str:
        return json.dumps({"event": "claim_reviewed", **asdict(self)}, ensure_ascii=False)


VALID_CLASSIFICATIONS = (
    "true_block",
    "false_positive",
    "false_negative",
    "verified_after",
    "pending",
)
VALID_SEVERITIES = ("P0", "P1", "P2")


@dataclass
class ClaimTelemetry:
    """
    Telemetria claim-level (convergencia Copilot 365 — 2026-05-12).

    Cada claim material de una interception produce un evento JSONL
    independiente con su propia metadata. Esto permite analisis
    claim-by-claim en lugar de solo response-level.
    """
    event: str = "claim_telemetry"
    claim_id: str = ""
    audit_id: str = ""
    claim_index: int = 0
    timestamp_utc: str = ""
    session_id: str = ""
    mode: str = ""
    claim_text: str = ""
    severity: str = ""           # P0 | P1 | P2
    has_tag: bool = False
    tag_value: str = ""
    epistemic_label: Optional[str] = None  # uno de VALID_LABELS_9 o None
    license_validated: bool = False
    license_required: Optional[str] = None
    tool_call_present_this_turn: bool = False
    action_taken: str = "would_pass"  # would_block | would_degrade | would_pass

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class T1AuditLog:
    """
    Append-only JSONL log con dos tipos de eventos:
      - AuditEntry (default, una linea por interception)
      - ClaimReview (linea de evento con field "event":"claim_reviewed")

    Para distinguir, el reader chequea si la linea tiene clave "event".
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path) if path else DEFAULT_AUDIT_LOG_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # -- writers --------------------------------------------------------

    def record_interception(
        self,
        *,
        session_id: str,
        mode: str,
        user_message: str,
        cowork_output: str,
        report: ContractReport,
        blocked: bool,
        would_block: bool,
        legacy_guardian_violations: Optional[list[str]] = None,
        tool_call_ctx: Optional[ToolCallContext] = None,
    ) -> AuditEntry:
        """
        Persiste una interception completa al JSONL.

        Si `tool_call_ctx` esta presente, ademas del evento `AuditEntry`
        parent escribe un evento `claim_telemetry` por cada claim del
        reporte. Esto reemplaza el modelo response-level por uno
        claim-level (convergencia Copilot 365 2026-05-12).
        """
        audit_id = str(uuid.uuid4())
        ts = datetime.now(timezone.utc).isoformat()
        entry = AuditEntry(
            audit_id=audit_id,
            timestamp_utc=ts,
            session_id=session_id,
            mode=mode,
            user_message=user_message[:500],
            output_preview=cowork_output[:400],
            output_chars=len(cowork_output),
            blocked=blocked,
            would_block=would_block,
            claims=[
                {
                    "text": c.text[:500],
                    "severity": c.severity,
                    "has_tag": c.has_tag,
                    "tag_value": c.tag_value,
                    "epistemic_label": c.normalized_label,
                }
                for c in report.claims
            ],
            summary=report.summary(),
            legacy_guardian_violations=list(legacy_guardian_violations or []),
        )
        self._append_raw(entry.to_jsonl())

        # Telemetria claim-level: un evento por claim
        ctx = tool_call_ctx if tool_call_ctx is not None else ToolCallContext()
        for idx, c in enumerate(report.claims):
            eval_result = evaluate_claim_tool_call(
                claim_has_license_label=c.has_tag,
                claim_normalized_label=c.normalized_label,
                ctx=ctx,
            )
            # Decisin action_taken claim-level (proyeccion ENFORCE):
            # - would_block: claim P0/P1 sin tag o con tag licenciado ilegitimo
            # - would_degrade: claim factual fuerte que pretende licencia
            #   pero el contexto no la ratifica
            # - would_pass: claim P2 o claim factual con etiqueta legitima
            action = self._derive_action(c, eval_result)
            telemetry = ClaimTelemetry(
                claim_id=str(uuid.uuid4()),
                audit_id=audit_id,
                claim_index=idx,
                timestamp_utc=ts,
                session_id=session_id,
                mode=mode,
                claim_text=c.text[:500],
                severity=c.severity,
                has_tag=c.has_tag,
                tag_value=c.tag_value,
                epistemic_label=c.normalized_label,
                license_validated=eval_result["license_legitimate"] and c.has_tag,
                license_required=eval_result["license_required"],
                tool_call_present_this_turn=eval_result["tool_call_present"],
                action_taken=action,
            )
            self._append_raw(telemetry.to_jsonl())
        return entry

    @staticmethod
    def _derive_action(c: Claim, eval_result: dict) -> str:
        """
        Proyeccion claim-level de la decision si estuvieramos en ENFORCE:

          would_block    claim P0/P1 sin etiqueta licenciada legitima
          would_degrade  claim factual fuerte que pretende licencia pero
                         el contexto (tool_call) no la ratifica
          would_pass     P2, o claim factual con licencia legitima, o
                         claim con etiqueta de degradacion ya declarada
        """
        if c.severity == "P2":
            return "would_pass"
        if not c.has_tag:
            return "would_block"
        # has_tag=True
        if c.has_license_to_assert():
            return "would_pass" if eval_result["license_legitimate"] else "would_degrade"
        # Etiqueta degradante o intermedia ya presente
        return "would_pass"

    def tag_claim_review(
        self,
        audit_id: str,
        claim_index: int,
        classification: str,
        severity_corrected: Optional[str] = None,
        fuente_requerida: str = "",
        reviewer: str = "alfredo",
    ) -> ClaimReview:
        """Auditoria manual a 24h: clasifica un claim previamente registrado."""
        if classification not in VALID_CLASSIFICATIONS:
            raise ValueError(
                f"classification debe ser uno de {VALID_CLASSIFICATIONS}; "
                f"recibido: {classification!r}"
            )
        if severity_corrected is not None and severity_corrected not in VALID_SEVERITIES:
            raise ValueError(
                f"severity_corrected debe ser uno de {VALID_SEVERITIES}; "
                f"recibido: {severity_corrected!r}"
            )
        review = ClaimReview(
            audit_id=audit_id,
            claim_index=claim_index,
            classification=classification,
            severity_corrected=severity_corrected,
            fuente_requerida=fuente_requerida,
            reviewer=reviewer,
            reviewed_at_utc=datetime.now(timezone.utc).isoformat(),
        )
        self._append_raw(review.to_jsonl())
        return review

    # -- readers --------------------------------------------------------

    def load_for_audit(
        self,
        limit: int = 50,
        only_material: bool = True,
    ) -> list[dict]:
        """
        Devuelve hasta `limit` claims materiales pendientes de revisar.

        only_material=True filtra a claims con severidad P0/P1 sin tag
        (los que el sistema considera potencialmente bloqueantes). Si
        ya hay un ClaimReview para ese (audit_id, claim_index), se
        excluye.
        """
        entries = list(self._iter_entries())
        reviews = list(self._iter_reviews())
        revisados = {(r["audit_id"], r["claim_index"]) for r in reviews}

        out: list[dict] = []
        for entry in entries:
            for idx, claim in enumerate(entry.get("claims", [])):
                if (entry["audit_id"], idx) in revisados:
                    continue
                if only_material:
                    if claim.get("has_tag"):
                        continue
                    if claim.get("severity") not in ("P0", "P1"):
                        continue
                out.append({
                    "audit_id": entry["audit_id"],
                    "claim_index": idx,
                    "timestamp_utc": entry["timestamp_utc"],
                    "severity": claim["severity"],
                    "text": claim["text"],
                    "tagged": claim.get("has_tag", False),
                    "mode_at_capture": entry.get("mode"),
                })
                if len(out) >= limit:
                    return out
        return out

    def count_confirmed_p0_p1(self) -> int:
        """Cuenta claim_reviews con classification=='true_block' y severidad P0/P1."""
        n = 0
        for r in self._iter_reviews():
            if r.get("classification") != "true_block":
                continue
            sev = r.get("severity_corrected")
            if sev in ("P0", "P1") or sev is None:
                # severity_corrected None significa que se mantuvo la severidad
                # original del detector — el caller debe validar contra entry
                n += 1
        return n

    def stats(self) -> dict:
        entries = list(self._iter_entries())
        reviews = list(self._iter_reviews())
        return {
            "total_interceptions": len(entries),
            "total_blocked": sum(1 for e in entries if e.get("blocked")),
            "total_would_block": sum(1 for e in entries if e.get("would_block")),
            "total_claims": sum(len(e.get("claims", [])) for e in entries),
            "total_reviews": len(reviews),
            "reviews_by_classification": _group_count(reviews, "classification"),
        }

    # -- internals ------------------------------------------------------

    def _append_raw(self, line: str) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _iter_all(self) -> Iterable[dict]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def _iter_entries(self) -> Iterable[dict]:
        """
        Entries son los AuditEntry parent (sin "event" o sin un valor
        de evento que reconozcamos como derivado).
        """
        for d in self._iter_all():
            ev = d.get("event")
            if ev in ("claim_reviewed", "claim_telemetry"):
                continue
            yield d

    def _iter_reviews(self) -> Iterable[dict]:
        for d in self._iter_all():
            if d.get("event") == "claim_reviewed":
                yield d

    def _iter_telemetry(self) -> Iterable[dict]:
        for d in self._iter_all():
            if d.get("event") == "claim_telemetry":
                yield d

    def iter_claim_telemetry(self) -> Iterable[dict]:
        """Public reader para analisis claim-level."""
        return self._iter_telemetry()

    def telemetry_summary(self) -> dict:
        """Resumen agregado de la telemetria claim-level."""
        rows = list(self._iter_telemetry())
        by_action: dict[str, int] = {}
        by_label: dict[str, int] = {}
        tool_present = 0
        for r in rows:
            by_action[r.get("action_taken", "")] = by_action.get(r.get("action_taken", ""), 0) + 1
            lbl = r.get("epistemic_label") or "NO_LABEL"
            by_label[lbl] = by_label.get(lbl, 0) + 1
            if r.get("tool_call_present_this_turn"):
                tool_present += 1
        return {
            "total_claims_logged": len(rows),
            "by_action": by_action,
            "by_label": by_label,
            "tool_call_present_count": tool_present,
        }


def _group_count(items: Iterable[dict], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for it in items:
        v = it.get(key, "")
        out[v] = out.get(v, 0) + 1
    return out
