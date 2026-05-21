# AGENT OUTPUT — Manus C — B6-E6 Signature Chain Prep

## Metadata
- agente: manus_c
- rol real: preparador de evidencia documental
- fecha/hora: 2026-05-20T22:50 CST
- rama: control-tower/2026-05-20-batch-003-b6-e6-prep
- PR: N/A
- commit: pending
- estado fuente: EVIDENCE_PACK
- tocó código: no
- tocó main: no

## Qué hice
Preparé el procedimiento documental para validar firmas `minisign` utilizando la clave pública B6-E3 previamente firmada y publicada. No utilicé clave privada ni firmé archivos reales.

## Procedimiento de Validación de Firma (B6-E6)

### Objetivo
Verificar que un archivo (por ejemplo, una directiva de Dory Cure Kill Switch) fue firmado legítimamente por T1 utilizando la clave ed25519 `dory_cure_kill_switch`.

### Requisitos Previos
1. Clave pública B6-E3 disponible en el repo: `.monstruo/keys/dory_cure_kill_switch.pub`
2. Archivo a verificar (ej. `kill_switch_directive.json`)
3. Archivo de firma (ej. `kill_switch_directive.json.minisig`)
4. Utilidad `minisign` instalada en el entorno que verifica (ej. CI/CD o sandbox de Manus).

### Comando de Verificación
Para verificar la firma sin depender del path local, se debe usar la clave pública embebida directamente o referenciando el archivo en el repositorio:

```bash
# Opción 1: Usando el archivo .pub del repositorio
minisign -Vm kill_switch_directive.json -p .monstruo/keys/dory_cure_kill_switch.pub

# Opción 2: Usando la string pública directamente (más robusto para scripts)
minisign -Vm kill_switch_directive.json -P RWSdyrGTHIWR9o0MXjiVZ6zgeT0Y8YB/RFdkGEsPY+hYuqKmZNIT51Qe
```

### Resultados Esperados
- **Éxito:** Retorna exit code `0` y muestra `Signature and comment signature verified`.
- **Fallo:** Retorna exit code `>0` (ej. `1`) y muestra error (firma inválida, archivo modificado, clave incorrecta).

### Integración en CI/CD (Pipeline Propuesto)
Cualquier pull request que intente modificar el estado de Anti-Dory (Fase 1, Kill Switch, etc.) deberá incluir un archivo `.minisig` válido. Un GitHub Action verificará la firma automáticamente:

```yaml
name: Verify Dory Cure Kill Switch Signature
on:
  pull_request:
    paths:
      - 'kernel/anti_dory/status.json'
jobs:
  verify-signature:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install minisign
        run: sudo apt-get install -y minisign
      - name: Verify signature
        run: minisign -Vm kernel/anti_dory/status.json -P RWSdyrGTHIWR9o0MXjiVZ6zgeT0Y8YB/RFdkGEsPY+hYuqKmZNIT51Qe
```

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B6_E6_SIGNATURE_CHAIN_PREP.md | CREATED | control-tower/2026-05-20-batch-003-b6-e6-prep | pending | Solo prep documental |

## Confirmaciones
- No incluí secretos.
- No usé clave privada.
- No firmé archivos reales.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
