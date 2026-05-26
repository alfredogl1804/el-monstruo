"""
Tests para MinimalDispatcher — SPR-DISPATCHER-MINIMAL-001
El Monstruo — Vigilia Sincrónica

Valida que el Dispatcher:
1. Conecta correctamente con preflight_check
2. Registra eventos en event_log.v0.jsonl
3. Actualiza current_state.v0.json
4. Maneja loops inexistentes
5. Respeta la Escalera A0-A8
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

import yaml

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_engine.dispatcher import MinimalDispatcher


class TestMinimalDispatcher(unittest.TestCase):
    """Suite de tests para el Dispatcher mínimo."""

    @classmethod
    def setUpClass(cls):
        """
        Crea un entorno temporal que replica la estructura de
        state_fabric y policy_base_dir para tests aislados.
        """
        cls.test_dir = tempfile.mkdtemp(prefix="monstruo_dispatcher_test_")

        # --- Crear state_fabric_dir ---
        cls.state_fabric_dir = os.path.join(cls.test_dir, "state_fabric")
        os.makedirs(cls.state_fabric_dir)

        # current_state.v0.json
        current_state = {
            "stack_vertical_status": "APPROVED",
            "autonomy_ladder_status": "APPROVED",
            "state_fabric_status": "APPROVED",
            "active_blockers": [],
            "pending_t1_decisions": 8,
            "active_sprints": ["SPR-DISPATCHER-MINIMAL-001"],
            "last_event_id": 1,
            "last_updated_at": "2026-05-20T15:30:00Z",
        }
        with open(os.path.join(cls.state_fabric_dir, "current_state.v0.json"), "w") as f:
            json.dump(current_state, f, indent=2)

        # event_log.v0.jsonl (1 evento seed)
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
        with open(os.path.join(cls.state_fabric_dir, "event_log.v0.jsonl"), "w") as f:
            f.write(json.dumps(seed_event) + "\n")

        # loop_registry.v0.yaml
        loop_registry = {
            "loop_vigia": {
                "loop_id": "loop_vigia",
                "role": "Monitor Event Log",
                "status": "NOT_RUNNING",
                "max_autonomy_level": "A2",
                "allowed_event_types": ["OBSERVED"],
                "allowed_read_paths": ["bridge/"],
                "allowed_write_paths": [],
                "forbidden_actions": ["write_code", "touch_supabase", "modify_kernel"],
                "owner": "monstruo",
            },
            "loop_ejecutor": {
                "loop_id": "loop_ejecutor",
                "role": "Heavy execution: code, files, commits",
                "status": "NOT_RUNNING",
                "max_autonomy_level": "A5",
                "allowed_event_types": ["OBSERVED", "STATE_DELTA_PROPOSED"],
                "allowed_read_paths": ["bridge/", "src/"],
                "allowed_write_paths": ["bridge/", "src/"],
                "forbidden_actions": ["touch_supabase", "modify_kernel"],
                "owner": "monstruo",
            },
            "loop_oraculo_ias": {
                "loop_id": "loop_oraculo_ias",
                "role": "AI capability catalog",
                "status": "NOT_RUNNING",
                "max_autonomy_level": "A3",
                "allowed_event_types": ["OBSERVED", "STATE_DELTA_PROPOSED"],
                "allowed_read_paths": ["bridge/"],
                "allowed_write_paths": ["bridge/doctrine_candidates/"],
                "forbidden_actions": ["touch_supabase", "modify_kernel"],
                "owner": "monstruo",
            },
        }
        with open(os.path.join(cls.state_fabric_dir, "loop_registry.v0.yaml"), "w") as f:
            yaml.dump(loop_registry, f)

        # --- Crear policy_base_dir con autonomy_ladder ---
        cls.policy_base_dir = os.path.join(cls.test_dir, "policy_base")
        autonomy_dir = os.path.join(cls.policy_base_dir, "autonomy_ladder")
        os.makedirs(autonomy_dir)

        # action_registry_v0.yaml
        action_registry = {
            "version": "v0.1.0",
            "default_autonomy_level": "A8",
            "actions": {
                "observe_repo": {
                    "autonomy_level_required": "A0",
                    "allowed_by_default": True,
                    "t1_required": False,
                    "evidence_required": False,
                    "auditor_required": False,
                },
                "create_report": {
                    "autonomy_level_required": "A2",
                    "allowed_by_default": True,
                    "t1_required": False,
                    "evidence_required": False,
                    "auditor_required": False,
                },
                "update_thread_archive": {
                    "autonomy_level_required": "A3",
                    "allowed_by_default": True,
                    "t1_required": False,
                    "allowed_paths": ["bridge/thread_archives/"],
                    "evidence_required": True,
                    "auditor_required": False,
                },
                "write_code": {
                    "autonomy_level_required": "A5",
                    "allowed_by_default": False,
                    "t1_required": False,
                    "evidence_required": True,
                    "auditor_required": False,
                },
                "touch_supabase": {
                    "autonomy_level_required": "A7",
                    "allowed_by_default": False,
                    "t1_required": True,
                    "evidence_required": True,
                    "auditor_required": True,
                },
                "modify_kernel": {
                    "autonomy_level_required": "A8",
                    "allowed_by_default": False,
                    "t1_required": True,
                    "evidence_required": True,
                    "auditor_required": True,
                },
            },
        }
        with open(os.path.join(autonomy_dir, "action_registry_v0.yaml"), "w") as f:
            yaml.dump(action_registry, f)

    @classmethod
    def tearDownClass(cls):
        """Limpia el directorio temporal."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def _fresh_dispatcher(self):
        """Crea un dispatcher fresco re-leyendo los archivos."""
        return MinimalDispatcher(self.state_fabric_dir, self.policy_base_dir)

    def _reset_state(self):
        """Resetea current_state y event_log para tests independientes."""
        current_state = {
            "stack_vertical_status": "APPROVED",
            "last_event_id": 1,
            "last_updated_at": "2026-05-20T15:30:00Z",
        }
        with open(os.path.join(self.state_fabric_dir, "current_state.v0.json"), "w") as f:
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
        with open(os.path.join(self.state_fabric_dir, "event_log.v0.jsonl"), "w") as f:
            f.write(json.dumps(seed_event) + "\n")

    # ==================== TESTS ====================

    def test_01_allow_observe_repo_loop_vigia(self):
        """Loop Vigía (A2) solicita observe_repo (A0) → ALLOW."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action("loop_vigia", {"action": "observe_repo"})

        self.assertTrue(is_allowed)
        self.assertEqual(reason, "ALLOW")
        self.assertEqual(event["event_type"], "STATE_DELTA_PROPOSED")
        self.assertEqual(event["event_id"], 2)

    def test_02_deny_write_code_loop_vigia(self):
        """Loop Vigía (A2) solicita write_code (A5) → DENY por autonomía."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_vigia", {"action": "write_code", "target_path": "src/module.py", "has_evidence": True}
        )

        self.assertFalse(is_allowed)
        self.assertIn("Autonomy Exceeded", reason)
        self.assertEqual(event["event_type"], "BLOCKER_DECLARED")
        self.assertEqual(event["event_id"], 2)

    def test_03_allow_write_code_loop_ejecutor(self):
        """Loop Ejecutor (A5) solicita write_code (A5) con evidencia → ALLOW."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_ejecutor", {"action": "write_code", "target_path": "src/new_module.py", "has_evidence": True}
        )

        self.assertTrue(is_allowed)
        self.assertEqual(reason, "ALLOW")
        self.assertEqual(event["event_type"], "STATE_DELTA_PROPOSED")

    def test_04_deny_touch_supabase_no_t1(self):
        """Loop Ejecutor (A5) solicita touch_supabase (A7) → DENY por autonomía."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_ejecutor", {"action": "touch_supabase", "has_evidence": True, "t1_approval_present": True}
        )

        self.assertFalse(is_allowed)
        self.assertIn("Autonomy Exceeded", reason)

    def test_05_deny_unknown_loop(self):
        """Loop inexistente → DENY con motivo claro."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action("loop_fantasma", {"action": "observe_repo"})

        self.assertFalse(is_allowed)
        self.assertIn("not found in loop_registry", reason)
        self.assertEqual(event["event_type"], "BLOCKER_DECLARED")

    def test_06_deny_unknown_action(self):
        """Acción inexistente → DENY (asume A8)."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action("loop_ejecutor", {"action": "deploy_nuclear_weapon"})

        self.assertFalse(is_allowed)
        self.assertIn("not in registry", reason)

    def test_07_event_log_persistence(self):
        """Verifica que el event_log crece con cada dispatch."""
        self._reset_state()
        d = self._fresh_dispatcher()

        # Dispatch 1
        d.dispatch_action("loop_vigia", {"action": "observe_repo"})
        # Dispatch 2
        d.dispatch_action("loop_vigia", {"action": "create_report"})

        # Leer event_log
        with open(os.path.join(self.state_fabric_dir, "event_log.v0.jsonl"), "r") as f:
            lines = [l for l in f.readlines() if l.strip()]

        # Seed (1) + 2 dispatches = 3 líneas
        self.assertEqual(len(lines), 3)

        # Verificar IDs secuenciales
        events = [json.loads(l) for l in lines]
        self.assertEqual(events[0]["event_id"], 1)
        self.assertEqual(events[1]["event_id"], 2)
        self.assertEqual(events[2]["event_id"], 3)

    def test_08_current_state_update(self):
        """Verifica que current_state.last_event_id se actualiza."""
        self._reset_state()
        d = self._fresh_dispatcher()

        d.dispatch_action(
            "loop_ejecutor", {"action": "write_code", "target_path": "bridge/test.py", "has_evidence": True}
        )

        with open(os.path.join(self.state_fabric_dir, "current_state.v0.json"), "r") as f:
            state = json.load(f)

        self.assertEqual(state["last_event_id"], 2)
        self.assertNotEqual(state["last_updated_at"], "2026-05-20T15:30:00Z")

    def test_09_oraculo_update_archive_allowed(self):
        """Loop Oráculo (A3) solicita update_thread_archive en path permitido → ALLOW."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_oraculo_ias",
            {
                "action": "update_thread_archive",
                "target_path": "bridge/thread_archives/new_discovery.md",
                "has_evidence": True,
            },
        )

        self.assertTrue(is_allowed)
        self.assertEqual(reason, "ALLOW")

    def test_10_oraculo_write_code_denied(self):
        """Loop Oráculo (A3) solicita write_code (A5) → DENY."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_oraculo_ias", {"action": "write_code", "target_path": "src/oracle.py", "has_evidence": True}
        )

        self.assertFalse(is_allowed)
        self.assertIn("Autonomy Exceeded", reason)

    def test_11_multiple_dispatches_sequential_ids(self):
        """5 dispatches consecutivos producen IDs 2-6 secuenciales."""
        self._reset_state()
        d = self._fresh_dispatcher()

        for i in range(5):
            _, _, event = d.dispatch_action("loop_vigia", {"action": "observe_repo"})
            self.assertEqual(event["event_id"], i + 2)

    def test_12_deny_write_code_no_evidence(self):
        """Loop Ejecutor (A5) solicita write_code sin evidencia → DENY."""
        self._reset_state()
        d = self._fresh_dispatcher()

        is_allowed, reason, event = d.dispatch_action(
            "loop_ejecutor", {"action": "write_code", "target_path": "src/module.py", "has_evidence": False}
        )

        self.assertFalse(is_allowed)
        self.assertIn("Evidence required", reason)


if __name__ == "__main__":
    unittest.main()
