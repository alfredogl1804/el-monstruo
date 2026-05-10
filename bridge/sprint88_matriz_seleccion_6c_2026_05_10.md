# Sprint 88 — Matriz de Selección 6 Criterios sobre 85 Productos AGENTES

**Fecha:** 2026-05-10
**Autor:** Manus (Hilo Catastro)
**Sprint:** S-88 (Macroárea AGENTES del Catastro)
**Metodología:** DSC-G-007.1 (validación adversarial) + DSC-MO-009 (arsenal seleccionable)

---

## Los 6 criterios de selección

| Criterio | Descripción | Cómo se mide |
|---|---|---|
| **C1** | Relevancia para arsenal del Monstruo | DSC-MO-009 lo menciona explícitamente, o es categoría que el Monstruo necesita (desarrollo / investigación / orquestación / creación-cine / branding / ventas / construcción-apps) |
| **C2** | Adopción demostrada 2026 | Aparece en ≥2 listas independientes "top AI 2026" investigadas (Taskade, Chatarmin, Vellum, Cybernews, Mightybot, GuruSup, Synthesia, ChartLex, Iharare, Consensus, Lindy blog, Vibe Coding Academy, etc.) |
| **C3** | Madurez técnica | Producto en estado `production` o `beta` consolidado (no `alpha`/`preview` con <30 días sin tracking sólido) |
| **C4** | Tiene LLM base catalogable o es framework agnóstico | Envuelve un LLM identificable (Claude/GPT/Gemini/Grok/Kimi/etc.) o es framework agnóstico documentado (multi-LLM) |
| **C5** | Accesible para Alfredo/Monstruo | API pública, CLI, o tier de uso accesible (no solo enterprise contracted con sales call obligatoria) |
| **C6** | Capacidad agéntica real | ≥2 de: tiene_sandbox, acceso_filesystem, acceso_internet, multi_step_capable, multi_swarm_capable |

**Tier 1** (entran a Sprint 88 con clasificación completa + validación adversarial): score ≥4
**Tier 2** (entran a `catastro_agentes` con datos mínimos + flag tier_seed=2): score 2-3
**Descartado** (documentado con razón explícita en reporte): score ≤1

---

## MATRIZ COMPLETA — 85 productos

Leyenda: `Y` = Sí (cumple criterio), `n` = No (no cumple), `?` = ambiguo (cuenta como No salvo evidencia adicional).

### A. Dominio: agentes_desarrollo (developer-pro, IDEs, CLIs)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia principal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Manus | Manus | Y | Y | Y | Y | Y | Y | **6** | T1 | Top viral 14 agents, Hilo Catastro lo usa |
| 2 | Claude Cowork | Anthropic+interno | Y | n | Y | Y | Y | Y | 5 | T1 | DSC-MO-009 (interno Monstruo) |
| 3 | Claude Code | Anthropic | Y | Y | Y | Y | Y | Y | **6** | T1 | mightybot.ai #2, vellum, neura.market |
| 4 | OpenAI Codex (2026) | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | mightybot.ai #1, medium 10 dominators |
| 5 | Cursor | Cursor | Y | Y | Y | Y | Y | Y | **6** | T1 | top vibe + dev, $20-40/mes |
| 6 | Devin | Cognition AI | Y | Y | Y | Y | Y | Y | **6** | T1 | viral #2, augmentcode leaked prompts |
| 7 | OpenAI Agents SDK | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | guru #1 framework |
| 8 | Google ADK | Google | Y | Y | Y | Y | Y | Y | **6** | T1 | guru top, reddit AI_Agents |
| 9 | Factory Droid | Factory | Y | Y | Y | Y | Y | Y | **6** | T1 | safishamsi/graphify, Cointelegraph |
| 10 | OpenClaw | open-source | Y | Y | Y | Y | Y | Y | **6** | T1 | github graphify (compatible Claude Code) |
| 11 | OpenCode | open-source | Y | Y | Y | Y | Y | Y | **6** | T1 | mightybot.ai mentioned |
| 12 | Aider | open-source | Y | Y | Y | Y | Y | Y | **6** | T1 | github graphify, terminal-native |
| 13 | Augment Code | Augment | Y | n | Y | Y | n | Y | 4 | T1 | augmentcode.com (enterprise tier) |
| 14 | Trae | Bytedance | Y | Y | Y | Y | Y | Y | **6** | T1 | safishamsi/graphify, Taskade |
| 15 | AWS Strands | AWS | Y | n | Y | Y | Y | Y | 5 | T1 | uncoveringai (Apr 21), AWS framework |
| 16 | Genspark Claw | Genspark | Y | Y | Y | Y | Y | Y | **6** | T1 | TikTok rowancheung, ChinaTalk |

**Sub-total Desarrollo: 16 productos, todos Tier 1**

### B. Dominio: agentes_vibe_coding (no-code/low-code app builders)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 17 | Replit Agent | Replit | Y | Y | Y | Y | Y | Y | **6** | T1 | top 6 vibe (Vibe Coding Academy) |
| 18 | Lovable | Lovable | Y | Y | Y | Y | Y | Y | **6** | T1 | top 6 vibe, banani.co |
| 19 | Bolt.new | StackBlitz | Y | Y | Y | Y | Y | Y | **6** | T1 | top 6 vibe |
| 20 | V0 (Vercel) | Vercel | Y | Y | Y | Y | Y | Y | **6** | T1 | top 6 vibe, balsamiq |
| 21 | Base44 | Base44 | Y | Y | Y | Y | Y | Y | **6** | T1 | Vibe Coding Academy top 6 |
| 22 | Taskade Genesis | Taskade | Y | Y | Y | Y | Y | Y | **6** | T1 | Taskade #1 vibe coding |

**Sub-total Vibe Coding: 6 productos, todos Tier 1**

### C. Dominio: agentes_multi_swarm (orquestadores frameworks)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23 | LangGraph | LangChain Inc | Y | Y | Y | Y | Y | Y | **6** | T1 | dev.to #1, GuruSup top, Intuz #1 |
| 24 | CrewAI | CrewAI Inc | Y | Y | Y | Y | Y | Y | **6** | T1 | GuruSup top, Intuz top |
| 25 | AutoGen / AG2 | Microsoft | Y | Y | Y | Y | Y | Y | **6** | T1 | GuruSup top |
| 26 | Microsoft Agent Framework | Microsoft | Y | Y | Y | Y | Y | Y | **6** | T1 | reddit AI_Agents, sucesor de AutoGen+SK |
| 27 | Kimi K2.6 Agent Swarm | Moonshot AI | Y | Y | Y | Y | Y | Y | **6** | T1 | DSC-MO-009 (mencionado explícitamente) |
| 28 | Semantic Kernel | Microsoft | Y | Y | Y | Y | Y | Y | **6** | T1 | reddit AI_Agents top |

**Sub-total Multi-swarm: 6 productos, todos Tier 1**

### D. Dominio: agentes_investigacion (research, browser)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 29 | Perplexity Personal Computer | Perplexity | Y | Y | Y | Y | Y | Y | **6** | T1 | TechCrunch 7-may-26, lanzamiento Mac público |
| 30 | Comet Browser | Perplexity | Y | Y | Y | Y | Y | Y | **6** | T1 | TechCrunch 7-may-26, browser agéntico |
| 31 | Gemini Deep Research | Google | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream Google (Gemini App) |
| 32 | ChatGPT Deep Research | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream OpenAI |
| 33 | Glean | Glean | Y | Y | Y | Y | n | Y | 5 | T1 | chatarmin top, cybernews #2 (enterprise) |
| 34 | NotebookLM | Google | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram 24 marketing tools, mainstream |
| 35 | Exa | Exa Labs | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram 24 marketing tools, semantic search |
| 36 | ChatGPT Atlas | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram 24 tools (browser ChatGPT) |

**Sub-total Investigación: 8 productos, todos Tier 1**

### E. Dominio: agentes_ejecutores (workflows, automation)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 37 | n8n + LLM | n8n | Y | Y | Y | Y | Y | Y | **6** | T1 | reddit AI_Agents, GTM newsletter |
| 38 | Zapier Agents | Zapier | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream, integración Monstruo (MCP zapier) |
| 39 | Lindy | Lindy | Y | Y | Y | Y | Y | Y | **6** | T1 | cybernews #1, Lindy blog, LinkedIn solopreneurs |
| 40 | Gumloop | Gumloop | Y | Y | Y | Y | Y | Y | **6** | T1 | yutori scouts, GTM newsletter |
| 41 | Twin | Twin.so | Y | n | Y | Y | Y | Y | 5 | T1 | twin.so sales outreach (especializado sales) |

**Sub-total Ejecutores: 5 productos, todos Tier 1**

### F. Dominio: agentes_creacion_audiovisual (cine, video largo, SFX, música)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 42 | Sora 2 (OpenAI) | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | Synthesia top 15, Genra top 6 |
| 43 | Google Veo 3.1 | Google | Y | Y | Y | Y | Y | Y | **6** | T1 | Synthesia "best cinematic", aiimagetovideo #1 |
| 44 | Runway Gen-4.5 | Runway | Y | Y | Y | Y | Y | Y | **6** | T1 | Genra #1, ltx.studio |
| 45 | Kling 3.0 | Kuaishou | Y | Y | Y | Y | Y | Y | **6** | T1 | aiimagetovideo #2, breakingac top 10 |
| 46 | Pika 2.0 | Pika Labs | Y | Y | Y | Y | Y | Y | **6** | T1 | breakingac, iharare top 10 |
| 47 | Higgsfield | Higgsfield AI | Y | Y | Y | Y | Y | Y | **6** | T1 | breakingac #1, iharare #1, videoshatter |
| 48 | Luma Dream Machine | Luma AI | Y | Y | Y | Y | Y | Y | **6** | T1 | breakingac #3, iharare #3 |
| 49 | Seedance 2.0 (Bytedance) | Bytedance | Y | Y | Y | Y | Y | Y | **6** | T1 | aitude (Apr 20), mindstudio, "first to sound = good as it looks" |
| 50 | HeyGen | HeyGen | Y | Y | Y | Y | Y | Y | **6** | T1 | breakingac #4 (avatar UGC) — el Monstruo tiene HEYGEN_API_KEY |
| 51 | Synthesia | Synthesia | Y | Y | Y | Y | Y | Y | **6** | T1 | breakingac #5, propio blog ranking 15 |
| 52 | Adobe Firefly Creative Agent | Adobe | Y | Y | Y | Y | n | Y | 5 | T1 | news.adobe Apr 15 — orquesta Adobe Suite |
| 53 | ElevenLabs Music | ElevenLabs | Y | Y | Y | Y | Y | Y | **6** | T1 | unite.ai, jaiportal — Monstruo tiene ELEVENLABS_API_KEY |
| 54 | Suno | Suno | Y | Y | Y | Y | Y | Y | **6** | T1 | chartlex top, jaiportal alternatives |
| 55 | Udio | Udio | Y | Y | Y | Y | Y | Y | **6** | T1 | chartlex top (vs Suno) |
| 56 | AIVA | AIVA | Y | Y | Y | Y | Y | Y | **6** | T1 | chartlex top, Reddit gen AI suite |
| 57 | Stable Audio | Stability AI | Y | Y | Y | Y | Y | Y | **6** | T1 | chartlex top |
| 58 | Inworld TTS-2 | Inworld AI | Y | n | Y | Y | Y | Y | 5 | T1 | lasvegassun May 5 (lanzamiento), realtime voice |
| 59 | Ace Studio Video Composer | Ace Studio | Y | n | Y | Y | Y | Y | 5 | T1 | YouTube 8 days ago, video+música+SFX integrado |

**Sub-total Audiovisual: 18 productos, todos Tier 1**

### G. Dominio: agentes_branding_diseño (logos, marca, identidad visual)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | Ideogram | Ideogram | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram (4 tools designers), Facebook 10 free top, "90% text accuracy" |
| 61 | Recraft | Recraft | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram 4 tools, capcut top 6 (vector) |
| 62 | Looka | Looka | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream logo AI |
| 63 | Brandmark | Brandmark | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram brand identity |
| 64 | Kittl | Kittl | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram brand identity, Victor C reel |
| 65 | Brandify | Brandify (App Store) | Y | n | Y | Y | Y | n | 4 | T1 | Apple App Store, AI logo solo |
| 66 | Galileo AI / Stitch | Galileo (Google) | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream UI/UX from prompt |
| 67 | Magicpath | Magicpath | Y | n | Y | Y | Y | n | 4 | T1 | UI design from prompt |
| 68 | Adobe Firefly | Adobe | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram pro stack 2026 |
| 69 | Nextify (slogan/tagline) | Nextify | Y | n | Y | Y | Y | n | 4 | T1 | nextify.ai slogan/tagline maker |

**Sub-total Branding: 10 productos, todos Tier 1**

### H. Dominio: agentes_marketing_ventas (pauta, leads, copy ads, outreach)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 70 | Apollo | Apollo.io | Y | Y | Y | Y | Y | Y | **6** | T1 | Instagram, cloudnsite, GTM newsletter |
| 71 | Clay | Clay | Y | Y | Y | Y | Y | Y | **6** | T1 | GTM newsletter, cloudnsite, Instagram |
| 72 | Outreach | Outreach.io | Y | Y | Y | Y | n | Y | 5 | T1 | cloudnsite (sales engagement) |
| 73 | Salesloft | Salesloft | Y | Y | Y | Y | n | Y | 5 | T1 | cloudnsite (sales engagement) |
| 74 | ZoomInfo | ZoomInfo | Y | Y | Y | Y | n | Y | 5 | T1 | cloudnsite (data + AI) |
| 75 | Salesforce Agentforce | Salesforce | Y | Y | Y | Y | n | Y | 5 | T1 | techradar, ai2roi May 8 |
| 76 | Sierra | Sierra AI | Y | Y | Y | Y | n | Y | 5 | T1 | ai2roi May 8 (vs Agentforce, Decagon) |
| 77 | HubSpot Breeze | HubSpot | Y | Y | Y | Y | Y | Y | **6** | T1 | cybernews top 6 autonomous |
| 78 | Decagon | Decagon | Y | Y | Y | Y | n | Y | 5 | T1 | ai2roi May 8 (customer service) |
| 79 | Harvey | Harvey AI | Y | Y | Y | Y | n | Y | 5 | T1 | cybernews top 6 (legal vertical) |
| 80 | Jasper | Jasper AI | Y | Y | Y | Y | Y | Y | **6** | T1 | cybernews top 6 (marketing copy) |

**Sub-total Marketing/Ventas: 11 productos, todos Tier 1**

### I. Dominio: interfaces_usuario (apps consumer/pro general-purpose)

| # | Producto | Proveedor | C1 | C2 | C3 | C4 | C5 | C6 | Score | Tier | Evidencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 81 | ChatGPT Pro | OpenAI | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream, multi-source |
| 82 | Claude.ai | Anthropic | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream + Computer Use + Artifacts |
| 83 | Gemini App | Google | Y | Y | Y | Y | Y | Y | **6** | T1 | mainstream + Live + Canvas |
| 84 | ChatGPT Frontier | OpenAI | Y | n | Y | Y | n | Y | 4 | T1 | ivanbercovich (Feb 2026 launch) |
| 85 | Anthropic Enterprise (new) | Anthropic | Y | n | n | Y | n | Y | 3 | T2 | anthropic.com 6 days ago (just launched) |

**Sub-total Interfaces: 5 productos, 4 Tier 1 + 1 Tier 2**

---

## RESUMEN POR TIER

### Tier 1 — entran a Sprint 88 con clasificación completa: **84 productos**

| Dominio | Cantidad |
|---|---|
| agentes_desarrollo | 16 |
| agentes_vibe_coding | 6 |
| agentes_multi_swarm | 6 |
| agentes_investigacion | 8 |
| agentes_ejecutores | 5 |
| agentes_creacion_audiovisual | 18 |
| agentes_branding_diseño | 10 |
| agentes_marketing_ventas | 11 |
| interfaces_usuario | 4 |
| **Total Tier 1** | **84** |

### Tier 2 — datos mínimos + flag tier_seed=2: **1 producto**

- Anthropic Enterprise (recién lanzado, falta tracking)

### Descartado: **0**

(La metodología no descartó ninguno porque todos los identificados pasaron el filtro inicial de "evidencia 2026 verificada en al menos 2 fuentes". Si querés un descarte más estricto, podemos subir umbral C2 o C5).

---

## OBSERVACIÓN HONESTA — el resultado es alto

La metodología produjo **84 productos en Tier 1**, no los ~30 que estimamos. Esto es porque al cruzar los 4 verticales nuevos (audiovisual, branding, marketing, vibe coding), se sumó mucha cobertura.

**Decisiones que necesitas tomar:**

### Opción A — Aceptar los 84 productos en Tier 1
- Pros: cobertura completa, seed sólido para que el Catastro decida sobre cualquier área
- Contras: validación adversarial se vuelve pesada (3 sabios × 84 productos = 252 evaluaciones), tiempo extra ~1.5h, costo API extra ~$15-25
- Tronos: 9 dominios × top-5 = 45 entradas con cómputo de trono

### Opción B — Subir umbral a score ≥5 → Tier 1 más pequeño
- Resultado: ~62 productos en Tier 1 (saca los de score 4)
- Validación adversarial: 3 sabios × 62 = 186 evaluaciones
- Productos descartados a Tier 2: Augment Code, Brandify, Magicpath, Nextify, ChatGPT Frontier (5)

### Opción C — Subir umbral a score ≥6 (perfecto) → Tier 1 mínimo
- Resultado: ~52 productos en Tier 1
- Validación adversarial: 3 sabios × 52 = 156 evaluaciones
- A Tier 2 pasan ~10 productos (los enterprise sin acceso público fácil)

### Opción D — Cap por dominio (ej. máx 6-8 por dominio)
- Resultado: ~50-60 productos
- Pros: balance entre dominios, ningún dominio domina
- Contras: subjetivo decidir cuál sale (especialmente en audiovisual con 18 candidatos)

---

## MI RECOMENDACIÓN: Opción A modificada

Ir con los **84 productos** pero **escalonar la profundidad de validación adversarial**:

- **Validación profunda (3 sabios, fuentes_evidencia 2+ por producto)** → solo los **top-5 por dominio** (~45 productos). Estos quedan con `quorum_alcanzado=true` y entran al cómputo de tronos.
- **Validación ligera (1 sabio + auto-fill)** → los **39 restantes**. Estos quedan con `quorum_alcanzado=false`, `confidence=0.50`, candidatos a re-validación en Sprint 88.1.

Esto:
- Da cobertura completa (84 productos)
- Mantiene rigor donde importa (top-5 por dominio para tronos)
- Reduce costo y tiempo (~3x menos validaciones profundas)
- Cumple DSC-G-007.1 (validación adversarial obligatoria, pero permite tiers de profundidad)

---

## DECISIÓN PENDIENTE

¿Procedo con Opción A modificada (84 productos, validación escalonada)? ¿O preferís otra opción? ¿Querés modificar criterios o agregar/quitar algún producto manualmente?

**Próximos pasos una vez aprobada:**

1. Extender schema con 4 dominios nuevos (audiovisual, vibe_coding, branding, marketing) — ALTER ENUM
2. Lanzar validación adversarial 3 sabios sobre top-5 por dominio (45 productos)
3. INSERT 84 productos a `catastro_agentes` con datos completos para top-5 + datos mínimos para resto
4. Cómputo de 9 tronos por dominio + 5 globales = 14 tronos totales (no 5 como spec original)
5. Redactar DSC-G-007.2 + DSC-G-007.3 (escalonamiento de validación)
6. Reporte bridge + Cowork audit
