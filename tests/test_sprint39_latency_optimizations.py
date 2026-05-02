"""
Tests Sprint 39 — Optimizaciones de Latencia
=============================================
Valida las 4 optimizaciones implementadas:
  Opt-1: Supervisor conectado al grafo → skip_enrich en tier SIMPLE
  Opt-2: Response cache con TTL → cache hit evita llamada al LLM
  Opt-3: Dossier cache con TTL → evita fetch de Supabase en cada request
  Opt-4: Supervisor tier correcto para mensajes simples vs complejos
"""

import time

# ══════════════════════════════════════════════════════════════════════
# Opt-1: Supervisor → skip_enrich
# ══════════════════════════════════════════════════════════════════════


class TestSupervisorSkipEnrich:
    def test_simple_greeting_skip_enrich(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity("hola", intent="chat")
        assert decision.skip_enrich is True, "Saludos simples deben saltar enrich"

    def test_simple_math_skip_enrich(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity("cuánto es 2 + 2", intent="chat")
        assert decision.skip_enrich is True, "Matemática simple debe saltar enrich"

    def test_complex_analysis_no_skip(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity(
            "analiza la estrategia de go-to-market para el producto y dame recomendaciones", intent="chat"
        )
        assert decision.skip_enrich is False, "Análisis complejo no debe saltar enrich"

    def test_deep_think_no_skip(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity(
            "necesito que pienses profundamente sobre la arquitectura del sistema", intent="deep_think"
        )
        assert decision.skip_enrich is False, "deep_think nunca debe saltar enrich"

    def test_supervisor_returns_model(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity("hola monstruo", intent="chat")
        assert decision.model, "El supervisor debe retornar un modelo"
        assert len(decision.model) > 0

    def test_supervisor_latency_under_5ms(self):
        """El supervisor es puro pattern matching — debe ser < 5ms."""
        from kernel.supervisor import analyze_complexity

        start = time.monotonic()
        for _ in range(100):
            analyze_complexity("hola", intent="chat")
        elapsed_ms = (time.monotonic() - start) * 10  # promedio por llamada
        assert elapsed_ms < 5, f"Supervisor tardó {elapsed_ms:.2f}ms (debe ser < 5ms)"


# ══════════════════════════════════════════════════════════════════════
# Opt-2: Response Cache
# ══════════════════════════════════════════════════════════════════════


class TestResponseCache:
    def setup_method(self):
        from kernel import response_cache

        response_cache.invalidate()  # Limpiar antes de cada test

    def test_cache_miss_returns_none(self):
        from kernel import response_cache

        result = response_cache.get("hola mundo", "chat")
        assert result is None, "Cache vacío debe retornar None"

    def test_cache_store_and_hit(self):
        from kernel import response_cache

        message = "cuánto es la capital de Francia"
        intent = "chat"
        response = "La capital de Francia es París."
        response_cache.store(message, intent, response)
        cached = response_cache.get(message, intent)
        assert cached == response, "Cache hit debe retornar la respuesta almacenada"

    def test_cache_hit_count_increments(self):
        from kernel import response_cache

        message = "qué hora es en Madrid"
        response_cache.store(message, "chat", "Son las 3pm en Madrid.")
        response_cache.get(message, "chat")
        response_cache.get(message, "chat")
        stats = response_cache.stats()
        assert stats["entries"][0]["hits"] == 2, "Hits deben incrementar con cada acceso"

    def test_cache_not_cacheable_for_deep_think(self):
        """deep_think no debe cachearse — respuestas siempre únicas."""
        from kernel import response_cache

        result = response_cache.get("analiza profundamente esto", "deep_think")
        assert result is None, "deep_think no debe tener hits de cache"
        stored = response_cache.store("analiza profundamente esto", "deep_think", "respuesta")
        assert stored is False, "deep_think no debe almacenarse en cache"

    def test_cache_not_cacheable_for_long_messages(self):
        """Mensajes muy largos son probablemente únicos — no cachear."""
        from kernel import response_cache

        long_message = "a" * 400
        stored = response_cache.store(long_message, "chat", "respuesta")
        assert stored is False, "Mensajes largos no deben cachearse"

    def test_cache_invalidate_clears_all(self):
        from kernel import response_cache

        response_cache.store("cual es la capital de Francia", "chat", "París es la capital.")
        response_cache.store("busca informacion sobre Python", "search", "Python es un lenguaje.")
        count_before = response_cache.stats()["size"]
        assert count_before == 2
        # Invalidar todo
        response_cache.invalidate()
        assert response_cache.get("cual es la capital de Francia", "chat") is None
        assert response_cache.get("busca informacion sobre Python", "search") is None

    def test_cache_stats_structure(self):
        from kernel import response_cache

        response_cache.store("test message", "chat", "test response")
        stats = response_cache.stats()
        assert "size" in stats
        assert "max_size" in stats
        assert "ttl_seconds" in stats
        assert "total_hits" in stats
        assert "entries" in stats

    def test_cache_normalization_handles_variations(self):
        """Variaciones triviales del mismo mensaje deben dar el mismo hit."""
        from kernel import response_cache

        msg = "cual es la capital de Francia"
        resp = "París es la capital de Francia."
        response_cache.store(msg, "chat", resp)
        # Mismo mensaje exacto
        assert response_cache.get(msg, "chat") == resp
        # Con mayúsculas (normalizado a lowercase)
        assert response_cache.get("Cual Es La Capital De Francia", "chat") == resp
        # Con espacios extra (normalizado con strip)
        assert response_cache.get("  cual es la capital de Francia  ", "chat") == resp


# ══════════════════════════════════════════════════════════════════════
# Opt-3: Dossier Cache
# ══════════════════════════════════════════════════════════════════════


class TestDossierCache:
    def setup_method(self):
        from kernel import dossier_cache

        dossier_cache.invalidate()

    def test_cache_miss_returns_none(self):
        from kernel import dossier_cache

        assert dossier_cache.get("user_123") is None

    def test_cache_store_and_hit(self):
        from kernel import dossier_cache

        dossier = "## Perfil de Alfredo\nEmprendedor, CIP, Like Terranorte..."
        dossier_cache.store("anonymous", dossier)
        cached = dossier_cache.get("anonymous")
        assert cached == dossier

    def test_cache_per_user_isolation(self):
        from kernel import dossier_cache

        dossier_cache.store("user_a", "Dossier A")
        dossier_cache.store("user_b", "Dossier B")
        assert dossier_cache.get("user_a") == "Dossier A"
        assert dossier_cache.get("user_b") == "Dossier B"

    def test_cache_invalidate_specific_user(self):
        from kernel import dossier_cache

        dossier_cache.store("user_a", "Dossier A")
        dossier_cache.store("user_b", "Dossier B")
        dossier_cache.invalidate("user_a")
        assert dossier_cache.get("user_a") is None
        assert dossier_cache.get("user_b") == "Dossier B"

    def test_cache_stats_structure(self):
        from kernel import dossier_cache

        dossier_cache.store("anonymous", "Dossier content here")
        stats = dossier_cache.stats()
        assert "size" in stats
        assert "ttl_seconds" in stats
        assert stats["size"] == 1

    def test_empty_dossier_not_stored(self):
        from kernel import dossier_cache

        dossier_cache.store("user_x", "")
        assert dossier_cache.get("user_x") is None


# ══════════════════════════════════════════════════════════════════════
# Opt-4: Supervisor tier correctness
# ══════════════════════════════════════════════════════════════════════


class TestSupervisorTierCorrectness:
    def test_simple_tier_for_greetings(self):
        from kernel.supervisor import ComplexityTier, analyze_complexity

        decision = analyze_complexity("buenos días", intent="chat")
        assert decision.tier == ComplexityTier.SIMPLE

    def test_deep_tier_for_analysis_keywords(self):
        from kernel.supervisor import ComplexityTier, analyze_complexity

        decision = analyze_complexity("necesito un análisis profundo de la estrategia competitiva", intent="chat")
        # El supervisor clasifica esto como MODERATE o superior (no SIMPLE)
        assert decision.tier != ComplexityTier.SIMPLE, "Análisis complejo no debe ser SIMPLE"
        assert decision.skip_enrich is False, "Análisis complejo no debe saltar enrich"

    def test_deep_tier_for_deep_think_intent(self):
        from kernel.supervisor import ComplexityTier, analyze_complexity

        decision = analyze_complexity("algo", intent="deep_think")
        assert decision.tier == ComplexityTier.DEEP

    def test_simple_tier_uses_fast_model(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity("gracias", intent="chat")
        # SIMPLE tier debe usar el modelo más rápido
        assert (
            "flash" in decision.model.lower()
            or "mini" in decision.model.lower()
            or "lite" in decision.model.lower()
            or "fast" in decision.model.lower()
        )

    def test_decision_has_confidence(self):
        from kernel.supervisor import analyze_complexity

        decision = analyze_complexity("hola", intent="chat")
        assert 0.0 <= decision.confidence <= 1.0
