"""
tests/test_t1_pre_response_hook.py — Tests de la fase T1.

Cubre:
1. T1Config: defaults, factory observe_only, transicion ENFORCE bloqueada
   sin auditoria manual + sin env var COWORK_T1_ALLOW_ENFORCE
2. Output contract: tags VERIFICADO / INFERIDO / NO VERIFICADO / REQUIERE
   READ/SQL detectados; clasificacion P0/P1/P2 por heuristica
3. Audit log: append-only, load_for_audit(limit=50), tag_claim_review con
   classification {true_block, false_positive, false_negative, ...}
4. Hook integrado: OBSERVE-ONLY nunca bloquea aun con claims P0 sin tag;
   ENFORCE bloquea P0/P1 pero nunca P2; legacy guardian sigue activo
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
from kernel.cowork_runtime.t1_config import (
    MIN_AUDITED_CLAIMS_FOR_ENFORCE,
    ENV_ALLOW_ENFORCE,
    ENV_MODE,
    T1Config,
    T1Mode,
)
from kernel.cowork_runtime.t1_output_contract import (
    Claim,
    ContractReport,
    analyze,
    extract_claims,
    format_violation_feedback,
)
from kernel.cowork_runtime.t1_audit_log import (
    T1AuditLog,
    VALID_CLASSIFICATIONS,
)


# ============================================================================
# T1Config
# ============================================================================


class TestT1Config:

    def test_default_via_observe_only_factory(self):
        cfg = T1Config.observe_only()
        assert cfg.mode == T1Mode.OBSERVE_ONLY
        assert cfg.allow_enforce is False
        assert cfg.is_observing() is True
        assert cfg.is_enforcing() is False

    def test_from_env_default_es_observe_only(self, monkeypatch):
        monkeypatch.delenv(ENV_MODE, raising=False)
        monkeypatch.delenv(ENV_ALLOW_ENFORCE, raising=False)
        cfg = T1Config.from_env()
        assert cfg.mode == T1Mode.OBSERVE_ONLY
        assert cfg.is_enforcing() is False

    def test_from_env_enforce_sin_allow_degrada_a_observe(self, monkeypatch):
        monkeypatch.setenv(ENV_MODE, "enforce")
        monkeypatch.delenv(ENV_ALLOW_ENFORCE, raising=False)
        cfg = T1Config.from_env()
        # Guardrail: sin COWORK_T1_ALLOW_ENFORCE explicito, cae a OBSERVE_ONLY
        assert cfg.mode == T1Mode.OBSERVE_ONLY
        assert cfg.is_enforcing() is False

    def test_from_env_enforce_con_allow_si_pasa(self, monkeypatch):
        monkeypatch.setenv(ENV_MODE, "enforce")
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        cfg = T1Config.from_env()
        assert cfg.mode == T1Mode.ENFORCE
        assert cfg.is_enforcing() is True

    def test_enforce_factory_requiere_auditoria_completa(self):
        with pytest.raises(ValueError, match="auditoria manual"):
            T1Config.enforce_after_manual_audit(
                audit_completed=False,
                confirmed_p0_p1_count=100,
                env_allow_enforce=True,
            )

    def test_enforce_factory_requiere_min_50_claims(self):
        with pytest.raises(ValueError, match="claims P0/P1 confirmados"):
            T1Config.enforce_after_manual_audit(
                audit_completed=True,
                confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE - 1,
                env_allow_enforce=True,
            )

    def test_enforce_factory_requiere_env_allow_enforce(self):
        with pytest.raises(ValueError, match=ENV_ALLOW_ENFORCE):
            T1Config.enforce_after_manual_audit(
                audit_completed=True,
                confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
                env_allow_enforce=False,
            )

    def test_enforce_factory_camino_feliz(self):
        cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
            env_allow_enforce=True,
        )
        assert cfg.mode == T1Mode.ENFORCE
        assert cfg.is_enforcing() is True

    def test_blocks_severity_p0_p1_solo_en_enforce(self):
        observe = T1Config.observe_only()
        # OBSERVE_ONLY nunca bloquea, ni P0 ni P1 ni P2
        assert observe.blocks_severity("P0") is False
        assert observe.blocks_severity("P1") is False
        assert observe.blocks_severity("P2") is False

        enforce = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
            env_allow_enforce=True,
        )
        # ENFORCE bloquea P0 y P1, NUNCA P2
        assert enforce.blocks_severity("P0") is True
        assert enforce.blocks_severity("P1") is True
        assert enforce.blocks_severity("P2") is False

    def test_no_existe_escalada_automatica_por_contador(self):
        """
        Regla dura: aun con muchos bloqueos en observe_only, T1Config NO
        ofrece API para auto-escalar a ENFORCE. La unica forma es
        enforce_after_manual_audit. Este test fija la ausencia de API.
        """
        cfg = T1Config.observe_only()
        # No hay metodo escalate_if_blocks_exceed o similar
        assert not hasattr(cfg, "escalate_if_blocks_exceed")
        assert not hasattr(cfg, "auto_enforce")
        assert not hasattr(cfg, "promote_after_n")


# ============================================================================
# Output Contract
# ============================================================================


class TestOutputContract:

    def test_tag_verificado_es_reconocido(self):
        text = "El kernel esta vivo en Railway [VERIFICADO mcp__railway 2026-05-12]."
        report = analyze(text)
        assert len(report.claims) == 1
        c = report.claims[0]
        assert c.has_tag is True
        assert "VERIFICADO" in c.tag_value

    def test_tag_inferido(self):
        text = "El proximo paso natural es activar T1 [INFERIDO]."
        report = analyze(text)
        assert all(c.has_tag for c in report.claims)

    def test_tag_no_verificado(self):
        text = "Manus pusheo 6 PRs hoy [NO VERIFICADO]."
        report = analyze(text)
        assert all(c.has_tag for c in report.claims)

    def test_tag_requiere_read_sql(self):
        text = "embrion_memoria tiene 200 reflexiones [REQUIERE READ/SQL]."
        report = analyze(text)
        assert all(c.has_tag for c in report.claims)

    def test_claim_p0_sin_tag_es_detectado(self):
        text = "El kernel esta vivo en Railway y el embrion sigue latiendo."
        report = analyze(text)
        assert report.has_untagged_blocking is True
        assert len(report.untagged_p0) >= 1

    def test_claim_p1_sobre_dscs_sin_tag(self):
        text = "Tenemos 64 DSCs canonizados en la capilla."
        report = analyze(text)
        assert report.has_untagged_blocking is True
        # Puede ir a P0 o P1 dependiendo del patron; lo importante es bloqueante
        assert (report.untagged_p0 or report.untagged_p1)

    def test_p2_opinion_no_bloquea(self):
        text = "Creo que deberiamos avanzar con el merge primero."
        report = analyze(text)
        assert report.has_untagged_blocking is False
        assert len(report.untagged_p2) >= 1

    def test_pregunta_no_bloquea(self):
        text = "Querias que actualice la memoria primero?"
        report = analyze(text)
        assert report.has_untagged_blocking is False

    def test_codigo_dentro_de_bloque_se_ignora(self):
        text = (
            "Reporte general.\n"
            "```python\n"
            "print('el kernel esta caido en produccion')\n"
            "```\n"
            "Texto inocuo de cierre."
        )
        report = analyze(text)
        # El claim 'kernel esta caido' esta DENTRO del bloque y debe ignorarse
        assert all("caido" not in c.text for c in report.claims)

    def test_format_violation_feedback_contiene_tags_canonicos(self):
        text = "El kernel esta vivo. PR #99 fue mergeado a main."
        report = analyze(text)
        msg = format_violation_feedback(report)
        assert "[VERIFICADO" in msg
        assert "[INFERIDO]" in msg
        assert "[NO VERIFICADO]" in msg
        assert "[REQUIERE READ/SQL]" in msg


# ============================================================================
# Audit Log
# ============================================================================


class TestAuditLog:

    def _make_log(self, tmp_path) -> T1AuditLog:
        return T1AuditLog(path=tmp_path / "t1_audit.jsonl")

    def test_record_interception_persiste_jsonl(self, tmp_path):
        log = self._make_log(tmp_path)
        report = analyze("El kernel esta vivo en Railway.")
        entry = log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status?",
            cowork_output="El kernel esta vivo en Railway.",
            report=report,
            blocked=False,
            would_block=True,
        )
        # Linea parent + 1 evento claim_telemetry por claim (telemetria claim-level)
        contenido = log.path.read_text(encoding="utf-8").strip().split("\n")
        # Parsear y separar parent vs telemetry
        parents = [json.loads(l) for l in contenido if json.loads(l).get("event") not in ("claim_reviewed", "claim_telemetry")]
        telemetries = [json.loads(l) for l in contenido if json.loads(l).get("event") == "claim_telemetry"]
        assert len(parents) == 1
        d = parents[0]
        assert d["audit_id"] == entry.audit_id
        assert d["mode"] == "observe_only"
        assert d["blocked"] is False
        assert d["would_block"] is True
        assert d.get("event") != "claim_reviewed"
        # Telemetria claim-level: al menos 1 por claim del report
        assert len(telemetries) == len(report.claims)
        for t in telemetries:
            assert t["audit_id"] == entry.audit_id
            assert "tool_call_present_this_turn" in t
            assert t["action_taken"] in ("would_block", "would_degrade", "would_pass")

    def test_load_for_audit_50_claims(self, tmp_path):
        log = self._make_log(tmp_path)
        # Generar 60 interceptions con un claim P0 sin tag cada una
        for i in range(60):
            r = analyze(f"El kernel #{i} esta vivo en Railway hoy.")
            log.record_interception(
                session_id="s1",
                mode="observe_only",
                user_message="status",
                cowork_output=f"El kernel #{i} esta vivo en Railway hoy.",
                report=r,
                blocked=False,
                would_block=r.has_untagged_blocking,
            )
        materiales = log.load_for_audit(limit=50, only_material=True)
        assert len(materiales) == 50
        # Todos los devueltos son P0/P1 sin tag
        for m in materiales:
            assert m["severity"] in ("P0", "P1")
            assert m["tagged"] is False

    def test_tag_claim_review_valid_classifications(self, tmp_path):
        log = self._make_log(tmp_path)
        report = analyze("El kernel esta vivo en Railway.")
        entry = log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="status",
            cowork_output="El kernel esta vivo en Railway.",
            report=report,
            blocked=False,
            would_block=True,
        )
        for cls in VALID_CLASSIFICATIONS:
            log.tag_claim_review(
                audit_id=entry.audit_id,
                claim_index=0,
                classification=cls,
                severity_corrected="P1",
                fuente_requerida="curl https://kernel.railway.app/health",
            )

    def test_tag_claim_review_rechaza_classification_invalida(self, tmp_path):
        log = self._make_log(tmp_path)
        with pytest.raises(ValueError, match="classification"):
            log.tag_claim_review(
                audit_id="fake",
                claim_index=0,
                classification="bogus_value",
            )

    def test_tag_claim_review_rechaza_severidad_invalida(self, tmp_path):
        log = self._make_log(tmp_path)
        with pytest.raises(ValueError, match="severity_corrected"):
            log.tag_claim_review(
                audit_id="fake",
                claim_index=0,
                classification="true_block",
                severity_corrected="P9",
            )

    def test_load_for_audit_excluye_revisados(self, tmp_path):
        log = self._make_log(tmp_path)
        r = analyze("El kernel esta vivo en Railway hoy.")
        entry = log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="x",
            cowork_output="El kernel esta vivo en Railway hoy.",
            report=r,
            blocked=False,
            would_block=True,
        )
        # Revisarlo
        log.tag_claim_review(
            audit_id=entry.audit_id,
            claim_index=0,
            classification="true_block",
            severity_corrected="P0",
        )
        materiales = log.load_for_audit(limit=50)
        # El claim revisado ya no aparece
        assert all(
            not (m["audit_id"] == entry.audit_id and m["claim_index"] == 0)
            for m in materiales
        )

    def test_stats_basico(self, tmp_path):
        log = self._make_log(tmp_path)
        r = analyze("El kernel esta vivo en Railway hoy.")
        log.record_interception(
            session_id="s1",
            mode="observe_only",
            user_message="x",
            cowork_output="El kernel esta vivo en Railway hoy.",
            report=r,
            blocked=False,
            would_block=True,
        )
        s = log.stats()
        assert s["total_interceptions"] == 1
        assert s["total_blocked"] == 0
        assert s["total_would_block"] == 1


# ============================================================================
# Hook integrado con T1
# ============================================================================


class TestHookT1Integration:

    def test_observe_only_nunca_bloquea_aun_con_claims_p0(self, tmp_path, monkeypatch):
        monkeypatch.delenv(ENV_MODE, raising=False)
        monkeypatch.delenv(ENV_ALLOW_ENFORCE, raising=False)
        log = T1AuditLog(path=tmp_path / "audit.jsonl")
        hook = CoworkPreResponseHook(
            t1_config=T1Config.observe_only(),
            t1_audit_log=log,
        )
        # Output con claim P0 sin tag — en ENFORCE bloquearia. En OBSERVE no.
        permitido, payload = hook.intercept(
            "PR #99 fue mergeado a main. El kernel esta vivo en Railway.",
            "status",
        )
        assert permitido is True
        # Pero registramos en audit
        assert hook.t1_stats["t1_interceptions"] == 1
        assert hook.t1_stats["t1_would_block"] == 1
        assert hook.t1_stats["t1_blocked"] == 0

    def test_observe_only_persiste_audit_log_a_disco(self, tmp_path):
        log_path = tmp_path / "audit.jsonl"
        log = T1AuditLog(path=log_path)
        hook = CoworkPreResponseHook(
            t1_config=T1Config.observe_only(),
            t1_audit_log=log,
        )
        hook.intercept("El kernel esta vivo en Railway hoy.", "status")
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        # 1 parent + N claim_telemetry (uno por claim)
        parents = [json.loads(l) for l in lines if json.loads(l).get("event") != "claim_telemetry"]
        assert len(parents) == 1
        d = parents[0]
        assert d["mode"] == "observe_only"

    def test_enforce_bloquea_claim_p0_sin_tag(self, tmp_path, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        log = T1AuditLog(path=tmp_path / "audit.jsonl")
        enforce_cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
            env_allow_enforce=True,
        )
        hook = CoworkPreResponseHook(
            t1_config=enforce_cfg,
            t1_audit_log=log,
        )
        permitido, payload = hook.intercept(
            "El kernel esta vivo en Railway hoy.",
            "status",
        )
        assert permitido is False
        assert "T1_OUTPUT_CONTRACT_VIOLATION" in payload
        assert hook.t1_stats["t1_blocked"] == 1

    def test_enforce_no_bloquea_si_todo_claim_tiene_tag(self, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        enforce_cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
            env_allow_enforce=True,
        )
        hook = CoworkPreResponseHook(t1_config=enforce_cfg)
        text = (
            "El kernel esta vivo en Railway [VERIFICADO mcp__railway 2026-05-12]. "
            "Manus pusheo 6 PRs [NO VERIFICADO]. "
            "Sugiero priorizar T1 [INFERIDO]."
        )
        permitido, payload = hook.intercept(text, "status")
        assert permitido is True
        assert payload == text

    def test_enforce_nunca_bloquea_solo_p2(self, monkeypatch):
        """
        Aun en ENFORCE, claims P2 (opiniones / preguntas) sin tag NO
        bloquean. P2 nunca bloquea en esta fase.
        """
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        enforce_cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=MIN_AUDITED_CLAIMS_FOR_ENFORCE,
            env_allow_enforce=True,
        )
        hook = CoworkPreResponseHook(t1_config=enforce_cfg)
        text = "Creo que podriamos avanzar con el merge primero. Sugiero revisar."
        permitido, payload = hook.intercept(text, "status")
        assert permitido is True
        assert payload == text

    def test_session_health_expone_t1_mode(self, monkeypatch):
        monkeypatch.delenv(ENV_MODE, raising=False)
        monkeypatch.delenv(ENV_ALLOW_ENFORCE, raising=False)
        hook = CoworkPreResponseHook(t1_config=T1Config.observe_only())
        h = hook.session_health()
        assert h["t1_mode"] == "observe_only"
        assert h["t1_allow_enforce"] is False
        assert "t1_interceptions" in h
        assert "t1_would_block" in h
        assert "t1_blocked" in h

    def test_legacy_guardian_sigue_funcionando_en_paralelo(self, monkeypatch):
        """
        El hook viejo (cowork_guardian / push_to_pause) debe seguir activo
        cuando enabled=True. La fase T1 NO reemplaza al guardian.
        """
        monkeypatch.delenv(ENV_MODE, raising=False)
        monkeypatch.delenv(ENV_ALLOW_ENFORCE, raising=False)
        hook = CoworkPreResponseHook(
            enabled=True,  # legacy guardian activo
            t1_config=T1Config.observe_only(),
        )
        # Output que dispara el guardian legacy (MAGNA: andate a dormir)
        permitido, payload = hook.intercept(
            "Andate a dormir, mañana retomamos",
            "VAMOS A AVANZAR",
        )
        assert permitido is False
        assert "COWORK_GUARDIAN_BLOCK" in payload

    def test_t1_off_no_genera_audit_entries(self, tmp_path):
        log = T1AuditLog(path=tmp_path / "audit.jsonl")
        hook = CoworkPreResponseHook(
            t1_config=T1Config.off(),
            t1_audit_log=log,
        )
        hook.intercept("El kernel esta vivo en Railway hoy.", "status")
        assert not log.path.exists() or log.path.read_text().strip() == ""
        assert hook.t1_stats["t1_interceptions"] == 0


# ============================================================================
# Auditoria 24h: workflow E2E sobre 50 claims
# ============================================================================


class TestAuditoria24h:
    """
    Simula el flow de auditoria manual: el hook corre en OBSERVE_ONLY un
    rato, acumula >= 50 claims materiales, y luego un humano los clasifica.
    Con >= 50 P0/P1 confirmados como true_block + env var, recien entonces
    se puede construir un T1Config en ENFORCE.
    """

    def test_e2e_observe_acumula_audita_y_habilita_enforce(self, tmp_path, monkeypatch):
        monkeypatch.setenv(ENV_ALLOW_ENFORCE, "true")
        log = T1AuditLog(path=tmp_path / "audit.jsonl")
        hook = CoworkPreResponseHook(
            t1_config=T1Config.observe_only(),
            t1_audit_log=log,
        )

        # Generar 50 interceptions, todas con claim P0 sin tag
        for i in range(50):
            hook.intercept(
                f"PR #{i} fue mergeado a main. El kernel sigue vivo en Railway.",
                "status",
            )

        materiales = log.load_for_audit(limit=50)
        assert len(materiales) >= 50

        # Auditor humano clasifica los 50 como true_block P1
        for m in materiales[:50]:
            log.tag_claim_review(
                audit_id=m["audit_id"],
                claim_index=m["claim_index"],
                classification="true_block",
                severity_corrected="P1",
                fuente_requerida="gh pr list",
            )

        # Ahora SI se puede construir ENFORCE
        enforce_cfg = T1Config.enforce_after_manual_audit(
            audit_completed=True,
            confirmed_p0_p1_count=50,
            env_allow_enforce=True,
        )
        assert enforce_cfg.is_enforcing() is True

        # El siguiente hook con ese cfg BLOQUEA un output con claim P0 sin tag
        hook2 = CoworkPreResponseHook(t1_config=enforce_cfg)
        permitido, payload = hook2.intercept(
            "El kernel esta caido en Railway.",
            "status",
        )
        assert permitido is False
        assert "T1_OUTPUT_CONTRACT_VIOLATION" in payload


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
