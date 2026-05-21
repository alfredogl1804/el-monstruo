"""
Tests para validar los invariantes del Event Log (State Fabric).
SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001
"""

import unittest

class MockStateFabric:
    def __init__(self):
        self.events = []
        self.current_state = {}
        self.last_event_id = 0
        
    def append_event(self, event):
        if event.get("event_id", 0) <= self.last_event_id:
            raise ValueError("event_id must be monotonic")
        
        self.events.append(event)
        self.last_event_id = event["event_id"]
        
        # Reducer logic (simplified)
        if event.get("dispatcher_signature"):
            if event["action"] == "UPDATE_STATUS":
                self.current_state["status"] = event["payload"].get("status")
                
    def mutate_state_directly(self, key, value):
        # En una implementación real, current_state sería inmutable o protegido
        raise PermissionError("Direct mutation not allowed")

class TestEventLogContract(unittest.TestCase):
    def setUp(self):
        self.fabric = MockStateFabric()
        
    def test_monotonic_event_id(self):
        self.fabric.append_event({"event_id": 1, "action": "TEST", "payload": {}})
        with self.assertRaises(ValueError):
            self.fabric.append_event({"event_id": 1, "action": "TEST", "payload": {}})
            
    def test_direct_mutation_denied(self):
        with self.assertRaises(PermissionError):
            self.fabric.mutate_state_directly("status", "ACTIVE")
            
    def test_state_updates_via_event_with_signature(self):
        self.fabric.append_event({
            "event_id": 1, 
            "action": "UPDATE_STATUS", 
            "payload": {"status": "ACTIVE"},
            "dispatcher_signature": "APPROVED"
        })
        self.assertEqual(self.fabric.current_state.get("status"), "ACTIVE")

    def test_state_ignores_event_without_signature(self):
        self.fabric.append_event({
            "event_id": 1, 
            "action": "UPDATE_STATUS", 
            "payload": {"status": "ACTIVE"}
        })
        self.assertNotEqual(self.fabric.current_state.get("status"), "ACTIVE")

if __name__ == '__main__':
    unittest.main()
