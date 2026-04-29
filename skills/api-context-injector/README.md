# api-context-injector v2.0 — Arsenal Expandido

**Registro centralizado, router inteligente e inyector de contexto universal** para todas las IAs, APIs, MCPs, herramientas nativas y skills del ecosistema de Alfredo.

## Cambio Fundamental en v2.0

Cada conector no es una herramienta plana — es una **puerta a un ecosistema completo**:

| Conector-Puerta | Ecosistema Accesible |
|----------------|---------------------|
| OpenRouter | 500+ modelos de IA |
| Apify | 23,000+ actors de scraping |
| Cloudflare | 15+ productos cloud |
| AWS | 200+ servicios |
| Zapier | 8,000+ apps |
| GitHub | Millones de repos + CI/CD |
| Google Workspace | Suite productividad completa |
| Supabase | BaaS con PostgreSQL + Vector |

**Alcance real: 82 recursos directos + acceso a ~31,700+ herramientas via conectores-puerta.**

## Arquitectura

Diseñado por el Consejo de 6 Sabios (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro, Grok 4.20, DeepSeek R1, Perplexity Sonar) el 2026-04-08. Rediseñado con enfoque de arsenal expandido tras segunda consulta.

```
api-context-injector/
├── SKILL.md                    # Cerebro — lógica, routing, reglas
├── README.md                   # Documentación para humanos
├── references/                 # Registros planos (82 recursos directos)
│   ├── llm-registry.yaml       # 7 LLMs con capacidades y conexión
│   ├── media-apis.yaml         # 8 APIs de generación media
│   ├── infra-apis.yaml         # 9 APIs de infraestructura
│   ├── data-apis.yaml          # 7 APIs de datos/monitoreo/scraping
│   ├── payment-apis.yaml       # APIs de pagos
│   ├── mcp-registry.yaml       # 27 conectores Manus
│   ├── native-tools.yaml       # 10 herramientas nativas
│   └── skills-registry.yaml    # 12+ skills existentes
├── arsenals/                   # NUEVO v2.0 — Sub-servicios por conector-puerta
│   ├── openrouter.yaml         # 500+ modelos, 15 top catalogados
│   ├── apify.yaml              # 23,000+ actors, 16 top catalogados
│   ├── cloudflare.yaml         # 15+ productos, 12 catalogados
│   ├── aws.yaml                # 200+ servicios, 15 top catalogados
│   ├── zapier.yaml             # 8,000+ apps, 25 top catalogadas
│   ├── github.yaml             # Repos + CI/CD, 6 capacidades
│   ├── google_workspace.yaml   # Suite productividad, 6 servicios
│   └── supabase.yaml           # BaaS completo, 6 servicios
├── routing/                    # NUEVO v2.0 — Lógica de decisión
│   ├── decision_router.yaml    # Tarea → herramienta específica
│   └── use_case_index.yaml     # Índice invertido: caso_uso → [herramientas]
├── scripts/
│   ├── scan_env.py             # Verifica env vars disponibles
│   ├── sync_notion.py          # Sincroniza desde Notion DB
│   ├── health_check.py         # Ping a todas las APIs
│   ├── inject_context.py       # Genera contexto por tipo de tarea
│   └── validate_registry.py    # Valida integridad de registros
└── templates/
    └── api_connection.py       # Plantilla de conexión universal
```

## Seguridad

- **NUNCA** se almacenan credenciales en archivos del skill
- Solo se referencian nombres de variables de entorno
- Credenciales adicionales se consultan dinámicamente desde Notion DB
- Script `validate_registry.py` detecta exposiciones accidentales

## Uso Rápido

```bash
# Verificar qué APIs están disponibles
python3.11 scripts/scan_env.py

# Obtener contexto para un tipo de tarea
python3.11 scripts/inject_context.py --task-type web_scraping

# Listar todos los tipos de tarea
python3.11 scripts/inject_context.py --list-types

# Validar integridad
python3.11 scripts/validate_registry.py
```

## Fuentes de Verdad

1. Variables de entorno del sandbox (más frescas, 13 APIs)
2. Semilla v7.3 en Notion (modelos verificados de los 6 Sabios)
3. Base de datos "API Keys y Credenciales" en Notion (25+ servicios)
4. Archivos YAML en `references/` y `arsenals/` (snapshot compilado)
5. Router de decisión en `routing/` (lógica de selección)
