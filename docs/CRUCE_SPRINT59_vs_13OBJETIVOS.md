# Cruce Sprint 59 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (modo detractor activado)
**Metodología:** Cada objetivo se evalúa como si un inversionista escéptico preguntara: "¿Esto realmente mueve la aguja o es feature creep?"

---

## Matriz de Impacto

| # | Objetivo | Impacto Sprint 59 | Cobertura Acumulada | Veredicto |
|---|---|---|---|---|
| 1 | Crear Empresas Digitales | MEDIO — i18n expande mercados pero no crea empresas nuevas | 85% | Habilitador, no creador |
| 2 | Todo Nivel Apple/Tesla | MEDIO — Embrión-Creativo eleva estándares visuales | 65% | Diseño sí, pero ¿enforcement? |
| 3 | Máximo Poder, Mínima Complejidad | **ALTO** — Conversational UX es exactamente esto | **70%** | Primer avance real en UX |
| 4 | Nunca Se Equivoca Dos Veces | BAJO — No agrega error learning | 70% | No es scope |
| 5 | Gasolina Magna vs Premium | BAJO — No toca tier routing | 75% | Ya cubierto |
| 6 | Vanguardia Perpetua | BAJO — trend_scan del Creativo es reactivo | 50% | No es auto-update |
| 7 | No Inventar la Rueda | ALTO — DeepL, react-i18next en vez de custom | 90% | Excelente adherencia |
| 8 | Inteligencia Emergente | **ALTO** — Primer tracker real de emergencia | **70%** | Finalmente medible |
| 9 | Transversalidad Universal | NULO — Ya completo | 100% | N/A |
| 10 | Simulador Predictivo | BAJO — Estratega puede alimentar simulador | 65% | Indirecto |
| 11 | Multiplicación de Embriones | **ALTO** — 5/7 embriones (Creativo + Estratega) | **71%** | Buen progreso |
| 12 | Ecosistema / Soberanía | MEDIO — LLM translation como fallback soberano | 40% | Parcial |
| 13 | Del Mundo | **MÁXIMO** — Primer sprint que lo aborda | **60%** | De 0% a 60% |

---

## Análisis Detractor por Épica

### Épica 59.1 — i18n Engine

**Lo que funciona:** Arquitectura de dos niveles (interno + proyectos) es correcta. DeepL para EU + LLM para el resto es pragmático. Locale configs con RTL support.

**Lo que no funciona:**

1. **500K chars/mes de DeepL Free es NADA para producción.** Un solo proyecto con 50 páginas de contenido consume ~100K chars. 5 proyectos al mes = límite alcanzado. El plan dice "$0" pero en realidad necesitará Pro ($5.49/mes + per-char) rápidamente.

2. **Detección de idioma por heurística de caracteres es frágil.** ¿Qué pasa con texto mixto (spanglish, code-switching)? ¿Qué pasa con idiomas que comparten script latino (es, pt, fr, it)? La heurística solo funciona para CJK y Arabic.

3. **10 idiomas iniciales pero solo 2 en los templates React.** El template `_react_i18n_template()` solo genera es/en. ¿Dónde están los otros 8? El usuario esperaría soporte completo.

4. **No hay quality assurance de traducciones.** Traducir con LLM puede producir errores sutiles (false friends, cultural inappropriateness). No hay back-translation check ni human-in-the-loop.

5. **RTL (Arabic) mencionado pero no implementado.** Solo hay `direction: "rtl"` en config. ¿Dónde está el CSS? ¿Los templates React manejan RTL? No hay evidencia.

### Épica 59.2 — Conversational UX Layer

**Lo que funciona:** Intent parsing con LLM es el approach correcto. Quick commands como shortcuts. Confidence threshold con clarification. Suggestions de next actions.

**Lo que no funciona:**

1. **Depende 100% de LLM para intent parsing.** Si el LLM está lento (>3s) o caído, toda la UX se rompe. No hay fallback local (regex, keyword matching) para intents obvios.

2. **9 intent types es muy limitado.** ¿Qué pasa con "quiero cambiar el color del logo"? ¿"Necesito una factura"? ¿"Cancela mi suscripción"? Muchos requests reales no encajan en los 9 tipos.

3. **No hay contexto conversacional.** Cada request se parsea de forma aislada. No hay memoria de la conversación anterior. "Hazlo más grande" — ¿qué es "lo"? Sin contexto, es imposible.

4. **El endpoint /chat no tiene rate limiting.** Un usuario podría spamear requests y quemar el budget de LLM. Necesita integración con el rate_limiter existente.

5. **No hay feedback loop.** Si el usuario dice "no, eso no es lo que quise" — ¿cómo aprende el sistema? No hay mecanismo de corrección.

### Épica 59.3 — Embrión-Creativo

**Lo que funciona:** System prompt estricto anti-AI-slop. Brand identity generation con constraints reales (WCAG, Google Fonts). Design review con scoring dimensional.

**Lo que no funciona:**

1. **"Nivel Apple/Tesla" es un claim vacío sin calibración.** ¿Qué score en design_review corresponde a "nivel Apple"? ¿8/10? ¿9/10? Sin calibración contra diseños reales de Apple, el scoring es arbitrario.

2. **No genera assets visuales reales.** Genera un `logo_prompt` pero ¿quién ejecuta la generación? No hay integración con DALL-E, Midjourney, o Stable Diffusion. El embrión es "all talk, no action" en lo visual.

3. **scan_design_trends() usa LLM, no web scraping real.** Las "tendencias" que reporta son las que el LLM conoce de su training data, no las tendencias ACTUALES. Para tendencias reales necesita acceso a Dribbble, Behance, Awwwards.

4. **No hay persistencia de decisiones de diseño.** Si genera una brand identity, ¿dónde se guarda? ¿Cómo se reutiliza en futuras iteraciones? No hay design system storage.

### Épica 59.4 — Embrión-Estratega

**Lo que funciona:** ICE framework para priorización. Kill criteria en strategic plans. Competitive intelligence como tarea autónoma.

**Lo que no funciona:**

1. **Market analysis basado en LLM es unreliable.** Los LLMs inventan números de mercado. "TAM de $50B" puede ser completamente fabricado. Sin acceso a Statista, IBISWorld, o datos reales, el análisis es ficción.

2. **scan_market_opportunities() es genérico.** Siempre producirá las mismas "oportunidades" porque el LLM no tiene acceso a datos en tiempo real. Necesita integración con APIs de tendencias (Google Trends, Product Hunt, etc.).

3. **No hay validación cruzada.** El Estratega produce análisis pero nadie lo verifica. Los Sabios deberían cross-check sus claims, no solo generarlos.

4. **competitive_intel cada 48h es demasiado lento.** En mercados digitales, 48 horas es una eternidad. Un competidor puede lanzar un producto en ese tiempo.

### Épica 59.5 — Emergent Behavior Tracker

**Lo que funciona:** Definición estricta de emergencia (4 criterios). Deduplication por hash. Novelty + usefulness scoring. Persistence en Supabase.

**Lo que no funciona:**

1. **El tracker usa LLM para evaluar emergencia — ¿quién evalúa al evaluador?** Si el LLM dice "esto es emergente" con confidence 0.8, ¿es realmente emergente o el LLM está siendo complaciente? No hay ground truth.

2. **False positive rate será ALTO.** Los LLMs tienden a ser optimistas. Decir "esto es emergente" es más interesante que "esto es normal." El threshold de 0.7 probablemente no es suficiente.

3. **No hay definición operacional de "no programado explícitamente."** ¿Cómo sabe el tracker qué está programado y qué no? Necesitaría un inventario de todos los handlers/behaviors del sistema para comparar.

4. **Reproducibility es un campo de texto, no un test.** Dice "condiciones para reproducir" pero no intenta reproducirlo. Un comportamiento verdaderamente emergente debería ser reproducible — ¿por qué no intentarlo automáticamente?

---

## Correcciones Mandatorias

### C1: i18n Engine necesita fallback local para detección de idioma latino

**Problema:** Heurística de caracteres no distingue entre es/pt/fr/it/en.
**Corrección:** Agregar n-gram based language detection como capa intermedia antes de LLM.

```python
# Usar langdetect o fasttext para scripts latinos
# Solo recurrir a LLM si confidence < 0.8
from langdetect import detect, detect_langs

async def detect_language(self, text: str) -> str:
    # Layer 1: Character set (CJK, Arabic, etc.)
    charset_result = self._detect_by_charset(text)
    if charset_result:
        return charset_result
    
    # Layer 2: Statistical detection (fast, no LLM cost)
    try:
        detected = detect(text)
        if detected in [e.value for e in SupportedLocale]:
            return detected
    except:
        pass
    
    # Layer 3: LLM (only if layers 1-2 fail)
    ...
```

**Dependencia adicional:** `langdetect>=1.0.9` en requirements.txt

### C2: Conversational UX necesita memoria conversacional

**Problema:** Cada request se parsea aisladamente, sin contexto.
**Corrección:** Agregar `ConversationMemory` que mantiene últimos N turns.

```python
@dataclass
class ConversationMemory:
    """Memoria de conversación para contexto."""
    max_turns: int = 10
    turns: list[dict] = field(default_factory=list)
    
    def add_turn(self, role: str, content: str, intent: Optional[str] = None):
        self.turns.append({"role": role, "content": content, "intent": intent})
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
    
    def get_context_prompt(self) -> str:
        """Generar contexto para el LLM."""
        if not self.turns:
            return ""
        context = "Previous conversation:\n"
        for turn in self.turns[-5:]:
            context += f"- {turn['role']}: {turn['content'][:100]}\n"
        return context
```

### C3: Embrión-Creativo necesita integración con generación de imágenes

**Problema:** Genera `logo_prompt` pero no ejecuta la generación.
**Corrección:** Integrar con el tool `generate_image` existente o con API de generación.

```python
async def generate_visual_asset(self, prompt: str, asset_type: str = "logo") -> str:
    """Generar asset visual usando el pipeline de generación."""
    # Enrich prompt based on brand identity
    enriched_prompt = await self._enrich_visual_prompt(prompt, asset_type)
    
    # Call image generation (via existing tool or API)
    result = await self._image_generator.generate(
        prompt=enriched_prompt,
        style="professional",
        size="1024x1024",
    )
    return result.url
```

### C4: Embrión-Estratega necesita acceso a datos reales (no solo LLM)

**Problema:** Market analysis basado solo en LLM produce datos fabricados.
**Corrección:** Integrar con Perplexity/Sonar Pro para datos en tiempo real.

```python
async def analyze_market(self, niche: str, geography: str = "global") -> MarketAnalysis:
    """Analizar mercado con datos REALES via Perplexity."""
    # Step 1: Get real data from Perplexity (web-grounded)
    real_data = await self._perplexity.research(
        f"market size and growth rate for {niche} in {geography} 2026"
    )
    
    # Step 2: Structure with LLM using real data as input
    prompt = f"""Structure this market data into analysis format.
    RAW DATA (from web research): {real_data}
    ..."""
```

### C5: Emergence Tracker necesita behavior inventory para comparación

**Problema:** No puede determinar si algo es "no programado" sin saber qué SÍ está programado.
**Corrección:** Mantener un registro de todos los handlers/behaviors conocidos.

```python
# Behavior registry — updated each sprint
KNOWN_BEHAVIORS = {
    "translate_text": ["i18n_engine"],
    "parse_intent": ["conversational_ux"],
    "generate_brand": ["embrion_creativo"],
    "analyze_market": ["embrion_estratega"],
    # ... all known behaviors
}

def is_known_behavior(self, action_type: str, components: list[str]) -> bool:
    """Verificar si este comportamiento está en el registry."""
    known = KNOWN_BEHAVIORS.get(action_type, [])
    return set(components) == set(known)
```

### C6: Rate limiting para /chat endpoint

**Problema:** El endpoint /chat no tiene protección contra abuse.
**Corrección:** Integrar con el rate_limiter existente (Sprint 3).

```python
# En kernel/main.py
@app.post("/chat")
@rate_limited(rpm=30, rph=200)  # Más restrictivo que endpoints normales
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    ...
```

### C7: Templates i18n deben cubrir todos los locales soportados

**Problema:** Template React solo genera es/en, pero el engine soporta 10 locales.
**Corrección:** `generate_i18n_template()` debe generar archivos para TODOS los locales activos.

```python
def _react_i18n_template(self) -> dict[str, str]:
    files = {}
    # Generate locale file for EACH supported locale
    for locale in SupportedLocale:
        files[f"src/i18n/locales/{locale.value}.json"] = self._generate_locale_strings(locale.value)
    # ... rest of template
    return files
```

---

## Resumen de Correcciones

| ID | Corrección | Severidad | Épica Afectada |
|---|---|---|---|
| C1 | Fallback local para detección de idioma (langdetect) | ALTA | 59.1 |
| C2 | Memoria conversacional para contexto | ALTA | 59.2 |
| C3 | Integración con generación de imágenes | MEDIA | 59.3 |
| C4 | Datos reales via Perplexity (no solo LLM) | ALTA | 59.4 |
| C5 | Behavior inventory para emergence comparison | MEDIA | 59.5 |
| C6 | Rate limiting para /chat | ALTA | 59.2 |
| C7 | Templates para todos los locales soportados | MEDIA | 59.1 |

---

## Veredicto Final

Sprint 59 es **ambicioso y necesario** pero tiene un problema fundamental: **demasiada dependencia en LLM para todo.** Intent parsing, language detection, market analysis, emergence evaluation, design trends — todo pasa por el LLM. Esto crea:

1. **Single point of failure:** Si el LLM está lento/caído, TODO se rompe
2. **Cost explosion:** Cada feature agrega más LLM calls
3. **Reliability issues:** LLMs son probabilísticos, no determinísticos

**Fortalezas:**
- Finalmente aborda Obj #13 (de 0% a 60% — el salto más grande de cualquier sprint)
- Conversational UX es el primer paso real hacia Obj #3
- Emergence Tracker hace medible lo que antes era aspiracional
- 5/7 embriones es buen progreso hacia Obj #11

**Debilidades:**
- Over-reliance en LLM sin fallbacks locales
- Embrión-Estratega produce análisis sin datos reales
- Embrión-Creativo no genera assets (solo prompts)
- Conversational UX sin memoria = frustración del usuario

**Recomendación:** Implementar C1, C2, C4, y C6 como parte del sprint (son P0). C3 y C5 pueden ser Sprint 60.

---

## Estado Acumulado de los 13 Objetivos (Post Sprint 59)

| # | Objetivo | Cobertura | Sprints que contribuyen |
|---|---|---|---|
| 1 | Crear Empresas Digitales | 85% | 51, 52, 53, 57, 58 |
| 2 | Todo Nivel Apple/Tesla | 65% | 53, 57, 59 |
| 3 | Máximo Poder, Mínima Complejidad | 70% | 52, 53, **59** |
| 4 | Nunca Se Equivoca Dos Veces | 70% | 53, 54, 58 |
| 5 | Gasolina Magna vs Premium | 75% | 52, 55, 56, 57 |
| 6 | Vanguardia Perpetua | 50% | 55, 56 |
| 7 | No Inventar la Rueda | 90% | 52, 55, 56, 57, 58, 59 |
| 8 | Inteligencia Emergente | 70% | 54, 55, 56, **59** |
| 9 | Transversalidad Universal | 100% | 57, 58 |
| 10 | Simulador Predictivo | 65% | 55, 56 |
| 11 | Multiplicación de Embriones | 71% | 54, 56, 57, 58, **59** |
| 12 | Ecosistema / Soberanía | 40% | 56 |
| 13 | Del Mundo | 60% | **59** |

**Gaps restantes para Sprint 60:**
- Obj #6 (Vanguardia Perpetua): 50% — necesita auto-update proactivo
- Obj #12 (Ecosistema/Soberanía): 40% — necesita más infraestructura propia
- Obj #10 (Simulador Predictivo): 65% — necesita calibración y UI
- Obj #1 (Crear Empresas): 85% — necesita demo end-to-end
