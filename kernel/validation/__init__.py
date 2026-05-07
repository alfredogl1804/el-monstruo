# kernel/validation/__init__.py
"""
El Monstruo — Validacion magna (DSC-V-001).

Decorator + storage para garantizar que claims de estado-del-mundo
(precios, modelos LLM, API endpoints, fechas, market data) NO se shipen
sin haber sido validados via Perplexity (o equivalente magna source) en
una ventana temporal aceptable.

Uso:
    from kernel.validation import requires_perplexity_validation

    @requires_perplexity_validation(
        claim_type="model_availability",
        ttl_hours=24,
    )
    def get_current_top_llm() -> str:
        return "claude-opus-4-7"  # Sin log valido en 24h, esto raise.

Para validar un claim:
    from kernel.validation import record_validation

    record_validation(
        claim_type="model_availability",
        claim_value="claude-opus-4-7",
        validator="perplexity",
        evidence_url="https://perplexity.ai/...",
        ttl_hours=24,
    )

Origen: DSC-V-001, DSC-G-017.
"""
from kernel.validation.perplexity_decorator import (
    ClaimRecord,
    StaleClaimError,
    ValidationLogStorage,
    record_validation,
    requires_perplexity_validation,
)

__all__ = [
    "ClaimRecord",
    "StaleClaimError",
    "ValidationLogStorage",
    "record_validation",
    "requires_perplexity_validation",
]
