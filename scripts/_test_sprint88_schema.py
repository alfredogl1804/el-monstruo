#!/usr/bin/env python3
"""
Sprint 88 - Test rapido del schema Pydantic CatastroAgente.

Ejecutar via:
    railway run --service el-monstruo-kernel python3 scripts/_test_sprint88_schema.py
"""
from __future__ import annotations

import sys


def main() -> int:
    # Importar directamente del modulo, no via __init__ (evita cargar pipeline + sources)
    import importlib.util
    from pathlib import Path
    schema_path = Path(__file__).parent.parent / "kernel" / "catastro" / "schema.py"
    spec = importlib.util.spec_from_file_location("_catastro_schema", schema_path)
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.CatastroAgente.model_rebuild(_types_namespace=vars(schema))
    schema.CatastroModelo.model_rebuild(_types_namespace=vars(schema))
    CatastroAgente = schema.CatastroAgente
    CostoPorUsoTipico = schema.CostoPorUsoTipico
    DominioAgentes = schema.DominioAgentes
    Macroarea = schema.Macroarea
    PersistenciaMemoria = schema.PersistenciaMemoria

    failures = []

    # Test 1: instancia basica con todos los campos
    try:
        a = CatastroAgente(
            id="manus",
            nombre="Manus",
            proveedor="Manus",
            dominio=DominioAgentes.AGENTES_DESARROLLO,
            tiene_sandbox=True,
            acceso_filesystem=True,
            acceso_internet=True,
            multi_step_capable=True,
            persistencia_memoria=PersistenciaMemoria.PERSISTENT,
            costo_por_uso_tipico=CostoPorUsoTipico.MEDIO,
        )
        assert a.macroarea == Macroarea.AGENTES, "macroarea default"
        assert a.dominio == DominioAgentes.AGENTES_DESARROLLO
        print("TEST_1_OK: instancia basica valida")
    except Exception as e:
        failures.append(("TEST_1", str(e)))
        print(f"TEST_1_FAIL: {e}")

    # Test 2: invariante swarm implies multistep
    try:
        bad = CatastroAgente(
            id="bad-swarm",
            nombre="Bad",
            proveedor="Test",
            dominio=DominioAgentes.AGENTES_MULTI_SWARM,
            multi_swarm_capable=True,
            multi_step_capable=False,
        )
        failures.append(("TEST_2", "debio fallar pero no lo hizo"))
        print("TEST_2_FAIL: invariante NO se ejecuto")
    except Exception as e:
        if "multi_swarm_capable" in str(e) or "multi_step_capable" in str(e):
            print(f"TEST_2_OK: invariante validado ({type(e).__name__})")
        else:
            failures.append(("TEST_2", f"error inesperado: {e}"))
            print(f"TEST_2_FAIL: error inesperado: {e}")

    # Test 3: slug format
    try:
        bad = CatastroAgente(
            id="Bad_Slug",
            nombre="X",
            proveedor="X",
            dominio=DominioAgentes.AGENTES_DESARROLLO,
        )
        failures.append(("TEST_3", "debio fallar pero no lo hizo"))
        print("TEST_3_FAIL: slug format NO validado")
    except Exception as e:
        if "lowercase" in str(e) or "guiones" in str(e) or "underscores" in str(e):
            print(f"TEST_3_OK: slug format validado")
        else:
            failures.append(("TEST_3", f"error inesperado: {e}"))
            print(f"TEST_3_FAIL: error inesperado: {e}")

    # Test 4: Enums tienen los 5 dominios esperados
    try:
        expected = {
            # Originales Sprint 88 v1
            "agentes_desarrollo",
            "agentes_investigacion",
            "agentes_ejecutores",
            "agentes_multi_swarm",
            "interfaces_usuario",
            # Expandidos Sprint 88 v2
            "agentes_vibe_coding",
            "agentes_creacion_audiovisual",
            "agentes_branding_diseno",
            "agentes_marketing_ventas",
        }
        actual = {d.value for d in DominioAgentes}
        assert actual == expected, f"esperado {expected}, actual {actual}"
        print(f"TEST_4_OK: 9 dominios canonicos {sorted(actual)}")
    except Exception as e:
        failures.append(("TEST_4", str(e)))
        print(f"TEST_4_FAIL: {e}")

    # Test 5: serializacion a dict con field aliases
    try:
        a = CatastroAgente(
            id="claude-cowork",
            nombre="Claude Cowork",
            proveedor="Anthropic",
            dominio=DominioAgentes.AGENTES_DESARROLLO,
            llm_base_id="claude-opus-4-7",
            multi_step_capable=True,
            tools_nativas=["editor", "shell", "browser"],
        )
        d = a.model_dump(mode="json")
        assert d["macroarea"] == "agentes"
        assert d["dominio"] == "agentes_desarrollo"
        print("TEST_5_OK: serializacion JSON correcta")
    except Exception as e:
        failures.append(("TEST_5", str(e)))
        print(f"TEST_5_FAIL: {e}")

    print("\n" + "=" * 60)
    if failures:
        print(f"FAILED: {len(failures)} tests")
        for name, err in failures:
            print(f"  {name}: {err}")
        return 1
    print("ALL_TESTS_OK: schema CatastroAgente validado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
