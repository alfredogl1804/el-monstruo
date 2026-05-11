# tests/test_transversales_operaciones_implement_monitor.py
"""
Sprint TRANSVERSAL-001 T6 — tests de OperacionesLayer.implement+monitor.
"""
from __future__ import annotations

import pytest

from kernel.transversales.base import (
    BusinessModelArchetype,
    TransversalContext,
    VerticalId,
)
from kernel.transversales.operaciones import OperacionesLayer


@pytest.fixture
def liketickets_ctx() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.LIKETICKETS,
        archetype=BusinessModelArchetype.TICKETING_LIMITED_INVENTORY,
    )


@pytest.fixture
def cip_ctx() -> TransversalContext:
    return TransversalContext(
        vertical=VerticalId.CIP,
        archetype=BusinessModelArchetype.TOKENIZED_REAL_ESTATE,
    )


def test_implement_returns_helpdesk_plan(liketickets_ctx):
    layer = OperacionesLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert "helpdesk_plan" in impl
    assert isinstance(impl["helpdesk_plan"], list)
    assert len(impl["helpdesk_plan"]) >= 1
    for c in impl["helpdesk_plan"]:
        assert "channel" in c
        assert "helpdesk_target" in c
        assert "endpoints" in c
        assert "ready" in c


def test_implement_sla_seconds_derived(liketickets_ctx):
    """sla_first_response_seconds = sla_first_response_hours * 3600."""
    layer = OperacionesLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert impl["sla_first_response_seconds"] is not None
    assert impl["sla_first_response_seconds"] == (
        impl["sla_first_response_hours"] * 3600
    )


def test_implement_helpdesk_endpoints_canonical(liketickets_ctx):
    """Endpoints REST deben coincidir con docs oficiales 2026."""
    layer = OperacionesLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    targets = {c["helpdesk_target"] for c in impl["helpdesk_plan"]}
    # LIKETICKETS canonico tiene chat_web + email + whatsapp + phone → intercom/front
    valid_targets = {
        "intercom", "front", "twilio", "discord_bot", "telegram_bot"
    }
    assert targets.issubset(valid_targets)
    # Validar URL canonica de Intercom si presente.
    for c in impl["helpdesk_plan"]:
        if c["helpdesk_target"] == "intercom":
            assert "api.intercom.io" in c["endpoints"]["create_conversation"]
        if c["helpdesk_target"] == "front":
            assert "api2.frontapp.com" in c["endpoints"]["create_conversation"]


def test_implement_regulatory_gates_block_cip(cip_ctx):
    """CIP no puede launch MX hoy (DSC-CIP-PEND fideicomiso)."""
    layer = OperacionesLayer()
    rec = layer.recommend(cip_ctx)
    impl = layer.implement(rec)
    gates = impl["regulatory_gates"]
    assert gates["operations_can_launch_mx_today"] is False
    assert gates["blocker_reason"] is not None


def test_monitor_cip_returns_blocker(cip_ctx):
    """CIP debe retornar blocker en monitor por regulatory gate."""
    layer = OperacionesLayer()
    mon = layer.monitor(cip_ctx)
    assert len(mon["blockers"]) >= 1
    assert any("MX" in b or "launch" in b for b in mon["blockers"])


def test_monitor_liketickets_no_blocker(liketickets_ctx):
    """LIKETICKETS sin regulatory blockers → 0 blockers en monitor."""
    layer = OperacionesLayer()
    mon = layer.monitor(liketickets_ctx)
    assert mon["blockers"] == []


def test_monitor_sla_health(liketickets_ctx):
    layer = OperacionesLayer()
    mon = layer.monitor(liketickets_ctx)
    assert "sla_health" in mon
    assert mon["sla_health"]["sla_first_response_seconds"] is not None
    assert mon["sla_health"]["status"] == "pending_storage_injection"


def test_implement_validation_log_anchors(liketickets_ctx):
    """CA5: implement debe anchor helpdesk_api_2026."""
    layer = OperacionesLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    claim_types = {a["claim_type"] for a in impl["validation_log_anchors"]}
    assert "helpdesk_api_2026" in claim_types
    assert any(
        c.startswith("regulatory_landscape_2026:") for c in claim_types
    )


def test_implement_dry_run_default_true(liketickets_ctx):
    layer = OperacionesLayer()
    rec = layer.recommend(liketickets_ctx)
    impl = layer.implement(rec)
    assert impl["dry_run"] is True
    assert "DSC-G-002" in impl["dry_run_reason"]
