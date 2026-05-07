---
id: DSC-G-009
proyecto: GLOBAL
tipo: antipatron
titulo: "Recomendaciones de seguridad de Cowork (o cualquier hilo) merecen DSC firmado en la misma sesión donde se proponen, o se descartan explícitamente con razón documentada. PROHIBIDO recomendaciones huérfanas que queden en chat sin canonización."
estado: firme
fecha: 2026-05-06
fuentes:
  - chat:cowork-2026-05-04-04:36 (recomendación huérfana original — política de credenciales que NO se firmó)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md (incidente que detonó esta semilla)
  - repo:discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-001_politica_de_credenciales.md (recomendación finalmente firmada 2 días después)
cruza_con: [TODOS, DSC-G-008, DSC-S-001]
---

# Recomendaciones de seguridad firmadas en la misma sesión

## Decisión

Toda recomendación de seguridad propuesta por Cowork (o cualquier hilo: Manus, Embrión, futuros) durante una sesión de trabajo DEBE quedar como uno de dos resultados antes de cerrar la sesión:

1. **Firmada como DSC** en la Capilla de Decisiones (`discovery_forense/CAPILLA_DECISIONES/<scope>/`), o
2. **Descartada explícitamente** con razón documentada en el bridge file de cierre de sesión.

**PROHIBIDO** dejar recomendaciones de seguridad como párrafos en chat de sesión sin destino formal. El patrón "recomiendo X y Y" sin canonización ni descarte explícito produce **recomendaciones huérfanas** que se olvidan dentro de 24-72 horas y luego se manifiestan como incidentes evitables.

## Por qué

### El caso paradigmático que detonó este DSC

El 2026-05-04 04:36 UTC, durante sesión Cowork sobre rotación de tokens GitHub, Cowork recomendó textualmente a Alfredo:

> **"Política duradera (agregar a AGENTS.md):**
> 1. Cero credenciales en plaintext en git history, bridge files, ni Notion
> 2. Bóveda primaria: 1Password/Bitwarden
> 3. Mac local: `gh auth login` web flow, no PAT manual
> 4. Servicios remotos: env vars con scope mínimo, una sola variable por servicio
> 5. Rotación: 12 meses para PATs, anual auditoría de Last Used"

> "Sembrar como semilla: `seed_credenciales_dispersas_sin_audit`. 8va semilla del proyecto."

> "Query Supabase `thoughts` y `episodic` por leakage de tokens... Si encuentra rows, esos tokens están leakedos en memoria persistente."

**Ninguna de esas 7 recomendaciones se firmó como DSC ni como semilla en `error_memory`.** Quedaron como párrafos en el chat de Cowork. El cierre de sesión NO incluyó una decisión formal sobre cada una (firmar o descartar).

48 horas después, el 2026-05-06, Manus Hilo Catastro detectó el incidente P0: el password del DB Supabase estaba hardcoded en al menos 5 scripts del repo público desde Sprint 51.5. Si las recomendaciones del 2026-05-04 se hubieran firmado como DSC, el commit de Sprint 51.5 habría tenido referencia normativa explícita prohibiendo el patrón, y el cierre Sprint 51.5 habría sido rechazado por Cowork bajo DSC-S-001. El incidente NO habría ocurrido.

**Las recomendaciones huérfanas son deuda de canonización que se manifiesta como incidente.**

### Por qué pasa este patrón

1. **Cowork termina sesión con muchas recomendaciones acumuladas.** Cada sesión larga produce 5-15 recomendaciones de seguridad (entre operativas, arquitectónicas, defensivas). Es trabajo cognitivo formalizar todas como DSC en la misma sesión.

2. **No hay enforcement automático.** Sin una regla explícita, es fácil que Cowork termine con "ya las pensé, no necesito firmarlas" — confiando en memoria que sabemos no es confiable entre sesiones.

3. **Compaction de contexto las pierde.** Cuando una sesión se compacta (resumen automático), las recomendaciones quedan en el resumen pero NO en archivos canónicos. La próxima sesión no las ve.

4. **Manus no las ve si no están en archivos.** Cualquier hilo que cargue contexto del proyecto lee AGENTS.md, los DSCs canónicos, el `_INDEX.md` — pero NO lee chats de Cowork de sesiones previas. Si la recomendación no llegó a archivo canónico, Manus opera sin ella.

## Reglas

### 1. Cada recomendación de seguridad de Cowork tiene 3 destinos posibles

| Resultado | Acción | Cuándo aplica |
|---|---|---|
| **FIRMAR como DSC** | Crear archivo en `discovery_forense/CAPILLA_DECISIONES/<scope>/DSC-<TIPO>-<N>_*.md` con frontmatter completo | Default — la mayoría de recomendaciones de seguridad merecen ser DSCs |
| **SEMBRAR en error_memory** | `ErrorRule(...)` agregada al script de seeds + commit | Para patrones de fallo recurrente que no son decisiones normativas pero merecen alerta automática |
| **DESCARTAR con razón** | Línea en bridge de cierre: "Descarté recomendación X porque Y" | Solo si la recomendación es transitoria, redundante con DSC existente, o no aplica al contexto |

### 2. Cierre de sesión Cowork incluye sección "Recomendaciones de seguridad"

El bridge file de cierre de sesión Cowork (formato `bridge/cowork_to_manus_SESION_<fecha>_CIERRE.md`) DEBE incluir sección explícita:

```markdown
## Recomendaciones de seguridad de esta sesión

| # | Recomendación | Destino | Archivo / Razón de descarte |
|---|---|---|---|
| 1 | [texto corto] | DSC | `DSC-S-006_*.md` |
| 2 | [texto corto] | seed | `seed_X` en error_memory.py |
| 3 | [texto corto] | descartado | redundante con DSC-S-001 punto 4 |
```

Sin esta sección, el cierre de sesión es incompleto — Cowork no firma cierre verde de sesión hasta que esté.

### 3. Aplicación retroactiva (catch-up)

Las recomendaciones huérfanas detectadas en sesiones previas (auditando bridges archived o transcripts) tienen 2 opciones:

- **Si todavía aplica** (la realidad operativa no cambió): firmar como DSC retroactivamente con fecha de origen + fecha de firma, ambas documentadas en frontmatter.
- **Si ya no aplica**: documentar en bridge actual con razón ("descartada retroactivamente porque ya está cubierta por DSC-X").

DSC-S-001 a S-005 son ejemplos de aplicación retroactiva: originadas en chat 2026-05-04, firmadas 2026-05-06 post-incidente.

### 4. Cowork no es el único hilo con esta obligación

Aunque el caso paradigmático fue Cowork, la regla aplica a CUALQUIER hilo que proponga recomendaciones de seguridad:

- **Manus** durante audit pre-sprint o post-cierre — si propone "deberíamos prohibir X", firma DSC o descarta.
- **Embrión** en background loops — si su análisis dice "este patrón es vulnerable", abre PR con DSC propuesto.
- **Alfredo** en sesiones de planning — si propone "necesitamos política de Y", Cowork lo formaliza como DSC inmediato.

## Implicaciones

### Para Cowork

- Cierre de sesión incluye revisión de "qué recomendaciones de seguridad surgieron y dónde quedaron" como paso obligatorio.
- En sesiones largas, Cowork mantiene tracker explícito (en task list o nota interna) de recomendaciones acumuladas para revisarlas al cierre.
- DSC-G-009 evita que el patrón "recomendaciones en chat huérfanas" se repita.

### Para Manus

- Cuando Manus propone hardening durante audit, NO escribe "deberíamos hacer X" en el reporte sin acción concreta. O propone DSC borrador, o pide a Cowork que lo formalice.
- Cuando Cowork firma cierre de sprint que toca seguridad, audita que las recomendaciones de Manus tengan destino formal (DSC o descarte).

### Para futuros incidentes

- Cualquier postmortem futuro debe incluir sección "Recomendaciones de seguridad previas que estaban huérfanas y se manifestaron en este incidente". Si encontramos alguna → ese es señal de que DSC-G-009 no se aplicó correctamente y vale revisar el patrón.

## Estado de validación

**firme — fruto del incidente P0 del 2026-05-06.** Recomendaciones de seguridad de Cowork del 2026-05-04 (política de credenciales) quedaron huérfanas durante 48 horas → incidente P0. Canonización del meta-patrón en este DSC el 2026-05-06 cierra estructuralmente la brecha. Aplicación de DSC-G-009 a sí mismo: este DSC es exactamente el tipo de recomendación que en el patrón viejo habría quedado en chat — al firmarlo en la misma sesión donde lo propuse, cumplo la regla que el DSC mismo prescribe.
