# SÍNTESIS — Metodología de Ranking Real de Agentes de IA

## Consenso de los 5 Sabios (Semilla v7.2)

Respondieron: 5/5 (GPT-5.4, Claude Opus 4, Grok 4, Perplexity Sonar, Gemini 3.1 Pro — este último truncado a 707 chars)

## PUNTO DE CONVERGENCIA ABSOLUTO (5/5 sabios)

"La única forma de medir autonomía es ejecutar tareas reales y medir resultados. Todo lo demás es teatro."

Los 5 sabios coinciden en que:

Ejecución empírica obligatoria — nada de documentación, nada de marketing

Batería estandarizada de tareas — las mismas tareas para todos

Múltiples dominios — no solo coding

Normalización estadística — z-scores o percentiles, no puntos brutos

Repetición — mínimo 3 ejecuciones por tarea para reducir varianza

Evaluación ciega — ocultar identidad del agente durante scoring

## DIMENSIONES CONSENSUADAS

## PROTOCOLO DE PRUEBA — SÍNTESIS

### Estructura de 3 niveles (Perplexity + Claude)

Nivel 1: Baseline Común (15 tareas multi-dominio)
Tareas que TODOS los agentes pueden intentar, sin ventaja de especialización:

5 tareas técnicas (código, debugging, API integration)

5 tareas analíticas (investigación, datos, matemáticas)

5 tareas creativas/comunicativas (redacción, planificación, síntesis)

Nivel 2: Especialidad (10 tareas por dominio)
Donde cada agente demuestra fortaleza en su dominio:

Coding: SWE-bench adaptado + suite propia

Web: WebArena variante + flujos reales

Investigación: GAIA variante + análisis de papers

Business: análisis de datos + estrategia

Nivel 3: Estrés Multi-Dominio (5 tareas)
Tareas que requieren saltar entre dominios sin aviso:

"Investiga una startup, escribe código para visualizar su mercado, calcula ROI"

### Protocolo de ejecución

Prompts idénticos para todos los agentes

Timeout: 30 min por tarea (constraint de producción real)

3 ejecuciones por tarea (mediana, no máximo)

Logging completo: {timestamp, action, tool, params, result, error_flag}

Evaluación ciega: código aleatorio por agente

### Scoring por tarea (Claude)

0 pts: No completa o falla críticamente

1 pt: Completa parcialmente con errores

2 pts: Completa correctamente

3 pts: Completa + insight/optimización adicional

## NORMALIZACIÓN CROSS-DOMAIN — CONSENSO

Método: Z-score adaptativo con baselines humanos (Perplexity + Grok)

Establecer baselines humanos: 3 expertos por dominio completan cada tarea

Score relativo: (Agente - Baseline Mínimo) / (Baseline Experto - Baseline Mínimo)

Z-score por cohorte: Estandarizar dentro de grupos de agentes similares

Perfiles de capacidad: No promediar entre dominios — publicar breakdown completo

Ranking global: Mediana de los 3 dominios (no promedio)

## AGENTES SIN ACCESO DIRECTO — CONSENSO

Estrategia de 3 capas (Claude + Perplexity):

Proxy Testing: Contactar 2-3 usuarios reales con acceso, enviarles batería estandarizada

Análisis de ejecuciones públicas: Demos, tweets, videos donde se pueda medir output

Evaluación indirecta: Marcar como "Datos de Terceros" con factor de corrección 0.85x

Regla de exclusión: Si un agente tiene <2 evaluaciones confiables, NO entra al ranking principal — va a "ranking secundario / pendiente de evaluación".

## TAMAÑO DE MUESTRA — CONSENSO

## ANTI-SESGO — PROTOCOLO DE 6 CAPAS (Claude)

Sesgo de documentación → Evaluación ciega (código aleatorio)

Sesgo cultural/regional → Tareas en múltiples idiomas, 20% tareas no-occidentales

Sesgo de dominio → Igual número de tareas por dominio, normalización percentil

Sesgo de acceso → Budget fijo, metodología proxy, transparencia

Sesgo de evaluador → 2 sabios por tarea, tercer sabio si desacuerdo >20%

Sesgo temporal → Ventana de 2 semanas, control de versiones, re-test a 1 mes

## PROPUESTA EJECUTABLE INMEDIATA

### Lo que podemos hacer MAÑANA con nuestras herramientas:

Herramientas disponibles:

Manus (shell, browser, APIs, archivos)

5 sabios vía API (GPT-5.4, Claude, Gemini, Grok, Perplexity)

OpenRouter (acceso a múltiples modelos)

Cloudflare Workers AI

Apify (scraping)

AWS

Fase Piloto (1 semana):

Diseñar 15 tareas Nivel 1 estandarizadas

Ejecutar contra los 10 agentes que tenemos acceso vía API

Los 5 sabios evalúan outputs de forma ciega

Calcular z-scores y publicar ranking piloto

Validar con benchmarks públicos como sanity check

Agentes con acceso directo vía API:

Claude (Anthropic API) ✓

GPT/Codex (OpenAI API) ✓

Gemini (Google API) ✓

Grok (xAI API) ✓

Perplexity (Sonar API) ✓

Modelos vía OpenRouter (Kimi, DeepSeek, Qwen, etc.) ✓

Cloudflare Workers AI (modelos open source) ✓

Agentes que requieren proxy:

Devin, Cursor, Manus, Copilot, Windsurf, etc. (requieren interfaz, no solo API)

## DIFERENCIA CLAVE CON NUESTROS INTENTOS ANTERIORES

## FUENTES

GPT-5.4: Framework de 7 dimensiones con PCA

Claude Opus 4: SETC (Sistema de Evaluación Triangulada por Capacidad) — el más detallado

Grok 4: Sandbox de simulación híbrida con tareas mutantes

Perplexity Sonar: Batería Triple con baselines humanos — el más ejecutable

Gemini 3.1 Pro: (truncado) Manus como orquestador universal



| Dimensión | GPT-5.4 | Claude | Grok | Perplexity | Peso consenso |

| Task Success Rate (TSR) | ✓ | ✓ (40%) | ✓ (25%) | ✓ (30%) | 30% |

| Recuperación de errores | ✓ | ✓ (30%) | ✓ (20%) | ✓ (20%) | 20% |

| Versatilidad/Alcance | ✓ | ✓ (20%) | ✓ (20%) | — | 15% |

| Independencia (sin humano) | ✓ | ✓ (10%) | ✓ (20%) | — | 15% |

| Calidad de trayectoria | — | — | — | ✓ (20%) | 10% |

| Eficiencia (tiempo/costo) | ✓ | — | ✓ (15%) | ✓ (10%) | 10% |





| Parámetro | Claude | Grok | Perplexity | Consenso |

| Tareas por agente | 15 + 5 complejas | 10 × 3 rep = 30 | 85 total | 30 mínimo |

| Repeticiones | No especifica | 3 | 3 | 3 |

| Confianza | 95% | 95% | 95% | 95% |

| Margen error | ±5% | <5% | ±5% | ±5% |

| Tiempo total | 5 semanas | 2 semanas | 2 semanas | 2-3 semanas |





| Aspecto | v1.0 (fallido) | v2.0 (fallido) | v3.0 (propuesta) |

| Fuente de datos | Documentación | Benchmarks ajenos | Ejecución propia |

| Evaluación | 1 API por agente | Triangulación | Batería estandarizada + ciega |

| Dominios | Todos mezclados | Sesgado a coding | 3 niveles balanceados |

| Normalización | Ninguna | Ninguna | Z-score + baselines humanos |

| Reproducibilidad | Nula | Parcial | 100% (logs + código abierto) |

| Agentes excluidos | Muchos | Muchos | Protocolo proxy para todos |

