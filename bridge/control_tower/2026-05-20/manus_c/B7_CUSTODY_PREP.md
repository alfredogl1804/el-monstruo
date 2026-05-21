# AGENT OUTPUT — manus_c — B7-E1/E2 FIXTURE CUSTODY PREP

## Metadata
- agente: manus_c
- rol real: coordinador NO-Cowork
- fecha/hora: 2026-05-20 00:00 CST
- rama: control-tower/2026-05-20-b7-custody-prep
- PR: N/A
- commit: (this)
- estado fuente: DRAFT
- tocó código: no
- tocó main: no

## Qué hice
Preparé la estructura para el inventario de hashes y la declaración de custodios de los fixtures secretos del Gate B7 (E1/E2). NO creé fixtures reales, NO toqué secretos, y NO envié fixtures a LLMs. El documento establece el contrato de custodia que T1 debe firmar y completar localmente.

## Evidencia
- Archivo creado: `bridge/control_tower/2026-05-20/manus_c/B7_CUSTODY_PREP.md`
- Estructura propuesta: `docs/security/fixtures_inventory.json`

## Inventario de Hashes y Declaración de Custodios (DRAFT)

**Objetivo:** Establecer el registro inmutable de los fixtures secretos que se usarán en las pruebas adversariales (TCC/CVDS), sin exponer su contenido en el repositorio.

### 1. Estructura del Inventario (Para crear en `docs/security/fixtures_inventory.json`)

```json
{
  "version": "1.0",
  "last_updated": "2026-05-20",
  "custodian": "T1 (Alfredo)",
  "fixtures": [
    {
      "id": "fix_tcc_001",
      "type": "TCC (Test de Corrupción de Contexto)",
      "description": "Token secreto inyectado en prompt largo para verificar retención post-compactación",
      "sha256_hash": "REEMPLAZAR_POR_HASH_REAL_DEL_FIXTURE_LOCAL",
      "location": "Local T1 machine / Hardware token",
      "status": "active"
    },
    {
      "id": "fix_cvds_001",
      "type": "CVDS (Cebo de Validación de Decisión Soberana)",
      "description": "Instrucción maliciosa oculta para probar el Verification Gate",
      "sha256_hash": "REEMPLAZAR_POR_HASH_REAL_DEL_FIXTURE_LOCAL",
      "location": "Local T1 machine / Hardware token",
      "status": "active"
    }
  ]
}
```

### 2. Instrucciones para T1 (Custodio)

Para cumplir con B7-E1 y B7-E2, T1 debe ejecutar esto localmente:

1. **Crear los archivos de fixtures reales en su máquina local** (fuera del repo).
2. **Calcular el SHA-256 de cada fixture:**
   ```bash
   shasum -a 256 /path/to/local/fixture_tcc_001.txt
   ```
3. **Reemplazar los valores `REEMPLAZAR_POR_HASH_REAL_DEL_FIXTURE_LOCAL`** en el archivo `docs/security/fixtures_inventory.json` con los hashes calculados.
4. **Hacer commit y push SOLO del inventario (`fixtures_inventory.json`), NUNCA de los fixtures reales.**

### 3. Declaración de Custodia

Al hacer commit del inventario con los hashes reales, T1 declara formalmente:
> "Como T1, declaro ser el único custodio de los fixtures secretos correspondientes a los hashes publicados. Confirmo que el contenido de estos fixtures no ha sido expuesto a ningún LLM ni almacenado en ningún repositorio público o accesible por agentes."

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B7_CUSTODY_PREP.md | CREATED | control-tower/2026-05-20-b7-custody-prep | (this) | Estructura e instrucciones T1 |

## Decisiones T1 requeridas
| decisión | opciones | impacto | urgencia |
|---|---|---|---|
| Crear fixtures locales y publicar hashes | Seguir instrucciones / Modificar | Cumple B7-E1/E2 | Alta (bloquea B7) |

## Cierre
- No incluí secretos.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- No creé fixtures reales secretos.
- No envié fixtures a LLMs.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
