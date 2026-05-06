# 📍 CIP — Manifest Unificado de Ubicaciones (para Cowork)

> **Fecha:** 2026-05-06 · **Compilado por:** Manus  
> **Para:** Cowork (Claude Desktop)  
> **Propósito:** Ubicaciones reales y verificadas de TODO lo referente al proyecto CIP en el ecosistema de Alfredo, con instrucciones de cómo acceder a cada fuente.

---

## 1. Definición canónica de CIP

**CIP** = *Plataforma de Inversión Inmobiliaria Fraccionada con tokens anclados a bienes raíces reales*. Democratiza inversión en inmuebles desde **$1 USD**. La propiedad nunca se vende, es ancla permanente del token. Fusiona **crowdfunding inmobiliario + crowdfunding social + marketing de impacto**.

**Reglas inquebrantables:** (1) la propiedad NUNCA se vende, (2) autorregulación orgánica, (3) gobierno como aliado (5% de tokens institucionales), (4) verificación en tiempo real de toda decisión.

**Estructura tokens por inmueble:** 25% gobernanza + 70% inversión + 5% institucional (gobierno local).

**Mercado inicial:** Sureste de México. Plan B legal: Argentina/Chile.

**Stack recomendado pendiente:** Polygon + ERC-3643 (token regulado).

**Relación con El Monstruo:** CIP es el **primer producto que El Monstruo va a fabricar**. Monstruo = constructor; CIP = creación.

---

## 2. Fuente PRIMARIA — Skill canónico

📂 **`/home/ubuntu/skills/creacion-cip/`** (también en repo: `skills/creacion-cip/`)

| Archivo | Tamaño | Contenido |
|---|---|---|
| `SKILL.md` | 5.4 KB | Reglas, modelo de negocio, 7 principios, decisiones pendientes |
| `references/manifiesto-fundacional-cip.md` | 7.0 KB | **LEER PRIMERO** — Manifiesto fundacional |
| `references/vision-completa.md` | 5.9 KB | Visión completa + tabla decisiones pendientes |
| `references/stack-y-arquitectura.md` | 4.4 KB | Decisiones técnicas (Polygon, ERC-3643) |
| `references/analisis-mercado-regulacion.md` | 6.9 KB | Análisis legal/regulatorio |
| `references/sweetspot-final-codigo-abierto.md` | 20 KB | **BLUEPRINT EJECUTABLE del sweet spot** |
| `references/sintesis-ronda2-codigo-abierto.md` | 28 KB | CIP como código abierto (implicaciones) |
| `references/sintesis-5angulos-gpt54.md` | 29 KB | Síntesis 5 ángulos por GPT-5.4 |
| `references/proyeccion-20-anos-gpt54.md` | 33 KB | Proyección a 20 años |
| `references/angulo-1-plataforma.md` | 8.9 KB | Visión expandida plataforma |
| `references/angulo-arte-diseno-ia.md` | 8.2 KB | Arte, diseño e IA |
| `references/angulo-infraestructura-escala.md` | 11 KB | Infraestructura y escalamiento |
| `references/angulo-infraestructura-fierros.md` | 8.6 KB | Hardware por nivel |
| `references/escenario-civilizatorio.md` | 4.8 KB | Escenario civilizatorio |

**Total:** 14 documentos, ~190 KB de contexto curado y canónico.

**Cómo accederlos desde Cowork:**
```bash
cd ~/el-monstruo/skills/creacion-cip
cat SKILL.md  # punto de entrada
cat references/manifiesto-fundacional-cip.md  # leer primero
cat references/sweetspot-final-codigo-abierto.md  # blueprint ejecutable
```

---

## 3. Notion — Páginas relacionadas

| Título | URL/ID Notion | Relevancia |
|---|---|---|
| `inverfrac.com` | `33814c6f8bba81afb60fe4a73276ba21` | 🔴 **CRÍTICA** — análisis de dominio candidato para CIP |
| `assetfraction.io` | (en workspace, query "asset fraction") | 🟡 Dominio alternativo evaluado |
| `fractrealty.ai` | (en workspace, query "fractrealty") | 🟡 Dominio alternativo evaluado |
| `yucatanconnect.com` | `33814c6f8bba81e5a219db2eca1c65dc` | 🟡 Posible relación con mercado Sureste |

**Búsqueda Notion para Cowork:**
```bash
# Vía Notion MCP
manus-mcp-cli tool call notion-search --server notion --input '{"query":"CIP inverfrac plataforma inversion fraccionada","query_type":"internal"}'
```

⚠️ **Nota:** Búsquedas exhaustivas en Notion (5 queries) NO encontraron una página titulada "CIP" o "Manifiesto CIP" como tal. La doctrina canónica vive en el **skill local**, no en Notion. Cowork debería **crear una página índice maestro de CIP en Notion** importando el contenido del skill.

---

## 4. Google Drive — Archivos

| Archivo | ID Drive | Modificado | Tipo | Relevancia |
|---|---|---|---|---|
| `VEREDICTO_ESTRATEGICO_CIP_HERMES.md` | (búsqueda Drive) | 2026-04-22 | MD | 🔴 **CRÍTICA** — único archivo Drive con "CIP" en nombre |
| `TRANSCRIPCION_COMPLETA_HILO.md` | (búsqueda Drive) | 2026-04-12 | MD | 🟡 Menciona CIP en contenido |
| `MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md` | (búsqueda Drive) | 2026-04-06 | MD | 🟡 Menciona CIP+CÍES en SOP |
| `repaldo sop v3 181025.txt` | (búsqueda Drive) | 2025-10-19 | TXT | 🟡 Definición histórica CIP+CÍES |
| `roadmap_v2_raw.json` | (mencionado en INVENTARIO_PROYECTOS_MAGNA) | 2026-04-25 | JSON | 🟡 Roadmap raw |
| `roadmap_mundial_raw.json` | (mencionado en INVENTARIO_PROYECTOS_MAGNA) | 2026-04-25 | JSON | 🟡 Roadmap mundial raw |

**Búsqueda Drive para Cowork:**
```bash
gws drive files list --params '{"q":"name contains \"CIP\" or fullText contains \"inverfrac\"","pageSize":50,"fields":"files(id,name,modifiedTime,webViewLink)","corpora":"allDrives","includeItemsFromAllDrives":true,"supportsAllDrives":true}'
```

---

## 5. Dropbox — Menciones contextuales

⚠️ **No hay archivos dedicados a CIP en Dropbox.** Solo aparecen menciones de "CIP+CÍES" como concepto estratégico dentro de respaldos del SOP:

- `Respaldo_SOP__13_de_sep_25.md` (~líneas 5, 85, 118, 170, 198, 211) — Definición CIP+CÍES como proyecto estratégico
- `Ok___Aquí_tienes_el_Listado_Consolidado_de_Reglas_SOP_activas.md` (línea 15)

Ya están normalizados y presentes en: `discovery_forense/raw_text/dropbox/normalized_md/`

---

## 6. S3 — Buckets

⚠️ **Sin matches.** Escaneo exhaustivo de los 8 buckets (204 objetos) → 0 archivos sobre CIP.

---

## 7. GitHub — Repos

⚠️ **No existe un repositorio dedicado a CIP** en `alfredogl1804/*`. Inventario:
- 34 repos totales
- Ningún repo con "cip", "inverfrac", "token", "real-estate", "inmob" o "fraccion" en nombre/descripción
- **Acción sugerida:** Cowork debe **crear `alfredogl1804/cip-platform`** (privado) cuando se inicie la construcción

---

## 8. Discovery Forense (repo local) — Referencias

| Archivo | Mención CIP |
|---|---|
| `docs/INVENTARIO_PROYECTOS_MAGNA_2026.md` | Línea 10, 27, 142 — CIP como "Proyecto en Transición" con documentación fragmentada (48 archivos Drive / 5 Notion top), sin repos activos. Estado: 🟡 Fragmentado. |
| `discovery_forense/REPORTE_FORENSE_MAGNA.md` | Mención de CIP+CÍES |
| `discovery_forense/raw_text/manifest_unified.json` | Manifest del dataset Sprint Memento (232 archivos) |

---

## 9. Decisiones pendientes (8) — Estado actual

| # | Decisión | Estado actual |
|---|---|---|
| 1 | Inversión mínima | Inclinación a $1 USD (enganche emocional) |
| 2 | Blockchain vs tradicional | **Recomendación:** Polygon + ERC-3643 |
| 3 | Jurisdicción legal | Sureste MX, plan B: Argentina/Chile |
| 4 | Figura legal | Fideicomiso irrevocable (pendiente confirmar) |
| 5 | Tokens institucionales (5%) | Concepto aprobado, implementación pendiente |
| 6 | Mercado secundario | Implícito (intercambio entre personas) |
| 7 | Gobernanza del 25% | Tenedores deciden destino |
| 8 | Distribución de rendimientos | **PENDIENTE** |

---

## 10. Sugerencias para Cowork (acciones propuestas)

### A. Crear página índice maestro en Notion
- **Título:** `📜 CIP — Índice Maestro Canónico v1.0`
- **Contenido:** Importar SKILL.md del skill `creacion-cip`
- **Subpáginas:** Una por cada archivo de `references/` (14 subpáginas)
- **Tag:** `#proyecto:CIP` `#estado:diseño-fase`

### B. Crear repo GitHub
- `gh repo create alfredogl1804/cip-platform --private --description "Plataforma de Inversión Inmobiliaria Fraccionada (CIP) — tokens anclados a bienes raíces"`
- Estructura inicial: `/contracts/` (Solidity ERC-3643), `/api/`, `/web/`, `/legal/`, `/docs/` (importar skill references)

### C. Resolver decisión #4 (figura legal) y #8 (rendimientos)
- Consultar a sabios (semilla v7.3) con focus específico en fideicomiso vs SAPI vs SOFOM
- Validar regulación CNBV / SHCP / Banxico para tokens anclados a inmuebles en México 2026

### D. Indexar el corpus CIP en Supabase pgvector
- Junto con Tarea 3 del Sprint Memento (que ya quedó desbloqueada)
- Tag los chunks con `project:CIP`
- Permite búsqueda semántica cruzada con SOP/EPIA/MAOC

---

## 11. Resumen ejecutivo para Cowork

**Estado documental de CIP:**
- ✅ **Doctrina canónica completa** en skill local (`skills/creacion-cip/`, 14 docs, ~190 KB)
- 🟡 **Documentación fragmentada** en Drive (6 archivos relevantes, sin estructura)
- 🟡 **Notion sin página índice** (existen análisis de dominios candidatos: inverfrac.com, assetfraction.io, fractrealty.ai)
- ❌ **Sin repositorio GitHub** activo
- ❌ **Sin código** (smart contracts, backend, frontend) — fase 100% diseño/legal

**Acción inmediata recomendada:** Cowork ejecuta acciones A + B (crear índice maestro Notion + crear repo GitHub) para que CIP deje de ser "Proyecto en Transición" y pase a "Proyecto en Construcción".

---

**Archivo generado por Manus el 2026-05-06.**  
**Verificación:** Todas las ubicaciones fueron escaneadas con código (boto3 S3, gws Drive, Notion MCP, Dropbox SDK, gh CLI, grep recursivo).  
**Sin alucinaciones — solo lo que existe.**
