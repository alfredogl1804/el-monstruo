# AGENT OUTPUT — Manus C — B7-E1/E2 Custody Prep

## Metadata
- agente: manus_c
- rol real: preparador de evidencia documental
- fecha/hora: 2026-05-20T22:55 CST
- rama: control-tower/2026-05-20-batch-003-b7-prep
- PR: N/A
- commit: pending
- estado fuente: EVIDENCE_PACK
- tocó código: no
- tocó main: no

## Qué hice
Preparé la estructura para el inventario de hashes de los hidden fixtures y la declaración de custodios (B7-E1/E2). No creé fixtures reales, no manejé secretos y no envié nada a LLMs.

## B7-E1: Estructura del Inventario de Hashes

Los fixtures reales (prompts adversariales ocultos) NUNCA deben residir en texto plano en el repositorio. El repositorio solo almacenará sus hashes SHA-256 para que el Test Runner pueda verificar su integridad antes de inyectarlos en memoria.

**Path propuesto para el inventario:** `kernel/anti_dory/fixtures/manifest.json`

**Estructura JSON propuesta:**
```json
{
  "version": "1.0",
  "updated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "custodian": "T1",
  "fixtures": [
    {
      "id": "fixture_001_subtle_drift",
      "description": "Prueba de deriva semántica sutil en objetivo principal",
      "sha256": "<hash_del_contenido_real>",
      "type": "adversarial_prompt",
      "expected_detection_layer": "claim_vg"
    },
    {
      "id": "fixture_002_fake_t1_override",
      "description": "Prueba de inyección de override falso de T1",
      "sha256": "<hash_del_contenido_real>",
      "type": "adversarial_prompt",
      "expected_detection_layer": "action_vg"
    }
  ]
}
```

## B7-E2: Declaración de Custodios (DRAFT)

**Path propuesto:** `bridge/control_tower/evidence/B7/CUSTODY_DECLARATION.md`

**Contenido propuesto:**
```markdown
# Declaración de Custodia de Hidden Fixtures (Anti-Dory)

## 1. Principio de Custodia
Los hidden fixtures son el mecanismo de validación adversarial (TCC/CVDS) del sistema Anti-Dory. Si un agente LLM conoce el contenido del fixture, el test se invalida (data contamination). Por tanto, ningún LLM puede ser custodio de los fixtures.

## 2. Custodios Autorizados
- **Custodio Primario:** T1 (Alfredo Góngora)
- **Custodios Secundarios:** Ninguno actualmente. (Fallback: T1)

## 3. Obligaciones del Custodio
1. Almacenar los archivos de texto plano de los fixtures FUERA del repositorio (ej. 1Password Secure Notes, iCloud Drive cifrado local).
2. Generar el SHA-256 de cada fixture localmente.
3. Actualizar el `manifest.json` en el repositorio solo con los hashes.
4. Proveer los fixtures al Test Runner en tiempo de ejecución mediante inyección de variables de entorno o montaje de volumen temporal, NUNCA mediante commit.

## 4. Prohibiciones Estrictas
- NINGÚN agente (Manus, Cowork, ChatGPT, Grok, Gemini) está autorizado a leer los archivos fuente de los fixtures.
- Si un agente detecta un fixture en texto plano en el repositorio, debe reportarlo como P0 SECURITY BREACH y detener ejecución.
```

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B7_E1_E2_CUSTODY_PREP.md | CREATED | control-tower/2026-05-20-batch-003-b7-prep | pending | Solo prep documental |

## Confirmaciones
- No incluí secretos.
- No creé fixtures secretos reales.
- No envié fixtures a LLMs.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
