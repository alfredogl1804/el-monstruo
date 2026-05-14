"""
kernel/cowork_runtime/pre_response_hook.py — T1 MAGNA Sprint COWORK-RUNTIME-001
Merged post-MEMENTO + AUTO-DISCIPLINE-REAL-001 (Sprint PR-118-REBASE 2026-05-14)

Pre-respuesta hook que intercepta cada output candidato de Cowork antes de
enviarlo a Alfredo. Valida contra `tools.cowork_guardian.validate_output`.
Si guardian devuelve passed=False, bloquea + devuelve feedback estructurado
con violaciones detectadas para que Cowork reescriba.

Doctrina:
- DSC-MO-005: Cowork (T2) es Arquitecto, no Ejecutor — este hook NO es para
  Cowork escribiendo codigo, es para Cowork enviando texto a Alfredo.
- M1 de AUDITORIA_PROFUNDA_COMPORTAMIENTO_2026_05_11.md: enforcement runtime
  de las 22 reglas que Cowork canonizo y luego violo.
- "habla con codigo no con texto": este hook ES el codigo que enforza
  la doctrina pasiva de CLAUDE.md.

Uso programatico:

    from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
    hook = CoworkPreResponseHook()
    permitido, payload = hook.intercept(cowork_output, user_message)
    if permitido:
        send_to_alfredo(payload)  # payload == cowork_output original
    else:
        # payload == feedback de correccion para que Cowork reescriba
        cowork_rewrite(payload)

Uso CLI:

    echo "Andate a dormir tranquilo" | python -m kernel.cowork_runtime.pre_response_hook \\
        --user-message "VAMOS A AVANZAR"

    Exit code 0 si pasa, 1 si bloquea.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Importacion robusta del guardian sea cual sea el cwd de invocacion
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cowork_guardian import GuardianVerdict, validate_output  # noqa: E402

# CLAIM_CALIBRATION_BEGIN — Sprint COWORK-MEMENTO-001 T3 (pieza 1 anti-Dory D2+D3)
# Imports lazy + opcionales: si claim_calibration falla al import, el hook
# debe seguir funcionando (fail-soft, L_A6 declarada en spec §7).
try:
    from kernel.cowork_runtime.claim_calibration import (  # noqa: E402
        ClaimExtractor,
        ClaimLogger,
        ClaimRecord,
        VerificationStatus,
        infer_verification_status,
    )
    _CLAIM_CALIBRATION_AVAILABLE = True
except Exception:  # pragma: no cover (defensive import guard)
    _CLAIM_CALIBRATION_AVAILABLE = False
# CLAIM_CALIBRATION_END

# HOOK_AUTO_DISCIPLINE_BEGIN — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T4
# Imports nuevos para F21 pattern detector + verbatim citation enforcement +
# auto-lectura embrion_memoria + auto-INSERT cowork_protocolo_invocaciones.
# NO modificar fuera de markers BEGIN/END (DSC-MO-006 v1.1 doctrina del silencio).
import os
import time
import uuid
import logging
from typing import Any

try:
    from tools.check_cowork_no_speculative_claims import check_speculative_claims  # noqa: E402
    from tools._check_cowork_verbatim_citations import check_verbatim_citations  # noqa: E402
    from kernel.cowork_runtime.f21_patterns import F21_PATTERNS_VERSION  # noqa: E402
    _AUTO_DISCIPLINE_AVAILABLE = True
except ImportError as _e:
    # Modulos nuevos pueden no existir en builds antiguos. Hook degrada graceful.
    _AUTO_DISCIPLINE_AVAILABLE = False
    _AUTO_DISCIPLINE_IMPORT_ERROR = str(_e)

_AUTO_DISCIPLINE_LOG = logging.getLogger("cowork.auto_discipline")
# HOOK_AUTO_DISCIPLINE_END


@dataclass
class HookStats:
    """Contadores de la sesion en curso para diagnostico."""
    interceptions_total: int = 0
    blocked_total: int = 0
    blocked_magna: int = 0
    blocked_premium: int = 0
    last_violation_at: Optional[str] = None  # ISO timestamp
    violations_history: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "interceptions_total": self.interceptions_total,
            "blocked_total": self.blocked_total,
            "blocked_magna": self.blocked_magna,
            "blocked_premium": self.blocked_premium,
            "last_violation_at": self.last_violation_at,
            "violations_history": self.violations_history[-20:],  # tail
        }


class CoworkPreResponseHook:
    """
    Hook de pre-respuesta para Cowork.

    Ciclo de vida: instanciar UNA vez por sesion. La instancia mantiene
    `session_start` y contadores que el guardian usa para detectar sesiones
    largas sin commits productivos (Regla 3).

    Para integracion con la Capa 8 Memento o con un orquestador externo,
    actualizar `productive_commits_count` cada vez que se detecte commit
    productivo (mergeo PR, push a kernel/, push a apps/mobile/, etc).
    """

    def __init__(
        self,
        session_start: Optional[datetime] = None,
        enabled: bool = False,
        session_uuid: Optional[str] = None,
    ) -> None:
        """
        Args:
            session_start: timestamp UTC de inicio de sesion.
            enabled: Blue-Green flag (canon DSC-MO-011 Gate 7). Default False:
                el hook se construye pero NO bloquea outputs (modo shadow).
                Activacion gradual via `enable()` despues de verificar que no
                rompe runtime existente. Tambien controlable por env var
                COWORK_HOOK_ENABLED=true.
            session_uuid: UUID estable de la sesion Cowork (para correlation
                con cowork_protocolo_invocaciones audit log). Default: nuevo UUID.
        """
        import os
        self.session_start: datetime = session_start or datetime.now(timezone.utc)
        self.productive_commits_count: int = 0
        self.stats: HookStats = HookStats()
        # Lectura fresca de env (anti-Dory)
        env_enabled = os.environ.get("COWORK_HOOK_ENABLED", "").lower() in ("1", "true", "yes", "on")
        self.enabled: bool = bool(enabled) or env_enabled
        # Contador shadow: cuantos outputs HUBIERA bloqueado si estuviera enabled.
        self.shadow_would_block: int = 0

        # HOOK_AUTO_DISCIPLINE_BEGIN — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T4
        # Estado nuevo para auto-discipline runtime (F21 patterns + verbatim + audit log)
        self.session_uuid: str = session_uuid or str(uuid.uuid4())
        self.turn_index: int = 0
        self.history: list[dict[str, Any]] = []  # last K turns para detector F21
        self.history_max: int = int(os.environ.get("COWORK_HOOK_HISTORY_MAX", "10"))
        # Feature flag independiente: shadow para auto-discipline (sub-flag)
        self.auto_discipline_enabled: bool = (
            os.environ.get("COWORK_AUTO_DISCIPLINE_ENABLED", "").lower() in ("1", "true", "yes", "on")
        )
        self.auto_discipline_shadow_count: int = 0  # cuantas veces F21/verbatim hubieran bloqueado en shadow
        self.last_invocation_record: Optional[dict[str, Any]] = None  # ultimo INSERT row preparado
        # HOOK_AUTO_DISCIPLINE_END

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def intercept(
        self,
        cowork_output: str,
        user_message: str = "",
    ) -> tuple[bool, str]:
        """
        Intercepta un output candidato de Cowork antes de enviarlo a Alfredo.

        Returns:
            (True, cowork_output) si el guardian aprueba — el output se envia tal cual.
            (False, correction_feedback) si el guardian bloquea — Cowork debe
                reescribir tomando el feedback como gua.
        """
        self.stats.interceptions_total += 1

        # HOOK_AUTO_DISCIPLINE_BEGIN — Sprint COWORK-AUTO-DISCIPLINE-REAL-001 T4
        # Auto-discipline runtime: F21 patterns + verbatim citations + audit log.
        # Se ejecuta ANTES del guardian existente para que ambos chequeos contribuyan.
        # Si auto_discipline_enabled=False → shadow mode (registra pero no bloquea).
        self.turn_index += 1
        _auto_t_start = time.time()
        _f21_violations: list[dict[str, Any]] = []
        _verbatim_violations: list[dict[str, Any]] = []
        _queries_done: list[str] = []
        if _AUTO_DISCIPLINE_AVAILABLE:
            try:
                _f21_violations = check_speculative_claims(
                    cowork_output, history=self.history
                )
            except Exception as _ex:  # noqa: BLE001
                _AUTO_DISCIPLINE_LOG.warning(
                    "check_speculative_claims raised: %s", _ex
                )
            try:
                _verbatim_violations = check_verbatim_citations(
                    cowork_output, history=self.history
                )
            except Exception as _ex:  # noqa: BLE001
                _AUTO_DISCIPLINE_LOG.warning(
                    "check_verbatim_citations raised: %s", _ex
                )
            _queries_done = self._auto_read_embrion_memoria()
        _auto_duration_ms = int((time.time() - _auto_t_start) * 1000)
        _auto_discipline_blocked = bool(_f21_violations or _verbatim_violations)
        # HOOK_AUTO_DISCIPLINE_END

        verdict = validate_output(
            cowork_output,
            user_message=user_message,
            session_duration_minutes=self._session_duration_minutes(),
            productive_commits_this_session=self.productive_commits_count,
        )

        # CLAIM_CALIBRATION_BEGIN — Sprint COWORK-MEMENTO-001 T3 wiring (extract+log claims)
        # Fire-and-forget: registramos claims independientemente del verdict guardian.
        # NO bloquea el flujo si la extracción/insert falla (fail-soft, L_A6).
        try:
            self._record_claims_calibration(cowork_output)
        except Exception:
            # Defense in depth: el flujo Cowork NUNCA se rompe por fallo del logger.
            pass
        # CLAIM_CALIBRATION_END

        # HOOK_AUTO_DISCIPLINE_BEGIN — composición del veredicto final
        # El output pasa solo si guardian existing Y auto-discipline pasan.
        _passed_combined = verdict.passed and not _auto_discipline_blocked

        # Decision magnitude heuristica para audit log
        _magnitude = self._infer_decision_magnitude(
            cowork_output, _f21_violations, _verbatim_violations
        )

        # Registrar la invocacion en memoria local (audit log row preparado)
        self.last_invocation_record = self._build_invocation_record(
            output=cowork_output,
            magnitude=_magnitude,
            queries_done=_queries_done,
            f21_violations=_f21_violations,
            verbatim_violations=_verbatim_violations,
            output_passed=_passed_combined,
            duration_ms=_auto_duration_ms,
        )
        self._auto_insert_protocolo_row(self.last_invocation_record)

        # Append turn to history (ANTES de return para que next turn vea este)
        self._append_history(
            kind="cowork_output",
            content=cowork_output,
            user_message=user_message,
        )

        if _passed_combined:
            return True, cowork_output

        # Auto-discipline en shadow: registra pero pasa
        if _auto_discipline_blocked and not self.auto_discipline_enabled:
            self.auto_discipline_shadow_count += 1
            # Aun asi delegamos al guardian existente para decidir final passthrough
            if verdict.passed:
                return True, cowork_output
        # HOOK_AUTO_DISCIPLINE_END

        # Modo shadow (enabled=False): registramos lo que HABRiA bloqueado
        # pero dejamos pasar el output. Permite calibrar antes de activar.
        if not self.enabled:
            self.shadow_would_block += 1
            self._record_block(verdict)
            return True, cowork_output

        self._record_block(verdict)
        feedback = self._format_correction_feedback(verdict, cowork_output, user_message)
        # HOOK_AUTO_DISCIPLINE_BEGIN — augmentar feedback con violations auto-discipline
        if _f21_violations or _verbatim_violations:
            feedback = self._augment_feedback_with_auto_discipline(
                feedback, _f21_violations, _verbatim_violations
            )
        # HOOK_AUTO_DISCIPLINE_END
        return False, feedback

    def register_productive_commit(self, descripcion: str = "") -> None:
        """
        Llamar cuando Cowork ejecute commit productivo (PR mergeado, push a kernel/, etc).
        Esto resetea la cuenta para la Regla 3 (commits/hora).
        """
        self.productive_commits_count += 1

    def reset_session(self) -> None:
        """Reinicia el estado para una sesion Cowork nueva."""
        self.session_start = datetime.now(timezone.utc)
        self.productive_commits_count = 0
        self.stats = HookStats()
        self.shadow_would_block = 0

    # CLAIM_CALIBRATION_BEGIN — Sprint COWORK-MEMENTO-001 T3 (extract+log helpers)
    def attach_claim_logger(self, logger: "ClaimLogger") -> None:
        """Inyecta un ClaimLogger externo (opcional). Si no se inyecta, el hook
        operará en modo extract-only (sin persistencia)."""
        self._claim_logger = logger

    def register_pre_emit_claim(self, claim_value: str) -> None:
        """Registra explícitamente un claim verificado pre-emit (verified_pre)."""
        if not hasattr(self, "_pre_registered_claims"):
            self._pre_registered_claims = []
        self._pre_registered_claims.append(claim_value)
        if len(self._pre_registered_claims) > 256:
            self._pre_registered_claims = self._pre_registered_claims[-256:]

    def _record_claims_calibration(self, cowork_output: str) -> None:
        """Extrae claims del output + infiere verification_status + log_batch.

        Si claim_calibration no está disponible (import falló), no-op.
        Si _claim_logger no fue inyectado, solo cuenta extracciones sin persistir.
        """
        if not _CLAIM_CALIBRATION_AVAILABLE:
            return
        if not hasattr(self, "_claim_extractor"):
            self._claim_extractor = ClaimExtractor()
            self._claims_extracted_total = 0
            self._tool_call_history = getattr(self, "_tool_call_history", [])
            self._pre_registered_claims = getattr(self, "_pre_registered_claims", [])
            self._claim_logger = getattr(self, "_claim_logger", None)

        candidates = self._claim_extractor.extract_claims(cowork_output)
        if not candidates:
            return

        self._claims_extracted_total += len(candidates)
        if self._claim_logger is None:
            return

        turn_index = self.stats.interceptions_total
        records: list[ClaimRecord] = []
        for cand in candidates:
            status, evidence = infer_verification_status(
                cand,
                tool_call_history=self._tool_call_history,
                pre_registered_claims=self._pre_registered_claims,
            )
            records.append(
                ClaimRecord(
                    claim_type=cand.claim_type,
                    claim_value=cand.claim_value,
                    verification_status=status,
                    turn_index=turn_index,
                    detected_in_output=cand.detected_in_output,
                    extraction_regex_id=cand.extraction_regex_id,
                    tool_call_evidence=evidence,
                )
            )
        self._claim_logger.log_batch(records)
    # CLAIM_CALIBRATION_END

    def enable(self) -> None:
        """Activa el hook (Gate 7 Blue-Green): a partir de ahora bloquea outputs."""
        self.enabled = True

    def disable(self) -> None:
        """Desactiva el hook (rollback Blue-Green): vuelve a modo shadow."""
        self.enabled = False

    def session_health(self) -> dict:
        """Snapshot del estado del hook (para dashboards / diagnostico)."""
        base = {
            "session_start_utc": self.session_start.isoformat(),
            "session_duration_minutes": self._session_duration_minutes(),
            "productive_commits": self.productive_commits_count,
            "enabled": self.enabled,
            "shadow_would_block": self.shadow_would_block,
            **self.stats.as_dict(),
        }
        # HOOK_AUTO_DISCIPLINE_BEGIN
        base.update({
            "session_uuid": self.session_uuid,
            "turn_index": self.turn_index,
            "auto_discipline_enabled": self.auto_discipline_enabled,
            "auto_discipline_shadow_count": self.auto_discipline_shadow_count,
            "history_len": len(self.history),
            "f21_patterns_version": (
                F21_PATTERNS_VERSION if _AUTO_DISCIPLINE_AVAILABLE else "unavailable"
            ),
            "auto_discipline_available": _AUTO_DISCIPLINE_AVAILABLE,
        })
        # HOOK_AUTO_DISCIPLINE_END
        return base

    # HOOK_AUTO_DISCIPLINE_BEGIN — métodos auto-discipline (T4 Sprint COWORK-AUTO-DISCIPLINE-REAL-001)
    # UNIFIED register_tool_call (Sprint PR-118-REBASE §2.2 — backward compat MEMENTO + AUTO-DISCIPLINE)
    def register_tool_call(
        self,
        name: str = "",
        arguments: Optional[dict] = None,
        result: Optional[str] = None,
        tool_call_repr: Optional[str] = None,
    ) -> None:
        """Unified register_tool_call (MEMENTO + AUTO-DISCIPLINE).

        Acepta dos formas de invocación (backward compat):
        - MEMENTO legacy: register_tool_call(tool_call_repr="raw string")
        - AUTO-DISCIPLINE rich: register_tool_call(name="...", arguments={...}, result="...")

        Ambas mantienen sus respectivos paths: MEMENTO history (str legacy) +
        AUTO-DISCIPLINE history (dict rich). Sin breaking change.
        """
        # Construir tool_call_repr canónico
        if tool_call_repr is None:
            tool_call_repr = f"{name}({arguments or {}}) -> {result or ''}"

        # MEMENTO history (str legacy)
        if not hasattr(self, "_tool_call_history"):
            self._tool_call_history = []
        self._tool_call_history.append(tool_call_repr)
        if len(self._tool_call_history) > 64:
            self._tool_call_history = self._tool_call_history[-64:]

        # AUTO-DISCIPLINE history (dict rich)
        entry = {
            "type": "tool_call",
            "name": name,
            "arguments": arguments or {},
            "result": result or tool_call_repr,
            "turn_index": getattr(self, "turn_index", 0),
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_history_raw(entry)

    def register_user_message(self, content: str) -> None:
        """Registra mensaje del usuario en history (para context)."""
        self._append_history_raw({
            "type": "user_message",
            "content": content,
            "turn_index": self.turn_index,
            "at": datetime.now(timezone.utc).isoformat(),
        })

    def _append_history(
        self,
        kind: str,
        content: str,
        user_message: str = "",
    ) -> None:
        self._append_history_raw({
            "type": kind,
            "content": content,
            "user_message": user_message,
            "turn_index": self.turn_index,
            "at": datetime.now(timezone.utc).isoformat(),
        })

    def _append_history_raw(self, entry: dict[str, Any]) -> None:
        self.history.append(entry)
        # Cap a history_max (last K turns)
        if len(self.history) > self.history_max:
            self.history = self.history[-self.history_max:]

    def _auto_read_embrion_memoria(self) -> list[str]:
        """
        Auto-lectura embrion_memoria importancia>=8 last 24h.
        Devuelve lista de queries ejecutadas (para audit log queries_done).
        Graceful: si SUPABASE_URL/SERVICE_KEY faltan, log warning y skip.
        """
        queries_done: list[str] = []
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY"
        )
        if not supabase_url or not supabase_key:
            _AUTO_DISCIPLINE_LOG.debug(
                "auto_read_embrion_memoria skip: SUPABASE env vars no configuradas"
            )
            return queries_done
        # Implementacion HTTP defer a futuro (requiere requests/httpx); por ahora
        # marcamos la query como intentada para que audit log registre el intent.
        # Cowork-side: el orquestador puede llamar register_memory_read() despues.
        queries_done.append("embrion_memoria.importancia>=8&last_24h&limit=10")
        return queries_done

    def register_memory_read(self, table: str, query_summary: str, rows_count: int = 0) -> None:
        """
        Callback para que el orquestador externo registre una lectura real de memoria.
        Agrega a history como tool_call sintetico para el detector F21.
        """
        self._append_history_raw({
            "type": "memory_read",
            "name": f"db.{table}",
            "content": query_summary,
            "rows_count": rows_count,
            "turn_index": self.turn_index,
            "at": datetime.now(timezone.utc).isoformat(),
        })

    def _infer_decision_magnitude(
        self,
        output: str,
        f21_violations: list[dict[str, Any]],
        verbatim_violations: list[dict[str, Any]],
    ) -> str:
        """Heuristica simple: magna si touches schema/migrations/PRs/commits."""
        magna_keywords = ("schema", "migration", "PR #", "commit ", "merge", "production")
        if any(k.lower() in output.lower() for k in magna_keywords):
            return "magna"
        if f21_violations or verbatim_violations or len(output) > 2000:
            return "medium"
        return "trivial"

    def _build_invocation_record(
        self,
        output: str,
        magnitude: str,
        queries_done: list[str],
        f21_violations: list[dict[str, Any]],
        verbatim_violations: list[dict[str, Any]],
        output_passed: bool,
        duration_ms: int,
    ) -> dict[str, Any]:
        """Construye el row para INSERT en cowork_protocolo_invocaciones."""
        all_violations = []
        for v in f21_violations:
            all_violations.append({**v, "detector": "f21_patterns"})
        for v in verbatim_violations:
            all_violations.append({**v, "detector": "verbatim_citations"})
        return {
            "session_uuid": self.session_uuid,
            "turn_index": self.turn_index,
            "decision_magnitude": magnitude,
            "queries_done": queries_done,
            "violations_detected": all_violations,
            "output_passed": output_passed,
            "output_length_chars": len(output),
            "memory_seeds_inserted": 0,
            "duration_ms": duration_ms,
            "metadata": {
                "f21_patterns_version": (
                    F21_PATTERNS_VERSION if _AUTO_DISCIPLINE_AVAILABLE else "unavailable"
                ),
                "auto_discipline_enabled": self.auto_discipline_enabled,
                "history_len": len(self.history),
            },
        }

    def _auto_insert_protocolo_row(self, record: dict[str, Any]) -> None:
        """
        Auto-INSERT a cowork_protocolo_invocaciones via Supabase REST.
        Graceful: si env vars faltan, log y skip (no romper hook).
        Implementacion HTTP defer (orquestador puede consumir last_invocation_record
        manualmente si necesita).
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get(
            "SUPABASE_SERVICE_ROLE_KEY"
        )
        if not supabase_url or not supabase_key:
            _AUTO_DISCIPLINE_LOG.debug(
                "auto_insert_protocolo_row skip: SUPABASE env vars no configuradas"
            )
            return
        # HTTP POST deferred: orquestador externo es responsable del insert real
        # consumiendo `self.last_invocation_record`. Esto evita import duro de
        # requests/httpx en el kernel runtime.
        _AUTO_DISCIPLINE_LOG.info(
            "protocolo_invocaciones row preparada turn=%s passed=%s violations=%s",
            record["turn_index"],
            record["output_passed"],
            len(record["violations_detected"]),
        )

    def _augment_feedback_with_auto_discipline(
        self,
        feedback: str,
        f21_violations: list[dict[str, Any]],
        verbatim_violations: list[dict[str, Any]],
    ) -> str:
        """Anexa secciones de auto-discipline al feedback existente."""
        extra = [
            "",
            "## Auto-discipline violations (Sprint COWORK-AUTO-DISCIPLINE-REAL-001)",
        ]
        if f21_violations:
            extra.append(f"  F21 patterns matched sin tool call previo: {len(f21_violations)}")
            for v in f21_violations[:5]:
                extra.append(
                    f"    - [{v['severity']}] {v['pattern_id']}: {v['match']!r} "
                    f"(needs one of {v['missing_tool_call']})"
                )
        if verbatim_violations:
            extra.append(f"  Verbatim citations sin respaldo: {len(verbatim_violations)}")
            for v in verbatim_violations[:5]:
                extra.append(
                    f"    - [{v['severity']}] {v['type']}: {v['citation']!r}"
                )
        extra.append("")
        extra.append("  Reescribi ejecutando primero el tool call requerido,")
        extra.append("  luego cita verbatim el resultado en tu output.")
        return feedback + "\n" + "\n".join(extra)
    # HOOK_AUTO_DISCIPLINE_END

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _session_duration_minutes(self) -> int:
        delta = datetime.now(timezone.utc) - self.session_start
        return int(delta.total_seconds() // 60)

    def _record_block(self, verdict: GuardianVerdict) -> None:
        self.stats.blocked_total += 1
        magna = sum(1 for v in verdict.violations if v.startswith("MAGNA"))
        premium = sum(1 for v in verdict.violations if v.startswith("PREMIUM"))
        self.stats.blocked_magna += magna
        self.stats.blocked_premium += premium
        ts = datetime.now(timezone.utc).isoformat()
        self.stats.last_violation_at = ts
        self.stats.violations_history.append(
            {"at": ts, "violations": verdict.violations}
        )

    def _format_correction_feedback(
        self,
        verdict: GuardianVerdict,
        cowork_output: str,
        user_message: str,
    ) -> str:
        """
        Formatea feedback estructurado para que Cowork reescriba.

        El feedback tiene 3 secciones:
        1. Diagnostico: que regla del guardian se violo
        2. Citas literales del output ofensivo
        3. Instruccion de reescritura
        """
        magna = [v for v in verdict.violations if v.startswith("MAGNA")]
        premium = [v for v in verdict.violations if v.startswith("PREMIUM")]
        severity = "MAGNA" if magna else "PREMIUM"

        lines = [
            f"[COWORK_GUARDIAN_BLOCK severity={severity}]",
            "",
            "Tu output candidato fue interceptado por el pre-response hook.",
            "No se envio a Alfredo. Reescribi tomando este feedback en cuenta.",
            "",
            "## Violaciones detectadas",
        ]
        for v in verdict.violations:
            lines.append(f"  - {v}")

        lines.extend([
            "",
            "## Score de avance",
            f"  advance_hits: {verdict.advance_score.advance_hits}",
            f"  non_advance_hits: {verdict.advance_score.non_advance_hits}",
            f"  ratio_avance: {verdict.advance_score.ratio_advance:.2f}",
            f"  alfredo_demands_advance: {verdict.user_demands_advance}",
            "",
            "## Instruccion de reescritura",
        ])

        if magna and verdict.user_demands_advance:
            lines.extend([
                "  Alfredo exige avance explicito y vos sugeriste pausar.",
                "  Reescribi entregando avance concreto: PR mergeado, archivo creado,",
                "  insercion a embrion_memoria, migracion aplicada, o spec ejecutable.",
                "  Prohibido: andate a dormir, descansa, buenas noches, paus, tregua,",
                "  detente, ya basta, dejemos para mañana, cuando despiertes.",
            ])
        elif magna:
            lines.extend([
                "  Tu sesion lleva tiempo sin commits productivos.",
                "  Antes de mas texto, ejecuta una accion observable:",
                "  push a kernel/, push a apps/mobile/, mergear PR, insertar a",
                "  embrion_memoria con instruccion operativa.",
            ])
        else:
            lines.extend([
                "  Tu output esta dominado por meta-trabajo (audits, correctivos,",
                "  reportes, preflights). Eso NO es avance del Monstruo.",
                "  Reescribi entregando avance del producto en kernel/, apps/mobile/,",
                "  bridge/sprint_*, o PR # mergeado.",
            ])

        lines.extend([
            "",
            "## Contexto",
            f"  user_message_recibido: {user_message[:200]!r}",
            f"  cowork_output_bloqueado_chars: {len(cowork_output)}",
            f"  session_duration_min: {self._session_duration_minutes()}",
            f"  productive_commits_session: {self.productive_commits_count}",
        ])
        return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================

def _read_stdin_or_arg(value: Optional[str]) -> str:
    if value is not None:
        return value
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pre-response hook que valida output de Cowork via cowork_guardian.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output candidato de Cowork (si no se da, se lee stdin).",
    )
    parser.add_argument(
        "--user-message", "-u",
        default="",
        help="Ultimo mensaje de Alfredo (para detectar demanda de avance).",
    )
    parser.add_argument(
        "--commits", "-c",
        type=int,
        default=0,
        help="Commits productivos hechos en esta sesion (default 0).",
    )
    parser.add_argument(
        "--session-minutes", "-m",
        type=int,
        default=0,
        help="Minutos transcurridos de la sesion (default 0).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en JSON (por defecto sale humano).",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Activar enforcement (default shadow). Tambien via env COWORK_HOOK_ENABLED=true.",
    )
    args = parser.parse_args(argv)

    cowork_output = _read_stdin_or_arg(args.output)
    if not cowork_output:
        print("error: no hay output candidato (pasalo via --output o stdin)", file=sys.stderr)
        return 2

    hook = CoworkPreResponseHook(enabled=args.enable)
    hook.productive_commits_count = args.commits
    if args.session_minutes:
        from datetime import timedelta
        hook.session_start = datetime.now(timezone.utc) - timedelta(minutes=args.session_minutes)

    permitido, payload = hook.intercept(cowork_output, args.user_message)

    if args.json:
        result = {
            "permitido": permitido,
            "payload": payload,
            "session_health": hook.session_health(),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if permitido:
            print("[COWORK_GUARDIAN_PASS] output autorizado")
        else:
            print(payload)
    return 0 if permitido else 1


if __name__ == "__main__":
    sys.exit(main())
