# AGENT OUTPUT — manus_c — B6-E3 PUBLIC KEY PREP

## Metadata
- agente: manus_c
- rol real: coordinador NO-Cowork
- fecha/hora: 2026-05-20 00:00 CST
- rama: control-tower/2026-05-20-b6-e3-public-key-prep
- PR: N/A
- commit: (this)
- estado fuente: DRAFT
- tocó código: no
- tocó main: no

## Qué hice
Preparé la estructura documental para publicar la clave pública `ed25519` (minisign/signify) requerida por el Gate B6-E3. Diseñé las instrucciones exactas que T1 (Alfredo) debe ejecutar en su máquina local para generar el par de claves de forma segura y publicar únicamente la clave pública. No generé claves, no pedí la clave privada y no toqué el runtime.

## Evidencia
- Archivo creado: `bridge/control_tower/2026-05-20/manus_c/B6_E3_PUBLIC_KEY_PREP.md`
- Estructura propuesta: `docs/security/keys/`

## Instrucciones para T1 (Ejecución Local Segura)

**Objetivo:** Generar par de claves ed25519 y publicar SOLO la pública.

1. **Abrir terminal en tu máquina local (NO en el sandbox, NO en el servidor):**
   ```bash
   # Asegurar que minisign está instalado (macOS)
   brew install minisign
   ```

2. **Generar el par de claves en un directorio seguro (ej. `~/.monstruo/keys/`):**
   ```bash
   mkdir -p ~/.monstruo/keys
   minisign -G -p ~/.monstruo/keys/dory_cure.pub -s ~/.monstruo/keys/dory_cure.key
   ```
   *(Te pedirá una contraseña para proteger la clave privada. Guárdala en tu gestor de contraseñas, ej. 1Password).*

3. **Copiar SOLO la clave pública al repositorio:**
   ```bash
   cd ~/path/to/el-monstruo
   mkdir -p docs/security/keys
   cp ~/.monstruo/keys/dory_cure.pub docs/security/keys/
   ```

4. **Crear el archivo de manifiesto de la clave:**
   Crea `docs/security/keys/manifest.json` con este contenido:
   ```json
   {
     "key_id": "dory_cure_primary",
     "algorithm": "ed25519",
     "format": "minisign",
     "purpose": "Sign Anti-Dory v3.0 core decisions and DORY_CURE_DISABLED state",
     "custodian": "T1 (Alfredo)",
     "created_at": "2026-05-20",
     "status": "active"
   }
   ```

5. **Hacer commit y push:**
   ```bash
   git add docs/security/keys/dory_cure.pub docs/security/keys/manifest.json
   git commit -m "security(b6): publish ed25519 public key for Dory Cure signatures"
   git push origin main
   ```

**ADVERTENCIA CRÍTICA:** NUNCA copies, muevas, ni hagas commit del archivo `dory_cure.key`. Ese archivo debe permanecer exclusivamente en tu máquina local y/o hardware token.

## Archivos tocados
| archivo | acción | branch | commit | nota |
|---|---|---|---|---|
| bridge/control_tower/2026-05-20/manus_c/B6_E3_PUBLIC_KEY_PREP.md | CREATED | control-tower/2026-05-20-b6-e3-public-key-prep | (this) | Estructura e instrucciones T1 |

## Decisiones T1 requeridas
| decisión | opciones | impacto | urgencia |
|---|---|---|---|
| Ejecutar generación local | Seguir instrucciones / Modificar | Cumple B6-E3 | Alta (bloquea B6) |

## Cierre
- No incluí secretos.
- No canonizo nada.
- No desbloqueo R1.
- No recomiendo merge/deploy sin T1.
- Este output queda listo para revisión de Perplexity Torre de Control PBA.
