---
id: DSC-LF-004
proyecto: LA-FORJA
tipo: contrato_arquitectonico
titulo: "Magna validation usa Perplexity sonar-reasoning-pro y devuelve PerplexityMagnaResponse con citations: string[]. Es la única capa de validación en tiempo real porque ningún otro proveedor (Anthropic/OpenAI/Google) expone citations nativas como contrato"
estado: firme (canonizado retroactivamente 2026-05-16)
fecha_decision: 2026-04-XX (durante D2 spec)
fecha_firma_T1: 2026-05-16 (firma retroactiva por canonización capilla LA-FORJA)
fecha_firma_T2A: 2026-05-16 (Cowork audit D2 — verificó router.ts enrutamiento + tipo PerplexityMagnaResponse)
fuentes:
  - repo:apps/la-forja/api/src/lib/llm/router.ts (magna_validation → sonar-reasoning-pro)
  - repo:apps/la-forja/api/src/lib/llm/perplexity.ts (PerplexityMagnaResponse type)
  - repo:apps/la-forja/api/src/routes/tutor.ts (magna PRE-stream con citations en headers)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md:23 (DSC propuesto)
  - repo:bridge/cowork_to_manus_LA_FORJA_001_D2_AUDIT_RESULT.md:24 (router enforced verificado)
  - skill:protocolo-operativo-core (capa de validación tiempo real obligatoria)
  - skill:validacion-tiempo-real (ventaja competitiva de Manus sobre training cutoff)
cruza_con: [DSC-LF-001, DSC-LF-002, DSC-LF-003, DSC-LF-005, DSC-G-005]
---

# Magna validation con Perplexity Sonar Reasoning Pro

## Decisión

La misión `magna_validation` enruta exclusivamente al modelo **Perplexity `sonar-reasoning-pro`** y devuelve la forma canónica:

```ts
type PerplexityMagnaResponse = {
  text: string;          // razonamiento sintetizado
  citations: string[];   // URLs verificables, contrato no-vacío en respuesta exitosa
  model: string;         // siempre "sonar-reasoning-pro"
  usage: { /* tokens */ };
};
```

**Citations es contrato.** Cualquier respuesta sin `citations: string[]` con al menos una URL en happy-path es regresión bloqueante.

## Por qué Perplexity y no Anthropic/OpenAI/Google

Anthropic Claude, OpenAI GPT y Google Gemini exponen búsqueda web como **tool call opcional**, no como contrato del response. Eso significa:

- **Claude:** puede usar `web_search` tool, pero el modelo puede ignorarlo o invocarlo parcialmente. Citations no son un campo garantizado del response.
- **GPT:** función `browsing` similar — opcional, sin contrato de URLs.
- **Gemini:** `grounding` reciente, pero respuestas estructuradas no incluyen URLs como campo top-level.

**Perplexity Sonar Reasoning Pro** está diseñado como motor de validación web — `citations: string[]` es campo obligatorio del API response. Es el único proveedor donde "validación con citaciones verificables" es contrato API, no comportamiento emergente.

Esto se alinea con la doctrina del Monstruo: `skill:validacion-tiempo-real` exige que toda síntesis pase por validación con fuentes externas verificables. DSC-LF-004 es la materialización en La Forja de esa doctrina.

## Rol de magna en el flujo del tutor (post-D3.2)

En el flujo SSE del chat tutor (DSC-LF-005), magna corre **PRE-stream** (no post-stream) cuando `requireValidation === true`:

```
preCallCheck classifier → invokeClassifier (JSON, ~200ms)
  → preCallCheck magna → invokeMagna (Perplexity, ~3-8s)
    → postCallCommit magna
    → preCallCheck tutor → buildTutorStream (Anthropic SSE)
      → toUIMessageStreamResponse({ headers: { "x-la-forja-citations-b64": ... } })
```

Las citations viajan al frontend en el header `x-la-forja-citations-b64` (base64url + cap 2KB iterativo, ver F-D3.2-03/04 y F-D3.2.1-01 cerrados en D3.2.2). Razón del orden PRE-stream documentada en `apps/la-forja/api/src/routes/tutor.ts` banner: el stream una vez iniciado no permite agregar headers de respuesta, y las citations son metadata pre-stream por contrato.

## Implicaciones

- **Cualquier sprint que toque `lib/llm/router.ts` debe preservar el enrutamiento `magna_validation → sonar-reasoning-pro`.** Cambiarlo requiere DSC nuevo + auditar el contrato de citations del nuevo proveedor.
- **Sprint D6 (provider unification)** podría agregar fallback secundario (e.g. Tavily, Exa) si Perplexity tiene outage, pero la respuesta default sigue siendo Perplexity. Cualquier fallback requiere mapeo del response al tipo `PerplexityMagnaResponse` para mantener el contrato del tutor estable.
- **El ratio costo/valor de magna es alto** (~0.040 USD por validación vs. ~0.075 USD por turn de tutor). Por eso `requireValidation` es opt-in del frontend (default `false` en D3.2, UI toggle agendado D3.3).

## Estado de validación

**firme.** Cowork audit D2 verificó `router.ts` enrutamiento + tipo `PerplexityMagnaResponse`. Cowork audit D3.2 (commit `2ac7f81`) revalidó como punto P-06 ("magna PRE-stream con citations en headers, doctrina §4.5 _DOCTRINA_D3.md cumplida"). Disputa F-D3.2-08 (sdk legacy preservado) — el SDK legacy `@anthropic-ai/sdk@0.96.0` mantiene `invokeTutor` JSON-blocking, pero magna NUNCA usa ese path porque su contrato Perplexity es ortogonal al SDK Anthropic.
