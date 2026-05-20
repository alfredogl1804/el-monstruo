# 05 LOOP REGISTRY MODEL

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Definición
El `loop_registry.v0.yaml` es el catálogo de todos los loops que el Dispatcher conoce y puede instanciar. En v0, es estático y define las plantillas de los loops candidatos.

## Reglas
1. **Identidad:** Cada entrada en el registry define un `role` (ej. `loop_peritos`, `loop_auditor`).
2. **Policy Binding:** El registry inyecta el `max_autonomy_level` y los `forbidden_actions` que el Policy Engine usará en el Preflight Check.
3. **No Ejecución (v0):** En esta fase, todos los loops tienen `status: NOT_RUNNING`. Son solo contratos inactivos.

## Loops Candidatos Mínimos
- `loop_vigia`: Monitorea el Event Log y detecta anomalías.
- `loop_memoria_memento`: Gestiona la persistencia a largo plazo (Anti-Dory).
- `loop_oraculo_ias`: Embrión perito que predice capacidades de modelos.
- `loop_humanplus_e2e`: Interfaz unificada con Alfredo.
- `loop_peritos`: Plantilla base para especialistas.
- `loop_ejecutor`: Manus/Cowork realizando trabajo pesado.
- `loop_auditor`: Perplexity/Grok validando trabajo.
- `loop_aprendizaje`: Analiza logs pasados para extraer lecciones.
- `loop_unified_face`: El enrutador principal de la Vigilia Sincrónica.
