"""
Sprint 88.3 Fix #1: tests para CTA sanitizer + vertical detector + name derivation.

Cubre los 5 verticales del eval canónico que produjeron el bug original.
"""
from __future__ import annotations

import pytest

from kernel.e2e.deploy.real_deploy import (
    _derive_project_name,
    _detect_vertical,
    _cta_primary_for_vertical,
    _cta_secondary_for_vertical,
)


class TestDeriveProjectName:
    """Verifica que el nombre derivado NO contenga verbos conjugados."""

    def test_vendemos_joyeria_oaxaca_no_verb(self):
        """Bug original: 'Comprar Vendemos joyeria' viene de 'Vendemos joyeria oaxaca'."""
        nombre = _derive_project_name("Vendemos joyeria oaxaca")
        # NO debe contener "Vendemos"
        assert "vendemos" not in nombre.lower(), f"Got: {nombre}"
        # Debe contener algo significativo
        assert "joyeria" in nombre.lower() or "oaxaca" in nombre.lower(), f"Got: {nombre}"

    def test_pintura_oleo_merida(self):
        nombre = _derive_project_name("Hacemos pintura al oleo en merida")
        assert "hacemos" not in nombre.lower(), f"Got: {nombre}"
        assert "pintura" in nombre.lower() or "oleo" in nombre.lower(), f"Got: {nombre}"

    def test_cursos_python_latam(self):
        nombre = _derive_project_name("Ofrecemos cursos de python para latam")
        assert "ofrecemos" not in nombre.lower(), f"Got: {nombre}"

    def test_cafe_polanco(self):
        nombre = _derive_project_name("Tenemos un café en polanco")
        assert "tenemos" not in nombre.lower(), f"Got: {nombre}"

    def test_coaching_ctos(self):
        nombre = _derive_project_name("Damos coaching para CTOs")
        assert "damos" not in nombre.lower(), f"Got: {nombre}"

    def test_empty_input(self):
        assert _derive_project_name("") == "Tu Negocio"

    def test_only_stopwords(self):
        # "haz una landing premium" — todas son stopwords
        assert _derive_project_name("haz una landing premium") == "Tu Negocio"


class TestDetectVertical:
    """Verifica que cada uno de los 5 verticales del eval se detecte correctamente."""

    def test_joyeria_oaxaca_es_ecommerce(self):
        v = _detect_vertical(
            frase_input="Vendemos joyeria oaxaca",
            brief={"problema": "Quiero vender joyeria online"},
            ventas={},
        )
        assert v == "ecommerce", f"Got: {v}"

    def test_pintura_oleo_es_ecommerce(self):
        v = _detect_vertical(
            frase_input="Hacemos pintura al oleo en merida",
            brief={},
            ventas={},
        )
        assert v == "ecommerce", f"Got: {v}"

    def test_cursos_python_es_saas(self):
        v = _detect_vertical(
            frase_input="Cursos de python online para latam",
            brief={"solucion": "Plataforma de cursos online"},
            ventas={},
        )
        assert v == "saas", f"Got: {v}"

    def test_cafe_polanco_es_local(self):
        v = _detect_vertical(
            frase_input="Café en polanco",
            brief={"solucion": "cafetería en polanco"},
            ventas={},
        )
        assert v == "local", f"Got: {v}"

    def test_coaching_ctos_es_servicios(self):
        v = _detect_vertical(
            frase_input="Coaching para CTOs ejecutivos",
            brief={"problema": "CTOs necesitan acompañamiento estratégico"},
            ventas={},
        )
        assert v == "servicios", f"Got: {v}"


class TestCTAPerVertical:
    """Verifica los CTAs que se renderizan por vertical."""

    def test_ecommerce_ctas(self):
        assert _cta_primary_for_vertical("ecommerce") == "Comprar ahora"
        assert _cta_secondary_for_vertical("ecommerce") == "Ver catálogo"

    def test_saas_ctas(self):
        assert _cta_primary_for_vertical("saas") == "Empezar gratis"
        assert _cta_secondary_for_vertical("saas") == "Ver demo"

    def test_servicios_ctas(self):
        assert _cta_primary_for_vertical("servicios") == "Agendar llamada"
        assert _cta_secondary_for_vertical("servicios") == "Ver portafolio"

    def test_local_ctas(self):
        assert _cta_primary_for_vertical("local") == "Visitarnos"
        assert _cta_secondary_for_vertical("local") == "Cómo llegar"

    def test_generico_fallback(self):
        assert _cta_primary_for_vertical("generico") == "Empezar ahora"
        assert _cta_secondary_for_vertical("generico") == "Conocer más"

    def test_no_comprar_vendemos_bug(self):
        """Bug original: f'Comprar {nombre}' producía 'Comprar Vendemos joyeria'.
        Ahora debe ser 'Comprar ahora' fijo per ecommerce vertical."""
        cta = _cta_primary_for_vertical("ecommerce", nombre="Vendemos joyeria")
        assert "vendemos" not in cta.lower(), f"Got: {cta}"
        assert cta == "Comprar ahora"
