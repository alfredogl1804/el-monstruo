---
name: usar-biblia-template
description: Genera la "biblia magna" canónica del Monstruo para cualquier proyecto nuevo (CIP, Marketplace Interiorismo, Vivir Sano, futuras empresas-hijas). Toma docs/templates/biblia-master-plan-template.md y lo rellena con los datos del proyecto en 12 capas (L0–L12) más Brand DNA + 7 capas transversales. Usar al iniciar cualquier proyecto-hijo del Monstruo.
---

# usar-biblia-template — Cómo generar la biblia magna de un proyecto

> Toda iniciativa del Monstruo (proyecto-hijo, empresa-hija, módulo magna) tiene **una biblia**. Esta biblia es source of truth de identidad + arquitectura + roadmap + operación + capa de aprendizaje. Sin biblia, el proyecto no existe formalmente.

---

## Cuándo usar este skill

**SÍ usar:**
- Iniciar proyecto-hijo nuevo (CIP frontend, Marketplace Interiorismo, etc.)
- Iniciar empresa-hija nueva
- Iniciar módulo magna del kernel (ej: Embrión Creativo, Simulador Causal)
- Refactor mayor de un proyecto existente sin biblia (deuda)

**NO usar:**
- Sprint individual sin proyecto detrás (eso es spec en `bridge/sprints_propuestos/`)
- DSC firmado (eso va a `discovery_forense/CAPILLA_DECISIONES/`)
- Documentación de API de un endpoint específico (eso es `docs/api/...`)

---

## Las 12 capas de la biblia (estructura inviolable)

| Capa | Qué contiene |
|---|---|
| **L0 — Identidad** | Una frase. Si no se puede, no estás listo. |
| **L1 — Contexto y propósito** | Por qué existe. Qué pasaría si no existiera. Encaje en arquitectura del Monstruo. |
| **L2 — Brand DNA** | Tokens visuales canónicos + tono + naming convention |
| **L3 — Arquitectura técnica** | Stack + DSCs locales + dependencias críticas |
| **L4 — 7 Capas Transversales** | Estado de cada capa (Obj #9) |
| **L5 — Roadmap de sprints** | Sprint 0 + N + backlog |
| **L6 — Métricas** | KPIs técnicos + de negocio + Critic Score |
| **L7 — Operación** | URLs vivas + secrets + comandos op |
| **L8 — Capa de aprendizaje** | Errores cometidos + decisiones que cambiaríamos + anti-patrones |
| **L9 — Vínculos** | Dependencias bidireccionales + catastros que alimenta/consume |
| **L10 — Hand-off** | Onboarding + plan de archivado |
| **L11 — Glosario** | Términos del proyecto |
| **L12 — Instrucciones operacionales** | Para el agente que ejecuta. Sin literatura. |

---

## Protocolo de uso (6 pasos)

### Paso 1 — Crear directorio del proyecto

```bash
mkdir -p docs/biblias_proyectos/{{PROYECTO}}
```

Ejemplo: `docs/biblias_proyectos/cip/`, `docs/biblias_proyectos/marketplace_interiorismo/`.

### Paso 2 — Copiar template

```bash
cp docs/templates/biblia-master-plan-template.md docs/biblias_proyectos/{{PROYECTO}}/BIBLIA_MAGNA.md
```

### Paso 3 — Rellenar variables canónicas

Buscar y reemplazar (todas case-sensitive):

| Variable | Reemplazar por |
|---|---|
| `{{NOMBRE_PROYECTO}}` | Nombre canónico (ej: "CIP", "Marketplace Interiorismo Sureste MX") |
| `{{OWNER}}` | Quién es responsable (ej: "Hilo Ejecutor", "Alfredo + Cowork") |
| `{{YYYY-MM-DD}}` | Fecha de creación de la biblia |
| `{{SPRINT_ID}}` | Sprint que generó esta biblia (ej: "Sprint Catastro-B") |
| `{{DRAFT \| EN_REVISION \| FIRMADA \| ARCHIVADA}}` | Estado actual |
| `{{C0 / C1 / C2 / C3 / C4}}` | Capa arquitectónica del Monstruo |
| `{{PROYECTO}}` | Slug del proyecto (snake_case, ej: `cip`, `marketplace_interiorismo`) |
| `{{DSC-X, DSC-G, DSC-MO, ...}}` | DSCs aplicables |

### Paso 4 — Rellenar contenido capa por capa

**Orden recomendado:**
1. L0 (identidad — si esto no se puede en una frase, parar y volver al diseño)
2. L1 (contexto — por qué existe)
3. L9 (vínculos — entender dependencias antes de stack)
4. L3 (stack — ahora con dependencias claras)
5. L2 (Brand DNA — usar `@monstruo/design-tokens`)
6. L7 (operación — endpoints + secrets)
7. L5 (roadmap)
8. L4 (7 capas transversales)
9. L6 (métricas)
10. L11 (glosario — al final, capturar términos que aparecieron)
11. L12 (instrucciones operacionales — síntesis para agentes)
12. L8 (vacío inicialmente, se llena conforme hay aprendizajes)
13. L10 (hand-off — al final, cuando ya tenés todo lo demás)

### Paso 5 — Validación pre-firma

Antes de cambiar el estado a `FIRMADA`, verificar:

- [ ] L0 es una frase (literalmente, no un párrafo)
- [ ] L1 responde "qué pasaría si no existiera" con consecuencias concretas
- [ ] L2 NO usa naming prohibido (`primary`, `secondary`, `gray`)
- [ ] L3 lista DSCs locales firmados
- [ ] L4 tiene estado para las 7 capas (incluso si es "DEUDA" o "N/A")
- [ ] L5 tiene al menos Sprint 0 + Sprint 1 definidos
- [ ] L7 tiene al menos un health endpoint funcionando
- [ ] L9 lista al menos 2 dependencias (consumes O alimenta)
- [ ] L12 está en formato directo, sin párrafos largos

### Paso 6 — Firmar y commitear

```bash
git add docs/biblias_proyectos/{{PROYECTO}}/BIBLIA_MAGNA.md
git commit -m "docs(biblia): {{PROYECTO}} v1.0 inicial — firmada por {{OWNER}}

Capas L0–L12 completadas. Brand DNA on-brand (forja+graphite+acero).
DSCs locales: {{lista}}.

Sprint origen: {{SPRINT_ID}}"
git push
```

Después actualizar `docs/biblias_proyectos/_INDEX.md` para listar la biblia nueva.

---

## Cuándo actualizar la biblia

**SIEMPRE actualizar:**
- Cierre de sprint que cambia algo de las 12 capas
- Cambio de stack o dependencia crítica
- Error grave firmado en DSC (actualizar L8)
- Vínculo nuevo con otro proyecto-hijo (actualizar L9)
- Cambio de owner (actualizar header)

**NO necesitás actualizar:**
- Bug fix sin impacto arquitectónico
- Refactor interno que no cambia interfaces
- Update de copy en una página

---

## Anti-patrones específicos de bibliias

❌ **L0 con párrafos** — debe ser UNA frase. Si no podés, no estás listo para escribir esta biblia.  
❌ **L4 con todas las capas en "N/A"** — si todas son N/A, no es un proyecto del Monstruo, es otra cosa.  
❌ **L9 vacía** — si no tiene vínculos con nada del ecosistema, ¿por qué existe?  
❌ **L12 con párrafos largos** — esto es para agentes que ejecutan. Lista o tabla.  
❌ **L7 con valores reales de secrets** — solo nombres. Los valores en el secret manager.  
❌ **Crear biblia "por compliance" sin contenido real** — vale más una L0 buena que 12 capas con `TBD`.

---

## Ejemplos vivos

| Proyecto | Path | Estado |
|---|---|---|
| CIP | `docs/biblias_proyectos/cip/BIBLIA_MAGNA.md` | (pendiente — debería ser primer cliente del template) |
| Marketplace Interiorismo | `docs/biblias_proyectos/marketplace_interiorismo/BIBLIA_MAGNA.md` | (pendiente) |
| Roche Bobois | `docs/biblias_proyectos/roche_bobois/BIBLIA_MAGNA.md` | (pendiente) |
| Mundo Tata | `docs/biblias_proyectos/mundo_tata/BIBLIA_MAGNA.md` | (pendiente) |
| Command Center | `docs/biblias_proyectos/command_center/BIBLIA_MAGNA.md` | (pendiente) |

---

## Cross-links

- `docs/templates/biblia-master-plan-template.md` — el template canónico
- `docs/biblias_proyectos/_INDEX.md` — índice de bibliias del Monstruo
- `discovery_forense/CAPILLA_DECISIONES/` — donde viven los DSCs que las bibliias referencian
- DSC-G-004 — Brand Engine
- DSC-G-008 — auditar codebase antes de specs (aplica también a bibliias)

---

— Hilo Catastro, Sprint Catastro-B 2026-05-06
