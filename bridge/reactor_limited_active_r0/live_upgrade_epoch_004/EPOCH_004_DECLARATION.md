# EPOCH 004 DECLARATION

**Effective Date:** 2026-05-21T02:00:00Z
**Authorization:** T1 (SPR-EPOCH004-R0PLUS-PRODUCTION-FABRIC-001)

## Declaración
Se declara el inicio de la Epoch 004 del piloto, promovido a la categoría `LIMITED_ACTIVE_R0_PLUS`. 
El piloto deja de ser solo una herramienta de monitoreo y reporte, para convertirse en una fábrica de producción supervisada.

## Capacidades y Gobernanza (R0_PLUS)
1. **Duración:** 7 días a partir de la declaración.
2. **Frecuencia:** Máximo 2 ciclos por día.
3. **Presupuesto:** 
   - Máximo diario: $0.25 USD.
   - Máximo por ciclo: $0.05 USD.
4. **Producción Permitida:**
   - Generación de código Python local.
   - Generación de tests unitarios.
   - Generación de HTML local read-only.
   - Generación de fixtures JSON.
   - Generación de reportes en el bridge.
   - Generación de sprint drafts (sin firma).
   - Generación de archivos locales para el State Fabric y Event Log.
5. **Restricciones (Hard Rules):**
   - NO R1 productivo.
   - NO PR, NO deploy, NO modificaciones a `main`.
   - NO escrituras en Supabase o DB real.
   - NO exposición de secrets.
   - NO escrituras en memoria externa (Memento/Anti-Dory).
   - NO modificaciones a `APP_VISION` o al canon.
   - NO PRE-IA close.
   - NO uso de Perplexity o DeepSeek.
   - NO auto-reemplazo de proveedores.
   - NO retries en llamadas a proveedores.
   - NO extensión permanente del scheduler más allá del piloto.
   - NO uso de runtime SHELL.
   - NO raw CoT en outputs finales.
   - NO approve/reject real en UIs.

## Control T1
El `kill-switch` file-based mantiene la supremacía absoluta sobre la ejecución del piloto.
Los freeze triggers se han ampliado para incluir violaciones de presupuesto, uso de proveedores no permitidos, drift de modelos, intentos de R1, escrituras prohibidas, modificaciones al canon, interacciones no permitidas en el Cockpit, fallos del Auditor y auto-auditorías de loops.
