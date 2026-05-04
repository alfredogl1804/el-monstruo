"""Smoke test del Quorum Validator (Sprint 86 Bloque 2)."""
from kernel.catastro.quorum import QuorumValidator, FuenteVote, FieldType, QuorumOutcome


def main() -> None:
    v = QuorumValidator()

    # Caso 1: 3 fuentes con valores cercanos → unanimous
    r = v.validate(
        field_name="quality_score",
        field_type=FieldType.NUMERIC,
        votes=[
            FuenteVote("artificial_analysis", 87.4),
            FuenteVote("openrouter", 88.0),
            FuenteVote("lmarena", 86.5),
        ],
    )
    print(f"Caso 1: {r.outcome.value}, consensus={r.consensus_value:.2f}, conf={r.confidence_score}")
    assert r.outcome == QuorumOutcome.QUORUM_UNANIMOUS, f"esperado unanimous, got {r.outcome}"

    # Caso 2: 2-de-3 con outlier → quorum_reached
    r = v.validate(
        field_name="quality_score",
        field_type=FieldType.NUMERIC,
        votes=[
            FuenteVote("artificial_analysis", 87.0),
            FuenteVote("openrouter", 88.0),
            FuenteVote("lmarena", 50.0),
        ],
    )
    print(f"Caso 2: {r.outcome.value}, consensus={r.consensus_value}, dissenting={r.dissenting_sources}")
    assert r.outcome == QuorumOutcome.QUORUM_REACHED
    assert "lmarena" in r.dissenting_sources

    # Caso 3: insuficiente data → insufficient_data
    r = v.validate(
        field_name="quality_score",
        field_type=FieldType.NUMERIC,
        votes=[
            FuenteVote("artificial_analysis", 87.0),
            FuenteVote("openrouter", None),
            FuenteVote("lmarena", None),
        ],
    )
    print(f"Caso 3: {r.outcome.value}, silent={r.silent_sources}")
    assert r.outcome == QuorumOutcome.INSUFFICIENT_DATA

    # Caso 4: categorical normalizado → unanimous
    r = v.validate(
        field_name="license",
        field_type=FieldType.CATEGORICAL,
        votes=[
            FuenteVote("artificial_analysis", "Proprietary"),
            FuenteVote("openrouter", "proprietary"),
            FuenteVote("lmarena", "PROPRIETARY"),
        ],
    )
    print(f"Caso 4: {r.outcome.value}, consensus={r.consensus_value}")
    assert r.outcome == QuorumOutcome.QUORUM_UNANIMOUS

    # Caso 5: trust deltas (1 dissent)
    r2 = v.validate(
        field_name="quality_score",
        field_type=FieldType.NUMERIC,
        votes=[
            FuenteVote("artificial_analysis", 87.0),
            FuenteVote("openrouter", 88.0),
            FuenteVote("lmarena", 50.0),
        ],
    )
    deltas = v.compute_trust_deltas([r2])
    print(f"Caso 5: trust_deltas={deltas}")
    assert deltas.get("lmarena", 0) < 0
    assert deltas.get("artificial_analysis", 0) == 0
    assert deltas.get("openrouter", 0) == 0

    # Caso 6: presence quorum
    r3 = v.validate(
        field_name="modelo_existe",
        field_type=FieldType.PRESENCE,
        votes=[
            FuenteVote("artificial_analysis", True),
            FuenteVote("openrouter", True),
            FuenteVote("lmarena", None),
        ],
    )
    print(f"Caso 6: {r3.outcome.value}, confirming={r3.confirming_sources}")
    assert r3.outcome == QuorumOutcome.QUORUM_REACHED
    assert r3.consensus_value is True

    print("\nQuorum smoke: 6/6 PASS")


if __name__ == "__main__":
    main()
