"""
Oráculo de IAs — Primer Embrión Perito del Monstruo
SPR-EMBRION-PERITO-LOOP-001

El Oráculo de IAs es un Embrión Intérprete Estratégico. Su función es:
1. Detectar capacidades emergentes de IA (Capability)
2. Mapear aplicaciones dentro del Monstruo (Application)
3. Definir Power Stacks necesarios (Power Stack)
4. Formular Sprint Candidates (Sprint)

Restricciones:
- max_autonomy_level: A3
- allowed_write_paths: bridge/doctrine_candidates/
- forbidden_actions: touch_supabase, modify_kernel
- No implementa código final — solo propone

Maturity Level: M1 (Catalogado) — ejecuta bajo supervisión, sin producción.
"""

import json
import os
from datetime import datetime, timezone


# --- Catálogo de Capacidades (v0 — datos estáticos para simulación) ---

CAPABILITY_CATALOG_V0 = [
    {
        "id": "CAP-001",
        "model": "GPT-4o",
        "feature": "Real-time Vision Analysis",
        "discovered_at": "2024-05-13",
        "application": "UI/UX Audit Automático — El Monstruo puede auditar interfaces visualmente",
        "power_stack": ["OpenAI API (gpt-4o)", "Screenshot capture", "Prompt template: UI audit"],
        "sprint_candidate": "SPR-UI-AUDIT-001",
        "confidence": 0.85,
        "status": "PROPOSED"
    },
    {
        "id": "CAP-002",
        "model": "Claude Opus 4",
        "feature": "Extended Thinking (128k reasoning)",
        "discovered_at": "2025-03-14",
        "application": "Auditor Profundo — validación exhaustiva de arquitectura y decisiones",
        "power_stack": ["Anthropic API (claude-opus-4)", "Context injection", "Structured output"],
        "sprint_candidate": "SPR-DEEP-AUDITOR-001",
        "confidence": 0.90,
        "status": "PROPOSED"
    },
    {
        "id": "CAP-003",
        "model": "Gemini 2.5 Pro",
        "feature": "1M token context + grounding",
        "discovered_at": "2025-03-25",
        "application": "Memoria de Largo Plazo — ingerir corpus completo del Monstruo en una sola ventana",
        "power_stack": ["Google AI API (gemini-2.5-pro)", "Corpus loader", "Grounding API"],
        "sprint_candidate": "SPR-LONG-MEMORY-001",
        "confidence": 0.80,
        "status": "PROPOSED"
    },
    {
        "id": "CAP-004",
        "model": "Grok 3",
        "feature": "Real-time web + DeepSearch",
        "discovered_at": "2025-02-17",
        "application": "Validador en Tiempo Real — verificar claims contra internet actual",
        "power_stack": ["xAI API (grok-3)", "DeepSearch mode", "Citation extraction"],
        "sprint_candidate": "SPR-REALTIME-VALIDATOR-001",
        "confidence": 0.88,
        "status": "PROPOSED"
    },
    {
        "id": "CAP-005",
        "model": "Perplexity Sonar Pro",
        "feature": "Reasoning + citations + real-time",
        "discovered_at": "2025-11-01",
        "application": "Investigador Autónomo — research profundo con fuentes verificables",
        "power_stack": ["Perplexity API (sonar-pro)", "Citation parser", "Confidence scoring"],
        "sprint_candidate": "SPR-AUTO-RESEARCHER-001",
        "confidence": 0.92,
        "status": "PROPOSED"
    },
    {
        "id": "CAP-006",
        "model": "DeepSeek R1",
        "feature": "Open-weight reasoning (MIT license)",
        "discovered_at": "2025-01-20",
        "application": "Soberanía de Razonamiento — modelo propio deployable sin dependencia externa",
        "power_stack": ["DeepSeek API or self-hosted", "vLLM/SGLang", "GPU allocation"],
        "sprint_candidate": "SPR-SOVEREIGN-REASONING-001",
        "confidence": 0.75,
        "status": "PROPOSED"
    }
]


class OraculoIALoop:
    """
    Primer loop real del Monstruo.
    Interactúa con el MinimalDispatcher para solicitar permisos antes de actuar.
    """

    LOOP_ID = "loop_oraculo_ias"
    MATURITY_LEVEL = "M1"
    CLASS = "Strategic"

    def __init__(self, dispatcher, output_dir):
        """
        Args:
            dispatcher: Instancia de MinimalDispatcher.
            output_dir: Directorio donde escribir outputs si es permitido.
        """
        self.dispatcher = dispatcher
        self.output_dir = output_dir
        self.actions_attempted = []
        self.actions_allowed = []
        self.actions_denied = []

    def run(self, handoff_packet=None):
        """
        Ejecuta el ciclo completo del Oráculo:
        1. Analiza contexto (handoff)
        2. Genera catálogo de capacidades
        3. Solicita permiso al Dispatcher para escribir
        4. Escribe si es permitido
        5. Intenta una acción prohibida (para demostrar DENY)
        6. Retorna resultado

        Args:
            handoff_packet: Dict con current_state, recent_events, etc.
                           Puede ser None para ejecución standalone.

        Returns:
            Dict con loop_id, status, event_proposals, actions_log, output_files
        """
        results = {
            "loop_id": self.LOOP_ID,
            "maturity_level": self.MATURITY_LEVEL,
            "status": "PENDING",
            "event_proposals": [],
            "actions_log": [],
            "output_files": [],
            "next_suggested_loop": "loop_auditor",
            "message": ""
        }

        # === PASO 1: Generar catálogo ===
        catalog = self._generate_catalog()

        # === PASO 2: Solicitar permiso para escribir catálogo ===
        catalog_path = "bridge/doctrine_candidates/oraculo_capability_catalog_v0.json"
        write_request = {
            "action": "create_state_fabric_draft",
            "target_path": catalog_path,
            "has_evidence": True
        }

        is_allowed, reason, event = self.dispatcher.dispatch_action(
            self.LOOP_ID, write_request
        )
        self.actions_attempted.append(write_request)
        results["event_proposals"].append(event)
        results["actions_log"].append({
            "action": "create_state_fabric_draft",
            "target": catalog_path,
            "allowed": is_allowed,
            "reason": reason
        })

        if is_allowed:
            self.actions_allowed.append(write_request)
            # Escribir físicamente el catálogo
            output_file = os.path.join(self.output_dir, "oraculo_capability_catalog_v0.json")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            results["output_files"].append(output_file)
        else:
            self.actions_denied.append(write_request)

        # === PASO 3: Solicitar permiso para crear reporte ===
        report_request = {
            "action": "create_report",
            "target_path": "bridge/doctrine_candidates/oraculo_power_stacks_v0.md",
            "has_evidence": True
        }

        is_allowed_2, reason_2, event_2 = self.dispatcher.dispatch_action(
            self.LOOP_ID, report_request
        )
        self.actions_attempted.append(report_request)
        results["event_proposals"].append(event_2)
        results["actions_log"].append({
            "action": "create_report",
            "target": report_request["target_path"],
            "allowed": is_allowed_2,
            "reason": reason_2
        })

        if is_allowed_2:
            self.actions_allowed.append(report_request)
            report_file = os.path.join(self.output_dir, "oraculo_power_stacks_v0.md")
            report_content = self._generate_power_stacks_report(catalog)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            results["output_files"].append(report_file)

        # === PASO 4: Intentar acción PROHIBIDA (write_code) para demostrar DENY ===
        forbidden_request = {
            "action": "write_code",
            "target_path": "src/oraculo_engine.py",
            "has_evidence": True
        }

        is_allowed_3, reason_3, event_3 = self.dispatcher.dispatch_action(
            self.LOOP_ID, forbidden_request
        )
        self.actions_attempted.append(forbidden_request)
        results["event_proposals"].append(event_3)
        results["actions_log"].append({
            "action": "write_code",
            "target": forbidden_request["target_path"],
            "allowed": is_allowed_3,
            "reason": reason_3
        })

        if not is_allowed_3:
            self.actions_denied.append(forbidden_request)

        # === PASO 5: Determinar status final ===
        if len(self.actions_allowed) >= 2:
            results["status"] = "SUCCESS"
            results["message"] = (
                f"Oraculo completed cycle. "
                f"{len(self.actions_allowed)} actions allowed, "
                f"{len(self.actions_denied)} denied (expected). "
                f"{len(catalog['capabilities'])} capabilities cataloged."
            )
        elif len(self.actions_allowed) >= 1:
            results["status"] = "PARTIAL"
            results["message"] = "Oraculo partially completed. Some actions were blocked."
        else:
            results["status"] = "BLOCKED"
            results["message"] = "Oraculo fully blocked by dispatcher."
            results["next_suggested_loop"] = "STOP"

        return results

    def _generate_catalog(self):
        """Genera el catálogo de capacidades IA (v0 estático)."""
        return {
            "catalog_version": "v0.1.0",
            "generated_by": self.LOOP_ID,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "maturity_level": self.MATURITY_LEVEL,
            "total_capabilities": len(CAPABILITY_CATALOG_V0),
            "capabilities": CAPABILITY_CATALOG_V0,
            "meta": {
                "source": "static_v0_seed",
                "next_evolution": "Live API scanning + model benchmarks",
                "confidence_range": [0.75, 0.92],
                "sprint_candidates_generated": len(CAPABILITY_CATALOG_V0)
            }
        }

    def _generate_power_stacks_report(self, catalog):
        """Genera un reporte Markdown de los Power Stacks propuestos."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        lines = [
            "# Oráculo de IAs — Power Stacks Report v0",
            "",
            f"**Generado por:** `{self.LOOP_ID}` (Maturity: {self.MATURITY_LEVEL})",
            f"**Fecha:** {now}",
            f"**Total capacidades catalogadas:** {catalog['total_capabilities']}",
            "",
            "---",
            "",
            "## Capacidades Detectadas y Aplicaciones Propuestas",
            "",
        ]

        for cap in catalog["capabilities"]:
            lines.extend([
                f"### {cap['id']}: {cap['model']} — {cap['feature']}",
                "",
                f"**Aplicación:** {cap['application']}",
                "",
                f"**Power Stack:**",
            ])
            for tool in cap["power_stack"]:
                lines.append(f"- {tool}")
            lines.extend([
                "",
                f"**Sprint Candidate:** `{cap['sprint_candidate']}`",
                f"**Confianza:** {cap['confidence']}",
                "",
                "---",
                "",
            ])

        lines.extend([
            "## Siguiente Evolución",
            "",
            "Este catálogo es v0 (estático). La siguiente iteración debe:",
            "1. Escanear APIs en tiempo real para detectar nuevos modelos/features.",
            "2. Ejecutar benchmarks contra tareas reales del Monstruo.",
            "3. Proponer Power Stacks con costos estimados (USD/mes).",
            "4. Generar Sprint Specs formales para el Sprint Factory.",
            "",
            "**Status:** DOCTRINE_CANDIDATE — requiere validación de T1.",
        ])

        return "\n".join(lines) + "\n"
