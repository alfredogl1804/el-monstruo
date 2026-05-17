# D2 Drift Audit — código vs doctrina

Generated: 2026-05-17T23:16:47Z

## 1. apps/mobile/lib/ (Flutter source code, NO build/cache)

### Top-level files in lib/
app.dart
[34mcore[39;49m[0m
[34mfeatures[39;49m[0m
main.dart
[34mmodels[39;49m[0m
[34mmodes[39;49m[0m
[34mproviders[39;49m[0m
[34mrouting[39;49m[0m
[34mwidgets[39;49m[0m

### Theme / colores hardcoded en lib/
./apps/mobile/lib/core/theme/brand_dna.dart:10:  static const Color primary = Color(0xFF00E5FF);
./apps/mobile/lib/core/theme/brand_dna.dart:12:  static const Color secondary = Color(0xFFBB86FC);
./apps/mobile/lib/core/theme/brand_dna.dart:34:  static const Color borderFocused = Color(0xFF00E5FF);
./apps/mobile/lib/core/theme/brand_dna.dart:44:    colors: [Color(0xFF00E5FF), Color(0xFFBB86FC)],
./apps/mobile/lib/core/theme/brand_dna.dart:50:    colors: [Color(0xFF00E5FF), Color(0xFF00B8D4)],
./apps/mobile/lib/core/theme/brand_dna.dart:56:    colors: [Color(0x4000E5FF), Color(0x40BB86FC)],

## 2. apps/la-forja/

[34mapi[39;49m[0m
[34mweb[39;49m[0m

### subprojects con package.json
./apps/la-forja/web/.next/package.json

## 3. bridge/ A2UI / AG-UI

a2ui_spec_draft_FIRMADO_2026_05_11.md
a2ui_spec_draft_para_firma.md
cowork_to_manus_RESULTADO_AUDIT_A2UI_2026_05_11.md
sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md

## 4. kernel/ subdirs

__init__.py
[34m__pycache__[39;49m[0m
a2a_registry.py
a2a_routes.py
[34ma2ui[39;49m[0m
adaptive_model_selector.py
agui_adapter.py
[34malerts[39;49m[0m
[34manti_dory[39;49m[0m
audit_middleware.py
auth.py
autonomy_routes.py
background_store.py
[34mbrand[39;49m[0m
[34mbrowser[39;49m[0m
browser_automation.py
[34mcatastro[39;49m[0m
[34mcatastros[39;49m[0m
causal_decomposer.py
causal_seeder.py
causal_simulator.py
[34mcollective[39;49m[0m
[34mcomponents[39;49m[0m
cost_optimizer.py
cowork_routes.py
[34mcowork_runtime[39;49m[0m
[34mdashboards[39;49m[0m
deep_think_pipeline.py
deployments_routes.py
[34mdesign[39;49m[0m
dossier_cache.py
[34me2e[39;49m[0m
embrion_budget.py
embrion_inbox.py
embrion_inbox_parser.py
embrion_inbox_sanitizer.py
embrion_loop.py
embrion_routes.py
embrion_scheduler.py
embrion_self_verifier.py
[34membrion_specializations[39;49m[0m
embrion_tecnico.py
embrion_ventas.py
embrion_vigia.py
embrion_write_policy.py
[34membriones[39;49m[0m
emergent_tracker.py
engine.py
error_memory.py
[34mescape[39;49m[0m
[34mespiral[39;49m[0m
execution_verifier.py
external_agents.py
fallback_engine.py
fastmcp_server.py
finops.py
finops_routes.py
guardian.py
[34mguardian_runner[39;49m[0m
hitl.py
[34mi18n[39;49m[0m
[34mlearning[39;49m[0m
magna_classifier.py
magna_routes.py
main.py
manus_bridge.py
[34mmarketplace[39;49m[0m
mcp_client.py
mcp_hub_config.py
[34mmemento[39;49m[0m
memento_routes.py
memory_routes.py
[34mmilestones[39;49m[0m
mission_routes.py
[34mmoc[39;49m[0m
moc_routes.py
[34mmotion[39;49m[0m
multi_agent.py
nodes.py
onboarding.py
openai_adapter.py
output_sanitizer.py
planner_routes.py
[34mplugins[39;49m[0m
[34mportability[39;49m[0m
prediction_validator.py
rate_limiter.py
reranker.py
response_cache.py
[34mrotor[39;49m[0m
[34mrunner[39;49m[0m
[34msecurity[39;49m[0m
seeds_sprint_84_5.py
seeds_sprint_84_7.py
[34msimulator[39;49m[0m
sovereign_llm.py
[34msovereignty[39;49m[0m
spec_driven.py
state.py
supervisor.py
task_planner.py
tool_broker.py
tool_dispatch.py
tool_registry.py
[34mtransversales[39;49m[0m
usage_routes.py
usage_tracker.py
[34mutils[39;49m[0m
[34mux[39;49m[0m
[34mvalidation[39;49m[0m
[34mvanguard[39;49m[0m
[34mzero_config[39;49m[0m

## 5. packages/

README.md
[34mdesign-tokens[39;49m[0m

## 6. Capabilities Cap 4 — hits en kernel/ y bridge/

