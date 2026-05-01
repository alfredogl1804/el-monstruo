"""
Tests del Sprint 60 — Brand Checklist Check #6
===============================================
Cubre: SovereigntyEngine, TechRadar, CausalSimulatorV2, EmbrionFinanciero, EmbrionInvestigador
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ── Tests Sprint 60.1 — Sovereignty Engine ──────────────────────────────────

class TestSovereigntyEngine:
    def test_importacion(self):
        from kernel.sovereignty.engine import SovereigntyEngine
        assert SovereigntyEngine is not None

    def test_instanciacion(self):
        from kernel.sovereignty.engine import SovereigntyEngine
        engine = SovereigntyEngine()
        assert engine is not None

    def test_to_dict_tiene_campos_requeridos(self):
        from kernel.sovereignty.engine import SovereigntyEngine
        engine = SovereigntyEngine()
        d = engine.to_dict()
        assert "modulo" in d
        assert "sprint" in d
        assert "objetivo" in d

    def test_singleton_init(self):
        from kernel.sovereignty.engine import init_sovereignty_engine, get_sovereignty_engine
        engine = init_sovereignty_engine()
        assert get_sovereignty_engine() is engine

    def test_naming_con_identidad(self):
        from kernel.sovereignty import engine as mod
        assert hasattr(mod, 'SovereigntyEngine')


# ── Tests Sprint 60.2 — Tech Radar ──────────────────────────────────────────

class TestTechRadar:
    def test_importacion(self):
        from kernel.vanguard.tech_radar import TechRadar
        assert TechRadar is not None

    def test_instanciacion(self):
        from kernel.vanguard.tech_radar import TechRadar
        radar = TechRadar()
        assert radar is not None

    def test_to_dict_tiene_campos_requeridos(self):
        from kernel.vanguard.tech_radar import TechRadar
        radar = TechRadar()
        d = radar.to_dict()
        assert "modulo" in d
        assert "sprint" in d
        assert "objetivo" in d

    def test_singleton_init(self):
        from kernel.vanguard.tech_radar import init_tech_radar, get_tech_radar
        radar = init_tech_radar()
        assert get_tech_radar() is radar

    def test_naming_con_identidad(self):
        from kernel.vanguard import tech_radar as mod
        assert hasattr(mod, 'TechRadar')


# ── Tests Sprint 60.3 — CausalSimulatorV2 ───────────────────────────────────

class TestCausalSimulatorV2:
    def test_importacion(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        assert CausalSimulatorV2 is not None

    def test_instanciacion(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        assert sim is not None

    def test_escenarios_predefinidos(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        assert "optimista" in sim.ESCENARIOS
        assert "base" in sim.ESCENARIOS
        assert "pesimista" in sim.ESCENARIOS
        assert "black_swan" in sim.ESCENARIOS

    def test_simulate_base(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        result = sim.simulate(escenario_nombre="base", n_simulaciones=100)
        assert result.p10 <= result.p50 <= result.p90
        assert result.n_simulaciones == 100

    def test_simulate_mrr_positivo(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        result = sim.simulate(escenario_nombre="optimista", metric="mrr", n_simulaciones=100)
        assert result.p50 >= 0

    def test_calibrate_from_financials(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        sim.calibrate_from_financials({
            "mrr_actual": 5000,
            "clientes_actuales": 50,
            "cac": 300,
            "ltv": 1800,
            "burn_rate": 8000,
            "runway_meses": 18,
        })
        assert sim._calibration is not None
        assert sim._calibration["mrr_actual"] == 5000

    def test_to_dict_tiene_campos_requeridos(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        d = sim.to_dict()
        assert "modulo" in d
        assert "escenarios_disponibles" in d
        assert "calibrado" in d

    def test_escenario_invalido_lanza_error(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2, SimulatorV2Error
        sim = CausalSimulatorV2()
        with pytest.raises(SimulatorV2Error):
            sim.simulate(escenario_nombre="escenario_inexistente")

    def test_singleton_init(self):
        from kernel.simulator.causal_simulator_v2 import init_simulator_v2, get_simulator_v2
        sim = init_simulator_v2()
        assert get_simulator_v2() is sim

    def test_resultado_to_dict(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        result = sim.simulate(n_simulaciones=50)
        d = result.to_dict()
        assert "p10" in d
        assert "p50" in d
        assert "p90" in d
        assert "escenario" in d

    def test_simulate_clientes(self):
        from kernel.simulator.causal_simulator_v2 import CausalSimulatorV2
        sim = CausalSimulatorV2()
        result = sim.simulate(metric="clientes", n_simulaciones=50)
        assert result.metric == "clientes"
        assert result.p50 >= 0


# ── Tests Sprint 60.4 — EmbrionFinanciero ───────────────────────────────────

class TestEmbrionFinanciero:
    def test_importacion(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        assert EmbrionFinanciero is not None

    def test_instanciacion(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        embrion = EmbrionFinanciero()
        assert embrion is not None

    def test_calculate_unit_economics(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        embrion = EmbrionFinanciero()
        ue = embrion.calculate_unit_economics(
            proyecto_id="test-001",
            mrr=10000,
            clientes=100,
            total_marketing_spend=5000,
            nuevos_clientes_mes=20,
            burn_rate=8000,
            cash_disponible=96000,
        )
        assert ue.proyecto_id == "test-001"
        assert ue.mrr == 10000
        assert ue.cac == 250.0  # 5000 / 20
        assert ue.runway_meses == 12.0  # 96000 / 8000

    def test_unit_economics_saludable(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        embrion = EmbrionFinanciero()
        ue = embrion.calculate_unit_economics(
            proyecto_id="saludable",
            mrr=20000,
            clientes=200,
            total_marketing_spend=3000,
            nuevos_clientes_mes=30,
            burn_rate=5000,
            cash_disponible=120000,
        )
        assert ue.runway_meses == 24.0
        assert ue.es_saludable  # runway >= 6, ltv_cac >= 3, churn <= 5%

    def test_to_dict_tiene_campos_requeridos(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        embrion = EmbrionFinanciero()
        d = embrion.to_dict()
        assert "modulo" in d
        assert "sprint" in d
        assert "objetivo" in d
        assert "total_mrr_usd" in d

    def test_singleton_init(self):
        from kernel.embriones.embrion_financiero import init_embrion_financiero, get_embrion_financiero
        embrion = init_embrion_financiero()
        assert get_embrion_financiero() is embrion

    def test_unit_economics_to_dict(self):
        from kernel.embriones.embrion_financiero import EmbrionFinanciero
        embrion = EmbrionFinanciero()
        ue = embrion.calculate_unit_economics(
            proyecto_id="dict-test",
            mrr=5000,
            clientes=50,
            total_marketing_spend=2000,
            nuevos_clientes_mes=10,
        )
        d = ue.to_dict()
        assert "proyecto_id" in d
        assert "ltv_cac_ratio" in d
        assert "runway_meses" in d


# ── Tests Sprint 60.5 — EmbrionInvestigador ─────────────────────────────────

class TestEmbrionInvestigador:
    def test_importacion(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        assert EmbrionInvestigador is not None

    def test_instanciacion(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        embrion = EmbrionInvestigador()
        assert embrion is not None

    def test_to_dict_tiene_campos_requeridos(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        embrion = EmbrionInvestigador()
        d = embrion.to_dict()
        assert "modulo" in d
        assert "milestone" in d
        assert d["milestone"] == "COLMENA_COMPLETA_7_DE_7"
        assert "embriones_activos" in d
        assert len(d["embriones_activos"]) == 7

    def test_colmena_completa_7_embriones(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        embrion = EmbrionInvestigador()
        d = embrion.to_dict()
        embriones = d["embriones_activos"]
        assert "ventas" in embriones
        assert "tecnico" in embriones
        assert "vigia" in embriones
        assert "creativo" in embriones
        assert "estratega" in embriones
        assert "financiero" in embriones
        assert "investigador" in embriones

    def test_budget_check_lanza_error_cuando_agotado(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador, EmbrionInvestigadorError
        embrion = EmbrionInvestigador(budget_daily_usd=0.0)
        embrion._spent_today = 1.0
        with pytest.raises(EmbrionInvestigadorError):
            embrion._check_budget()

    def test_singleton_init_milestone(self):
        from kernel.embriones.embrion_investigador import init_embrion_investigador, get_embrion_investigador
        embrion = init_embrion_investigador()
        assert get_embrion_investigador() is embrion

    def test_extract_json_con_markdown(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        embrion = EmbrionInvestigador()
        raw = '```json\n{"key": "value"}\n```'
        extracted = embrion._extract_json(raw)
        assert extracted.strip() == '{"key": "value"}'

    def test_default_tasks_definidas(self):
        from kernel.embriones.embrion_investigador import EmbrionInvestigador
        embrion = EmbrionInvestigador()
        assert "daily_briefing" in embrion.DEFAULT_TASKS
        assert "competitor_monitor" in embrion.DEFAULT_TASKS
        assert "trend_analysis" in embrion.DEFAULT_TASKS
        assert "fact_check" in embrion.DEFAULT_TASKS
