# 04 — PRODUCTION INVENTORY

**Inventario de aplicaciones y servicios del Monstruo y su entorno desplegados en producción al 2026-05-17.**

---

## Producción del Monstruo

La superficie de producción que efectivamente sirve usuarios del Monstruo se compone de tres componentes operativos. El primero es el **Command Center** (`el-monstruo-command-center`) desplegado en Vercel como aplicación Next.js. Expone 7 superficies funcionales (chat, finops, fleet, memory, runs, security, settings) bajo `/protected/*`. Es el punto de entrada principal para el operador humano del Monstruo. Tiene autenticación implementada, conecta con la API del kernel y consume datos en vivo. Contradice la doctrina de 12-15 superficies del Cockpit definida en APP_VISION cap. 8, lo cual constituye drift documentado.

El segundo es el **Bot de Telegram** (`el-monstruo-bot`) desplegado en Railway. Es transport conversacional de baja latencia. Permite invocar capabilities del kernel desde Telegram: comandos, queries, ejecución de scripts agénticos. Estado: MVP en operación, evolución roadmap definida en skill `el-monstruo-bot`.

El tercero es la **API del kernel** (parte del monorepo `el-monstruo`) desplegada también en Railway. Contiene endpoints de A2UI, Memento, Sovereignty, Embriones, AG-UI Gateway. Es el cerebro detrás del Command Center y del Bot.

## Producción de proyectos adyacentes (no del Monstruo, pero del ecosistema Alfredo)

Existen además seis aplicaciones de proyectos adyacentes que comparten infraestructura con el Monstruo pero no son parte de él. La primera es **ticketlike.mx** (boletería Leones de Yucatán), desplegada con base de datos TiDB, integración Stripe Checkout y deploy en Railway. Tiene admin panel funcional y schema de eventos con butacas VIP. La segunda es la app de **Crisol-7**, plataforma de investigación política masiva, con frontend web y backend de orquestación de los 6 Sabios. La tercera es el **simulador de escenarios IA** desplegado en Railway con motor externo, accesible vía API para correr simulaciones de alta fidelidad. La cuarta es el dashboard del **softrestaurant-ai-10x**. La quinta es el pipeline frontend de **proyecto-renders**. La sexta es el frontend de **CIP** (tokenización inmobiliaria).

## Infraestructura compartida (cross-project)

La infraestructura que sostiene tanto el Monstruo como los proyectos adyacentes incluye una base de datos **Supabase** con políticas RLS universales (AGENTS.md Regla 7) y una base **TiDB** para proyectos de alto volumen como ticketlike. El storage compartido es **AWS S3** y **Dropbox** para artefactos heavy. La capa de observabilidad usa **Langfuse** para LLM traces. El gateway de LLMs usa el `OPENROUTER_API_KEY` y los específicos por modelo (Anthropic, OpenAI, Gemini, Grok, Perplexity, ElevenLabs, HeyGen, Cloudflare). Las migraciones SQL están versionadas en `migrations/sql/` del monorepo `el-monstruo` con linter pre-commit `_check_rls_default.py`.

## Dominios y endpoints conocidos

| Dominio/Endpoint | Servicio | Estado |
|---|---|---|
| Command Center (Vercel) | UI principal del Monstruo | PRODUCCION_VIVA |
| Bot Telegram | Transport conversacional | PRODUCCION_VIVA |
| API kernel (Railway) | Backend del kernel | PRODUCCION_VIVA |
| ticketlike.mx | Boletería Leones | PRODUCCION_VIVA |
| Simulador IA (Railway) | Engine simulación | PRODUCCION_VIVA |
| CIP frontend | Tokenización inmobiliaria | PRODUCCION_VIVA |
| Mobile App (Flutter) | App nativa Monstruo | NO_DEPLOYED (drift binario en código) |
| La Forja (web) | Backend Hono + frontend Next.js | EN_DESARROLLO sprint la-forja-001-d4 |

## Brechas de producción respecto a doctrina

La doctrina del Monstruo define múltiples superficies, transports y capabilities que aún no llegaron a producción. La **app móvil Flutter** existe en código (`apps/mobile/`) pero tiene drift binario en brand DNA (cyan/púrpura vs forja/graphite/acero) y aún no está deployed. Los **transports** definidos en APP_VISION (transport conversacional, transport visual, transport agéntico, transport voz) están parcialmente implementados: solo el conversacional (Telegram + chat web) tiene producción. **A2UI Protocol** tiene spec firmada (SRC-004) y código incipiente en `kernel/a2ui/` pero no está conectado a una superficie real en producción. **Cronos** y **Modo Cripta** están canonizados en doctrina pero 0% en código y 0% en producción. **Las 8 capabilities transversales** están en 0% según audit Cowork 2026-05-11.

---

*Procedé con `05_CANON_REGISTRY.md`.*
