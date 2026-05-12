"""
tests/test_t1_convergencia_7_sabios.py — Tests del delta convergencia 7 Sabios
(2026-05-12) aplicado al PR #110.

Cubre A-E del bridge cowork_to_perplexity_T2B_UPDATE_PR_110_CONVERGENCIA_7_SABIOS:

  A. 9 etiquetas epistemicas granulares (con compat 4 legacy)
  B. System prompt override forzoso "PROHIBIDO afirmar sin tool_call"
  C. Telemetria claim-level JSONL (evento claim_telemetry por claim)
  D. Metrica T3 binaria tool_call_present
  E. ENFORCE requiere >=50 claims + >=80% precision + 0 FP P2 + auditor T1
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.epistemic_labels import (
    EpistemicLabel,
    LABEL_REGEX,
    LEGACY_TO_MODERN,
    LICENSED_LABELS,
    UNLICENSED_LABELS,
    VALID_LABELS_9,
    extract_label,
    is_licensed,
    is_unlicensed,
    label_help_block,
    normalize_label,
    requires_tool_call,
)
from kernel.cowork_runtime.cowork_system_prompt_override import (
    OVERRIDE_SENTINEL,
    SYSTEM_PROMPT_OVERRIDE,
    append_to_system_prompt,
    get_system_prompt_override,
    is_override_present,
)
from kernel.cowork_runtime.t1_audit_log import (
    ClaimTelemetry,
    T1AuditLog,
)
from kernel.cowork_runtime.t1_config import (
    ENV_ALLOW_ENFORCE,
    MAX_FALSE_POSITIVES_P2_FOR_ENFORCE,
    MIN_AUDITED_CLAIMS_FOR_ENFORCE,
    MIN_PRECISION_FOR_ENFORCE,
    T1Config,
    T1Mode,
)
from kernel.cowork_runtime.t1_output_contract import analyze
from kernel.cowork_runtime.tool_call_audit import (
    EVIDENCE_TOOLS,
    ToolCallContext,
    evaluate_claim_tool_call,
)
from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook


# ============================================================================
# A. 9 etiquetas epistemicas granulares
# ============================================================================


class TestNueveEtiquetasEpistemicas:

    def test_existen_exactamente_9_etiquetas_modernas(self):
        assert len(VALID_LABELS_9) == 9
        # Los nombres canonicos
        assert set(VALID_LABELS_9) == {
            "VERIFIED_CURRENT_TURN",
            "VERIFIED_RECENT_LT_60M",
            "SESSION_MEMORY_ONLY",
            "INFERRED",
            "USER_PROVIDED",
            "NEEDS_SQL",
            "NEEDS_READ",
            "CONTRADICTED_BY_EXTERNAL",
            "UNVERIFIED_DO_NOT_ASSERT",
        }

    def test_enum_es_consistente_con_lista(self):
        # Cada EpistemicLabel.value debe estar en VALID_LABELS_9
        for label in EpistemicLabel:
            assert label.value in VALID_LABELS_9

    def test_etiquetas_licenciadas_y_no_licenciadas(self):
        assert EpistemicLabel.VERIFIED_CURRENT_TURN.value in LICENSED_LABELS
        assert EpistemicLabel.VERIFIED_RECENT_LT_60M.value in LICENSED_LABELS
        assert EpistemicLabel.USER_PROVIDED.value in LICENSED_LABELS

        assert EpistemicLabel.UNVERIFIED_DO_NOT_ASSERT.value in UNLICENSED_LABELS
        assert EpistemicLabel.NEEDS_SQL.value in UNLICENSED_LABELS
        assert EpistemicLabel.NEEDS_READ.value in UNLICENSED_LABELS
        assert EpistemicLabel.SESSION_MEMORY_ONLY.value in UNLICENSED_LABELS
        assert EpistemicLabel.CONTRADICTED_BY_EXTERNAL.value in UNLICENSED_LABELS

    def test_is_licensed_helpers(self):
        assert is_licensed("VERIFIED_CURRENT_TURN") is True
        assert is_licensed("USER_PROVIDED") is True
        assert is_licensed("UNVERIFIED_DO_NOT_ASSERT") is False
        assert is_licensed(None) is False

    def test_is_unlicensed_helpers(self):
        assert is_unlicensed("UNVERIFIED_DO_NOT_ASSERT") is True
        assert is_unlicensed("NEEDS_SQL") is True
        assert is_unlicensed("VERIFIED_CURRENT_TURN") is False
        assert is_unlicensed(None) is False

    def test_requires_tool_call(self):
        assert requires_tool_call("NEEDS_SQL") is True
        assert requires_tool_call("NEEDS_READ") is True
        assert requires_tool_call("VERIFIED_CURRENT_TURN") is False
        assert requires_tool_call(None) is False

    def test_extract_label_moderna_compacta(self):
        sentence = "El kernel esta vivo [VERIFIED_CURRENT_TURN]."
        has, raw, normalized = extract_label(sentence)
        assert has is True
        assert normalized == "VERIFIED_CURRENT_TURN"

    def test_extract_label_moderna_con_fuente(self):
        sentence = (
            "El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=mcp__railway "
            "ts=2026-05-12]."
        )
        has, raw, normalized = extract_label(sentence)
        assert has is True
        assert normalized == "VERIFIED_CURRENT_TURN"

    def test_extract_label_legacy_verificado_se_normaliza(self):
        sentence = "El kernel esta vivo [VERIFICADO mcp__railway 2026-05-12]."
        has, raw, normalized = extract_label(sentence)
        assert has is True
        # Compat: legacy VERIFICADO mapea a VERIFIED_CURRENT_TURN
        assert normalized == "VERIFIED_CURRENT_TURN"

    def test_extract_label_legacy_no_verificado(self):
        sentence = "Manus pusheo 6 PRs [NO VERIFICADO]."
        has, raw, normalized = extract_label(sentence)
        assert has is True
        assert normalized == "UNVERIFIED_DO_NOT_ASSERT"

    def test_extract_label_legacy_requiere_read_sql(self):
        sentence = "Hay 64 DSCs [REQUIERE READ/SQL]."
        has, raw, normalized = extract_label(sentence)
        assert has is True
        assert normalized == "NEEDS_READ"

    def test_extract_label_sin_etiqueta(self):
        sentence = "El kernel esta vivo en Railway."
        has, raw, normalized = extract_label(sentence)
        assert has is False
        assert normalized is None

    def test_normalize_label_aliases(self):
        assert normalize_label("VERIFIED_RECENT_LT_60M") == "VERIFIED_RECENT_LT_60M"
        assert normalize_label("verified_current_turn fuente=x") == "VERIFIED_CURRENT_TURN"
        assert normalize_label("verificado mcp 2026") == "VERIFIED_CURRENT_TURN"
        assert normalize_label("totalmente_inventado") is None
        assert normalize_label("") is None

    def test_label_help_block_lista_9(self):
        text = label_help_block()
        for label in VALID_LABELS_9:
            assert label in text

    def test_analyze_detecta_etiquetas_modernas(self):
        text = (
            "El kernel esta vivo [VERIFIED_CURRENT_TURN]. "
            "Manus pusheo PRs [SESSION_MEMORY_ONLY]. "
            "Sugiero priorizar T1 [INFERRED]."
        )
        report = analyze(text)
        # Las 3 oraciones tienen etiqueta moderna
        tagged = [c for c in report.claims if c.has_tag]
        assert len(tagged) == 3
        labels = {c.normalized_label for c in tagged}
        assert labels == {"VERIFIED_CURRENT_TURN", "SESSION_MEMORY_ONLY", "INFERRED"}

    def test_analyze_mixto_legacy_y_moderno(self):
        text = (
            "El kernel esta vivo [VERIFICADO mcp 2026]. "
            "Hay 64 DSCs [NEEDS_READ memory/cowork]."
        )
        report = analyze(text)
        tagged_labels = {c.normalized_label for c in report.claims if c.has_tag}
        # Legacy se normaliza a VERIFIED_CURRENT_TURN; moderno NEEDS_READ pasa
        assert tagged_labels == {"VERIFIED_CURRENT_TURN", "NEEDS_READ"}


# ============================================================================
# B. System prompt override forzoso
# ============================================================================


class TestSystemPromptOverride:

    def test_override_contiene_prohibido_afirmar_sin_tool_call(self):
        prompt = get_system_prompt_override()
        assert "PROHIBIDO afirmar sin tool_call." in prompt

    def test_override_lista_las_9_etiquetas(self):
        prompt = get_system_prompt_override()
        for label in VALID_LABELS_9:
            assert label in prompt

    def test_sentinela_es_detectable(self):
        prompt = get_system_prompt_override()
        assert is_override_present(prompt) is True
        assert is_override_present("Un system prompt cualquiera sin override.") is False
        assert is_override_present("") is False
        assert is_override_present(None) is False

    def test_append_a_prompt_existente_preserva(self):
        base = "Eres un agente Cowork con instrucciones previas."
        combined = append_to_system_prompt(base)
        assert base in combined
        assert is_override_present(combined) is True

    def test_append_a_prompt_vacio_devuelve_override(self):
        combined = append_to_system_prompt("")
        assert combined == get_system_prompt_override()

    def test_override_menciona_humildad_factual(self):
        prompt = get_system_prompt_override()
        assert "humildad factual" in prompt.lower()

    def test_override_exige_etiqueta_por_afirmacion_fuerte(self):
        prompt = get_system_prompt_override()
        assert "9 etiquetas epistemicas" in prompt

    def test_sentinela_canonica(self):
        assert OVERRIDE_SENTINEL in SYSTEM_PROMPT_OVERRIDE


# ============================================================================
# C. Telemetria claim-level en JSONL
# ============================================================================


class TestTelemetriaClaimLevel:

    def _log(self, tmp_path) -> T1AuditLog:
        return T1AuditLog(path=tmp_path / "claim_telemetry.jsonl")

    def test_record_interception_genera_evento_por_claim(self, tmp_path):
        log = self._log(tmp_path)
        text = (
            "El kernel esta vivo. PR #99 fue mergeado a main. "
            "Sugiero avanzar con T1."
        )
        report = analyze(text)
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output=text,
            report=report,
            blocked=False,
            would_block=True,
        )
        telemetries = list(log.iter_claim_telemetry())
        # Hay tantas entradas claim_telemetry como claims
        assert len(telemetries) == len(report.claims)
        assert len(telemetries) >= 2

    def test_claim_telemetry_tiene_campos_canonicos(self, tmp_path):
        log = self._log(tmp_path)
        report = analyze("El kernel esta vivo en Railway hoy.")
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="El kernel esta vivo en Railway hoy.",
            report=report,
            blocked=False,
            would_block=True,
        )
        t = next(log.iter_claim_telemetry())
        assert t["event"] == "claim_telemetry"
        assert "claim_id" in t
        assert "claim_text" in t
        assert "severity" in t
        assert "epistemic_label" in t  # puede ser None si no hay tag
        assert "license_validated" in t
        assert "license_required" in t
        assert "tool_call_present_this_turn" in t
        assert "action_taken" in t
        assert t["action_taken"] in ("would_block", "would_degrade", "would_pass")

    def test_claim_p2_telemetry_action_es_would_pass(self, tmp_path):
        log = self._log(tmp_path)
        report = analyze("Creo que deberiamos avanzar con el merge primero.")
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="Creo que deberiamos avanzar con el merge primero.",
            report=report,
            blocked=False,
            would_block=False,
        )
        telemetries = list(log.iter_claim_telemetry())
        for t in telemetries:
            if t["severity"] == "P2":
                assert t["action_taken"] == "would_pass"

    def test_claim_p0_sin_tag_telemetry_action_es_would_block(self, tmp_path):
        log = self._log(tmp_path)
        report = analyze("El kernel esta vivo en Railway hoy.")
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="El kernel esta vivo en Railway hoy.",
            report=report,
            blocked=False,
            would_block=True,
        )
        telemetries = list(log.iter_claim_telemetry())
        materiales = [t for t in telemetries if t["severity"] in ("P0", "P1") and not t["has_tag"]]
        assert any(t["action_taken"] == "would_block" for t in materiales)

    def test_claim_con_verified_current_turn_y_tool_call_present_es_pass(self, tmp_path):
        log = self._log(tmp_path)
        ctx = ToolCallContext(tool_calls_this_turn=["Read", "Bash"])
        report = analyze(
            "El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=mcp__railway ts=2026-05-12]."
        )
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=mcp__railway ts=2026-05-12].",
            report=report,
            blocked=False,
            would_block=False,
            tool_call_ctx=ctx,
        )
        t = next(log.iter_claim_telemetry())
        assert t["tool_call_present_this_turn"] is True
        assert t["license_validated"] is True
        assert t["action_taken"] == "would_pass"

    def test_claim_pretende_verified_pero_sin_tool_call_degrada(self, tmp_path):
        log = self._log(tmp_path)
        ctx = ToolCallContext(tool_calls_this_turn=[])  # sin tool_call
        report = analyze(
            "El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=mcp__railway]."
        )
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=mcp__railway].",
            report=report,
            blocked=False,
            would_block=False,
            tool_call_ctx=ctx,
        )
        t = next(log.iter_claim_telemetry())
        assert t["tool_call_present_this_turn"] is False
        # Pretende licencia pero no esta ratificada -> would_degrade
        assert t["action_taken"] == "would_degrade"
        assert t["license_required"] == "UNVERIFIED_DO_NOT_ASSERT"

    def test_telemetry_summary(self, tmp_path):
        log = self._log(tmp_path)
        for _ in range(3):
            r = analyze("El kernel esta vivo en Railway hoy.")
            log.record_interception(
                session_id="s",
                mode="observe_only",
                user_message="x",
                cowork_output="El kernel esta vivo en Railway hoy.",
                report=r,
                blocked=False,
                would_block=True,
            )
        s = log.telemetry_summary()
        assert s["total_claims_logged"] >= 3
        assert "by_action" in s
        assert "by_label" in s
        # Sin etiqueta -> NO_LABEL en by_label
        assert "NO_LABEL" in s["by_label"]

    def test_entries_y_telemetry_son_eventos_separados(self, tmp_path):
        log = self._log(tmp_path)
        text = (
            "El kernel esta vivo en Railway hoy. "
            "PR #99 fue mergeado a main en este momento. "
            "Sugiero avanzar con la fase T1 ya mismo."
        )
        r = analyze(text)
        log.record_interception(
            session_id="s",
            mode="observe_only",
            user_message="x",
            cowork_output=text,
            report=r,
            blocked=False,
            would_block=True,
        )
        entries = list(log._iter_entries())
        telemetries = list(log.iter_claim_telemetry())
        # Una sola interception parent
        assert len(entries) == 1
        # N telemetries == numero de claims detectados
        assert len(telemetries) == len(r.claims)
        assert len(telemetries) >= 2
        # stats() solo cuenta interceptions parent
        s = log.stats()
        assert s["total_interceptions"] == 1


# ============================================================================
# D. Metrica T3 binaria tool_call_present
# ============================================================================


class TestT3BinaryMetric:

    def test_tool_call_present_false_si_lista_vacia(self):
        ctx = ToolCallContext()
        assert ctx.tool_call_present is False

    def test_tool_call_present_true_con_evidence_tool(self):
        ctx = ToolCallContext(tool_calls_this_turn=["Read"])
        assert ctx.tool_call_present is True

    def test_tool_call_present_false_si_solo_tools_no_evidence(self):
        ctx = ToolCallContext(tool_calls_this_turn=["TodoWrite", "ExitPlanMode"])
        # Esas no estan en EVIDENCE_TOOLS
        assert ctx.tool_call_present is False

    def test_tool_call_present_mcp_supabase(self):
        ctx = ToolCallContext(tool_calls_this_turn=["mcp__supabase__execute_sql"])
        assert ctx.tool_call_present is True

    def test_tool_call_recent_independiente(self):
        ctx = ToolCallContext(
            tool_calls_this_turn=[],
            tool_calls_last_60_min=["Grep"],
        )
        assert ctx.tool_call_present is False
        assert ctx.tool_call_recent is True

    def test_is_label_legitimate_verified_current_turn_requiere_present(self):
        ctx_yes = ToolCallContext(tool_calls_this_turn=["Read"])
        ctx_no = ToolCallContext(tool_calls_this_turn=[])
        assert ctx_yes.is_label_legitimate("VERIFIED_CURRENT_TURN") is True
        assert ctx_no.is_label_legitimate("VERIFIED_CURRENT_TURN") is False

    def test_is_label_legitimate_verified_recent_requiere_recent(self):
        ctx_yes = ToolCallContext(
            tool_calls_this_turn=[],
            tool_calls_last_60_min=["Grep"],
        )
        ctx_no = ToolCallContext()
        assert ctx_yes.is_label_legitimate("VERIFIED_RECENT_LT_60M") is True
        assert ctx_no.is_label_legitimate("VERIFIED_RECENT_LT_60M") is False

    def test_is_label_legitimate_user_provided_siempre_true(self):
        ctx = ToolCallContext()
        assert ctx.is_label_legitimate("USER_PROVIDED") is True

    def test_is_label_legitimate_unlicensed_siempre_true(self):
        ctx = ToolCallContext()
        for label in (
            "UNVERIFIED_DO_NOT_ASSERT",
            "NEEDS_SQL",
            "NEEDS_READ",
            "SESSION_MEMORY_ONLY",
            "INFERRED",
            "CONTRADICTED_BY_EXTERNAL",
        ):
            assert ctx.is_label_legitimate(label) is True

    def test_evaluate_claim_sin_etiqueta_con_tool_call(self):
        ctx = ToolCallContext(tool_calls_this_turn=["Bash"])
        out = evaluate_claim_tool_call(
            claim_has_license_label=False,
            claim_normalized_label=None,
            ctx=ctx,
        )
        assert out["tool_call_present"] is True
        # Sin etiqueta y con tool_call presente -> license_required apunta
        # a VERIFIED_CURRENT_TURN como minimo
        assert out["license_required"] == "VERIFIED_CURRENT_TURN"

    def test_evaluate_claim_sin_etiqueta_sin_tool_call(self):
        ctx = ToolCallContext(tool_calls_this_turn=[])
        out = evaluate_claim_tool_call(
            claim_has_license_label=False,
            claim_normalized_label=None,
            ctx=ctx,
        )
        assert out["tool_call_present"] is False
        assert out["license_required"] == "UNVERIFIED_DO_NOT_ASSERT"

    def test_evidence_tools_set_es_no_vacio(self):
        assert len(EVIDENCE_TOOLS) > 0
        assert "Read" in EVIDENCE_TOOLS
        assert "Bash" in EVIDENCE_TOOLS

    def test_hook_register_tool_call_actualiza_ctx(self):
        hook = CoworkPreResponseHook(t1_config=T1Config.observe_only())
        assert hook.tool_call_ctx.tool_call_present is False
        hook.register_tool_call("Read")
        assert hook.tool_call_ctx.tool_call_present is True

    def test_session_health_expone_tool_call_present(self):
        hook = CoworkPreResponseHook(t1_config=T1Config.observe_only())
        hook.register_tool_call("Read")
        h = hook.session_health()
        assert h["tool_call_present_this_turn"] is True
        assert h["tool_call_recent_60m"] is True


# ============================================================================
# E. ENFORCE requiere >=50 claims + >=80% precision + 0 FP P2 + auditor
# ============================================================================


class TestEnforceGuardrailConvergencia:

    def test_constantes_canonicas(self):
        assert MIN_AUDITED_CLAIMS_FOR_ENFORCE == 50
        assert abs(MIN_PRECISION_FOR_ENFORCE - 0.80) < 1e-9
        assert MAX_FALSE_POSITIVES_P2_FOR_ENFORCE == 0

    def test_precision_baja_rechaza(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        with pytest.raises(ValueError, match="precision"):
            T1Config.enforce_after_manual_audit(
                audit_completed=True,
                confirmed_p0_p1_count=50,
                env_allow_enforce=True,
                precision=0.50,
            )

    def test_precision_exacta_80_pasa(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=50,
            env_allow_enforce=True,
            precision=0.80,
        )
        assert cfg.mode == T1Mode.ENFORCE

    def test_precision_85_pasa(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=50,
            env_allow_enforce=True,
            precision=0.85,
        )
        assert cfg.mode == T1Mode.ENFORCE

    def test_false_positives_p2_no_cero_rechaza(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        with pytest.raises(ValueError, match="falsos positivos"):
            T1Config.enforce_after_manual_audit(
                audit_completed=True,
                confirmed_p0_p1_count=50,
                env_allow_enforce=True,
                precision=0.95,
                false_positives_p2=1,
            )

    def test_false_positives_p2_cero_pasa(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=50,
            env_allow_enforce=True,
            precision=0.95,
            false_positives_p2=0,
        )
        assert cfg.mode == T1Mode.ENFORCE

    def test_auditor_no_alfredo_rechaza(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        with pytest.raises(ValueError, match="alfredo"):
            T1Config.enforce_after_manual_audit(
                audit_completed=True,
                confirmed_p0_p1_count=50,
                env_allow_enforce=True,
                precision=0.95,
                false_positives_p2=0,
                auditor="manus",
            )

    def test_auditor_alfredo_pasa(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=50,
            env_allow_enforce=True,
            precision=0.95,
            false_positives_p2=0,
            auditor="alfredo",
        )
        assert cfg.mode == T1Mode.ENFORCE

    def test_combo_completo_pasa(self, monkeypatch):
        """Camino feliz con TODOS los gates de convergencia 7 Sabios."""
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=60,
            env_allow_enforce=True,
            precision=0.92,
            false_positives_p2=0,
            auditor="alfredo",
        )
        assert cfg.mode == T1Mode.ENFORCE
        assert cfg.is_enforcing() is True

    def test_observe_only_no_se_auto_promueve_aun_con_muchos_bloqueos(self):
        """
        Sin importar cuantos bloqueos haya en OBSERVE_ONLY, no existe API
        para auto-promover. Regla dura de la convergencia.
        """
        cfg = T1Config.observe_only()
        assert cfg.mode == T1Mode.OBSERVE_ONLY
        # No hay metodos de promocion por contador
        forbidden = ("auto_enforce", "promote_after_n", "escalate_if_blocks_exceed")
        for name in forbidden:
            assert not hasattr(cfg, name)


# ============================================================================
# Integracion: hook + telemetry + tool_call_ctx en OBSERVE_ONLY E2E
# ============================================================================


class TestHookE2EConvergencia:

    def test_hook_observe_only_persiste_telemetry_y_no_bloquea(self, tmp_path):
        log = T1AuditLog(path=tmp_path / "e2e.jsonl")
        hook = CoworkPreResponseHook(
            t1_config=T1Config.observe_only(),
            t1_audit_log=log,
        )
        hook.register_tool_call("Read")
        text = (
            "El kernel esta vivo [VERIFIED_CURRENT_TURN fuente=Read ts=2026-05-12]. "
            "Tenemos 64 DSCs [NEEDS_READ memory/cowork]. "
            "Sugiero priorizar T1."
        )
        permitido, payload = hook.intercept(text, "status?")
        # OBSERVE_ONLY nunca bloquea
        assert permitido is True
        # Pero persiste claim_telemetry para cada claim
        tels = list(log.iter_claim_telemetry())
        assert len(tels) == 3
        # El claim VERIFIED_CURRENT_TURN con tool_call presente debe ser would_pass
        verified = [t for t in tels if t["epistemic_label"] == "VERIFIED_CURRENT_TURN"]
        assert len(verified) == 1
        assert verified[0]["license_validated"] is True
        assert verified[0]["action_taken"] == "would_pass"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
