# PROMPT PARA HILO NUEVO — Implementar 4 Automatizaciones DTA

> **Instrucción para el piloto**: copia todo el contenido de este archivo y pégalo como primer mensaje en un hilo nuevo de Manus. El hilo implementará las 4 automatizaciones sin necesitar contexto adicional.

---

## CONTEXTO QUE NECESITAS SABER

Estoy trabajando en el repositorio `alfredogl1804/el-monstruo` (privado, GitHub). Existe una bitácora viva en `forja_omega_tramo_1/bitacora.jsonl` que captura eventos de alto valor (doctrinas, chispas del piloto, decisiones, anti-patrones) en formato JSONL append-only.

El problema: la captura en JSONL es autónoma, pero las siguientes 4 piezas de resguardo NO lo son — dependen de que un humano o agente las dispare manualmente:

1. **Commit + push automático** al repo cuando se acumulan eventos
2. **Index auto-regenerado** (`bitacora_index.md`) al commitear
3. **Guardian memoria persistente** actualizado post-push
4. **Genome Vivo** (Supabase) actualizado post-push

## TU TAREA

Implementar las 4 automatizaciones como **scripts ejecutables** que puedan correr como:
- Git hooks (post-commit / pre-push)
- O cron jobs en Railway
- O GitHub Actions
- O combinación

Elige la implementación más simple y robusta. Principios rectores:
- **No parches**: solución universal que funcione para cualquier bitácora JSONL futura
- **Menos es más**: si puedes hacer las 4 con 1 script, hazlo con 1 script
- **Si no es fácil no lo uso**: debe ser zero-config después de instalado

## ESPECIFICACIONES TÉCNICAS

### Automatización 1: Commit + Push automático

**Trigger**: cuando `forja_omega_tramo_1/bitacora.jsonl` acumule ≥5 líneas nuevas respecto al último commit, O cuando se detecte un evento de tipo `estado` con ref que contenga "cerrada" (cierre de bloque temático).

**Acción**:
```bash
git add forja_omega_tramo_1/bitacora.jsonl forja_omega_tramo_1/bitacora_index.md
git commit -m "auto-sync: bitácora +N eventos [DTA-auto]"
git push origin <branch-actual>
```

**Restricciones**:
- Solo commitea archivos de `forja_omega_tramo_1/`
- NO commitea nada más del repo
- Si hay conflicto de merge, NO fuerza — loguea error y espera intervención
- Pre-commit hooks del repo deben pasar (gitleaks, etc.)

### Automatización 2: Index auto-regenerado

**Trigger**: se ejecuta como parte del commit de Automatización 1 (pre-commit o script encadenado).

**Acción**: lee `bitacora.jsonl` completo y regenera `bitacora_index.md` con:
- Conteo total de eventos
- Lista de doctrinas (tipo `doctrina`) con #, sigla, nombre
- Lista de chispas del piloto (tipo `chispa`, autor `alfredo`)
- Lista de anti-patrones
- Estado de las Q (extraer de eventos tipo `estado`)
- Últimas 5 citas verbatim (campo `v`)
- Estado DTA (hardcoded por ahora, actualizable manualmente)

**Template**: usa el formato actual de `bitacora_index.md` como referencia (está en el repo en `forja_omega_tramo_1/bitacora_index.md`).

### Automatización 3: Guardian memoria persistente

**Contexto**: Guardian V5 es un sistema de memoria persistente del Monstruo. Vive como skill en `/home/ubuntu/skills/` del sandbox Manus y tiene un endpoint en el kernel Railway.

**Trigger**: post-push exitoso de Automatización 1.

**Acción**: invocar el endpoint del Guardian para registrar un resumen denso de los eventos nuevos. El resumen debe incluir:
- Doctrinas nuevas firmadas (solo siglas + nombres)
- Chispas magnas del piloto (solo refs)
- Anti-patrones detectados
- Estado actualizado de las Q

**Endpoint Guardian** (verificar en el kernel):
- Railway app: `el-monstruo-kernel` 
- Ruta probable: `POST /v1/guardian/memory` o similar
- Auth: Bearer token desde env `KERNEL_API_KEY`

**Si no encuentras el endpoint exacto**: crea un script placeholder que genere el payload JSON correcto y lo loguee a `forja_omega_tramo_1/_guardian_pending.jsonl` para envío manual posterior. NO bloquees las otras 3 automatizaciones por esto.

### Automatización 4: Genome Vivo actualizado

**Contexto**: Genome Vivo es la fuente de verdad estructural del Monstruo en Supabase. Tiene un endpoint REST.

**Trigger**: post-push exitoso de Automatización 1.

**Acción**: actualizar el campo relevante del Genome con:
- `doctrinas_firmadas_count`: número total
- `ultima_doctrina_firmada`: sigla + nombre
- `ultimo_evento_bitacora_ts`: timestamp del último evento
- `fase_detonacion_estado`: resumen de Q cerradas/abiertas

**Endpoint Genome Vivo** (verificar en el kernel):
- Ruta probable: `PATCH /v1/genome/now` o `POST /v1/genome/update`
- Auth: Bearer token desde env `KERNEL_API_KEY`

**Si no encuentras el endpoint exacto**: mismo approach que Guardian — placeholder con payload correcto logueado.

## ARCHIVOS DE REFERENCIA EN EL REPO

```
forja_omega_tramo_1/bitacora.jsonl          ← la bitácora viva (104 líneas actualmente)
forja_omega_tramo_1/bitacora_index.md       ← el index que se regenera
forja_omega_tramo_1/CIERRE_DIA_2026_05_28.md ← ejemplo de documento de cierre
```

## SCHEMA JSONL DE LA BITÁCORA

```json
{
  "ts": "ISO8601",
  "t": "firma|chispa|propuesta|descarte|doctrina|antipattern|estado|pregunta|pregunta_pendiente|validacion|decision",
  "a": "alfredo|manus",
  "ref": "componente_o_concepto",
  "c": "contenido_denso",
  "v": "verbatim_si_aplica (puede no existir)",
  "s": "id_supersede_si_aplica (puede no existir)"
}
```

## ENTREGABLES ESPERADOS

1. Script(s) implementando las 4 automatizaciones
2. Instrucciones de instalación (1 comando si es posible)
3. Test de que funciona: agregar 5 líneas dummy a la bitácora y verificar que el pipeline completo se dispara
4. Documentación mínima en un README dentro de `forja_omega_tramo_1/scripts/`

## BRANCH DE TRABAJO

Crea branch `feat/dta-automatizaciones` desde `tramo-1-bitacora-y-dta` y abre PR contra esa misma branch.

## RESTRICCIONES

- NO toques código fuera de `forja_omega_tramo_1/`
- NO instales dependencias globales pesadas
- Preferir bash + python3 estándar (ya disponible en el Mac del usuario)
- Si necesitas Railway CLI o Supabase CLI, instálalos solo si es estrictamente necesario
- Pre-commit hooks del repo DEBEN pasar en tu PR

---

**FIN DEL PROMPT — pega todo lo anterior en un hilo nuevo de Manus**
