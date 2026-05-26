#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime

import yaml


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_jsonl(path):
    events = []
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
    return events


def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def save_jsonl(events, path):
    with open(path, "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")


def save_text(text, path):
    with open(path, "w") as f:
        f.write(text)


# --- MOCK LOOPS ---


def loop_vigia(handoff):
    # Simula leer estado y detectar algo
    return {
        "loop_id": "loop_vigia",
        "status": "SUCCESS",
        "event_proposals": [
            {
                "event_type": "OBSERVED",
                "subject": "System Status",
                "summary": "State Fabric initialized correctly. Awaiting next steps.",
                "autonomy_level": "A1",
                "status": "PROPOSED",
            }
        ],
        "next_suggested_loop": "loop_memoria_memento",
    }


def loop_memoria_memento(handoff):
    # Simula validar contexto
    return {
        "loop_id": "loop_memoria_memento",
        "status": "SUCCESS",
        "event_proposals": [
            {
                "event_type": "RESTORE_TEST_PASSED",
                "subject": "Context Restore",
                "summary": "Context is intact. No Dory syndrome detected.",
                "autonomy_level": "A1",
                "status": "PROPOSED",
            }
        ],
        "next_suggested_loop": "loop_auditor",
    }


def loop_auditor(handoff):
    # Simula auditoría
    return {
        "loop_id": "loop_auditor",
        "status": "SUCCESS",
        "event_proposals": [
            {
                "event_type": "AUDIT_COMPLETED",
                "subject": "A0-A8 Compliance",
                "summary": "All recent proposals are within allowed autonomy levels.",
                "autonomy_level": "A2",
                "status": "PROPOSED",
            }
        ],
        "next_suggested_loop": "loop_unified_face",
    }


def loop_unified_face(handoff):
    # Produce el output final
    summary = "# Monstruo Multinúcleo Status\n\nEl sistema está operando correctamente en modo Vigilia Sincrónica (Simulada).\n- Vigía reporta: State Fabric OK.\n- Memoria reporta: Contexto intacto.\n- Auditor reporta: Compliance A0-A8 verificado.\n\nA la espera de instrucciones de T1."

    return {
        "loop_id": "loop_unified_face",
        "status": "SUCCESS",
        "event_proposals": [],
        "next_suggested_loop": "STOP",
        "message": summary,
    }


# --- DISPATCHER ---


class Dispatcher:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.current_state = load_json(os.path.join(input_dir, "current_state.sample.json"))
        self.event_log = load_jsonl(os.path.join(input_dir, "event_log.sample.jsonl"))
        self.loop_registry = load_yaml(os.path.join(input_dir, "loop_registry.sample.yaml"))

        self.event_proposals_all = []
        self.unified_summary = ""
        self.loops_executed = []

    def create_handoff(self, loop_id):
        contract = self.loop_registry.get(loop_id, {})
        return {
            "loop_id": loop_id,
            "max_autonomy_level": contract.get("max_autonomy_level", "A0"),
            "current_state": self.current_state,
            "recent_events": self.event_log[-5:],
            "forbidden_actions": contract.get("forbidden_actions", []),
        }

    def apply_reducer(self, proposals):
        # Simula reducer simple: acepta todos los PROPOSED y actualiza ID
        last_id = self.current_state.get("last_event_id", 0)
        for p in proposals:
            last_id += 1
            p["event_id"] = last_id
            p["status"] = "ACCEPTED"
            p["created_at"] = datetime.utcnow().isoformat() + "Z"
            p["source_loop"] = "dispatcher_reducer"
            p["source_lineage"] = "sim_run"
            p["dedupe_key"] = f"sim_{last_id}"

            self.event_log.append(p)
            self.event_proposals_all.append(p)

        self.current_state["last_event_id"] = last_id
        self.current_state["last_updated_at"] = datetime.utcnow().isoformat() + "Z"

    def run_cycle(self):
        print("Starting Vigilia Sincronica Cycle Simulation...")

        # Secuencia estática para simulación
        sequence = [loop_vigia, loop_memoria_memento, loop_auditor, loop_unified_face]

        for loop_func in sequence:
            loop_id = loop_func.__name__
            print(f"-> Dispatching {loop_id}...")

            handoff = self.create_handoff(loop_id)
            output = loop_func(handoff)

            self.loops_executed.append(loop_id)

            if output["event_proposals"]:
                self.apply_reducer(output["event_proposals"])

            if loop_id == "loop_unified_face":
                self.unified_summary = output.get("message", "")

            if output["next_suggested_loop"] == "STOP":
                print("-> STOP requested. Ending cycle.")
                break

        self.save_outputs()

    def save_outputs(self):
        save_jsonl(self.event_proposals_all, os.path.join(self.output_dir, "event_proposals.jsonl"))
        save_jsonl(self.event_log, os.path.join(self.output_dir, "event_log.after.jsonl"))
        save_json(self.current_state, os.path.join(self.output_dir, "current_state.after.json"))
        save_text(self.unified_summary, os.path.join(self.output_dir, "unified_face_summary.md"))

        manifest = {
            "run_id": "sim_" + datetime.utcnow().strftime("%Y%md%H%M%S"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "loops_executed": self.loops_executed,
            "events_proposed": len(self.event_proposals_all),
            "events_accepted": len(self.event_proposals_all),
            "validation_score": "PENDING",
            "files_generated": [
                "event_proposals.jsonl",
                "event_log.after.jsonl",
                "current_state.after.json",
                "unified_face_summary.md",
            ],
        }
        save_json(manifest, os.path.join(self.output_dir, "manifest.json"))
        print(f"Outputs saved to {self.output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    dispatcher = Dispatcher(args.input, args.output)
    dispatcher.run_cycle()
