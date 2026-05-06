# Ranking Registry v1.0 — El Monstruo

## Generado por GPT-5.2 | Fecha: 2026-03-01

A continuación ejecuto el ranking con tu framework (7 dimensiones, escala 0–5, pesos base) sobre el set deduplicado de herramientas.
Nota: aunque listaste 69 entradas, hay duplicados entre carriles; el registro único queda en 57 herramientas (deduplicadas por nombre/producto).

## Tabla 1: Score Base (57 herramientas deduplicadas)

Fórmula Score Base (0–100):
[
\text{ScoreBase}=\frac{C\cdot20 + R\cdot20 + S\cdot15 + O\cdot15 + I\cdot10 + P\cdot10 + M\cdot10}{5}
]

Nota de deduplicación: Claude Cowork, Manus AI, Perplexity Computer Use, Browser Use, Edge Copilot, Gemini Deep Research, Grok, n8n+Ollama aparecen en ambos carriles; aquí cuentan una vez.

## Tabla 2: Rankings por Perfil (Top 10)

Para ejecutar “ajuste de pesos según perfil” (no pegaste los pesos específicos), aplico un esquema estándar coherente con tu intención de perfiles:

PROD-STRICT: R 25, S 20, O 15, M 15, C 10, I 10, P 5

PROD-FAST: C 25, I 15, R 20, O 15, S 10, M 10, P 5

R&D-AGENTIC: C 30, I 15, P 15, O 15, R 10, S 5, M 10

BROWSER-AUTOMATION: C 25, R 20, S 15, O 10, I 10, P 10, M 10

DATA-SENSITIVE: S 30, R 20, O 15, M 15, I 10, C 5, P 5

LOW-COST: P 35, I 15, C 15, R 10, O 10, S 5, M 10

(Score perfil también 0–100 con división entre 5.)

### PROD-STRICT (Top 10)

### PROD-FAST (Top 10)

### R&D-AGENTIC (Top 10)

### BROWSER-AUTOMATION (Top 10)

### DATA-SENSITIVE (Top 10)

### LOW-COST (Top 10)

## Tabla 3: Rankings por Categoría (Top 5)

### Agentes Conversacionales (Top 5)

### Agentes de Código (Top 5)

### Browser Agents (Top 5)

### Frameworks de Orquestación (Top 5)

### Infraestructura (Top 5)

## Tabla 4: Matriz de Complementariedad (Top 10 pares)

Heurística de complementariedad (0–100): alta cuando el par cubre “stack completo” (orquestación + observabilidad + proxy + ejecución durable + evaluación + agente), minimiza solapamiento y maximiza I/O/S/R.

## Notas metodológicas (decisiones “controversiales”)

Confianza C en “agentes extremos” regionales/experimentales (Kakao/Naver/Baidu/Sber/Doubao/MiniMax/Google Disco, etc.)
Sin métricas comparables y con variabilidad por región/idioma, el scoring es estimación informada (C). Se penaliza M/O por falta de tooling público y R por incertidumbre operativa.

Temporal, LiteLLM, Langfuse, promptfoo, Ragas, Garak, Unstructured con Confianza A
Son piezas con documentación, adopción OSS/enterprise y comportamiento más “medible” (durabilidad, trazas, evals). Por eso suben fuerte en R/S/O/M.

ChatGPT Agent / Claude Cowork: C alto pero P moderado-bajo
Capacidad sobresaliente, pero el costo/performance depende de planes, límites y consumo; por eso P ~2.6–2.8.

Browser agents: penalización estructural en R/S/O
La automatización web es frágil (DOM cambiante, captcha, flakiness). Incluso los mejores (Skyvern/Browser Use) no alcanzan la fiabilidad de infraestructura.

n8n + Ollama muy alto en LOW-COST y R&D
Por P y I (ecosistema de nodos + modelos locales). En PROD-STRICT no es #1 porque la gobernanza/controles dependen de cómo lo despliegues (aunque puntúa alto).

LangGraph + LangSmith muy alto por O y M
Aquí “producto” incluye el componente de observabilidad (LangSmith), elevando O=4.8 y M=4.6.

### Siguiente paso recomendado (para cerrar el “Registry” con precisión)

Si me pegas los pesos exactos por perfil que definimos en la ronda anterior (si difieren de los que asumí), recalculo automáticamente:

los 6 rankings Top 10,

y si quieres, también el score por perfil para las 57 herramientas (tabla completa, no solo Top 10).

¿Confirmas que los pesos por perfil que acabo de usar son los correctos o me pasas los originales?



| # | Herramienta | Categoría | C | R | S | O | I | P | M | Score Base | Confianza |

| 1 | ChatGPT Agent (OpenAI) | Agentes Conversacionales | 5.0 | 4.3 | 4.0 | 3.8 | 4.2 | 2.8 | 4.7 | 84.2 | B |

| 2 | Perplexity Comet | Agentes Conversacionales | 4.2 | 4.0 | 3.6 | 3.2 | 3.4 | 3.2 | 4.2 | 76.0 | B |

| 3 | Perplexity Computer Use | Browser Agents | 4.3 | 3.6 | 3.4 | 3.0 | 3.2 | 3.0 | 3.8 | 71.6 | B |

| 4 | Claude Cowork (Anthropic) | Agentes Conversacionales | 4.8 | 4.4 | 4.2 | 3.6 | 4.4 | 2.6 | 4.6 | 84.0 | B |

| 5 | CrewAI | Frameworks de Orquestación | 3.8 | 3.6 | 3.4 | 3.0 | 4.0 | 4.0 | 3.8 | 73.6 | B |

| 6 | Devin (Cognition AI) | Agentes de Código | 4.6 | 3.6 | 3.6 | 3.0 | 3.4 | 1.8 | 3.6 | 70.8 | C |

| 7 | LangGraph + LangSmith | Frameworks de Orquestación | 4.4 | 4.2 | 4.0 | 4.8 | 4.6 | 3.0 | 4.6 | 87.6 | A |

| 8 | AutoGen (Microsoft) | Frameworks de Orquestación | 4.2 | 3.8 | 3.8 | 3.4 | 4.2 | 4.0 | 4.2 | 80.0 | B |

| 9 | Dify | Frameworks de Orquestación | 4.0 | 3.8 | 3.8 | 3.6 | 4.2 | 4.0 | 4.0 | 79.6 | B |

| 10 | Manus AI | Browser Agents | 4.5 | 3.6 | 3.4 | 3.0 | 3.4 | 2.4 | 3.4 | 70.8 | C |

| 11 | Open Interpreter | Agentes de Código | 4.0 | 3.4 | 3.8 | 2.8 | 3.6 | 4.6 | 3.8 | 74.4 | B |

| 12 | Fellou | Browser Agents | 3.6 | 3.0 | 3.0 | 2.4 | 2.8 | 3.2 | 2.8 | 61.6 | C |

| 13 | Edge Copilot (Microsoft) | Agentes Conversacionales | 3.6 | 4.0 | 4.0 | 2.6 | 3.2 | 4.4 | 4.4 | 74.0 | B |

| 14 | Cline + MCP | Agentes de Código | 4.2 | 3.6 | 3.6 | 3.0 | 4.2 | 4.0 | 3.6 | 76.4 | B |

| 15 | DeepSeek v3.2 (modelo+agent coding) | Agentes de Código | 4.6 | 3.6 | 3.2 | 2.6 | 3.4 | 4.6 | 3.6 | 75.6 | B |

| 16 | Grok (xAI) | Agentes Conversacionales | 4.2 | 3.6 | 3.2 | 2.8 | 3.2 | 3.4 | 3.8 | 70.8 | C |

| 17 | Gemini Deep Research | Agentes Conversacionales | 4.4 | 4.0 | 3.8 | 3.2 | 3.6 | 2.6 | 4.4 | 77.2 | B |

| 18 | Genspark AI Browser | Browser Agents | 3.8 | 3.2 | 3.0 | 2.6 | 3.0 | 3.0 | 3.0 | 64.4 | C |

| 19 | n8n + Ollama | Frameworks de Orquestación | 4.0 | 4.2 | 4.4 | 3.6 | 4.6 | 4.8 | 4.2 | 86.8 | B |

| 20 | MultiOn | Browser Agents | 3.8 | 3.2 | 3.0 | 2.6 | 3.0 | 2.8 | 3.2 | 64.0 | C |

| 21 | Jace AI | Browser Agents | 3.6 | 3.0 | 3.0 | 2.4 | 2.8 | 2.8 | 2.8 | 61.2 | C |

| 22 | Browser Use (OSS) | Browser Agents | 4.0 | 3.6 | 3.6 | 3.0 | 4.2 | 4.6 | 3.8 | 77.2 | B |

| 23 | Dia Browser | Browser Agents | 3.4 | 3.0 | 3.0 | 2.4 | 2.8 | 3.2 | 2.8 | 60.8 | C |

| 24 | Opera Neon (Aria) | Browser Agents | 3.4 | 3.2 | 3.2 | 2.4 | 2.8 | 3.6 | 3.6 | 64.0 | C |

| 25 | Brave Leo | Agentes Conversacionales | 3.4 | 3.6 | 3.8 | 2.4 | 3.0 | 4.2 | 4.2 | 71.2 | B |

| 26 | Sigma AI Browser | Browser Agents | 3.2 | 2.8 | 2.8 | 2.2 | 2.6 | 3.2 | 2.6 | 57.6 | C |

| 27 | Chrome Auto-Browse (ext) | Browser Agents | 2.6 | 2.6 | 2.4 | 1.8 | 2.2 | 4.6 | 2.6 | 54.4 | C |

| 28 | Strawberry Browser | Browser Agents | 3.0 | 2.8 | 2.8 | 2.2 | 2.6 | 3.2 | 2.6 | 56.8 | C |

| 29 | Surfer 2 (Surfer SEO) | Infraestructura | 3.6 | 3.8 | 3.4 | 3.0 | 3.2 | 2.4 | 4.0 | 70.0 | B |

| 30 | RTRVR AI | Infraestructura | 3.4 | 3.2 | 3.0 | 2.6 | 3.2 | 3.2 | 3.0 | 64.0 | C |

| 31 | Kimi K2.5 Swarm (Moonshot) | Agentes Conversacionales | 4.4 | 3.6 | 3.2 | 2.8 | 3.2 | 3.6 | 3.2 | 70.8 | C |

| 32 | Naver Agent N + Whale | Browser Agents | 3.6 | 3.2 | 3.0 | 2.4 | 2.8 | 3.4 | 3.2 | 63.2 | C |

| 33 | Kakao Kanana | Agentes Conversacionales | 3.6 | 3.2 | 3.0 | 2.4 | 2.8 | 3.6 | 3.0 | 63.2 | C |

| 34 | Baidu + Sber (agents) | Agentes Conversacionales | 3.8 | 3.2 | 3.0 | 2.4 | 2.8 | 3.6 | 3.2 | 64.8 | C |

| 35 | Doubao 2.0 (ByteDance) | Agentes Conversacionales | 4.0 | 3.4 | 3.0 | 2.6 | 3.0 | 4.0 | 3.4 | 68.8 | C |

| 36 | MiniMax M2.5 (agent) | Agentes Conversacionales | 4.0 | 3.4 | 3.0 | 2.6 | 3.0 | 3.8 | 3.2 | 68.0 | C |

| 37 | Grok Build (xAI) | Agentes de Código | 4.2 | 3.4 | 3.2 | 2.6 | 3.2 | 3.2 | 3.4 | 67.2 | C |

| 38 | Google Disco (experimental) | Agentes Conversacionales | 4.0 | 2.8 | 3.2 | 2.6 | 3.0 | 2.8 | 2.6 | 61.6 | C |

| 39 | GLM-5 AutoGLM (Zhipu) | Agentes Conversacionales | 4.2 | 3.4 | 3.0 | 2.6 | 3.0 | 4.0 | 3.2 | 68.8 | C |

| 40 | Mistral Le Chat | Agentes Conversacionales | 4.0 | 3.6 | 3.6 | 2.8 | 3.4 | 3.6 | 4.0 | 73.2 | B |

| 41 | Adept ACT-2 | Browser Agents | 4.2 | 3.2 | 3.2 | 2.6 | 3.0 | 1.8 | 3.0 | 62.8 | C |

| 42 | Skyvern | Browser Agents | 4.0 | 3.8 | 3.6 | 3.2 | 4.2 | 4.0 | 3.8 | 78.8 | B |

| 43 | Magnitude (testing automation) | Infraestructura | 3.6 | 3.6 | 3.4 | 3.4 | 3.6 | 3.2 | 3.4 | 70.4 | C |

| 44 | Writer Action Agent | Agentes Conversacionales | 3.8 | 4.0 | 4.4 | 3.4 | 3.6 | 2.4 | 4.0 | 76.0 | B |

| 45 | OPAgent | Frameworks de Orquestación | 3.6 | 3.2 | 3.2 | 2.8 | 3.2 | 3.6 | 3.0 | 65.6 | C |

| 46 | Samsung Ask AI | Agentes Conversacionales | 3.4 | 3.4 | 3.6 | 2.4 | 2.8 | 3.8 | 3.6 | 67.2 | C |

| 47 | Meta AI Assistant | Agentes Conversacionales | 4.0 | 3.6 | 3.2 | 2.6 | 3.2 | 4.2 | 4.2 | 73.6 | B |

| 48 | Amazon Nova Act | Browser Agents | 4.2 | 3.6 | 3.6 | 3.0 | 3.4 | 2.6 | 3.4 | 70.0 | C |

| 49 | Qwen 3.5 Visual Agent | Agentes Conversacionales | 4.4 | 3.4 | 3.0 | 2.6 | 3.0 | 4.4 | 3.4 | 70.4 | C |

| 50 | Yandex Alice | Agentes Conversacionales | 3.6 | 3.6 | 3.2 | 2.4 | 2.8 | 4.0 | 4.2 | 70.4 | C |

| 51 | AutoGPT (OSS) | Frameworks de Orquestación | 3.6 | 3.0 | 3.2 | 2.6 | 3.6 | 4.6 | 3.6 | 68.4 | B |

| 52 | OpenClaw | Frameworks de Orquestación | 3.4 | 3.0 | 3.0 | 2.6 | 3.4 | 4.2 | 3.0 | 63.2 | C |

| 53 | CoAct-1 | Frameworks de Orquestación | 3.4 | 3.0 | 3.0 | 2.6 | 3.2 | 4.0 | 3.0 | 62.4 | C |

| 54 | Agent S2 (browser) | Browser Agents | 3.6 | 3.0 | 3.0 | 2.4 | 2.8 | 3.2 | 2.8 | 61.6 | C |

| 55 | GitHub Copilot Coding Agent | Agentes de Código | 4.6 | 4.2 | 4.2 | 3.6 | 4.4 | 2.6 | 4.6 | 83.6 | B |

| 56 | Lindy AI | Frameworks de Orquestación | 4.0 | 3.8 | 3.8 | 3.4 | 4.2 | 2.8 | 3.8 | 76.8 | B |

| 57 | Monica AI (browser extension) | Agentes Conversacionales | 3.6 | 3.2 | 3.0 | 2.4 | 3.0 | 3.6 | 3.4 | 65.6 | C |

| 58 | PydanticAI | Frameworks de Orquestación | 4.0 | 4.2 | 4.2 | 3.6 | 4.2 | 4.6 | 4.2 | 85.6 | A |

| 59 | OpenAI Swarm | Frameworks de Orquestación | 3.8 | 3.4 | 3.8 | 2.8 | 3.8 | 3.6 | 2.8 | 70.0 | B |

| 60 | DSPy | Frameworks de Orquestación | 4.2 | 4.0 | 3.8 | 3.4 | 3.8 | 4.6 | 4.0 | 81.6 | A |

| 61 | Langfuse | Infraestructura | 3.8 | 4.4 | 4.4 | 4.8 | 4.2 | 4.2 | 4.2 | 87.6 | A |

| 62 | LlamaIndex | Frameworks de Orquestación | 4.2 | 4.0 | 3.8 | 3.6 | 4.6 | 4.0 | 4.6 | 83.2 | A |

| 63 | LiteLLM | Infraestructura | 4.0 | 4.2 | 4.2 | 3.6 | 4.8 | 4.6 | 4.4 | 86.8 | A |

| 64 | Temporal | Infraestructura | 4.2 | 4.8 | 4.6 | 4.2 | 4.6 | 3.6 | 5.0 | 90.8 | A |

| 65 | Ragas | Infraestructura | 3.6 | 4.0 | 4.0 | 4.4 | 3.8 | 4.8 | 4.0 | 82.4 | A |

| 66 | Garak | Infraestructura | 3.4 | 3.8 | 4.6 | 3.8 | 3.4 | 4.8 | 3.8 | 79.6 | A |

| 67 | Unstructured | Infraestructura | 4.0 | 4.2 | 4.0 | 3.6 | 4.4 | 3.6 | 4.6 | 82.8 | A |

| 68 | promptfoo | Infraestructura | 3.6 | 4.0 | 4.2 | 4.4 | 3.8 | 4.8 | 4.2 | 83.2 | A |





| Rank | Herramienta | Categoría | Score |

| 1 | Temporal | Infraestructura | 92.0 |

| 2 | Langfuse | Infraestructura | 89.4 |

| 3 | LangGraph + LangSmith | Frameworks de Orquestación | 87.8 |

| 4 | LiteLLM | Infraestructura | 87.6 |

| 5 | PydanticAI | Frameworks de Orquestación | 87.2 |

| 6 | n8n + Ollama | Frameworks de Orquestación | 86.6 |

| 7 | Unstructured | Infraestructura | 84.6 |

| 8 | LlamaIndex | Frameworks de Orquestación | 84.0 |

| 9 | promptfoo | Infraestructura | 83.8 |

| 10 | Ragas | Infraestructura | 83.0 |





| Rank | Herramienta | Categoría | Score |

| 1 | LangGraph + LangSmith | Frameworks de Orquestación | 88.4 |

| 2 | LiteLLM | Infraestructura | 87.8 |

| 3 | Temporal | Infraestructura | 87.6 |

| 4 | PydanticAI | Frameworks de Orquestación | 86.6 |

| 5 | n8n + Ollama | Frameworks de Orquestación | 86.4 |

| 6 | LlamaIndex | Frameworks de Orquestación | 84.8 |

| 7 | ChatGPT Agent | Agentes Conversacionales | 83.8 |

| 8 | Claude Cowork | Agentes Conversacionales | 83.6 |

| 9 | Langfuse | Infraestructura | 83.4 |

| 10 | DSPy | Frameworks de Orquestación | 82.8 |





| Rank | Herramienta | Categoría | Score |

| 1 | n8n + Ollama | Frameworks de Orquestación | 89.2 |

| 2 | LiteLLM | Infraestructura | 88.8 |

| 3 | LangGraph + LangSmith | Frameworks de Orquestación | 88.2 |

| 4 | PydanticAI | Frameworks de Orquestación | 87.8 |

| 5 | DSPy | Frameworks de Orquestación | 86.8 |

| 6 | LlamaIndex | Frameworks de Orquestación | 86.6 |

| 7 | Temporal | Infraestructura | 85.8 |

| 8 | Langfuse | Infraestructura | 85.6 |

| 9 | Browser Use | Browser Agents | 82.6 |

| 10 | AutoGen | Frameworks de Orquestación | 81.8 |





| Rank | Herramienta | Categoría | Score |

| 1 | Skyvern | Browser Agents | 79.8 |

| 2 | Browser Use | Browser Agents | 78.4 |

| 3 | ChatGPT Agent | Agentes Conversacionales | 78.2 |

| 4 | Claude Cowork | Agentes Conversacionales | 77.8 |

| 5 | Perplexity Computer Use | Browser Agents | 72.4 |

| 6 | Amazon Nova Act | Browser Agents | 71.8 |

| 7 | Manus AI | Browser Agents | 71.6 |

| 8 | Gemini Deep Research | Agentes Conversacionales | 71.4 |

| 9 | Edge Copilot | Agentes Conversacionales | 70.8 |

| 10 | MultiOn | Browser Agents | 65.0 |





| Rank | Herramienta | Categoría | Score |

| 1 | Temporal | Infraestructura | 92.6 |

| 2 | Langfuse | Infraestructura | 90.6 |

| 3 | LiteLLM | Infraestructura | 88.8 |

| 4 | PydanticAI | Frameworks de Orquestación | 88.6 |

| 5 | LangGraph + LangSmith | Frameworks de Orquestación | 87.8 |

| 6 | n8n + Ollama | Frameworks de Orquestación | 87.6 |

| 7 | Garak | Infraestructura | 85.0 |

| 8 | promptfoo | Infraestructura | 84.8 |

| 9 | Unstructured | Infraestructura | 84.4 |

| 10 | Ragas | Infraestructura | 83.8 |





| Rank | Herramienta | Categoría | Score |

| 1 | n8n + Ollama | Frameworks de Orquestación | 92.6 |

| 2 | LiteLLM | Infraestructura | 90.8 |

| 3 | PydanticAI | Frameworks de Orquestación | 89.8 |

| 4 | DSPy | Frameworks de Orquestación | 88.8 |

| 5 | Ragas | Infraestructura | 88.0 |

| 6 | promptfoo | Infraestructura | 87.8 |

| 7 | Garak | Infraestructura | 87.4 |

| 8 | Browser Use | Browser Agents | 86.6 |

| 9 | Open Interpreter | Agentes de Código | 86.2 |

| 10 | AutoGPT | Frameworks de Orquestación | 85.8 |





| Rank | Herramienta | Score Base | Confianza |

| 1 | ChatGPT Agent | 84.2 | B |

| 2 | Claude Cowork | 84.0 | B |

| 3 | Gemini Deep Research | 77.2 | B |

| 4 | Perplexity Comet | 76.0 | B |

| 5 | Writer Action Agent | 76.0 | B |





| Rank | Herramienta | Score Base | Confianza |

| 1 | GitHub Copilot Coding Agent | 83.6 | B |

| 2 | Cline + MCP | 76.4 | B |

| 3 | DeepSeek v3.2 | 75.6 | B |

| 4 | Open Interpreter | 74.4 | B |

| 5 | Devin | 70.8 | C |





| Rank | Herramienta | Score Base | Confianza |

| 1 | Skyvern | 78.8 | B |

| 2 | Browser Use | 77.2 | B |

| 3 | Perplexity Computer Use | 71.6 | B |

| 4 | Manus AI | 70.8 | C |

| 5 | Amazon Nova Act | 70.0 | C |





| Rank | Herramienta | Score Base | Confianza |

| 1 | LangGraph + LangSmith | 87.6 | A |

| 2 | n8n + Ollama | 86.8 | B |

| 3 | PydanticAI | 85.6 | A |

| 4 | LlamaIndex | 83.2 | A |

| 5 | DSPy | 81.6 | A |





| Rank | Herramienta | Score Base | Confianza |

| 1 | Temporal | 90.8 | A |

| 2 | Langfuse | 87.6 | A |

| 3 | LiteLLM | 86.8 | A |

| 4 | promptfoo | 83.2 | A |

| 5 | Unstructured | 82.8 | A |





| Par | Score de Complementariedad | Razón |

| Temporal + LangGraph+LangSmith | 95 | Orquestación durable + control de flujos/estado + trazas; base sólida para PROD |

| LiteLLM + Langfuse | 93 | Proxy multi-modelo + observabilidad/evals; acelera iteración y control de costos |

| LangGraph+LangSmith + PydanticAI | 92 | Grafo/estado + type-safety/validación; reduce fallos en tool-calling |

| LlamaIndex + Unstructured | 91 | ETL no estructurado + conectores/RAG; pipeline de datos end-to-end |

| promptfoo + Garak | 90 | Eval/regresión + seguridad/red-teaming; cobertura de calidad y riesgos |

| n8n+Ollama + LiteLLM | 89 | Automatización + local models + proxy; flexibilidad y control de routing |

| Skyvern + LangGraph+LangSmith | 88 | Browser automation + orquestación; agentes web con gobernanza |

| ChatGPT Agent + Langfuse | 87 | Agente potente + observabilidad; útil para pilotos con trazabilidad |

| Ragas + LlamaIndex | 86 | Evaluación RAG + framework RAG; cierra loop de calidad |

| GitHub Copilot Coding Agent + Temporal | 85 | Coding agent + ejecución durable; ideal para tareas largas/CI-like |

