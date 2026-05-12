# Ticket: MANUS_API_KEY_GOOGLE_REGEN_001 — DIFERIDO BAJO DECISIÓN T2-A DELEGADA T1

**Tipo:** Acción manual pendiente (Alfredo)
**Prioridad:** Diferida — hasta cierre Monstruo completo
**Estado:** **DIFERIDO** (re-evaluado 2026-05-12 ~10:55 UTC)
**Creado:** 2026-05-12 por Hilo Ejecutor 1
**Re-evaluado por:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 delegada ("lo que tu recomiendes" 2026-05-12 ~10:53 UTC)
**Bloquea:** Bridge inter-cuenta Manus completo (mitad Google sigue rota — aceptable como bridge half-operational)

---

## Decisión T2-A bajo autoridad T1 delegada

**APLICAR T1 absoluto "no rotar secrets, credenciales y apis keys hasta acabar el Monstruo"** también a esta regeneración reactiva. **DIFERIR regeneración hasta cierre Monstruo completo.**

## Distinción doctrinal canonizada

| Concepto | Aplica T1 "no rotar"? |
|---|---|
| Rotación preventiva (rotar key buena por seguridad) | SÍ aplica → diferir |
| Rotación reactiva ante leak parcial (caso Anthropic `972ea02`) | SÍ aplica → diferir |
| **Regeneración reactiva ante invalidez verificada (key muerta, HTTP 401)** | **SÍ aplica → diferir bajo decisión T2-A 2026-05-12** |

Razones decisión T2-A:
1. **Decisión T1 absoluta no tiene excepciones declaradas** — doctrinalmente coherente extender al regenerar reactivo
2. **Apple cuenta funciona** — bridge half-operational es suficiente para flujo operacional actual
3. **Coherencia con DEUDA-ROTACION-ANTHROPIC-FINAL-001** — ambos tickets diferidos hasta misma fecha (cierre Monstruo)
4. **Cierre Monstruo + rotación masiva coordinada** ya planificada en ticket DEUDA-ROTACION incluye regeneración Google Manus también
5. **Manus Hilo Ejecutor 2** (Google account) puede operar via Apple bridge si necesita Manus M2M API durante el avance magno

## Contexto original (preservado)

Durante el sprint TOKENS-BRIDGE-FIX (2026-05-12 commit `676797d`), verificación binaria reveló que `MANUS_API_KEY_GOOGLE` es **inválido**:

```
GET https://api.manus.ai/v2/skill.list
Header: x-manus-api-key: sk-mUTK3_ww...cC3KANqe (length=98, limpio)
Response: HTTP 401 {"error":{"code":"unauthenticated","message":"invalid api key"}}
```

Posibles causas (a investigar al cierre Monstruo):
1. Token revocado en Manus UI
2. Token expirado (TTL alcanzado)
3. Token nunca fue válido (capturado mal en origen, hace meses)
4. Token pertenece a una cuenta diferente que la esperada

## Acción al cierre Monstruo completo (Alfredo T1 decide cuándo)

Cuando T1 declare cierre Monstruo completo + arranque rotación masiva coordinada (ver `DEUDA_ROTACION_ANTHROPIC_FINAL_001.md`):

1. **Investigar causa root** (4 hipótesis arriba)
2. **Regenerar nueva API key Google Manus** desde Manus UI cuenta `alfredogl1@hotmail.com`
3. **Update Railway env var** `MANUS_API_KEY_GOOGLE` con nueva key
4. **Smoke test E2E** con `tools/manus_bridge.py` skill.list endpoint
5. **Verificar bridge inter-cuenta Google↔Apple** funciona ambos sentidos

## Estado operativo intermedio (hasta cierre Monstruo)

- ✅ Apple bridge: funcional (smoke test 4/4 verde)
- ⚠️ Google bridge: half-operational (key inválida, HTTP 401)
- ✅ Manus M2M API delegation: disponible vía Apple
- ✅ Producción: NO bloqueada
- ✅ Hilos paralelo Manus: operan con Apple bridge sin issue

## Trazabilidad

- Origen detección: Sprint TOKENS-BRIDGE-FIX commit `676797d` (Hilo Ejecutor 1, 2026-05-12 08:27 UTC)
- Decisión T2-A delegada: 2026-05-12 ~10:55 UTC bajo autoridad T1 verbatim "lo que tu recomiendes"
- T1 base verbatim: "lo de rotar secrets, credenciales y apis keys lo suspendemos hasta acabar el monstruo" 2026-05-12 ~09:42 UTC
- Ticket paralelo temporalmente vinculado: `DEUDA_ROTACION_ANTHROPIC_FINAL_001.md` (ambos diferidos hasta cierre Monstruo completo + regeneración masiva coordinada)
- DSC enforced: DSC-S-001 + DSC-S-016 (audit binario Cowork verificó estado real bridge)
