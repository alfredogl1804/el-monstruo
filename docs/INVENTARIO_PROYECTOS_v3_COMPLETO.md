# 📂 INVENTARIO MAESTRO DE PROYECTOS — v3 COMPLETO

**Fecha:** 2026-05-06
**Autor:** Manus (Hilo B)
**Origen:** Extiende `docs/INVENTARIO_PROYECTOS_MAGNA_2026.md` (v2 del 2026-05-05) con los 7+ proyectos operativos detectados que no estaban en el SOP histórico.
**Propósito:** Servir como **mapa único del portfolio completo** para Cowork (y cualquier otro agente / persona) que necesite contexto de TODOS los proyectos de Alfredo.

---

## 1. Cómo usar este documento

0. **🔥 LECTURA OBLIGATORIA PRIMERO** — `discovery_forense/PROJECT_MANIFESTS/_HALLAZGOS_FASE_II_RECUPERADOS.md`: hallazgos críticos de la Fase II Discovery Forense (5 mayo 2026) recuperados de screenshots tras compactación de contexto. Sobreescriben suposiciones previas sobre BioGuard, Top Control PC, Vivir Sano, Marketplace Muebles y la asimetría SOP/EPIA Drive vs Dropbox.
1. **Reporte forense Fase II** — `discovery_forense/REPORTE_FORENSE_MAGNA.md`: contexto del proceso completo (1,562 documentos analizados, 30 abiertos semánticamente).
2. **Tabla maestra** (sección 2 de este doc): visión rápida de los 20 proyectos clasificados por estado
3. **Manifests individuales** (`discovery_forense/PROJECT_MANIFESTS/{slug}.md`): un archivo por proyecto con definición, ubicaciones, decisiones pendientes y próximos pasos
4. **Skills canónicos** (`~/.../skills/{slug}/SKILL.md`): fuente de verdad doctrinal cuando exista skill
5. **Repos GitHub**: código + planes técnicos cuando el proyecto tenga repo activo

> **Para Cowork:** Lee primero `_HALLAZGOS_FASE_II_RECUPERADOS.md`, luego este archivo, luego entra al manifest del proyecto que te interese. No necesitas leer los 20 — solo el que el contexto requiere.

---

## 2. Tabla maestra del portfolio (20 proyectos)

### 🟢 ACTIVOS / EN PRODUCCIÓN (7)

| # | Proyecto | Skill | Repo GitHub | Stack/Estado |
|---|---|---|---|---|
| 1 | **Mena Baduy / Crisol-8** | `el-monstruo` (referencia) | `crisol-8` (PRIVATE) | Operación electoral OSINT activa |
| 2 | **LikeTickets / ticketlike.mx** | `ticketlike-ops` | `like-kukulkan-tickets` (PRIVATE) | Boletería Leones Yucatán — TiDB+Stripe+Railway |
| 3 | **Comercialización Zona Like 313** | `comercializacion-zona-like-313` | — | 313 butacas premium, narrativa Leoncio |
| 4 | **El Monstruo Bot (Telegram)** | `el-monstruo-bot` | `el-monstruo-bot` (PRIVATE) | Deployed en Railway, MVP activo |
| 5 | **El Monstruo Command Center** | — | `el-monstruo-command-center` (PRIVATE) | Dashboard interno del ecosistema |
| 6 | **Observatorio Mérida 2027** | `manus-memory-merida2027` | `observatorio-merida-2027` (PRIVATE) | Modelo bayesiano electoral |
| 7 | **Simulador Universal** | `simulador-escenarios-ia` | `simulador-universal` (PRIVATE) | Motor en Railway, ABM + Monte Carlo |

### 🟡 EN CONSTRUCCIÓN (4)

| # | Proyecto | Skill | Repo GitHub | Sprint actual |
|---|---|---|---|---|
| 8 | **El Monstruo (orquestador madre)** | `el-monstruo`, `el-monstruo-core`, `el-monstruo-plan`, `el-monstruo-toolkit`, `el-monstruo-armero`, `el-monstruo-estado` | `el-monstruo` (PUBLIC) | Sprint 87 — Discovery Fase III + Memento |
| 9 | **Kukulkán 365 (k365)** | — | `k365-knowledge-repo` (PRIVATE) | Distrito Entretenimiento Climatizado — repo de conocimiento |
| 10 | **El Mundo de Tata** | — | `el-mundo-de-tata` (PRIVATE) | Juego interactivo padre-hija estilo Toca Boca |
| 11 | **Roche Bobois / Alfombras Yaxché** | — | `rug-carousel` (PRIVATE) | Catálogo Las Vegas + crisis Clara Rosales |

### 🟠 EN DISEÑO (5)

| # | Proyecto | Skill | Repo GitHub | Estado |
|---|---|---|---|---|
| 12 | **CIP — Inversión Inmobiliaria Fraccionada** | `creacion-cip` | — (pendiente crear `cip-platform`) | Diseño completo — 8 decisiones, 2 bloqueantes |
| 13 | **SoftRestaurantAI 10x** | `softrestaurant-ai-10x` | — | Visión + radar herramientas + arquitectura 5 componentes |
| 14 | **Marketplace Muebles** | — | — | Documentación fragmentada Drive+Notion |
| 15 | **Top Control PC** *(alias CONTROL TOTAL)* | — | — | 8 planes en Drive, 2 en Notion, sin repo |
| 16 | **Vivir Sano** | — | — | 3 planes Drive, 6 planes Notion, sin repo |

### 🔵 NOMINALES (sólo en SOP, sin construcción) (4)

| # | Proyecto | Skill | Repo GitHub | Evidencia |
|---|---|---|---|---|
| 17 | **CIES** | — | — | 1 plan Drive, 1 plan Notion, sin código |
| 18 | **NIAS** | — | — | 1 plan Drive, sin Notion plans, sin código |
| 19 | **BIOGUARD** | — | — | 1 plan Drive, sin Notion plans, sin código |
| 20 | **OMNICOM** | — | — | 1 plan Drive, 1 plan Notion (📌 RESUMEN EJECUTIVO), sin código |

---

## 3. Subproyectos / componentes asociados

| Subproyecto | Asociado a | Notas |
|---|---|---|
| CrediVive | nominal SOP | 1 plan Drive |
| Interiorismo Estratégico | Marketplace Muebles | 1 plan Drive, 1 Notion (SketchUp + IA) |
| Crisis Clara Rosales | Roche Bobois | bucket S3 `alfombras-comparacion/crisis-yaxche-v2` |
| Honcho Railway | El Monstruo (infra) | repo `honcho-railway` (PRIVATE) |
| Observatorio Mérida — memoria | Observatorio Mérida 2027 | repo `manus-memory-merida2027` |

---

## 4. Capacidades transversales (skills no atadas a un proyecto)

Estos skills son herramientas/protocolos que aplican a múltiples proyectos:

| Skill | Función |
|---|---|
| `protocolo-operativo-core` | Protocolo CORE: validación tiempo real + 6 sabios + anti-autoboicot |
| `validacion-tiempo-real` | Mandato de validación contra realidad actual |
| `anti-autoboicot` | Verificación de versiones/modelos/SDKs antes de escribir código |
| `consulta-sabios` | Infraestructura para consultar a los 6 sabios (semilla v7.3) |
| `herramientas-planificacion` | 6 herramientas para planificar producción audiovisual |
| `media-crisis-control` | Control de crisis mediática (LATAM-POLICRIS v1) |
| `proyecto-renders` | Pipeline de renders fotorrealistas inmobiliarios |
| `site-reality-reconstructor` | Reconstrucción de sitios reales para renders |
| `tiktok-trend-creator` | Conceptos virales TikTok de música → seed videos |
| `music-prompter` | Framework de prompts para generación de música |
| `aliexpress-mx-validator` | Validación de seguridad compras AliExpress México |
| `manus-refund-auditor` | Auditoría de hilos para refund de créditos Manus |
| `optimizador-creditos` | Reglas para reducir consumo de créditos 50-70% |
| `manus-api` | Gestión de tasks/projects vía Manus API v2 |
| `manus-inter-cuenta` | Comunicación entre múltiples cuentas Manus |
| `gws-best-practices` | Mejores prácticas Google Workspace CLI |
| `persistent-computing` | Decidir entre sandbox vs WebDev vs VM persistente |
| `skill-creator` | Crear/actualizar skills |
| `skill-factory` | Pipeline industrial para crear skills complejas |
| `api-context-injector` | Registro/router central de IAs/APIs/MCPs |
| `ciclo-investigacion-descubrimiento-perpetuo` | Ciclo perpetuo de investigación-descubrimiento |

---

## 5. Estado consolidado

| Categoría | Count | Tienen Skill | Tienen Repo | Producción |
|---|---|---|---|---|
| 🟢 Activos | 7 | 6/7 | 7/7 | ✅ |
| 🟡 En Construcción | 4 | 6/4 (overlap) | 4/4 | parcial |
| 🟠 En Diseño | 5 | 2/5 | 0/5 | — |
| 🔵 Nominales | 4 | 0/4 | 0/4 | — |
| **TOTAL** | **20** | **14/20 (70%)** | **11/20 (55%)** | **7/20 (35%)** |

---

## 6. Notas de mantenimiento

- **Cuándo actualizar este documento:** cuando se cree/cierre un proyecto, cuando un proyecto cambie de estado, cuando se cree un nuevo skill o repo
- **Quién:** Cualquier hilo (Manus o Cowork) puede actualizar; el último commit gana
- **Manifests individuales:** se generan vía `map` paralelo; cada uno sigue plantilla fija para consistencia
- **Convención de nombres:** slug en kebab-case alineado con skill o repo cuando exista

---

## 7. Próximos pasos sugeridos para Cowork

1. **Leer este documento** para tener el mapa completo
2. **Crear página índice en Notion** llamada `🗂️ Portfolio Maestro Alfredo 2026` que liste los 20 proyectos con cross-link a cada manifest
3. **Para cada proyecto en estado 🟠 En Diseño**, evaluar si pasa a Sprint de construcción o se descarta
4. **Para los 🔵 Nominales**, decidir si:
   - (A) Se promueven a 🟠 En Diseño (necesitan plan)
   - (B) Se mantienen como ideas en backlog
   - (C) Se descartan (eliminar del SOP)
