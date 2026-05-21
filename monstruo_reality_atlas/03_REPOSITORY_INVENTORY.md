# 03 — REPOSITORY INVENTORY

**Inventario de repositorios accesibles del usuario `alfredogl1804`. Verificado vía `gh repo list` el 2026-05-17.**

---

## Repos core del Monstruo (relevantes para arquitectura)

El conjunto de repositorios que constituyen el núcleo operativo del Monstruo y sus extensiones críticas se compone de 15 entradas. El primer repositorio es `el-monstruo`, monorepo principal del proyecto que aloja la doctrina (APP_VISION, AGENTS.md, DSCs), el kernel completo (a2ui, agui_adapter, embriones, memento, sovereignty, brand, catastros, cronos), el bridge entre Manus y Cowork con sprints propuestos y resultados de audits, los apps (mobile, la-forja), el discovery forense con Capilla de Decisiones y manifests de proyectos, las migraciones SQL versionadas, los packages como design-tokens, los skills consumibles por agentes, y los scripts de gobierno como `_check_no_tokens.sh` y `_check_rls_default.py`. Es el repositorio de referencia para todo lo relacionado con el Monstruo.

El segundo repositorio core es `el-monstruo-command-center`, una aplicación Next.js que implementa el Command Center con 7 superficies en producción (chat, finops, fleet, memory, runs, security, settings). Está en producción viva pero presenta drift binario respecto a la canon de 12-15 superficies del Cockpit definidas en APP_VISION cap. 8. La separación en repo aparte de el-monstruo es deliberada para acelerar deploys de UI sin tocar el monorepo doctrinal.

El tercer repositorio es `el-monstruo-bot`, bot de Telegram MVP del Monstruo. Sirve como transport conversacional inicial mientras se construye el A2UI. Está deployed en Railway y tiene su propio skill `el-monstruo-bot` para context.

El cuarto es `like-kukulkan-tickets` (también referenciado como `ticketlike.mx`), plataforma de boletería para Leones de Yucatán. Es proyecto adyacente core de Alfredo, no del Monstruo, pero comparte infraestructura (TiDB, Stripe, Railway). Tiene skill propia `ticketlike-ops`.

El quinto es `crisol-7`, otro proyecto adyacente de Alfredo enfocado en investigación política masiva. Comparte la metodología de los 6 Sabios y enjambres iterativos. Tiene su propia base documental en Notion y Drive según su skill.

El sexto es `proyecto-renders`, pipeline de inteligencia inmobiliaria para análisis de terrenos y generación de renders 8x con IA top mundial. Skill propia `proyecto-renders`.

El séptimo es `softrestaurant-ai-10x`, software 10x superior a SoftRestaurant para gestión de restaurantes. Proyecto de Alfredo adyacente, skill propia.

El octavo es `videoclip-musical-clase-mundial`, pipeline de producción de videoclips frame-por-frame con IA de clase mundial. Skill propia.

El noveno es `tiktok-trend-creator`, herramienta de creación viral de tendencias en TikTok. Skill propia.

El décimo es `cip-tokenizacion-inmobiliaria`, plataforma de inversión inmobiliaria fraccionada con tokens. Skill propia `creacion-cip`.

El undécimo es `simulador-escenarios-ia`, simulador universal de escenarios para wargaming, stress-testing y análisis "qué pasaría si". Motor en Railway, skill propia.

El duodécimo es `media-crisis-control`, sistema LATAM-POLICRIS v1 de control de crisis en medios para políticos. Skill propia.

El decimotercero es `aliexpress-mx-validator`, validador de seguridad multi-capa para compras AliExpress envío a México. Skill propia.

El decimocuarto es `comercializacion-zona-like-313`, blueprint de comercialización IA-first para Zona Like (313 butacas premium Leones de Yucatán). Skill propia.

El decimoquinto es `ciclo-investigacion-descubrimiento-perpetuo`, sistema orquestado por GPT-5.4 para investigar software existente, descubrir mejoras y diseñar versiones 10x superiores con los 6 Sabios. Skill propia.

## Artefactos del Pipeline E2E (excluidos del inventario relevante)

Existen además aproximadamente **73 repositorios `monstruo-tbd-*`** generados automáticamente por el pipeline E2E (run e2e_*) durante pruebas de generación de proyectos. Estos repos son artefactos efímeros, no contienen doctrina ni código relevante, y deben ser tratados como ruido en cualquier análisis. Adicionalmente hay aproximadamente **12 landing-page artefactos** del mismo pipeline. Total de artefactos: ~85 repos que se ignoran sistemáticamente.

## Política de relevancia para análisis

Cuando un agente busque conceptos en repos de Alfredo, debe restringir el scope a los **15 repos core** listados arriba. Los artefactos del Pipeline E2E se excluyen explícitamente vía glob `!monstruo-tbd-*`.

## Tabla resumen

| Repo | Tipo | Estado | Skill asociado |
|---|---|---|---|
| el-monstruo | Monorepo core | ACTIVO | el-monstruo, el-monstruo-core, el-monstruo-estado, el-monstruo-plan, el-monstruo-toolkit, el-monstruo-armero |
| el-monstruo-command-center | App Next.js prod | PRODUCCION_VIVA | (sin skill) |
| el-monstruo-bot | Bot Telegram | PRODUCCION_VIVA | el-monstruo-bot |
| like-kukulkan-tickets | Adyacente Leones | ACTIVO | ticketlike-ops |
| crisol-7 | Adyacente política | ACTIVO | (no en lista de skills) |
| proyecto-renders | Adyacente inmobiliario | ACTIVO | proyecto-renders |
| softrestaurant-ai-10x | Adyacente restaurantero | ACTIVO | softrestaurant-ai-10x |
| videoclip-musical-clase-mundial | Adyacente video | ACTIVO | videoclip-musical-clase-mundial |
| tiktok-trend-creator | Adyacente TikTok | ACTIVO | tiktok-trend-creator |
| cip-tokenizacion-inmobiliaria | Adyacente fintech | ACTIVO | creacion-cip |
| simulador-escenarios-ia | Adyacente IA | ACTIVO | simulador-escenarios-ia |
| media-crisis-control | Adyacente media | ACTIVO | media-crisis-control |
| aliexpress-mx-validator | Adyacente comercio | ACTIVO | aliexpress-mx-validator |
| comercializacion-zona-like-313 | Adyacente Leones | ACTIVO | comercializacion-zona-like-313 |
| ciclo-investigacion-descubrimiento-perpetuo | Adyacente meta-IA | ACTIVO | ciclo-investigacion-descubrimiento-perpetuo |
| monstruo-tbd-* (73x) | Artefacto Pipeline E2E | EFIMERO | — (ignorar) |

---

*Procedé con `04_PRODUCTION_INVENTORY.md`.*
