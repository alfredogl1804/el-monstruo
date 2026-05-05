# A2UI Spec Draft — Para firma Alfredo + Cowork

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Draft v0.1 — pendiente de firma para que Sprint Mobile 1.B pueda arrancar
> **Bloquea:** Sprint Mobile 1.B (GenUI / A2UI Rendering en Flutter)
> **Lectura estimada Alfredo:** 5-10 min para firmar / proponer cambios

---

## Qué es A2UI

**A2UI = Agent-to-User-Interface protocol.** Es el contrato JSON entre el kernel del Monstruo y la app Flutter para que el kernel pueda generar **interfaces dinámicas** que la app renderiza, sin que el kernel necesite saber Flutter ni la app necesite hardcodear las pantallas.

Ejemplo concreto: cuando el Monstruo termina de generar una empresa (Sprint 87 NUEVO E2E), en lugar de devolver solo texto, devuelve un componente A2UI tipo `ResultCard` con campos estructurados (URL, screenshot, Critic Visual score, botones de acción) que la app renderiza con su look & feel del Brand DNA.

## Principios firmes

1. **JSON como contrato único.** Todo componente A2UI es un objeto JSON con `type`, `props`, `children` (recursivo).
2. **Whitelist de tipos cerrada.** La app solo renderiza tipos del whitelist. Tipos desconocidos → fallback a texto plano + warning.
3. **Brand DNA respetado.** Los componentes usan paleta forja + graphite + acero. El kernel NO especifica colores; la app los aplica según el tipo.
4. **Sin Turing-completeness.** A2UI NO ejecuta código arbitrario. NO hay loops, condicionales runtime, fetch dinámico. Solo describe layout + datos.
5. **Acciones declarativas.** Botones disparan eventos hacia el kernel via WebSocket (`{"type":"a2ui_action","action_id":"...","payload":{...}}`).
6. **Versionado.** Cada componente tiene `a2ui_version` (v1 inicial). Si en futuro se rompe compatibilidad, app respeta versionado.

## Tipos del whitelist v1 (firma minimal viable)

### Componentes contenedores

| Tipo | Props | Uso |
|---|---|---|
| `Stack` | `direction: "vertical" \| "horizontal"`, `spacing: int`, `padding: int` | Layout linear |
| `Card` | `title?: str`, `subtitle?: str`, `elevation: int` | Tarjeta con borde + Brand DNA |
| `Section` | `title: str`, `collapsible: bool` | Sección con título |

### Componentes de contenido

| Tipo | Props | Uso |
|---|---|---|
| `Text` | `value: str`, `style: "heading" \| "body" \| "caption" \| "code"`, `color: "primary" \| "secondary" \| "danger" \| "success"` | Texto con estilo Brand |
| `Markdown` | `value: str` | Markdown completo (re-usa renderer existente) |
| `Image` | `url: str`, `alt: str`, `aspect_ratio: float` | Imagen con loading state |
| `Link` | `url: str`, `label: str`, `external: bool` | Link clicable |
| `Code` | `value: str`, `language: str` | Bloque de código con highlighting |
| `Divider` | (vacío) | Separador horizontal |

### Componentes de acción

| Tipo | Props | Uso |
|---|---|---|
| `Button` | `label: str`, `action_id: str`, `variant: "primary" \| "secondary" \| "danger"`, `disabled: bool` | Botón que dispara acción al kernel |
| `ButtonGroup` | `buttons: [Button]`, `direction: "vertical" \| "horizontal"` | Grupo de botones |

### Componentes de datos estructurados

| Tipo | Props | Uso |
|---|---|---|
| `KeyValueList` | `pairs: [{key: str, value: str}]` | Lista clave-valor (ej. propiedades de una empresa generada) |
| `Table` | `headers: [str]`, `rows: [[str]]`, `max_rows_visible: int` | Tabla simple |
| `Badge` | `label: str`, `variant: "info" \| "success" \| "warning" \| "danger"` | Tag visual con color |

### Componentes de progreso

| Tipo | Props | Uso |
|---|---|---|
| `Progress` | `value: float (0-1)`, `label?: str` | Barra de progreso |
| `Stepper` | `steps: [{label, status}]`, `current: int` | Stepper para procesos multi-paso (ej. pipeline E2E del Sprint 87) |

### Componentes especializados Monstruo

| Tipo | Props | Uso |
|---|---|---|
| `EmpresaResultCard` | `nombre, propuesta, url, screenshot_url, critic_visual_score, comercializable: bool` | Tarjeta especializada para output del Sprint 87 NUEVO E2E |
| `LeadCard` | `nombre, empresa, score, qualification_status` | Tarjeta de lead del Sprint 90 Motor de Ventas |
| `ContenidoCard` | `titulo, keyword, longitud, estado, publicado_url?` | Tarjeta de contenido del Sprint 91 Motor de SEO |

## Esquema JSON canónico (ejemplo)

```json
{
  "a2ui_version": "1.0",
  "root": {
    "type": "Card",
    "props": {"title": "Tu empresa generada", "elevation": 2},
    "children": [
      {
        "type": "EmpresaResultCard",
        "props": {
          "nombre": "Forja Mate",
          "propuesta": "Plataforma de mate energético soberano",
          "url": "https://forjamate-x9k2.elmonstruo.dev",
          "screenshot_url": "https://cdn.elmonstruo/screenshots/forja-mate-x9k2.png",
          "critic_visual_score": 87,
          "comercializable": true
        }
      },
      {
        "type": "ButtonGroup",
        "props": {"direction": "horizontal"},
        "children": [
          {"type": "Button", "props": {"label": "Validar Test 1", "action_id": "validate_test_1", "variant": "primary"}},
          {"type": "Button", "props": {"label": "Regenerar", "action_id": "regenerate", "variant": "secondary"}},
          {"type": "Button", "props": {"label": "Descartar", "action_id": "discard", "variant": "danger"}}
        ]
      }
    ]
  }
}
```

## Acciones del usuario

Cuando el usuario clicka un `Button` con `action_id="validate_test_1"`, la app envía al kernel via WebSocket:

```json
{
  "type": "a2ui_action",
  "action_id": "validate_test_1",
  "payload": {
    "thread_id": "thr_abc123",
    "component_path": "root.children[0]",
    "context": {"empresa_url": "https://forjamate-x9k2.elmonstruo.dev"}
  },
  "timestamp": "2026-05-05T04:15:00Z"
}
```

El kernel responde con un nuevo componente A2UI que reemplaza o agrega al estado actual.

## Ciclo de vida de un componente A2UI

1. **Generación:** un Embrión o el orchestrator del Sprint 87 produce el JSON A2UI como output.
2. **Validación:** el kernel valida contra el schema de tipos whitelist antes de mandarlo. Si inválido → mandato error_card en lugar.
3. **Envío:** WebSocket message tipo `genui_component` con el JSON.
4. **Renderizado:** la app parsea el JSON, busca el renderer por `type`, recursivo en `children`.
5. **Interacción:** acciones del usuario se mandan de vuelta al kernel.
6. **Update:** el kernel puede mandar component nuevo que reemplaza o extiende el state.

## Validación del schema

El kernel mantiene `kernel/a2ui/schema.py` con Pydantic models de cada tipo. Cualquier output de Embrión o orchestrator que pretenda ser A2UI **DEBE** validar contra el schema antes de enviarse al WebSocket.

Si un Embrión genera A2UI inválido → fallback automático a `Markdown` con el contenido en texto plano + warning interno. NO se rompe la UX del usuario.

## Disciplina anti-Dory aplicada

- **Whitelist cerrada:** previene que un Embrión "alucine" un tipo nuevo y la app no sepa qué hacer.
- **Versionado:** previene drift cuando se agreguen tipos en v2.
- **Validación schema:** previene que JSON corrupto llegue a la app.
- **Sin Turing-completeness:** previene que el kernel se convierta en una vulnerabilidad de ejecución arbitraria en device.

## Conexiones cross-sprint

| Sprint | Cómo usa A2UI |
|---|---|
| Sprint 87 NUEVO E2E | Output final = `EmpresaResultCard` + `ButtonGroup` |
| Sprint 88 Embriones colectivos | Debate emergente puede mandar `Card` con `Stepper` mostrando ronda 1 → ronda 2 → conclusión |
| Sprint 89 Guardian Autónomo | Alertas críticas como `Card` rojo + `KeyValueList` con métrica afectada |
| Sprint 90 Motor de Ventas | `LeadCard` para cada lead capturado |
| Sprint 91 Motor de SEO | `ContenidoCard` para cada contenido publicado |

## Decisiones que necesito de Alfredo para firmar

1. **¿La whitelist v1 te parece completa?** Si querés algún tipo más (ej. `Chart` para FinOps, `Map` para empresas locales, `VideoPlayer`), agregamos antes de firmar.

2. **¿`EmpresaResultCard` con esos 6 campos te calza?** Es el output del Sprint 87 NUEVO. Si querés más campos (ej. `precio_estimado`, `industria`, `tags`), los agrego.

3. **¿Versionado v1 cerrado?** Una vez firmado, cualquier cambio implica `a2ui_version: 2.0` y migración explícita.

Si decís "**firmado**" o "**con tales cambios firmado**", quedo libre de despachar Sprint Mobile 1.B con este spec como contrato.

— Cowork (Hilo B)
