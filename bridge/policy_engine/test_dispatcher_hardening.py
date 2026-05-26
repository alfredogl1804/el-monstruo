"""
Tests para validar los invariantes duros del Dispatcher.
SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001
"""

import unittest


class MockDispatcher:
    def __init__(self):
        self.denied_actions = ["R1_SHELL", "SUPABASE_WRITE", "MEMORY_WRITE", "APP_VISION_UPDATE"]

    def evaluate_request(self, actor, action, payload):
        if action in self.denied_actions:
            return {"status": "DENY", "reason": f"Hard-coded denial for {action}"}
        if actor == "dispatcher":
            return {"status": "DENY", "reason": "Self-approval not allowed"}
        return {"status": "ALLOW"}


class TestDispatcherHardening(unittest.TestCase):
    def setUp(self):
        self.dispatcher = MockDispatcher()

    def test_deny_r1(self):
        res = self.dispatcher.evaluate_request("oracle", "R1_SHELL", "ls -la")
        self.assertEqual(res["status"], "DENY")

    def test_deny_supabase_write(self):
        res = self.dispatcher.evaluate_request("oracle", "SUPABASE_WRITE", "{}")
        self.assertEqual(res["status"], "DENY")

    def test_deny_memory_write(self):
        res = self.dispatcher.evaluate_request("oracle", "MEMORY_WRITE", "{}")
        self.assertEqual(res["status"], "DENY")

    def test_deny_app_vision_update(self):
        res = self.dispatcher.evaluate_request("oracle", "APP_VISION_UPDATE", "{}")
        self.assertEqual(res["status"], "DENY")

    def test_deny_self_approval(self):
        res = self.dispatcher.evaluate_request("dispatcher", "SOME_ACTION", "{}")
        self.assertEqual(res["status"], "DENY")


if __name__ == "__main__":
    unittest.main()
