# BIBLIA MAGNA — {{NOMBRE_PROYECTO}}

> **Versión:** v1.0
> **Owner:** {{OWNER}}
> **Última actualización:** {{YYYY-MM-DD}}
> **Sprint de origen:** {{SPRINT_ID}}
> **Estado:** {{DRAFT | EN_REVISION | FIRMADA | ARCHIVADA}}

---

## L0 — Identidad del proyecto

> Una frase. Si no podés decir qué es esto en una frase, no estás listo para escribirlo.

**Qué es:** ...

**Qué NO es:** ...

**Para quién:** ...

**Si esto desaparece mañana, ¿quién lo extraña?** ...

---

## L1 — Contexto y propósito

### ¿Por qué existe este proyecto?

(2-3 párrafos. Causa raíz. Qué dolor del Monstruo o del mundo lo origina. NO copywriting — análisis técnico-estratégico crudo.)

### ¿Qué pasaría si NO existiera?

(Lista de consecuencias concretas, no abstractas.)

### Encaje en la arquitectura del Monstruo

Capa: {{C0 / C1 / C2 / C3 / C4}}
DSCs aplicables: {{DSC-X, DSC-G, DSC-MO, ...}}
Catastro de pertenencia: {{Modelos / Agentes / Herramientas Verticales / Suppliers Humanos / N/A}}

---

## L2 — Brand DNA del proyecto

### Identidad visual

| Token | Valor canónico | Override del Monstruo (si lo hay) |
|---|---|---|
| Primary action | `forja-500` | — |
| Background canvas | `graphite-700` | — |
| Accent | `acero-400` | — |
| Display font | Bebas Neue | — |
| Body font | Inter | — |

> Naming inviolable: NUNCA `primary`, `secondary`, `gray`. SIEMPRE `forja-*`, `graphite-*`, `acero-*`.

### Tono de voz

- **Personalidad:** ...
- **Cuándo es directo:** ...
- **Cuándo es metafórico:** ...
- **Anti-tonos (lo que NUNCA suena):** ...

### Naming convention

- Endpoints: `/api/v1/{modulo}/...`
- Errores: `{modulo}_{action}_{failure_type}`
- Módulos: nombres con identidad (NUNCA `service`, `handler`, `utils`, `helper`, `misc`)

---

## L3 — Arquitectura técnica

### Stack canónico

| Capa | Elección | Por qué (vs alternativas evaluadas) |
|---|---|---|
| Frontend | ... | ... |
| Backend | ... | ... |
| DB | ... | ... |
| Auth | Manus-Oauth (DSC-X-003) | Provider canónico del Monstruo |
| Hosting | ... | ... |
| Observabilidad | ... | ... |

### Decisiones arquitectónicas firmadas (DSCs locales)

- DSC-{{PROYECTO}}-001: ...
- DSC-{{PROYECTO}}-002: ...

### Dependencias externas críticas

| Dep | Versión | Validación realtime (DSC-V-002) | Fallback |
|---|---|---|---|
| ... | ... | (link al check) | ... |

---

## L4 — Las 7 Capas Transversales (Obj #9)

> Toda producción del Monstruo nace con las 7 capas activas o se documenta el porqué de la deuda.

| Capa | Estado | Dueño | Notas |
|---|---|---|---|
| 1. Motor de Ventas | {{ACTIVA / DEUDA / N/A}} | ... | ... |
| 2. SEO y Descubrimiento | ... | ... | ... |
| 3. Publicidad y Campañas | ... | ... | ... |
| 4. Tendencias y Adaptación | ... | ... | ... |
| 5. Administración y Operaciones | ... | ... | ... |
| 6. Finanzas | ... | ... | ... |
| 7. Resiliencia Agéntica | ... | ... | ... |

---

## L5 — Roadmap de sprints

### Sprint 0 (cimientos)

- [ ] ...

### Sprint 1 (MVP)

- [ ] ...

### Sprint N (...)

- [ ] ...

### Backlog crudo (no priorizado)

- ...

---

## L6 — Métricas de éxito

### KPIs técnicos

| Métrica | Target sprint actual | Target v1.0 | Cómo se mide |
|---|---|---|---|
| ... | ... | ... | ... |

### KPIs de negocio

| Métrica | Target sprint actual | Target v1.0 | Cómo se mide |
|---|---|---|---|
| ... | ... | ... | ... |

### Critic Score (si aplica)

| Sprint | Score actual | Target |
|---|---|---|
| ... | ... | ... |

---

## L7 — Operación

### Endpoints / URLs vivas

| Servicio | URL | Health |
|---|---|---|
| ... | ... | `curl ...` |

### Secrets requeridos

(NUNCA pegar valores. Solo nombres.)

- `{{PROYECTO}}_API_KEY`
- `{{PROYECTO}}_DB_URL`
- `MANUS_OAUTH_CLIENT_ID`
- `MANUS_OAUTH_CLIENT_SECRET`

### Comandos operacionales

```bash
# Deploy
...

# Smoke
...

# Rollback
...
```

---

## L8 — Capa de aprendizaje

### Errores cometidos en este proyecto

| Sprint | Error | Lección | DSC firmado |
|---|---|---|---|
| ... | ... | ... | ... |

### Decisiones que cambiaríamos hoy

- ...

### Anti-patrones específicos del proyecto

- ❌ ...
- ❌ ...

---

## L9 — Dependencias y vínculos con el ecosistema

### Otros proyectos del Monstruo que dependen de este

- ...

### Proyectos del Monstruo de los que este depende

- ...

### Catastros que alimenta o consume

- ...

---

## L10 — Hand-off y continuidad

### Cómo onboarder a un nuevo agente/persona en este proyecto

1. Lee este documento completo
2. Lee `discovery_forense/CAPILLA_DECISIONES/_PROYECTOS/{{PROYECTO}}/`
3. Corre los smokes en orden ...
4. Verifica salud de las dependencias en L9
5. Lista de lecturas adicionales: ...

### Si este proyecto se archiva mañana

- Migración a: ...
- Datos a preservar: ...
- DSCs que se deprecan: ...

---

## L11 — Glosario

| Término | Definición operacional |
|---|---|
| ... | ... |

---

## L12 — Instrucciones operacionales (para el agente que ejecuta)

> Esta sección es lo que un agente IA lee al trabajar en este proyecto. Es directa, sin literatura.

### Antes de tocar código en este proyecto

1. Lee este documento completo (no opcional)
2. Verifica que el último deploy está verde: `curl <health_url>`
3. Si vas a tocar `auth/`, recuerda DSC-X-003 (Manus-Oauth)
4. Si vas a tocar UI, importa de `@monstruo/design-tokens` (NUNCA primary/secondary)
5. Si vas a tocar DB, valida schema con `drizzle-kit check` antes del commit

### Qué auditar antes de declarar un sprint cerrado

- [ ] L4 actualizada: ¿alguna capa transversal cambió de estado?
- [ ] L5 actualizada: el sprint cerrado movido a "completado"
- [ ] L6 actualizada: KPIs medidos y registrados
- [ ] L7 actualizada: si endpoints/secrets cambiaron
- [ ] L8 actualizada: si hubo error firmado en DSC
- [ ] L9 actualizada: si el grafo de dependencias cambió

### Si encontrás contradicción entre este doc y el código

- El código gana sólo si está deployed y funcionando
- Si el código no funciona y este doc dice cómo debería, este doc gana
- En cualquier caso: actualizá lo desactualizado en el mismo PR

---

## Cambios desde la versión anterior

| Versión | Fecha | Autor | Cambios principales |
|---|---|---|---|
| v1.0 | {{YYYY-MM-DD}} | {{OWNER}} | Initial |

---

— Generado desde `docs/templates/biblia-master-plan-template.md` v1.0  
— Skill: `usar-biblia-template`  
— Sprint: Catastro-B 2026-05-06
