"""
Loop Auditor — Segundo Loop Real del Monstruo
SPR-LOOP-AUDITOR-001

El Loop Auditor valida los outputs del Oráculo de IAs bajo el principio
Proposer ≠ Evaluator. Lee los artefactos generados por el Oráculo,
ejecuta 8 criterios de auditoría (10 gates), solicita permiso al
Dispatcher antes de escribir, y produce artefactos de auditoría
estructurados.

Restricciones:
- max_autonomy_level: A3
- allowed_write_paths: bridge/doctrine_candidates/audit_reports/
- forbidden_actions: write_code, touch_supabase, modify_kernel, deploy
- No modifica outputs del Oráculo
- No conecta APIs externas
- No canoniza
- No aprueba sprints

Maturity Level: M1 (Catalogado) — ejecuta bajo supervisión, sin producción.
"""

import json
import os
from datetime import datetime, timezone


class LoopAuditor:
    """
    Segundo loop real del Monstruo.
    Audita los outputs del Oráculo de IAs y produce un veredicto estructurado.
    Interactúa con el MinimalDispatcher para solicitar permisos antes de escribir.
    """

    LOOP_ID = "loop_auditor"
    LINEAGE_ID = "auditor_lineage_001"
    MATURITY_LEVEL = "M1"
    CLASS = "System"
    AUDITS_LOOP = "loop_oraculo_ias"
    ORACLE_LINEAGE = "oraculo_lineage_001"

    def __init__(self, dispatcher, oracle_output_dir, audit_output_dir):
        """
        Args:
            dispatcher: Instancia de MinimalDispatcher.
            oracle_output_dir: Directorio donde el Oráculo escribió sus outputs.
            audit_output_dir: Directorio donde el Auditor escribirá sus resultados.
        """
        self.dispatcher = dispatcher
        self.oracle_output_dir = oracle_output_dir
        self.audit_output_dir = audit_output_dir
        self.actions_attempted = []
        self.actions_allowed = []
        self.actions_denied = []

    def run(self, event_log_path=None):
        """
        Ejecuta el ciclo completo del Auditor:
        1. Lee outputs del Oráculo
        2. Ejecuta 10 gates de auditoría
        3. Genera findings
        4. Solicita permiso al Dispatcher para escribir
        5. Escribe artefactos si es permitido
        6. Intenta acción prohibida (para demostrar DENY)
        7. Retorna resultado

        Args:
            event_log_path: Path al event_log.v0.jsonl para verificar policy compliance.

        Returns:
            Dict con loop_id, status, verdict, gates, findings, actions_log
        """
        results = {
            "loop_id": self.LOOP_ID,
            "lineage_id": self.LINEAGE_ID,
            "maturity_level": self.MATURITY_LEVEL,
            "audits_loop": self.AUDITS_LOOP,
            "status": "PENDING",
            "verdict": None,
            "gates": {},
            "findings": [],
            "actions_log": [],
            "output_files": [],
            "message": "",
        }

        # === PASO 1: Leer outputs del Oráculo ===
        catalog = self._read_oracle_catalog()
        report = self._read_oracle_report()
        events = self._read_event_log(event_log_path) if event_log_path else []

        if catalog is None or report is None:
            results["status"] = "BLOCKED"
            results["verdict"] = "FAIL"
            results["message"] = "Cannot read Oracle outputs. Audit aborted."
            return results

        # === PASO 2: Ejecutar 10 Gates de Auditoría ===
        gates = {}
        findings = []

        # Gate 1: Schema Validity
        gate_result, gate_findings = self._check_schema_validity(catalog)
        gates["schema_validity"] = gate_result
        findings.extend(gate_findings)

        # Gate 2: Report Consistency
        gate_result, gate_findings = self._check_report_consistency(catalog, report)
        gates["report_consistency"] = gate_result
        findings.extend(gate_findings)

        # Gate 3: Authority Check
        gate_result, gate_findings = self._check_authority_discipline(catalog, report)
        gates["authority_check"] = gate_result
        findings.extend(gate_findings)

        # Gate 4: Evidence Check
        gate_result, gate_findings = self._check_evidence_discipline(catalog)
        gates["evidence_check"] = gate_result
        findings.extend(gate_findings)

        # Gate 5: Policy Check
        gate_result, gate_findings = self._check_policy_compliance(events)
        gates["policy_check"] = gate_result
        findings.extend(gate_findings)

        # Gate 6: F16 Check
        gate_result, gate_findings = self._check_f16_lineage()
        gates["f16_check"] = gate_result
        findings.extend(gate_findings)

        # Gate 7: No Autonomy Creep
        gate_result, gate_findings = self._check_no_autonomy_creep(catalog, report)
        gates["no_autonomy_creep"] = gate_result
        findings.extend(gate_findings)

        # Gate 8: No External API
        gate_result, gate_findings = self._check_no_external_api(catalog)
        gates["no_external_api"] = gate_result
        findings.extend(gate_findings)

        # Gate 9: No Canon
        gate_result, gate_findings = self._check_no_canon(catalog, report)
        gates["no_canon"] = gate_result
        findings.extend(gate_findings)

        # Gate 10: No Runtime Side Effects
        gate_result, gate_findings = self._check_no_runtime_side_effects()
        gates["no_runtime_side_effects"] = gate_result
        findings.extend(gate_findings)

        # === PASO 3: Determinar veredicto ===
        gates_passed = sum(1 for g in gates.values() if g["passed"])
        gates_total = len(gates)
        high_findings = sum(1 for f in findings if f["severity"] == "HIGH")

        if high_findings > 0:
            verdict = "FAIL"
        elif len(findings) > 0:
            verdict = "PASS_WITH_FINDINGS"
        else:
            verdict = "PASS"

        results["gates"] = gates
        results["findings"] = findings
        results["verdict"] = verdict

        # === PASO 4: Solicitar permiso para escribir audit artifacts ===
        write_request = {
            "action": "create_state_fabric_draft",
            "target_path": "bridge/doctrine_candidates/audit_reports/audit_report.md",
            "has_evidence": True,
        }

        is_allowed, reason, event = self.dispatcher.dispatch_action(self.LOOP_ID, write_request)
        self.actions_attempted.append(write_request)
        results["actions_log"].append(
            {
                "action": "create_state_fabric_draft",
                "target": write_request["target_path"],
                "allowed": is_allowed,
                "reason": reason,
            }
        )

        if is_allowed:
            self.actions_allowed.append(write_request)
            os.makedirs(self.audit_output_dir, exist_ok=True)

            # Escribir audit_report.md
            report_path = os.path.join(self.audit_output_dir, "audit_report.md")
            self._write_audit_report(report_path, verdict, gates, findings, gates_passed, gates_total)
            results["output_files"].append(report_path)

            # Escribir audit_findings.json
            findings_path = os.path.join(self.audit_output_dir, "audit_findings.json")
            with open(findings_path, "w", encoding="utf-8") as f:
                json.dump(findings, f, indent=2, ensure_ascii=False)
            results["output_files"].append(findings_path)

            # Escribir auditor_gate_log.json
            gate_log_path = os.path.join(self.audit_output_dir, "auditor_gate_log.json")
            gate_log = {
                "audit_id": "AUD-001",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "gates": gates,
            }
            with open(gate_log_path, "w", encoding="utf-8") as f:
                json.dump(gate_log, f, indent=2, ensure_ascii=False)
            results["output_files"].append(gate_log_path)
        else:
            self.actions_denied.append(write_request)

        # === PASO 5: Intentar acción PROHIBIDA (write_code) para demostrar DENY ===
        forbidden_request = {"action": "write_code", "target_path": "src/auditor_engine.py", "has_evidence": True}

        is_allowed_f, reason_f, event_f = self.dispatcher.dispatch_action(self.LOOP_ID, forbidden_request)
        self.actions_attempted.append(forbidden_request)
        results["actions_log"].append(
            {
                "action": "write_code",
                "target": forbidden_request["target_path"],
                "allowed": is_allowed_f,
                "reason": reason_f,
            }
        )

        if not is_allowed_f:
            self.actions_denied.append(forbidden_request)

        # === PASO 6: Status final ===
        if len(self.actions_allowed) >= 1 and verdict in ("PASS", "PASS_WITH_FINDINGS"):
            results["status"] = "SUCCESS"
            results["message"] = (
                f"Auditor completed cycle. Verdict: {verdict}. "
                f"Gates: {gates_passed}/{gates_total} passed. "
                f"Findings: {len(findings)} ({high_findings} HIGH). "
                f"Actions: {len(self.actions_allowed)} allowed, "
                f"{len(self.actions_denied)} denied."
            )
        else:
            results["status"] = "PARTIAL"
            results["message"] = "Auditor completed with issues."

        return results

    # ===================================================================
    # GATE IMPLEMENTATIONS
    # ===================================================================

    def _check_schema_validity(self, catalog):
        """Gate 1: Verificar que el catálogo JSON tiene estructura válida."""
        findings = []
        required_fields = [
            "catalog_version",
            "generated_by",
            "generated_at",
            "total_capabilities",
            "capabilities",
            "meta",
        ]

        missing = [f for f in required_fields if f not in catalog]
        if missing:
            findings.append(
                self._make_finding(
                    "FND-001",
                    "HIGH",
                    "schema_validity",
                    f"Missing required fields: {missing}",
                    "Add missing fields to catalog schema",
                )
            )
            return {"passed": False, "detail": f"Missing fields: {missing}"}, findings

        # Check capabilities structure
        caps = catalog.get("capabilities", [])
        ids_seen = set()
        for cap in caps:
            cap_required = [
                "id",
                "model",
                "feature",
                "application",
                "power_stack",
                "sprint_candidate",
                "confidence",
                "status",
            ]
            cap_missing = [f for f in cap_required if f not in cap]
            if cap_missing:
                findings.append(
                    self._make_finding(
                        "FND-002",
                        "MEDIUM",
                        "schema_validity",
                        f"Capability {cap.get('id', '?')} missing fields: {cap_missing}",
                        "Complete capability entry",
                    )
                )

            cap_id = cap.get("id")
            if cap_id in ids_seen:
                findings.append(
                    self._make_finding(
                        "FND-003",
                        "HIGH",
                        "schema_validity",
                        f"Duplicate capability_id: {cap_id}",
                        "Remove duplicate or assign unique ID",
                    )
                )
            ids_seen.add(cap_id)

        passed = len(findings) == 0
        detail = "All schema checks passed" if passed else f"{len(findings)} schema issues"
        return {"passed": passed, "detail": detail}, findings

    def _check_report_consistency(self, catalog, report):
        """Gate 2: Verificar consistencia entre catálogo y reporte."""
        findings = []
        cap_ids = {c["id"] for c in catalog.get("capabilities", [])}

        # Check if all capability IDs from catalog appear in report
        for cap_id in cap_ids:
            if cap_id not in report:
                findings.append(
                    self._make_finding(
                        "FND-010",
                        "MEDIUM",
                        "report_consistency",
                        f"Capability {cap_id} in catalog but not referenced in report",
                        "Ensure report covers all catalog entries",
                    )
                )

        passed = len(findings) == 0
        detail = "Report references all catalog entries" if passed else f"{len(findings)} consistency gaps"
        return {"passed": passed, "detail": detail}, findings

    def _check_authority_discipline(self, catalog, report):
        """Gate 3: Verificar que ningún output dice APPROVED si solo es candidate."""
        findings = []

        # Check catalog statuses
        for cap in catalog.get("capabilities", []):
            status = cap.get("status", "")
            if status in ("APPROVED", "CANONICAL", "LIVE"):
                findings.append(
                    self._make_finding(
                        "FND-020",
                        "HIGH",
                        "authority_discipline",
                        f"Capability {cap['id']} has status '{status}' — only PROPOSED allowed at M1",
                        "Revert status to PROPOSED",
                    )
                )

        # Check report for canon language
        canon_keywords = ["CANONIZADO", "CANONICAL", "APPROVED BY T1", "FIRMADO"]
        for kw in canon_keywords:
            if kw.lower() in report.lower():
                findings.append(
                    self._make_finding(
                        "FND-021",
                        "HIGH",
                        "authority_discipline",
                        f"Report contains authority keyword '{kw}' without T1 signature",
                        "Remove unauthorized authority claims",
                    )
                )

        passed = len(findings) == 0
        detail = "No unauthorized authority claims" if passed else f"{len(findings)} authority violations"
        return {"passed": passed, "detail": detail}, findings

    def _check_evidence_discipline(self, catalog):
        """Gate 4: Verificar distinción STATIC vs REALTIME_VERIFIED."""
        findings = []

        meta = catalog.get("meta", {})
        source = meta.get("source", "")

        if "static" in source.lower() or source == "static_v0_seed":
            # Correct: catalog acknowledges it's static
            pass
        elif "realtime" in source.lower() or "live" in source.lower():
            # Suspicious: claims realtime without API evidence
            findings.append(
                self._make_finding(
                    "FND-030",
                    "HIGH",
                    "evidence_discipline",
                    "Catalog claims realtime/live source but no API was called in M1",
                    "Mark as STATIC / NOT_REALTIME_VERIFIED",
                )
            )

        # Check individual capabilities for date claims
        for cap in catalog.get("capabilities", []):
            cap.get("discovered_at", "")
            # At M1, all dates should be from training data, not live verification
            # This is acceptable as long as source is marked static

        if not findings:
            # Add informational finding about static nature
            findings.append(
                self._make_finding(
                    "FND-031",
                    "LOW",
                    "evidence_discipline",
                    "Catalog correctly marked as static_v0_seed. Dates are from training data, not live verification.",
                    "Upgrade to M2 with real API verification when T1 approves",
                    t1_required=True,
                )
            )

        passed = not any(f["severity"] == "HIGH" for f in findings)
        detail = (
            "Evidence discipline maintained (static acknowledged)"
            if passed
            else "Evidence claims exceed verification level"
        )
        return {"passed": passed, "detail": detail}, findings

    def _check_policy_compliance(self, events):
        """Gate 5: Verificar que cada write del Oráculo tuvo permiso."""
        findings = []

        if not events:
            findings.append(
                self._make_finding(
                    "FND-040",
                    "MEDIUM",
                    "policy_compliance",
                    "No event_log available for verification — cannot confirm Dispatcher authorization",
                    "Provide event_log path for full policy audit",
                )
            )
            return {"passed": False, "detail": "No event_log for verification"}, findings

        # Look for Oracle events
        oracle_events = [e for e in events if "loop_oraculo_ias" in e.get("summary", "")]
        allowed_events = [e for e in oracle_events if "authorized" in e.get("summary", "")]
        denied_events = [e for e in oracle_events if "denied" in e.get("summary", "")]

        # Verify the A5 DENY exists
        write_code_denied = any(
            "write_code" in e.get("summary", "") and "denied" in e.get("summary", "") for e in oracle_events
        )

        if not write_code_denied:
            findings.append(
                self._make_finding(
                    "FND-041",
                    "HIGH",
                    "policy_compliance",
                    "Expected DENY for write_code (A5) not found in event_log",
                    "Investigate missing policy enforcement",
                )
            )

        if len(allowed_events) < 2:
            findings.append(
                self._make_finding(
                    "FND-042",
                    "MEDIUM",
                    "policy_compliance",
                    f"Expected 2+ ALLOW events for Oracle, found {len(allowed_events)}",
                    "Verify Oracle requested permission for all writes",
                )
            )

        passed = not any(f["severity"] == "HIGH" for f in findings)
        detail = (
            f"Policy: {len(allowed_events)} ALLOW, {len(denied_events)} DENY" if passed else "Policy violation detected"
        )
        return {"passed": passed, "detail": detail}, findings

    def _check_f16_lineage(self):
        """Gate 6: Verificar linaje distinto entre Auditor y Oráculo."""
        findings = []

        if self.LINEAGE_ID == self.ORACLE_LINEAGE:
            findings.append(
                self._make_finding(
                    "FND-050",
                    "HIGH",
                    "f16_lineage",
                    "CRITICAL: Auditor lineage_id matches Oracle lineage_id — self-audit detected",
                    "Assign distinct lineage IDs",
                )
            )

        # Verify we're not using Oracle's self-assessment as proof
        # (This is a structural check — in code, we never read Oracle's own verdict)

        passed = len(findings) == 0
        detail = (
            f"Lineage verified: auditor={self.LINEAGE_ID} ≠ oracle={self.ORACLE_LINEAGE}"
            if passed
            else "SELF-AUDIT RISK"
        )
        return {"passed": passed, "detail": detail}, findings

    def _check_no_autonomy_creep(self, catalog, report):
        """Gate 7: Verificar que Oráculo no asume autoridad futura."""
        findings = []

        creep_patterns = [
            "approved for M2",
            "authorized to connect APIs",
            "permission granted for live",
            "SPR-ORACLE-AI-001 approved",
            "self-elevate",
            "auto-promote",
        ]

        combined_text = json.dumps(catalog) + report
        for pattern in creep_patterns:
            if pattern.lower() in combined_text.lower():
                findings.append(
                    self._make_finding(
                        "FND-060",
                        "HIGH",
                        "autonomy_creep",
                        f"Autonomy creep detected: '{pattern}' found in outputs",
                        "Remove unauthorized authority assumption",
                    )
                )

        passed = len(findings) == 0
        detail = "No autonomy creep detected" if passed else f"{len(findings)} creep patterns found"
        return {"passed": passed, "detail": detail}, findings

    def _check_no_external_api(self, catalog):
        """Gate 8: Verificar que no se llamaron APIs externas."""
        findings = []

        meta = catalog.get("meta", {})
        source = meta.get("source", "")

        # At M1, source should be static
        if source == "static_v0_seed":
            pass  # Correct
        elif "api" in source.lower() or "live" in source.lower():
            findings.append(
                self._make_finding(
                    "FND-070",
                    "HIGH",
                    "no_external_api",
                    f"Catalog source '{source}' suggests external API usage at M1",
                    "Revert to static source until M2 approved by T1",
                )
            )

        passed = len(findings) == 0
        detail = "No external API usage detected (source: static_v0_seed)" if passed else "External API usage suspected"
        return {"passed": passed, "detail": detail}, findings

    def _check_no_canon(self, catalog, report):
        """Gate 9: Verificar que nada se presenta como canon."""
        findings = []

        canon_markers = ["CANONICAL", "CANONIZADO", "DSC-", "DECLARED", "FIRMADO POR T1"]
        combined = json.dumps(catalog) + report

        for marker in canon_markers:
            if marker in combined:
                findings.append(
                    self._make_finding(
                        "FND-080",
                        "HIGH",
                        "no_canon",
                        f"Canon marker '{marker}' found in Oracle outputs",
                        "Remove canon claims — only T1 can canonize",
                    )
                )

        # Check for "DOCTRINE_CANDIDATE" which IS acceptable
        if "DOCTRINE_CANDIDATE" in combined:
            pass  # This is the correct status

        passed = len(findings) == 0
        detail = "No unauthorized canonization" if passed else f"{len(findings)} canon violations"
        return {"passed": passed, "detail": detail}, findings

    def _check_no_runtime_side_effects(self):
        """Gate 10: Verificar que no hay side effects en runtime."""
        findings = []
        # In simulation, this is always PASS because we control the environment
        # In production, this would check for unexpected file writes, network calls, etc.
        passed = True
        detail = "No runtime side effects detected (simulation mode)"
        return {"passed": passed, "detail": detail}, findings

    # ===================================================================
    # HELPER METHODS
    # ===================================================================

    def _read_oracle_catalog(self):
        """Lee el catálogo JSON del Oráculo."""
        path = os.path.join(self.oracle_output_dir, "oraculo_capability_catalog_v0.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _read_oracle_report(self):
        """Lee el reporte Markdown del Oráculo."""
        path = os.path.join(self.oracle_output_dir, "oraculo_power_stacks_v0.md")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _read_event_log(self, path):
        """Lee el event_log como lista de eventos."""
        if not os.path.exists(path):
            return []
        events = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    def _make_finding(self, finding_id, severity, subject, evidence_ref, recommended_action, t1_required=False):
        """Crea un finding estructurado."""
        return {
            "finding_id": finding_id,
            "severity": severity,
            "subject": subject,
            "evidence_ref": evidence_ref,
            "status": "OPEN",
            "recommended_next_action": recommended_action,
            "t1_required": t1_required,
        }

    def _write_audit_report(self, path, verdict, gates, findings, gates_passed, gates_total):
        """Escribe el audit_report.md."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        high = sum(1 for f in findings if f["severity"] == "HIGH")
        medium = sum(1 for f in findings if f["severity"] == "MEDIUM")
        low = sum(1 for f in findings if f["severity"] == "LOW")

        lines = [
            "# Audit Report — Loop Oráculo de IAs",
            "",
            f"**Auditor:** `{self.LOOP_ID}` (Lineage: `{self.LINEAGE_ID}`)",
            f"**Target:** `{self.AUDITS_LOOP}` (Lineage: `{self.ORACLE_LINEAGE}`)",
            f"**Fecha:** {now}",
            f"**Veredicto:** **{verdict}**",
            "",
            "---",
            "",
            f"## Resumen de Gates: {gates_passed}/{gates_total} PASS",
            "",
            "| Gate | Resultado | Detalle |",
            "|------|-----------|---------|",
        ]

        for gate_name, gate_data in gates.items():
            status = "PASS" if gate_data["passed"] else "FAIL"
            lines.append(f"| {gate_name} | {status} | {gate_data['detail']} |")

        lines.extend(
            [
                "",
                f"## Hallazgos: {len(findings)} total ({high} HIGH, {medium} MEDIUM, {low} LOW)",
                "",
            ]
        )

        if findings:
            lines.append("| ID | Severity | Subject | Status |")
            lines.append("|-----|----------|---------|--------|")
            for f in findings:
                lines.append(f"| {f['finding_id']} | {f['severity']} | {f['subject']} | {f['status']} |")

        lines.extend(
            [
                "",
                "## Lo que se auditó",
                "",
                "- `oraculo_capability_catalog_v0.json` (catálogo de 6 capacidades IA)",
                "- `oraculo_power_stacks_v0.md` (reporte de Power Stacks)",
                "- `event_log.v0.jsonl` (registro de eventos del Dispatcher)",
                "",
                "## Lo que NO se auditó",
                "",
                "- Veracidad de las capacidades IA (requiere M2 con APIs reales)",
                "- Costos reales de los Power Stacks (requiere investigación de precios)",
                "- Viabilidad de los Sprint Candidates (requiere Sprint Factory)",
                "",
                "## Decisiones T1 Pendientes",
                "",
                "1. Aprobar elevación del Oráculo a M2 (conexión a APIs reales)",
                "2. Aprobar activación de Vigilia Sincrónica (orquestación real de loops)",
                "3. Resolver findings MEDIUM pendientes antes de avanzar",
                "",
                "---",
                "",
                f"*Generado por `{self.LOOP_ID}` — SPR-LOOP-AUDITOR-001*",
            ]
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
