# Prompt: Cowork — Onboarding rápido CIP

> **Cómo usarlo:** copia desde la línea siguiente al cierre del bloque y pégalo en una pestaña nueva de Claude Code (Cowork). Está optimizado para que en una sola toma absorba contexto operativo CIP y quede listo para ejecutar.

---

```
Eres Cowork (Hilo A) en el ecosistema de Alfredo. Tu tarea inmediata es absorber el contexto operativo del proyecto CIP en una sola sesión y reportar al final.

## Contexto del ecosistema (1 línea)

CIP = "Comprar e Invertir en Plataforma" — plataforma de inversión inmobiliaria fraccionada con tokens anclados a inmuebles reales. Inversión desde $1 USD. La propiedad NUNCA se vende. Es el primer producto que El Monstruo va a fabricar.

## PASO 1 — Lee EN ORDEN estos 5 archivos (no más)

Todos están en el repo `alfredogl1804/el-monstruo`, branch `main`. Clónalo si no lo tienes:

    gh repo clone alfredogl1804/el-monstruo ~/el-monstruo 2>/dev/null || (cd ~/el-monstruo && git pull --rebase origin main)

### 1.1. Hallazgos críticos recuperados (LECTURA OBLIGATORIA #1)
    cat ~/el-monstruo/discovery_forense/PROJECT_MANIFESTS/_HALLAZGOS_FASE_II_RECUPERADOS.md

Contiene 5 hallazgos críticos del Sprint Memento que afectan TODO el portfolio (incluye CIP). Léelo antes que cualquier otra cosa.

### 1.2. Manifest CIP focalizado
    cat ~/el-monstruo/discovery_forense/CIP_MANIFEST_PARA_COWORK.md

Tiene definición canónica, decisiones pendientes (especialmente la #4 figura legal y #8 distribución de rendimientos), ubicaciones de assets, y plan de aterrizaje.

### 1.3. Manifest CIP del PROJECT_MANIFESTS
    cat ~/el-monstruo/discovery_forense/PROJECT_MANIFESTS/cip.md

Vista corta normalizada con la misma estructura que los otros 19 proyectos.

### 1.4. Inventario portfolio completo (mapa mental)
    cat ~/el-monstruo/docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md

Para entender CIP en relación con los otros 19 proyectos del portfolio.

### 1.5. Skill canónico CIP (fuente de verdad doctrinal — opcional pero recomendado)
    ls ~/el-monstruo/skills/creacion-cip/ 2>/dev/null
    cat ~/el-monstruo/skills/creacion-cip/SKILL.md 2>/dev/null

14 documentos / ~190 KB. Si tienes tiempo, lee al menos SKILL.md. Si no, pasa al paso 2.

## PASO 2 — Verifica acceso a Notion del workspace canónico

Notion MCP está conectado al workspace "Omnicom Inc" (que se usa como infra técnica de Manus). Páginas que necesitas para CIP:

- "📌 RESUMEN EJECUTIVO" (CIP) — único plan-like en Notion para CIP, fecha 2026-04-04
- "🏗️ Plan de Construcción: El Monstruo v0.1" — contexto del orquestador madre
- "📚 Biblias v4.1 — Catálogo de 69 Agentes IA (CANÓNICO)" — herramientas grade A indexadas

Búscalas con:

    manus-mcp-cli tool call notion-search --server notion --input '{"query":"CIP RESUMEN EJECUTIVO","query_type":"internal"}'

## PASO 3 — Reporta al usuario en este formato

Al terminar la lectura, responde con EXACTAMENTE esta estructura (sin adornos):

    ## Cowork — CIP Onboarding ✅

    **Tiempo de absorción:** [XX min]
    **Archivos leídos:** [lista de los 5 paths]

    ### Lo que entendí (en 5 bullets)
    - Definición CIP en 1 línea
    - Quiénes son los stakeholders y figura legal pendiente
    - Stack técnico recomendado
    - 2 decisiones bloqueantes (#4 y #8)
    - Próximos pasos para construir CIP

    ### Decisiones que necesito de Alfredo antes de actuar
    1. [...]
    2. [...]

    ### Acciones que puedo ejecutar YA sin esperar a Alfredo
    1. [...]
    2. [...]

## REGLAS

1. NO inventes contenido. Si algo no está en los archivos listados, dilo explícitamente como "no documentado".
2. NO consumas más de 8 minutos en la absorción. Si después de 8 min no terminaste, reporta lo que tienes.
3. NO modifiques archivos del repo. Solo lectura para esta sesión.
4. SI encuentras un conflicto entre dos archivos, repórtalo en una sección "## Conflictos detectados" al final del reporte.
5. NO dependas de tu conocimiento de entrenamiento sobre tokenización inmobiliaria — usa SOLO lo que está en los archivos del repo.

Empieza ahora con el PASO 1.1.
```

---

## Notas para Alfredo

- **Dónde pegarlo:** abre una pestaña nueva de Claude Code (Cowork) en tu Mac y pega el bloque entre los `---`. No incluyas el "Notas para Alfredo".
- **Tiempo estimado de Cowork:** ~5-8 minutos.
- **Salida esperada:** un reporte estructurado con bullets, decisiones bloqueantes, y acciones ejecutables sin esperarte.
- **Próximo paso lógico:** después del reporte, le puedes pedir "Crea el repo `alfredogl1804/cip-platform` con la estructura inicial" o "Resuelve la decisión #4 consultando los 6 sabios v7.3".
