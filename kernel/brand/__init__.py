"""
El Monstruo — Brand Engine (Sprint 52)
======================================
Módulo que garantiza que TODO output del Monstruo sea consistente
con su identidad de marca. No es un wrapper genérico — es parte
del kernel, como Error Memory o Magna Classifier.

Componentes:
    brand_dna.py   → Identidad inmutable (BRAND_DNA dict)
    validator.py   → Validación de compliance (score 0-100)

Referencia: docs/BRAND_ENGINE_ESTRATEGIA.md
"""

from kernel.brand.brand_dna import BRAND_DNA, get_error_message, validate_output_name
from kernel.brand.validator import BrandValidator

__all__ = [
    "BRAND_DNA",
    "BrandValidator",
    "get_error_message",
    "validate_output_name",
]
