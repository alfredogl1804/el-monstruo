# El Monstruo

**Sistema de Inteligencia Artificial Soberana**

El Monstruo es un meta-orquestador de IAs con 19 capas que controla su propia lógica, memoria, políticas y gobernanza. Las herramientas externas son commodities intercambiables; el núcleo es soberano.

## Arquitectura

El sistema se organiza en 3 zonas:

| Zona | Principio | Componentes |
|------|-----------|-------------|
| **Núcleo Soberano** | Código propio, control total | Kernel, Router, Memoria, Conciencia |
| **Híbrida** | Open-source bajo nuestro control | Políticas, Skills, Consola, Observabilidad |
| **Commodity** | Intercambiable | LLMs, APIs, MCPs, Browser |

## Sprint 1 — Contratos Soberanos

Los 5 contratos que definen la soberanía del sistema:

| Contrato | Archivo | Responsabilidad |
|----------|---------|-----------------|
| KernelInterface | `contracts/kernel_interface.py` | Orquestación y flujo de ejecución |
| MemoryInterface | `contracts/memory_interface.py` | Memoria soberana con event sourcing |
| EventEnvelope | `contracts/event_envelope.py` | Formato canónico de eventos |
| PolicyHook | `contracts/policy_hook.py` | Gobernanza y guardrails |
| CheckpointStore | `contracts/checkpoint_model.py` | Persistencia de estado y replay |

## Stack Tecnológico

| Componente | Tecnología | Nota |
|-----------|------------|------|
| Kernel | State machine propia + FastAPI | Contrato soberano |
| Router | LiteLLM v1.83.7 (Docker only) | Supply chain risk mitigado |
| Memoria | Postgres + pgvector (Supabase) | Event sourcing propio |
| Bot | aiogram 3.17 | Async nativo |
| Observabilidad | OpenTelemetry + event store propio | Langfuse como espejo |
| Consola | Next.js 16 + shadcn v4 | PWA |

## Desarrollo

```bash
# Copiar variables de entorno
cp .env.example .env

# Levantar servicios
docker compose up -d

# Verificar salud
curl http://localhost:8000/health
curl http://localhost:4000/health
```

## Propiedad

Hive Business Center S.A. de C.V. — Alfredo Góngora
