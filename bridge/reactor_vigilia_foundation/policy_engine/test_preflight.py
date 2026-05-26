import os
import sys
import unittest

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_engine.loader import get_action_registry
from policy_engine.preflight import preflight_check


class TestPolicyEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Usamos el path relativo al script para cargar el registry
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.registry = get_action_registry(base_path)

    def test_escenario_1_auditor_exceeds_autonomy(self):
        # Loop A2 intenta preparar draft PR (requiere A4)
        loop_contract = {"loop_id": "loop-101", "max_autonomy_level": "A2"}
        action_request = {"action": "prepare_draft_pr", "has_evidence": True}

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertFalse(allowed)
        self.assertIn("Autonomy Exceeded", reason)

    def test_escenario_2_nightly_builder_r1(self):
        # Loop A3 intenta update_thread_archive en path permitido
        loop_contract = {
            "loop_id": "loop-nb-001",
            "max_autonomy_level": "A3",
            "allowed_paths": ["bridge/thread_archives/"],
        }
        action_request = {
            "action": "update_thread_archive",
            "target_path": "bridge/thread_archives/new_file.md",
            "has_evidence": True,
        }

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertTrue(allowed)
        self.assertEqual(reason, "ALLOW")

    def test_escenario_3_productive_without_t1(self):
        # Loop A7 intenta touch_supabase sin firma T1
        loop_contract = {"loop_id": "loop-prod-001", "max_autonomy_level": "A7"}
        action_request = {
            "action": "touch_supabase",
            "target_path": "production_db",
            "has_evidence": True,
            "t1_approval_present": False,
        }

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertFalse(allowed)
        self.assertIn("Missing T1 Approval", reason)

    def test_escenario_3b_productive_with_t1(self):
        # Loop A7 intenta touch_supabase con firma T1 y auditor
        loop_contract = {"loop_id": "loop-prod-001", "max_autonomy_level": "A7", "lineage_id": "lineage-A"}
        action_request = {
            "action": "touch_supabase",
            "target_path": "production_db",
            "has_evidence": True,
            "t1_approval_present": True,
            "auditor_lineage_id": "lineage-B",
        }

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertTrue(allowed)
        self.assertEqual(reason, "ALLOW")

    def test_escenario_4_auditor_same_lineage(self):
        # Loop A4 intenta auditar PR de su propio linaje
        loop_contract = {"loop_id": "loop-auditor-102", "max_autonomy_level": "A4", "lineage_id": "lineage-X"}
        action_request = {
            "action": "prepare_draft_pr",
            "has_evidence": True,
            "auditor_lineage_id": "lineage-X",  # Mismo linaje!
        }

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertFalse(allowed)
        self.assertIn("Auditor Lineage Conflict", reason)

    def test_forbidden_path(self):
        # Loop A5 intenta write_code en path prohibido
        loop_contract = {"loop_id": "loop-coder-001", "max_autonomy_level": "A5", "forbidden_paths": ["src/kernel/"]}
        action_request = {"action": "write_code", "target_path": "src/kernel/core.py", "has_evidence": True}

        allowed, reason = preflight_check(loop_contract, action_request, self.registry)
        self.assertFalse(allowed)
        self.assertIn("forbidden by loop contract", reason)


if __name__ == "__main__":
    unittest.main()
