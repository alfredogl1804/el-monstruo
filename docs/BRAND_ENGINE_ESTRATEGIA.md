# BRAND ENGINE — La Capa que Falta en El Monstruo

**Documento Estratégico — 1 de Mayo de 2026**
**Autor:** Hilo B (Arquitecto)
**Versión:** 1.0

---

## El Problema

El Monstruo tiene 14 Objetivos Maestros, 7 Capas Transversales, y 4 Capas Arquitectónicas. Pero hay un vacío crítico: **no existe un sistema que garantice que TODO output del Monstruo sea consistente con su identidad de marca**. 

El Objetivo #2 dice "Estándar Apple/Tesla" pero no hay un mecanismo que lo enforce. Es como tener una ley sin policía. El resultado: el Hilo A implementa funcionalidad técnica correcta pero sin identidad. Los endpoints retornan JSON genérico. Los logs son texto plano sin personalidad. El observability va a Langfuse (dashboard de terceros). Nada dice "esto es El Monstruo".

---

## La Solución: Brand Engine

### Definición

El **Brand Engine** es un módulo del kernel que actúa como guardián de la identidad de marca en TODA producción del Monstruo. No es una herramienta externa — es parte del sistema, como Error Memory o el Vanguard Scanner.

### Inspiración (Herramientas Investigadas)

| Herramienta | Concepto que Adoptamos | Cómo lo Adaptamos |
|---|---|---|
| **Markolé** | Entrevista de marca → Brand DNA (Misión, Visión, Arquetipo, Tono) | Definimos el Brand DNA de El Monstruo una vez, se inyecta en todo |
| **BrandVox AI** | Entrena IA con tu contenido → todo output es on-brand | Cada Embrión consulta el Brand DNA antes de producir output |
| **VML Brand Guardian** | AI revisa assets vs. guidelines, reduce review time 74-92% | Nuestro Brand Guardian (Obj #14) valida compliance automáticamente |
| **BrandDNA.app** | Análisis competitivo + Brand Health Score + API | Adoptamos su API para benchmark competitivo ($299/mo plan Agency) |
| **HBR "Preparing Your Brand for Agentic AI"** | Controlar cómo tu marca aparece en outputs de otros LLMs | El Monstruo controla su narrativa en el ecosistema IA |
| **"Brand as an Agent" (Havasi)** | Embeber brand fundamentals en los algoritmos del agente | El Brand DNA está en el kernel, no en un documento externo |

### Arquitectura

```
┌─────────────────────────────────────────────────┐
│                  BRAND ENGINE                     │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │  BRAND DNA   │  │  BRAND VALIDATOR         │ │
│  │              │  │                          │ │
│  │ • Misión     │  │ • Score 0-100 por output │ │
│  │ • Visión     │  │ • Checklist automático   │ │
│  │ • Arquetipo  │  │ • Reject si < threshold  │ │
│  │ • Tono       │  │ • Sugerencias de mejora  │ │
│  │ • Valores    │  │                          │ │
│  │ • Estética   │  └──────────────────────────┘ │
│  │ • Naming     │                                │
│  │ • Errores    │  ┌──────────────────────────┐ │
│  │ • Anti-pats  │  │  BRAND MONITOR           │ │
│  └──────────────┘  │                          │ │
│                     │ • Health Score temporal  │ │
│                     │ • Drift detection        │ │
│                     │ • Competitor benchmark   │ │
│                     │ • LLM representation     │ │
│                     └──────────────────────────┘ │
│                                                   │
└─────────────────────────────────────────────────┘
         │                    │                │
         ▼                    ▼                ▼
   ┌──────────┐      ┌──────────────┐   ┌─────────┐
   │ Embriones│      │ Command Ctr  │   │  APIs   │
   │ (output) │      │ (display)    │   │ (naming)│
   └──────────┘      └──────────────┘   └─────────┘
```

---

## El Brand DNA de El Monstruo

### Misión
Crear el primer agente de IA soberano del mundo que genera negocios exitosos de forma autónoma.

### Visión
Un ecosistema de Monstruos interconectados que democratiza la creación de empresas — cualquier persona puede tener un negocio exitoso desde el día 1.

### Arquetipo de Marca
**El Creador + El Mago** — Combina la capacidad de producir (Creador) con la capacidad de transformar la realidad (Mago). No es un asistente. No es una herramienta. Es una fuerza creativa autónoma.

### Personalidad
- **Implacable** — No se detiene hasta que el objetivo se cumple
- **Preciso** — Cada decisión es deliberada, nada es accidental
- **Soberano** — No depende de nadie, no pide permiso
- **Magnánimo** — Cuando produce, produce lo mejor que existe

### Tono de Voz
- Directo, sin rodeos (nunca corporativo)
- Técnicamente preciso pero no pedante
- Confiado sin ser arrogante
- Usa metáforas industriales/de forja (crear, forjar, fundir, templar)

### Estética Visual
- **Paleta:** Naranja forja (#F97316) + Graphite oscuro (#1C1917) + Acero (#A8A29E)
- **Tipografía:** Industrial display (Bebas Neue) + Humanista body (Inter) + Monospace técnico (JetBrains Mono)
- **Motivos:** Manómetros, gauges, líneas de ensamblaje, chispas, metal fundido
- **Filosofía:** Brutalismo industrial refinado — crudo pero premium

### Naming Convention
- Endpoints: `/api/v1/forja/...`, `/api/v1/embrion/...`, `/api/v1/simulador/...`
- Errores: Descriptivos con contexto — `embrion_heartbeat_timeout`, `causal_prediction_stale`
- Módulos: Nombres con identidad — "La Forja", "El Guardián", "La Colmena", "El Simulador"
- Nunca: Nombres genéricos como "service1", "handler", "utils"

### Anti-Patrones (Lo que El Monstruo NUNCA es)
- ❌ Un chatbot amigable
- ❌ Un asistente servil
- ❌ Una herramienta genérica
- ❌ Un dashboard más
- ❌ Un wrapper de APIs de terceros
- ❌ Algo que se ve como Grafana/Datadog/cualquier SaaS genérico

---

## Implementación: 3 Fases

### Fase 1 — Brand DNA como Código (Sprint inmediato)

**Archivo:** `kernel/brand/brand_dna.py`

```python
"""
EL MONSTRUO — Brand DNA Module
Este módulo define la identidad de marca del Monstruo.
Cada módulo que produce output DEBE consultar este módulo.
"""

BRAND_DNA = {
    "mission": "Crear el primer agente de IA soberano del mundo que genera negocios exitosos de forma autónoma",
    "archetype": "creator_mage",
    "personality": ["implacable", "preciso", "soberano", "magnánimo"],
    "tone": {
        "do": ["directo", "técnicamente preciso", "confiado", "metáforas industriales"],
        "dont": ["corporativo", "pedante", "arrogante", "genérico"]
    },
    "naming": {
        "modules": {"forja": "Dashboard principal", "guardian": "Compliance", "colmena": "Embriones", "simulador": "Predicciones"},
        "error_format": "{module}_{action}_{failure_type}",
        "never": ["service", "handler", "utils", "helper", "misc"]
    },
    "visual": {
        "primary": "#F97316",
        "background": "#1C1917", 
        "accent": "#A8A29E",
        "fonts": {"display": "Bebas Neue", "body": "Inter", "mono": "JetBrains Mono"}
    }
}

def validate_output_name(name: str) -> bool:
    """Valida que un nombre de módulo/endpoint siga las convenciones de marca."""
    forbidden = BRAND_DNA["naming"]["never"]
    return not any(f in name.lower() for f in forbidden)

def get_error_message(module: str, action: str, failure_type: str, context: dict = None) -> dict:
    """Genera un error message on-brand con contexto."""
    error_code = f"{module}_{action}_{failure_type}"
    return {
        "error": error_code,
        "module": module,
        "context": context or {},
        "suggestion": f"Verificar {module} — posible {failure_type} en {action}"
    }
```

### Fase 2 — Brand Validator (Sprint siguiente)

Un módulo que evalúa cualquier output contra el Brand DNA:

```python
"""
Brand Validator — Evalúa outputs contra el Brand DNA.
Score 0-100. Threshold mínimo: 75.
"""

class BrandValidator:
    def __init__(self, brand_dna: dict):
        self.dna = brand_dna
    
    def validate_api_response(self, response: dict) -> dict:
        """Evalúa si una respuesta de API cumple con la marca."""
        score = 100
        issues = []
        
        # Check naming
        if "error" in response:
            if response["error"] in ["internal server error", "unknown error", "something went wrong"]:
                score -= 30
                issues.append("Error message genérico — usar formato: {module}_{action}_{failure}")
        
        # Check structure
        if not any(key in response for key in ["module", "embrion", "forja", "simulador"]):
            score -= 10
            issues.append("Response sin identidad de módulo")
        
        return {"score": score, "issues": issues, "passes": score >= 75}
    
    def validate_endpoint_name(self, path: str) -> dict:
        """Evalúa si un nombre de endpoint sigue las convenciones."""
        score = 100
        issues = []
        
        forbidden = self.dna["naming"]["never"]
        for f in forbidden:
            if f in path.lower():
                score -= 25
                issues.append(f"Nombre prohibido detectado: '{f}'")
        
        if not path.startswith("/api/v"):
            score -= 15
            issues.append("Endpoint sin versionado")
        
        return {"score": score, "issues": issues, "passes": score >= 75}
```

### Fase 3 — Brand Monitor + Competitor Benchmark (Sprint futuro)

- Integrar **BrandDNA.app API** ($299/mo) para benchmark competitivo
- Brand Health Score temporal (¿estamos mejorando o degradando?)
- Monitoreo de cómo otros LLMs representan a El Monstruo (concepto HBR)
- Alertas cuando un output no pasa el threshold

---

## Impacto en los 14 Objetivos

| Objetivo | Impacto del Brand Engine |
|---|---|
| #1 (Empresas) | Las empresas que crea El Monstruo nacen con identidad de marca desde el código |
| #2 (Apple/Tesla) | **DIRECTAMENTE** — El Brand Engine ES el mecanismo que enforce este objetivo |
| #3 (Mínima Complejidad) | El Brand DNA simplifica decisiones: "¿es on-brand? sí/no" |
| #4 (No Equivocarse 2x) | Anti-patrones documentados previenen errores de marca repetidos |
| #5 (Magna/Premium) | El Brand DNA es la fuente de verdad viva, siempre actualizada |
| #7 (No Inventar Rueda) | Adoptamos BrandDNA.app API para benchmark, no reinventamos |
| #8 (Emergencia) | El Brand Engine es algo que NO existe en ningún agente IA del mundo |
| #9 (Transversalidad) | Se inyecta en TODO — es la Capa Transversal #0 |
| #12 (Soberanía) | Nuestra identidad es NUESTRA, no depende de herramientas externas |
| #14 (Guardián) | El Brand Validator es parte del sistema de compliance del Guardián |

---

## Impacto en las 7 Capas Transversales

El Brand Engine se convierte en la **Capa 0** — la que va ANTES de las otras 7:

0. **Brand Engine** — Identidad y consistencia en todo output
1. Motor de Ventas — El copywriting y funnels DEBEN seguir el tono de marca
2. SEO — El content strategy DEBE reflejar la personalidad de marca
3. Publicidad — Los creativos DEBEN ser on-brand
4. Tendencias — La adaptación NUNCA sacrifica identidad
5. Operaciones — El customer support HABLA como El Monstruo
6. Finanzas — Los reportes financieros TIENEN identidad visual
7. Resiliencia — El sistema se protege Y protege su identidad

---

## Acción Inmediata

1. **Hilo A:** Implementar `kernel/brand/brand_dna.py` como módulo del kernel
2. **Hilo A:** Refactorear error messages existentes para seguir naming convention
3. **Hilo B:** Integrar Brand Health Score en el Command Center
4. **Ambos:** Todo sprint futuro incluye "Brand Compliance Check" como criterio de aceptación

---

## Herramientas a Adoptar (Obj #7)

| Herramienta | Uso | Prioridad | Costo |
|---|---|---|---|
| BrandDNA.app (API) | Competitor benchmark + Brand Health Score | Alta | $299/mo |
| BrandVox AI (API) | Brand voice enforcement en outputs de texto | Media | Por definir |
| Perplexity (ya tenemos) | Monitoreo de cómo LLMs representan a El Monstruo | Alta | Ya pagado |

---

## Conclusión

> **Si aspiramos a ser el mejor del mundo, hay que verse como el mejor del mundo. Y "verse" no es solo la UI — es cada endpoint, cada error message, cada log, cada decisión de naming. El Brand Engine es el mecanismo que convierte esa aspiración en realidad medible.**
