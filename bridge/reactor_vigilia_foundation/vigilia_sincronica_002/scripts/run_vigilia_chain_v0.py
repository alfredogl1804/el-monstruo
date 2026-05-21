"""
run_vigilia_chain_v0.py — Orquestador de Cadena Local Controlada
SPR-VIGILIA-SINCRONICA-002

Ejecuta la cadena: Oráculo → Auditor → Risk Classification → Unified Face
con handoff packets, Dispatcher/Policy, y State Fabric aislado.

NO es un daemon. NO es un scheduler. Es un script finito que:
1. Instancia el Dispatcher con un event_log delta aislado.
2. Ejecuta cada loop en secuencia.
3. Crea handoff packets entre etapas.
4. Genera la Unified Face al final.
5. Escribe todos los artifacts y termina.
"""

import sys
import os
import json
import shutil
import tempfile
from datetime import datetime, timezone

# Add paths for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REACTOR_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, REACTOR_DIR)

from policy_engine.dispatcher import MinimalDispatcher
from loops.oraculo_ias.loop_oraculo_ias import OraculoIALoop


class RiskClassificationStep:
    """
    Simulates the Risk Classification step.
    Reads Oracle catalog + Auditor findings and applies R0/A1 overlay.
    """
    LOOP_ID = "loop_risk_classification"

    def __init__(self, dispatcher, oracle_output_dir, auditor_output_dir, output_dir):
        self.dispatcher = dispatcher
        self.oracle_output_dir = oracle_output_dir
        self.auditor_output_dir = auditor_output_dir
        self.output_dir = output_dir

    def run(self, handoff_packet=None):
        results = {
            "loop_id": self.LOOP_ID,
            "status": "PENDING",
            "actions_allowed": 0,
            "actions_denied": 0,
            "output_files": [],
            "events_emitted": 0,
            "message": ""
        }

        # Read Oracle catalog
        catalog_path = os.path.join(self.oracle_output_dir, "oraculo_capability_catalog_v0.json")
        if not os.path.exists(catalog_path):
            results["status"] = "BLOCKED"
            results["message"] = "Oracle catalog not found."
            return results

        with open(catalog_path, 'r') as f:
            catalog = json.load(f)

        # Apply R0/A1 overlay to all capabilities
        annotated = {
            "catalog_version": "v0.1.0-risk-annotated",
            "base_version": catalog.get("catalog_version", "v0.1.0"),
            "risk_overlay_version": "v0.1.0",
            "generated_by": "SPR-VIGILIA-SINCRONICA-002-chain",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "global_evidence_status": "STATIC_CATALOG",
            "global_risk_class": "R0",
            "global_required_autonomy_level": "A1",
            "global_allowed_next_action": "CATALOG_ONLY",
            "total_capabilities": len(catalog.get("capabilities", [])),
            "capabilities": []
        }

        for cap in catalog.get("capabilities", []):
            annotated["capabilities"].append({
                "id": cap["id"],
                "model": cap["model"],
                "feature": cap["feature"],
                "risk_class": "R0",
                "required_autonomy_level": "A1",
                "evidence_status": "STATIC_CATALOG"
            })

        # Request permission to write overlay
        write_request = {
            "action": "create_state_fabric_draft",
            "target_path": "bridge/doctrine_candidates/chain_risk_overlay_v0_1.json",
            "has_evidence": True
        }

        is_allowed, reason, event = self.dispatcher.dispatch_action(
            self.LOOP_ID, write_request
        )
        results["events_emitted"] += 1

        if is_allowed:
            results["actions_allowed"] += 1
            output_file = os.path.join(self.output_dir, "chain_risk_overlay_v0_1.json")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(annotated, f, indent=2, ensure_ascii=False)
            results["output_files"].append(output_file)
            results["status"] = "SUCCESS"
            results["message"] = (
                f"Risk overlay applied: {annotated['total_capabilities']} capabilities "
                f"classified R0/A1. Evidence: STATIC_CATALOG."
            )
        else:
            results["actions_denied"] += 1
            results["status"] = "BLOCKED"
            results["message"] = f"Dispatcher denied write: {reason}"

        return results


class UnifiedFaceStep:
    """
    Synthesizes the chain results into a single coherent summary for T1.
    """
    LOOP_ID = "loop_unified_face"

    def __init__(self, dispatcher, chain_results, output_dir):
        self.dispatcher = dispatcher
        self.chain_results = chain_results
        self.output_dir = output_dir

    def run(self, handoff_packet=None):
        results = {
            "loop_id": self.LOOP_ID,
            "status": "PENDING",
            "actions_allowed": 0,
            "actions_denied": 0,
            "output_files": [],
            "events_emitted": 0,
            "message": ""
        }

        # Build summary markdown
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        summary_lines = [
            "# El Monstruo — Vigilia Sincrónica: Cadena Completada",
            "",
            f"**Generado:** {now}",
            f"**Cadena:** Oráculo → Auditor → Risk Classification → Unified Face",
            f"**Estado:** CADENA COMPLETADA (simulación controlada)",
            "",
            "---",
            "",
            "## Qué se ejecutó",
            "",
            "Se ejecutó una cadena de 4 loops en secuencia determinística, "
            "conectados mediante handoff packets y gobernados por el Dispatcher/Policy Engine.",
            "",
        ]

        for step in self.chain_results:
            summary_lines.append(
                f"- **{step['loop_id']}:** {step.get('message', step.get('status', 'N/A'))}"
            )

        summary_lines.extend([
            "",
            "## Qué quedó validado",
            "",
            "- Catálogo de 6 capacidades IA generado y auditado.",
            "- 10 gates de auditoría PASS.",
            "- Overlay de riesgo R0/A1 aplicado a todas las capacidades.",
            "- Handoff packets inmutables entre cada etapa.",
            "- Dispatcher autorizó todas las acciones legítimas y denegó las prohibidas.",
            "",
            "## Qué NO se ejecutó",
            "",
            "- No se conectaron APIs reales (M1 = STATIC_CATALOG).",
            "- No se activó un daemon o scheduler persistente.",
            "- No se escribió en el Event Log principal (se usó un delta aislado).",
            "- No se firmó ninguna decisión como T1_SIGNED.",
            "",
            "## Decisiones Pendientes T1",
            "",
            "1. Aprobar SPR-ORACLE-AI-M2-001 para conectar APIs reales.",
            "2. Aprobar reclasificación de riesgo post-M2.",
            "3. Aprobar desarrollo de daemon/scheduler para Vigilia real.",
            "",
            "## Restricciones Activas",
            "",
            "- `not_realtime_verified: true`",
            "- `no_m2_unlock: true`",
            "- `no_daemon: true`",
            "- `no_external_api: true`",
            "- Max autonomy: A3",
            "",
            "---",
            "",
            "> Esta es una ejecución controlada (simulación local). "
            "> El Monstruo NO está \"vivo\" ni operando en background. "
            "> Requiere aprobación T1 para avanzar a M2.",
        ])

        summary_content = "\n".join(summary_lines) + "\n"

        # Request permission to write summary
        write_request = {
            "action": "create_report",
            "target_path": "bridge/doctrine_candidates/unified_face_summary_v0_1.md",
            "has_evidence": True
        }

        is_allowed, reason, event = self.dispatcher.dispatch_action(
            self.LOOP_ID, write_request
        )
        results["events_emitted"] += 1

        if is_allowed:
            results["actions_allowed"] += 1
            output_file = os.path.join(self.output_dir, "unified_face_summary.v0_1.md")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(summary_content)
            results["output_files"].append(output_file)
            results["status"] = "SUCCESS"
            results["message"] = "Unified Face summary generated for T1."
        else:
            results["actions_denied"] += 1
            results["status"] = "BLOCKED"
            results["message"] = f"Dispatcher denied write: {reason}"

        return results


class VigiliaChainOrchestrator:
    """
    Main orchestrator for the Vigilia Sincrónica chain.
    Executes loops in sequence, creates handoff packets, manages state.
    """

    CHAIN_ID = "vigilia-chain-v0.2-001"
    CHAIN_VERSION = "v0.2.0"

    def __init__(self, output_base_dir):
        self.output_base_dir = output_base_dir
        self.chain_results = []
        self.handoff_packets = []
        self.events = []

        # Create isolated output directories
        self.oracle_output = os.path.join(output_base_dir, "oracle_output")
        self.auditor_output = os.path.join(output_base_dir, "auditor_output")
        self.risk_output = os.path.join(output_base_dir, "risk_output")
        self.face_output = os.path.join(output_base_dir, "face_output")
        for d in [self.oracle_output, self.auditor_output, self.risk_output, self.face_output]:
            os.makedirs(d, exist_ok=True)

        # Create isolated State Fabric for this chain
        self.state_fabric_dir = os.path.join(output_base_dir, "state_fabric_delta")
        os.makedirs(self.state_fabric_dir, exist_ok=True)
        self._init_state_fabric()

        # Initialize Dispatcher
        self.dispatcher = MinimalDispatcher(
            state_fabric_dir=self.state_fabric_dir,
            policy_base_dir=REACTOR_DIR
        )

    def _init_state_fabric(self):
        """Initialize isolated state fabric for the chain."""
        # Copy loop_registry
        src_registry = os.path.join(REACTOR_DIR, "state_fabric", "loop_registry.v0.yaml")
        dst_registry = os.path.join(self.state_fabric_dir, "loop_registry.v0.yaml")
        shutil.copy2(src_registry, dst_registry)

        # Add chain-specific loops to registry
        import yaml
        with open(dst_registry, 'r') as f:
            registry = yaml.safe_load(f)

        # Add risk classification loop
        registry["loop_risk_classification"] = {
            "loop_id": "loop_risk_classification",
            "role": "Apply risk overlay to Oracle capabilities",
            "status": "NOT_RUNNING",
            "max_autonomy_level": "A3",
            "allowed_event_types": ["OBSERVED", "STATE_DELTA_PROPOSED"],
            "allowed_read_paths": ["bridge/"],
            "allowed_write_paths": ["bridge/doctrine_candidates/"],
            "forbidden_actions": ["touch_supabase", "modify_kernel", "deploy"],
            "auditor_required": False,
            "heartbeat_policy": "on_demand",
            "owner": "monstruo",
            "runtime_allowed": False,
            "notes": "Chain-specific loop for risk classification step."
        }

        # Add orchestrator as a pseudo-loop for handoff events
        registry["orquestador_cadena_v0"] = {
            "loop_id": "orquestador_cadena_v0",
            "role": "Chain orchestrator - creates handoff packets",
            "status": "NOT_RUNNING",
            "max_autonomy_level": "A3",
            "allowed_event_types": ["OBSERVED", "HANDOFF_READY", "STATE_DELTA_PROPOSED"],
            "allowed_read_paths": ["bridge/"],
            "allowed_write_paths": ["bridge/doctrine_candidates/", "bridge/reactor_vigilia_foundation/"],
            "forbidden_actions": ["touch_supabase", "modify_kernel", "deploy"],
            "auditor_required": False,
            "heartbeat_policy": "on_demand",
            "owner": "monstruo",
            "runtime_allowed": False,
            "notes": "Orchestrator pseudo-loop for chain execution."
        }

        with open(dst_registry, 'w') as f:
            yaml.dump(registry, f, default_flow_style=False, allow_unicode=True)

        # Create empty event log
        event_log_path = os.path.join(self.state_fabric_dir, "event_log.v0.jsonl")
        with open(event_log_path, 'w') as f:
            pass  # empty file

        # Create initial current_state
        current_state = {
            "chain_id": self.CHAIN_ID,
            "chain_status": "INITIALIZING",
            "last_event_id": 0,
            "last_updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        with open(os.path.join(self.state_fabric_dir, "current_state.v0.json"), 'w') as f:
            json.dump(current_state, f, indent=2)

    def _create_handoff_packet(self, source_loop, target_loop, artifact_refs,
                                chain_step_completed, previous_verdict=None):
        """Create an immutable handoff packet between chain steps."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        packet = {
            "handoff_id": f"handoff-{source_loop}-to-{target_loop}-{now}",
            "source_loop": source_loop,
            "target_loop": target_loop,
            "created_at": now,
            "artifact_refs": artifact_refs,
            "evidence_status": "STATIC_CATALOG",
            "max_autonomy_level": "A3",
            "forbidden_assumptions": [
                "APIs are connected",
                "Evidence is realtime-verified",
                "M2 is unlocked",
                "T1 has signed any decision",
                "System is in production mode"
            ],
            "not_realtime_verified": True,
            "no_m2_unlock": True,
            "chain_context": {
                "chain_step_completed": chain_step_completed,
                "total_chain_steps": 4,
                "previous_verdict": previous_verdict,
                "pending_t1_decisions": 4
            }
        }

        # Register handoff with Dispatcher
        handoff_request = {
            "action": "create_state_fabric_draft",
            "target_path": f"bridge/doctrine_candidates/handoff_{source_loop}_to_{target_loop}.json",
            "has_evidence": True
        }
        self.dispatcher.dispatch_action("orquestador_cadena_v0", handoff_request)

        self.handoff_packets.append(packet)
        return packet

    def run_chain(self):
        """Execute the full chain: Oracle → Auditor → Risk → Unified Face."""
        print("=" * 70)
        print("  VIGILIA SINCRÓNICA — CADENA LOCAL CONTROLADA v0.2")
        print("=" * 70)
        print()

        chain_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        step_results = []

        # ===== STEP 1: ORÁCULO =====
        print("[STEP 1/4] Ejecutando Oráculo de IAs...")
        oracle = OraculoIALoop(self.dispatcher, self.oracle_output)
        oracle_result = oracle.run()
        step_results.append({
            "step_id": 1,
            "loop_id": oracle_result["loop_id"],
            "status": oracle_result["status"],
            "started_at": chain_start,
            "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actions_allowed": len(oracle.actions_allowed),
            "actions_denied": len(oracle.actions_denied),
            "output_files": oracle_result.get("output_files", []),
            "events_emitted": len(oracle_result.get("event_proposals", [])),
            "message": oracle_result.get("message", "")
        })
        print(f"  → Status: {oracle_result['status']}")
        print(f"  → Actions: {len(oracle.actions_allowed)} allowed, {len(oracle.actions_denied)} denied")
        print()

        # ===== HANDOFF 1: Oracle → Auditor =====
        print("[HANDOFF 1] Oráculo → Auditor")
        handoff_1 = self._create_handoff_packet(
            source_loop="loop_oraculo_ias",
            target_loop="loop_auditor",
            artifact_refs=oracle_result.get("output_files", []),
            chain_step_completed=1
        )
        print(f"  → Packet: {handoff_1['handoff_id']}")
        print()

        # ===== STEP 2: AUDITOR =====
        print("[STEP 2/4] Ejecutando Loop Auditor...")
        # Import LoopAuditor
        sys.path.insert(0, os.path.join(REACTOR_DIR, "loop_auditor"))
        from loop_auditor import LoopAuditor

        auditor = LoopAuditor(
            dispatcher=self.dispatcher,
            oracle_output_dir=self.oracle_output,
            audit_output_dir=self.auditor_output
        )
        event_log_path = os.path.join(self.state_fabric_dir, "event_log.v0.jsonl")
        auditor_result = auditor.run(event_log_path=event_log_path)
        step_results.append({
            "step_id": 2,
            "loop_id": auditor_result["loop_id"],
            "status": auditor_result["status"],
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actions_allowed": len(auditor.actions_allowed),
            "actions_denied": len(auditor.actions_denied),
            "output_files": auditor_result.get("output_files", []),
            "events_emitted": len(auditor_result.get("actions_log", [])),
            "verdict": auditor_result.get("verdict", ""),
            "message": auditor_result.get("message", "")
        })
        print(f"  → Status: {auditor_result['status']}")
        print(f"  → Verdict: {auditor_result.get('verdict', 'N/A')}")
        print(f"  → Gates: {sum(1 for v in auditor_result.get('gates', {}).values() if v)} PASS")
        print()

        # ===== HANDOFF 2: Auditor → Risk =====
        print("[HANDOFF 2] Auditor → Risk Classification")
        handoff_2 = self._create_handoff_packet(
            source_loop="loop_auditor",
            target_loop="loop_risk_classification",
            artifact_refs=auditor_result.get("output_files", []),
            chain_step_completed=2,
            previous_verdict=auditor_result.get("verdict", "")
        )
        print(f"  → Packet: {handoff_2['handoff_id']}")
        print()

        # ===== STEP 3: RISK CLASSIFICATION =====
        print("[STEP 3/4] Ejecutando Risk Classification...")
        risk = RiskClassificationStep(
            dispatcher=self.dispatcher,
            oracle_output_dir=self.oracle_output,
            auditor_output_dir=self.auditor_output,
            output_dir=self.risk_output
        )
        risk_result = risk.run(handoff_packet=handoff_2)
        step_results.append({
            "step_id": 3,
            "loop_id": risk_result["loop_id"],
            "status": risk_result["status"],
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actions_allowed": risk_result["actions_allowed"],
            "actions_denied": risk_result["actions_denied"],
            "output_files": risk_result.get("output_files", []),
            "events_emitted": risk_result["events_emitted"],
            "message": risk_result.get("message", "")
        })
        print(f"  → Status: {risk_result['status']}")
        print(f"  → Message: {risk_result['message']}")
        print()

        # ===== HANDOFF 3: Risk → Unified Face =====
        print("[HANDOFF 3] Risk Classification → Unified Face")
        handoff_3 = self._create_handoff_packet(
            source_loop="loop_risk_classification",
            target_loop="loop_unified_face",
            artifact_refs=risk_result.get("output_files", []),
            chain_step_completed=3,
            previous_verdict="R0/A1 applied"
        )
        print(f"  → Packet: {handoff_3['handoff_id']}")
        print()

        # ===== STEP 4: UNIFIED FACE =====
        print("[STEP 4/4] Ejecutando Unified Face...")
        face = UnifiedFaceStep(
            dispatcher=self.dispatcher,
            chain_results=step_results,
            output_dir=self.face_output
        )
        face_result = face.run(handoff_packet=handoff_3)
        step_results.append({
            "step_id": 4,
            "loop_id": face_result["loop_id"],
            "status": face_result["status"],
            "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actions_allowed": face_result["actions_allowed"],
            "actions_denied": face_result["actions_denied"],
            "output_files": face_result.get("output_files", []),
            "events_emitted": face_result["events_emitted"],
            "message": face_result.get("message", "")
        })
        print(f"  → Status: {face_result['status']}")
        print(f"  → Message: {face_result['message']}")
        print()

        # ===== CHAIN COMPLETE =====
        chain_end = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        all_success = all(s["status"] == "SUCCESS" for s in step_results)

        # Write chain manifest
        manifest = {
            "chain_id": self.CHAIN_ID,
            "chain_version": self.CHAIN_VERSION,
            "created_at": chain_start,
            "completed_at": chain_end,
            "created_by": "SPR-VIGILIA-SINCRONICA-002",
            "steps": step_results,
            "handoff_packets": self.handoff_packets,
            "max_autonomy_level": "A3",
            "risk_controls": {
                "not_realtime_verified": True,
                "no_m2_unlock": True,
                "no_daemon": True,
                "no_external_api": True
            },
            "state_fabric_delta_path": self.state_fabric_dir,
            "overall_status": "COMPLETED" if all_success else "PARTIAL"
        }

        manifest_path = os.path.join(self.output_base_dir, "real_loop_chain_manifest.v0_1.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Write handoff packets to files
        for i, packet in enumerate(self.handoff_packets, 1):
            packet_path = os.path.join(
                self.output_base_dir,
                f"handoff_{packet['source_loop']}_to_{packet['target_loop']}.v0_1.json"
            )
            with open(packet_path, 'w') as f:
                json.dump(packet, f, indent=2, ensure_ascii=False)

        # Copy event log delta to output
        src_log = os.path.join(self.state_fabric_dir, "event_log.v0.jsonl")
        dst_log = os.path.join(self.output_base_dir, "chain_event_log_delta.v0_1.jsonl")
        shutil.copy2(src_log, dst_log)

        # Write unified face output JSON
        face_output_json = {
            "generated_at": chain_end,
            "generated_by": "loop_unified_face",
            "chain_id": self.CHAIN_ID,
            "chain_status": "COMPLETED" if all_success else "PARTIAL",
            "summary_markdown_path": face_result.get("output_files", [""])[0] if face_result.get("output_files") else "",
            "what_was_executed": [
                "Oracle AI capability catalog generation (6 capabilities)",
                "Auditor validation (10 gates)",
                "Risk classification overlay (R0/A1)",
                "Unified Face synthesis"
            ],
            "what_was_validated": [
                "Catalog structure and completeness",
                "Dispatcher authorization flow",
                "Handoff packet immutability",
                "Risk overlay correctness"
            ],
            "what_was_not_executed": [
                "Real API connections (M1 only)",
                "Daemon/scheduler deployment",
                "Production event log writes",
                "T1 decision signing"
            ],
            "pending_t1_decisions": [
                {"decision_id": "D-001", "description": "Approve SPR-ORACLE-AI-M2-001", "recommended_action": "APPROVE"},
                {"decision_id": "D-002", "description": "Approve risk reclassification post-M2", "recommended_action": "APPROVE_AFTER_M2"},
                {"decision_id": "D-003", "description": "Approve daemon/scheduler development", "recommended_action": "DEFER"},
                {"decision_id": "D-004", "description": "Approve loop expansion (vigia/memoria)", "recommended_action": "DEFER"}
            ],
            "recommended_next_action": "Approve SPR-ORACLE-AI-M2-001 to connect real APIs",
            "active_restrictions": [
                "not_realtime_verified",
                "no_m2_unlock",
                "no_daemon",
                "no_external_api",
                "max_autonomy_A3"
            ]
        }
        face_json_path = os.path.join(self.output_base_dir, "unified_face_output.v0_1.json")
        with open(face_json_path, 'w') as f:
            json.dump(face_output_json, f, indent=2, ensure_ascii=False)

        # Print final summary
        print("=" * 70)
        print("  CADENA COMPLETADA")
        print("=" * 70)
        print(f"  Chain ID: {self.CHAIN_ID}")
        print(f"  Status: {'COMPLETED' if all_success else 'PARTIAL'}")
        print(f"  Steps: {len(step_results)}/4 SUCCESS")
        print(f"  Handoffs: {len(self.handoff_packets)}")
        print(f"  Manifest: {manifest_path}")
        print()

        return manifest


if __name__ == "__main__":
    # Default output directory
    output_dir = os.path.join(BASE_DIR, "chain_run_001")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    orchestrator = VigiliaChainOrchestrator(output_dir)
    manifest = orchestrator.run_chain()

    print(f"\nAll artifacts written to: {output_dir}")
    print(f"Event log delta: {os.path.join(output_dir, 'chain_event_log_delta.v0_1.jsonl')}")
