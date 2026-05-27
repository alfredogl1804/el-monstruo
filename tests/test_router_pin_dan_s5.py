"""
Tests para DAN S5 Router Pin + Capa 4 Graceful Fallback (2026-05-27).

Cobertura:
1. supports_reliable_function_calling() — flag por modelo del catálogo.
2. pin_to_reliable_fc() — pin solo si modelo NO es FC-fiable; preserva si lo es.
3. RELIABLE_FC_FALLBACK_CHAIN — excluye Grok/Sonar/DeepSeek-R1.
4. Contrato semántico: para EXECUTE+tools+no-followup, modelo final ∈ {FC-fiables}.

Estos tests son la red de seguridad del fix S5 confirmado E2E iPhone 2026-05-27:
Grok 4.20 ignora tool_choice='required' → router pin garantiza que jamás llegue
a execute_with_tools cuando intent=EXECUTE+tools.
"""

from __future__ import annotations

import pytest

from config.model_catalog import (
    MODELS,
    RELIABLE_FC_FALLBACK_CHAIN,
    pin_to_reliable_fc,
    supports_reliable_function_calling,
)


# ════════════════════════════════════════════════════════════════════
# Grupo 1: Flag reliable_function_calling por modelo
# ════════════════════════════════════════════════════════════════════


class TestFlagFCFiable:
    """Verifica que cada modelo tenga el flag esperado en model_catalog."""

    @pytest.mark.parametrize(
        "model_key",
        [
            "gpt-5.5",
            "claude-opus-4-7",
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "gemini-3.1-pro",
            "gpt-4.1-nano",
            "gemini-3.1-flash-lite",
        ],
    )
    def test_fc_fiables_marcados_true(self, model_key: str) -> None:
        """Modelos FC-fiables tienen el flag en True."""
        assert supports_reliable_function_calling(model_key) is True, (
            f"{model_key} debería ser FC-fiable (respeta tool_choice='required')"
        )

    @pytest.mark.parametrize(
        "model_key,reason",
        [
            ("grok-4.20", "Confirmed E2E iPhone 2026-05-27: ignora tool_choice='required'"),
            ("grok-4.1-fast", "Variante grok mismo provider, mismo bug asumido"),
            ("sonar-reasoning-pro", "Sonar es modelo research, no FC nativo"),
            ("sonar-pro", "Sonar research, no FC nativo"),
            ("deepseek-r1-0528", "DeepSeek R1 reasoning-only, no FC nativo"),
            ("kimi-k2.5", "Kimi via OpenRouter, FC inconsistente — default conservador"),
        ],
    )
    def test_no_fc_fiables_marcados_false(self, model_key: str, reason: str) -> None:
        """Modelos NO FC-fiables tienen el flag en False (o ausente, default conservador)."""
        assert supports_reliable_function_calling(model_key) is False, (
            f"{model_key} debería ser NO FC-fiable. Razón: {reason}"
        )

    def test_modelo_inexistente_default_false(self) -> None:
        """Modelos no en el catálogo retornan False (default conservador)."""
        assert supports_reliable_function_calling("modelo-fantasma-inexistente") is False


# ════════════════════════════════════════════════════════════════════
# Grupo 2: pin_to_reliable_fc() — comportamiento del helper
# ════════════════════════════════════════════════════════════════════


class TestPinToReliableFC:
    """Verifica que el helper pin_to_reliable_fc() funcione correctamente."""

    @pytest.mark.parametrize(
        "fc_fiable_model",
        [
            "gpt-5.5",
            "claude-opus-4-7",
            "claude-opus-4-6",
            "claude-sonnet-4-6",
            "gemini-3.1-pro",
            "gpt-4.1-nano",
            "gemini-3.1-flash-lite",
        ],
    )
    def test_no_cambia_si_ya_es_fc_fiable(self, fc_fiable_model: str) -> None:
        """Si el modelo actual es FC-fiable, lo retorna sin cambios."""
        assert pin_to_reliable_fc(fc_fiable_model) == fc_fiable_model

    @pytest.mark.parametrize(
        "no_fc_model",
        [
            "grok-4.20",
            "grok-4.1-fast",
            "sonar-reasoning-pro",
            "sonar-pro",
            "deepseek-r1-0528",
            "kimi-k2.5",
        ],
    )
    def test_pin_aplica_si_no_es_fc_fiable(self, no_fc_model: str) -> None:
        """Si el modelo actual NO es FC-fiable, retorna el primer fallback de la cadena."""
        result = pin_to_reliable_fc(no_fc_model)
        # Debe ser distinto del original
        assert result != no_fc_model
        # Debe ser FC-fiable
        assert supports_reliable_function_calling(result)
        # Debe estar en la cadena de fallback
        assert result in RELIABLE_FC_FALLBACK_CHAIN

    def test_pin_aplica_modelo_inexistente(self) -> None:
        """Modelos no en el catálogo son tratados como NO FC-fiables → aplican pin."""
        result = pin_to_reliable_fc("modelo-fantasma-inexistente")
        assert result != "modelo-fantasma-inexistente"
        assert supports_reliable_function_calling(result)

    def test_pin_retorna_primer_fallback_disponible(self) -> None:
        """El pin retorna el primer modelo de RELIABLE_FC_FALLBACK_CHAIN que sea FC-fiable."""
        result = pin_to_reliable_fc("grok-4.20")
        # Por orden actual del catálogo, claude-opus-4-7 es el primero FC-fiable
        # de la cadena. Esto puede cambiar si reordenamos la chain — entonces
        # solo aseguramos que el resultado esté en la chain Y sea FC-fiable.
        assert result == RELIABLE_FC_FALLBACK_CHAIN[0]
        assert supports_reliable_function_calling(result)


# ════════════════════════════════════════════════════════════════════
# Grupo 3: Cadena de fallback FC-fiable
# ════════════════════════════════════════════════════════════════════


class TestReliableFCChain:
    """Verifica la composición y exclusiones de RELIABLE_FC_FALLBACK_CHAIN."""

    def test_chain_no_vacia(self) -> None:
        """La cadena debe tener al menos un modelo FC-fiable."""
        assert len(RELIABLE_FC_FALLBACK_CHAIN) > 0

    def test_todos_los_modelos_son_fc_fiables(self) -> None:
        """Cada modelo en la cadena debe ser FC-fiable según el flag del catálogo."""
        for model in RELIABLE_FC_FALLBACK_CHAIN:
            assert supports_reliable_function_calling(model), (
                f"{model} está en RELIABLE_FC_FALLBACK_CHAIN pero NO es FC-fiable. "
                f"Drift entre el flag y la cadena. Sincronizar."
            )

    def test_excluye_grok_y_variantes(self) -> None:
        """La cadena de fallback NO debe contener ningún modelo Grok."""
        for model in RELIABLE_FC_FALLBACK_CHAIN:
            assert "grok" not in model.lower(), (
                f"{model} (familia Grok) está en RELIABLE_FC_FALLBACK_CHAIN. "
                "Grok 4.20 confirmed E2E iPhone 2026-05-27 ignora tool_choice='required'."
            )

    def test_excluye_sonar(self) -> None:
        """La cadena de fallback NO debe contener Sonar (no soporta FC)."""
        for model in RELIABLE_FC_FALLBACK_CHAIN:
            assert "sonar" not in model.lower(), (
                f"{model} (familia Sonar) está en RELIABLE_FC_FALLBACK_CHAIN. "
                "Sonar es modelo research, no soporta function-calling nativo."
            )

    def test_excluye_deepseek_r1(self) -> None:
        """La cadena de fallback NO debe contener DeepSeek R1 (no FC)."""
        for model in RELIABLE_FC_FALLBACK_CHAIN:
            assert "deepseek" not in model.lower(), (
                f"{model} en RELIABLE_FC_FALLBACK_CHAIN. "
                "DeepSeek R1 es reasoning-only, no FC nativo."
            )

    def test_todos_los_modelos_existen_en_catalogo(self) -> None:
        """Cada modelo en la cadena debe existir en MODELS del catálogo."""
        for model in RELIABLE_FC_FALLBACK_CHAIN:
            assert model in MODELS, (
                f"{model} en RELIABLE_FC_FALLBACK_CHAIN pero NO existe en MODELS. "
                "Drift de catálogo."
            )


# ════════════════════════════════════════════════════════════════════
# Grupo 4: Contrato semántico — modelo final SIEMPRE FC-fiable
# ════════════════════════════════════════════════════════════════════


class TestContractSemantic:
    """Garantiza la propiedad clave del Router Pin: para cualquier input,
    el output del pin es FC-fiable."""

    @pytest.mark.parametrize(
        "input_model",
        [
            # FC-fiables — deben pasar sin cambio
            "gpt-5.5",
            "claude-opus-4-7",
            "claude-sonnet-4-6",
            # NO FC-fiables — deben ser pineados
            "grok-4.20",
            "sonar-reasoning-pro",
            "deepseek-r1-0528",
            # Inexistente — debe ser pineado
            "modelo-fantasma",
        ],
    )
    def test_output_siempre_es_fc_fiable(self, input_model: str) -> None:
        """Para cualquier input al pin, el output debe ser FC-fiable.
        Esta es la propiedad central del Router Pin: garantiza que ningún
        modelo NO FC-fiable llega a execute_with_tools cuando se aplica."""
        result = pin_to_reliable_fc(input_model)
        assert supports_reliable_function_calling(result), (
            f"pin_to_reliable_fc('{input_model}') retornó '{result}' que NO es FC-fiable. "
            "Esto rompe la propiedad central del Router Pin."
        )


# ════════════════════════════════════════════════════════════════════
# Grupo 5: Regresión bug iPhone 2026-05-27
# ════════════════════════════════════════════════════════════════════


class TestRegressionBugIphone:
    """Tests que reproducen el escenario exacto del repro V2 iPhone 2026-05-27."""

    def test_grok_para_execute_tools_es_pineado_a_fc_fiable(self) -> None:
        """Repro exacto: bug iPhone fue Grok 4.20 ruteado para EXECUTE+tools.
        El router pin debe convertirlo a un modelo FC-fiable."""
        # Modelo seleccionado por supervisor/dispatcher: Grok (V2 repro)
        selected_model = "grok-4.20"

        # Pin debe convertirlo a FC-fiable
        pinned = pin_to_reliable_fc(selected_model)

        # Aserciones del comportamiento esperado post-fix
        assert pinned != "grok-4.20", "Grok no debe sobrevivir al pin"
        assert supports_reliable_function_calling(pinned), (
            "El modelo pineado debe ser FC-fiable"
        )
        # Debe ser uno de los flagship FC (Claude Opus 4.7 o GPT-5.5)
        assert pinned in {"claude-opus-4-7", "gpt-5.5"} or pinned in RELIABLE_FC_FALLBACK_CHAIN

    def test_sonar_no_pasa_a_execute_with_tools(self) -> None:
        """Sonar no soporta FC nativo. Si llegara a EXECUTE+tools, el pin lo arregla."""
        pinned = pin_to_reliable_fc("sonar-reasoning-pro")
        assert pinned != "sonar-reasoning-pro"
        assert supports_reliable_function_calling(pinned)

    def test_claude_opus_47_pasa_sin_cambio_para_execute_tools(self) -> None:
        """Si supervisor ya escogió Claude Opus 4.7, el pin no debe alterarlo."""
        assert pin_to_reliable_fc("claude-opus-4-7") == "claude-opus-4-7"

    def test_gpt55_pasa_sin_cambio_para_execute_tools(self) -> None:
        """Si supervisor ya escogió GPT-5.5, el pin no debe alterarlo."""
        assert pin_to_reliable_fc("gpt-5.5") == "gpt-5.5"


# ════════════════════════════════════════════════════════════════════
# Grupo 6: DAN S5 OBS-1 Hotfix — Alias normalization (2026-05-27)
# ════════════════════════════════════════════════════════════════════


class TestAliasNormalization:
    """Verifica que ALIAS_TO_CATALOG resuelve mismatches entre /health y MODELS keys.

    Reportado por Cowork audit 2026-05-27 sobre #229: el kernel /health reporta
    'gemini-3.1-pro-preview' pero MODELS tiene 'gemini-3.1-pro' como key.
    Sin normalización, supports_reliable_function_calling('gemini-3.1-pro-preview')
    retornaba False (cae al default conservador), causando re-pin innecesario.
    """

    def test_normalize_passthrough_canonical(self) -> None:
        """Nombres canónicos (sin sufijo) pasan tal cual."""
        from config.model_catalog import normalize_model_name

        assert normalize_model_name("gpt-5.5") == "gpt-5.5"
        assert normalize_model_name("claude-opus-4-7") == "claude-opus-4-7"
        assert normalize_model_name("gemini-3.1-pro") == "gemini-3.1-pro"

    def test_normalize_resuelve_gemini_preview(self) -> None:
        """gemini-3.1-pro-preview se normaliza a gemini-3.1-pro."""
        from config.model_catalog import normalize_model_name

        assert normalize_model_name("gemini-3.1-pro-preview") == "gemini-3.1-pro"

    def test_normalize_resuelve_gemini_flash_lite_preview(self) -> None:
        """gemini-3.1-flash-lite-preview se normaliza a gemini-3.1-flash-lite."""
        from config.model_catalog import normalize_model_name

        assert normalize_model_name("gemini-3.1-flash-lite-preview") == "gemini-3.1-flash-lite"

    def test_normalize_passthrough_unknown(self) -> None:
        """Modelos sin alias retornan nombre original (passthrough)."""
        from config.model_catalog import normalize_model_name

        assert normalize_model_name("modelo-inventado-xyz") == "modelo-inventado-xyz"
        assert normalize_model_name("grok-4.20") == "grok-4.20"
        # NUNCA agregar alias a grok - es No-FC por diseño.

    def test_supports_fc_via_alias_gemini_preview(self) -> None:
        """gemini-3.1-pro-preview pasa por alias y resuelve a FC=True."""
        # Esta era la razón del hotfix: antes daba False (default), ahora debe dar True.
        assert supports_reliable_function_calling("gemini-3.1-pro-preview") is True

    def test_supports_fc_via_alias_gemini_flash_preview(self) -> None:
        """gemini-3.1-flash-lite-preview pasa por alias y resuelve a FC=True."""
        assert supports_reliable_function_calling("gemini-3.1-flash-lite-preview") is True

    def test_pin_no_reruta_gemini_preview(self) -> None:
        """REGRESIÓN OBS-1: pin_to_reliable_fc preserva gemini-3.1-pro-preview.

        Antes del hotfix, el flujo era:
        1. /health reporta gemini-3.1-pro-preview
        2. supports_reliable_function_calling('gemini-3.1-pro-preview') → False
        3. pin_to_reliable_fc rerouta a claude-opus-4-7 (innecesario)

        Después del hotfix:
        1. /health reporta gemini-3.1-pro-preview
        2. normalize_model_name → gemini-3.1-pro
        3. supports_reliable_function_calling → True
        4. pin_to_reliable_fc retorna el ORIGINAL (con sufijo -preview intacto).
        """
        result = pin_to_reliable_fc("gemini-3.1-pro-preview")
        assert result == "gemini-3.1-pro-preview", (
            "El alias debe preservar el nombre original con sufijo -preview "
            "(no rerutear a claude-opus innecesariamente)"
        )

    def test_pin_si_reruta_grok_aunque_haya_alias_pattern(self) -> None:
        """grok-4.20 sigue rerouteando aunque comparta familia con grok-4.1-fast."""
        # Verificar que NO inventamos un alias incorrecto que rescate a grok.
        result = pin_to_reliable_fc("grok-4.20")
        assert result != "grok-4.20", "Grok DEBE ser rerouteado por router pin"
        assert result in RELIABLE_FC_FALLBACK_CHAIN

    def test_alias_no_rescata_no_fc_models(self) -> None:
        """ALIAS_TO_CATALOG NO debe contener mappings que rescaten modelos No-FC."""
        from config.model_catalog import ALIAS_TO_CATALOG

        # Lista de modelos NO-FC que NUNCA deben ser destino de un alias.
        no_fc_models = [
            "grok-4.20",
            "grok-4.1-fast",
            "sonar-reasoning-pro",
            "sonar-pro",
            "deepseek-r1-0528",
            "kimi-k2.5",
            "groq-llama-scout",
            "together-llama-scout",
        ]

        for alias, canonical in ALIAS_TO_CATALOG.items():
            assert canonical not in no_fc_models, (
                f"ALIAS_TO_CATALOG['{alias}'] = '{canonical}' apunta a modelo No-FC. "
                f"Eso rescataría modelos No-FC de manera silenciosa. "
                f"Prohibido por DAN S5 Router Pin."
            )

    def test_alias_canonicals_existen_en_models(self) -> None:
        """Todos los destinos en ALIAS_TO_CATALOG deben existir como keys en MODELS."""
        from config.model_catalog import ALIAS_TO_CATALOG

        for alias, canonical in ALIAS_TO_CATALOG.items():
            assert canonical in MODELS, (
                f"ALIAS_TO_CATALOG['{alias}'] = '{canonical}' apunta a un modelo "
                f"que NO existe en MODELS. Esto causaría que supports_reliable_function_calling "
                f"caiga a default False silencioso. Verificar config/model_catalog.py."
            )
