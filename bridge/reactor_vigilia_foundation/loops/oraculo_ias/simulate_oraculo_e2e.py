#!/usr/bin/env python3
"""
Simulación End-to-End: Dispatcher + Oráculo de IAs
SPR-EMBRION-PERITO-LOOP-001

Este script demuestra el primer loop real del Monstruo operando dentro
de Vigilia Sincrónica:
1. Instancia el MinimalDispatcher con State Fabric temporal.
2. Instancia el OraculoIALoop pasándole el dispatcher.
3. Ejecuta el ciclo completo del Oráculo.
4. Valida que:
   - Acciones permitidas (A3) fueron ALLOW
   - Acciones prohibidas (A5) fueron DENY
   - event_log creció correctamente
   - Archivos de output fueron creados
   - current_state se actualizó

Resultado esperado: 2 ALLOW + 1 DENY = SUCCESS
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

import yaml

# Setup paths para imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REACTOR_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, REACTOR_DIR)

from policy_engine.dispatcher import MinimalDispatcher

from loops.oraculo_ias.loop_oraculo_ias import OraculoIALoop


def setup_test_environment():
    """Crea un entorno temporal que replica State Fabric + Policy."""
    test_dir = tempfile.mkdtemp(prefix="monstruo_oraculo_e2e_")

    # --- State Fabric ---
    state_fabric_dir = os.path.join(test_dir, "state_fabric")
    os.makedirs(state_fabric_dir)

    current_state = {
        "stack_vertical_status": "APPROVED",
        "autonomy_ladder_status": "APPROVED",
        "state_fabric_status": "APPROVED",
        "nightly_builder_r1_status": "UNLOCKED",
        "spr_oracle_ai_status": "APPROVED",
        "active_blockers": [],
        "pending_t1_decisions": 8,
        "active_sprints": ["SPR-EMBRION-PERITO-LOOP-001"],
        "last_event_id": 1,
        "last_updated_at": "2026-05-20T15:30:00Z",
    }
    with open(os.path.join(state_fabric_dir, "current_state.v0.json"), "w") as f:
        json.dump(current_state, f, indent=2)

    seed_event = {
        "event_id": 1,
        "created_at": "2026-05-20T15:30:00Z",
        "source_loop": "manus_a",
        "source_lineage": "manus_a_thread",
        "event_type": "STATE_DELTA_PROPOSED",
        "subject": "state_fabric_genesis",
        "summary": "State Fabric v0 initialized.",
        "autonomy_level": "A3",
        "status": "ACCEPTED",
        "dedupe_key": "state_fabric_genesis_v0",
    }
    with open(os.path.join(state_fabric_dir, "event_log.v0.jsonl"), "w") as f:
        f.write(json.dumps(seed_event) + "\n")

    loop_registry = {
        "loop_oraculo_ias": {
            "loop_id": "loop_oraculo_ias",
            "role": "AI capability catalog, model prediction, power stack",
            "status": "RUNNING",
            "max_autonomy_level": "A3",
            "allowed_event_types": ["OBSERVED", "STATE_DELTA_PROPOSED", "T1_DECISION_REQUIRED"],
            "allowed_read_paths": ["bridge/", "event_log.v0.jsonl"],
            "allowed_write_paths": ["bridge/doctrine_candidates/"],
            "forbidden_actions": ["touch_supabase", "modify_kernel", "deploy"],
            "owner": "monstruo",
        },
        "loop_auditor": {
            "loop_id": "loop_auditor",
            "role": "Validate work from other loops",
            "status": "NOT_RUNNING",
            "max_autonomy_level": "A2",
            "allowed_read_paths": ["bridge/"],
            "allowed_write_paths": ["bridge/control_tower/"],
            "forbidden_actions": ["write_code", "touch_supabase", "modify_kernel"],
            "owner": "monstruo",
        },
    }
    with open(os.path.join(state_fabric_dir, "loop_registry.v0.yaml"), "w") as f:
        yaml.dump(loop_registry, f)

    # --- Policy Base ---
    policy_base_dir = os.path.join(test_dir, "policy_base")
    autonomy_dir = os.path.join(policy_base_dir, "autonomy_ladder")
    os.makedirs(autonomy_dir)

    action_registry = {
        "version": "v0.1.0",
        "default_autonomy_level": "A8",
        "actions": {
            "observe_repo": {
                "autonomy_level_required": "A0",
                "t1_required": False,
                "evidence_required": False,
                "auditor_required": False,
            },
            "create_report": {
                "autonomy_level_required": "A2",
                "t1_required": False,
                "evidence_required": False,
                "auditor_required": False,
            },
            "create_state_fabric_draft": {
                "autonomy_level_required": "A3",
                "t1_required": False,
                "allowed_paths": ["bridge/doctrine_candidates/"],
                "evidence_required": True,
                "auditor_required": False,
            },
            "write_code": {
                "autonomy_level_required": "A5",
                "t1_required": False,
                "evidence_required": True,
                "auditor_required": False,
            },
            "touch_supabase": {
                "autonomy_level_required": "A7",
                "t1_required": True,
                "evidence_required": True,
                "auditor_required": True,
            },
        },
    }
    with open(os.path.join(autonomy_dir, "action_registry_v0.yaml"), "w") as f:
        yaml.dump(action_registry, f)

    # --- Output dir para el Oráculo ---
    output_dir = os.path.join(test_dir, "oraculo_output")
    os.makedirs(output_dir)

    return test_dir, state_fabric_dir, policy_base_dir, output_dir


def run_simulation():
    """Ejecuta la simulación completa y valida resultados."""
    print("=" * 70)
    print("  SIMULACIÓN END-TO-END: DISPATCHER + ORÁCULO DE IAs")
    print("  SPR-EMBRION-PERITO-LOOP-001 — Primer Loop Real del Monstruo")
    print("=" * 70)
    print()

    # Setup
    test_dir, state_fabric_dir, policy_base_dir, output_dir = setup_test_environment()

    try:
        # 1. Instanciar Dispatcher
        print("[1/5] Instanciando MinimalDispatcher...")
        dispatcher = MinimalDispatcher(state_fabric_dir, policy_base_dir)
        print("      OK — Dispatcher cargó loop_registry + action_registry")
        print()

        # 2. Instanciar Oráculo
        print("[2/5] Instanciando OraculoIALoop...")
        oraculo = OraculoIALoop(dispatcher, output_dir)
        print(f"      OK — Loop ID: {oraculo.LOOP_ID}, Maturity: {oraculo.MATURITY_LEVEL}")
        print()

        # 3. Preparar handoff (simulado)
        handoff = {
            "loop_id": "loop_oraculo_ias",
            "max_autonomy_level": "A3",
            "current_state": dispatcher.current_state,
            "recent_events": [],
            "forbidden_actions": ["touch_supabase", "modify_kernel"],
        }

        # 4. Ejecutar ciclo del Oráculo
        print("[3/5] Ejecutando ciclo del Oráculo...")
        print("-" * 50)
        result = oraculo.run(handoff)
        print("-" * 50)
        print()

        # 5. Reportar resultados
        print("[4/5] Resultados del ciclo:")
        print(f"      Status: {result['status']}")
        print(f"      Message: {result['message']}")
        print(f"      Events generados: {len(result['event_proposals'])}")
        print(f"      Next loop sugerido: {result['next_suggested_loop']}")
        print()

        print("      Actions Log:")
        for action in result["actions_log"]:
            status = "ALLOW" if action["allowed"] else "DENY"
            print(f"        [{status}] {action['action']} → {action['target']}")
            if not action["allowed"]:
                print(f"               Reason: {action['reason']}")
        print()

        # 6. Validaciones
        print("[5/5] Validaciones:")
        tests_passed = 0
        tests_total = 7

        # Test 1: Status es SUCCESS
        if result["status"] == "SUCCESS":
            print("      [PASS] Status = SUCCESS")
            tests_passed += 1
        else:
            print(f"      [FAIL] Status = {result['status']} (expected SUCCESS)")

        # Test 2: 2 acciones permitidas
        allowed_count = sum(1 for a in result["actions_log"] if a["allowed"])
        if allowed_count == 2:
            print("      [PASS] 2 acciones ALLOW (create_state_fabric_draft + create_report)")
            tests_passed += 1
        else:
            print(f"      [FAIL] {allowed_count} acciones ALLOW (expected 2)")

        # Test 3: 1 acción denegada
        denied_count = sum(1 for a in result["actions_log"] if not a["allowed"])
        if denied_count == 1:
            print("      [PASS] 1 acción DENY (write_code — A5 > A3)")
            tests_passed += 1
        else:
            print(f"      [FAIL] {denied_count} acciones DENY (expected 1)")

        # Test 4: Catálogo JSON creado
        catalog_file = os.path.join(output_dir, "oraculo_capability_catalog_v0.json")
        if os.path.exists(catalog_file):
            with open(catalog_file, "r") as f:
                catalog = json.load(f)
            if catalog["total_capabilities"] == 6:
                print(f"      [PASS] Catálogo creado con {catalog['total_capabilities']} capabilities")
                tests_passed += 1
            else:
                print(f"      [FAIL] Catálogo tiene {catalog['total_capabilities']} capabilities (expected 6)")
        else:
            print("      [FAIL] Catálogo JSON no fue creado")

        # Test 5: Reporte MD creado
        report_file = os.path.join(output_dir, "oraculo_power_stacks_v0.md")
        if os.path.exists(report_file):
            with open(report_file, "r") as f:
                content = f.read()
            if "Power Stacks Report" in content:
                print("      [PASS] Power Stacks Report creado")
                tests_passed += 1
            else:
                print("      [FAIL] Report existe pero contenido incorrecto")
        else:
            print("      [FAIL] Power Stacks Report no fue creado")

        # Test 6: Event log tiene 4 entradas (1 seed + 3 dispatches)
        with open(os.path.join(state_fabric_dir, "event_log.v0.jsonl"), "r") as f:
            event_lines = [l for l in f.readlines() if l.strip()]
        if len(event_lines) == 4:
            print("      [PASS] Event log tiene 4 entradas (1 seed + 3 dispatches)")
            tests_passed += 1
        else:
            print(f"      [FAIL] Event log tiene {len(event_lines)} entradas (expected 4)")

        # Test 7: current_state.last_event_id == 4
        with open(os.path.join(state_fabric_dir, "current_state.v0.json"), "r") as f:
            final_state = json.load(f)
        if final_state["last_event_id"] == 4:
            print("      [PASS] current_state.last_event_id = 4")
            tests_passed += 1
        else:
            print(f"      [FAIL] current_state.last_event_id = {final_state['last_event_id']} (expected 4)")

        print()
        print("=" * 70)
        verdict = "PASS" if tests_passed == tests_total else "FAIL"
        print(f"  RESULTADO FINAL: {tests_passed}/{tests_total} — {verdict}")
        print("=" * 70)

        # Guardar manifest de la simulación
        manifest = {
            "simulation_id": "oraculo_e2e_001",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sprint": "SPR-EMBRION-PERITO-LOOP-001",
            "loop_executed": "loop_oraculo_ias",
            "dispatcher_used": True,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "verdict": verdict,
            "actions_allowed": allowed_count,
            "actions_denied": denied_count,
            "capabilities_cataloged": 6,
            "output_files": result.get("output_files", []),
            "event_log_entries": len(event_lines),
            "final_last_event_id": final_state["last_event_id"],
        }

        manifest_path = os.path.join(output_dir, "simulation_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return verdict == "PASS", manifest

    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    success, manifest = run_simulation()
    sys.exit(0 if success else 1)
