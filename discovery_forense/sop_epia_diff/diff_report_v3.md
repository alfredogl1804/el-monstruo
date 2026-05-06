# Diff semantico SOP/EPIA v3 — Drive vs Dropbox (final)

**Fecha:** 2026-05-05
**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)
**Metodo:** strip Markdown -> split camelCase glued tokens -> SequenceMatcher + set diff

## Resumen ejecutivo

| # | Par | Tokens Drive | Tokens DBX | Similaridad | Tokens UNICOS Drive | Tokens UNICOS DBX | Veredicto |
|---|---|---|---|---|---|---|---|
| 1 | SOP Fundacional v1.2 | 5202 | 3996 | 0.863 | 196 | 2 | DIFS NOTABLES |
| 2 | EPIA Fundacional v1.0 | 2339 | 3648 | 0.764 | 8 | 286 | DIFS SIGNIFICATIVAS |
| 3 | Genealogia SOP/EPIA v2 | 750 | 750 | 1.000 | 0 | 0 | EQUIVALENTES |
| 4 | SOP+EPIA Reestructuracion 6 Sabios | 2650 | 2650 | 1.000 | 0 | 0 | EQUIVALENTES |
| 5 | EPIA Fundacional (md vs md) | 2339 | 3646 | 0.764 | 7 | 286 | DIFS SIGNIFICATIVAS |
| 6 | ENTREGABLE 2 SOP (md vs md) | 3998 | 5202 | 0.863 | 2 | 196 | DIFS NOTABLES |

## Conclusiones

- **Pares 3 y 4** (Genealogia y SOP+EPIA Reestructuracion): IDENTICOS / EQUIVALENTES. Drive y Dropbox estan sincronizados.
- **Pares 1, 2, 5, 6** (SOP/EPIA Fundacionales): DIFS NOTABLES. Hay que inspeccionar manualmente bloques presentes en solo uno para decidir cual es el canon.
- **Recomendacion:** la version mas larga (mas tokens) generalmente es la mas reciente y completa, pero hay que validarlo con Alfredo.

## Detalle por par

### 1. SOP Fundacional v1.2

- Drive: `SOP_v1.2_DRIVE.md` (5202 tokens, 1368 unicos)
- Dropbox: `ENTREGABLE_2_SOP_DBX.txt` (3996 tokens, 1167 unicos)
- Similaridad: **0.863** -> **DIFS NOTABLES**
- Tokens significativos solo en DRIVE (196): abiertas, abiertos, accesible, aceptación, aceptada, aclaraciones, acotada, actores, además, afectada, afecte, alineación, altamente, altera, amplio, analítica, aplica, aplicable, aplique, aportar, aprobado, aprobar, aprobarse, aprobó, audita, auditable, aumenta, autorizados, bloquea, bloqueo ...

- Tokens significativos solo en DROPBOX (2): componente, esquema

**Bloques grandes presentes en SOLO uno (>=30 tokens):**

#### Bloque 1 (DRIVE_ONLY)
```
2 5 glosario operativo cuantificable matriz de criticidad para evitar interpretaciones divergentes los siguientes términos se consideran operativamente definidos relevante un asunto es relevante cuando cumple al menos una de estas condiciones afecta doctrina arquitectura reglas impacta múltiples dominios agentes memorias modifica decisiones futuras altera seguridad costo trazabilidad validación requiere persistencia consolidación crítico un asunto es crítico cuando puede causar daño alto irrever
```

#### Bloque 2 (DRIVE_ONLY)
```
5 15 meta-principio de resolución de conflictos cuando dos principios constitucionales entren en tensión prevalecerá el siguiente orden de protección seguridad contención soberanía de memoria reversibilidad trazabilidad validación proporcional al riesgo eficiencia adaptativa regla la eficiencia nunca debe usarse para anular seguridad memoria reversibilidad trazabilidad en caso de conflicto no resuelto se activa confirmación n3 escalamiento humano
```

#### Bloque 3 (DRIVE_ONLY)
```
6 7 ciclo de vida de las normas toda norma debe recorrer un ciclo de vida explícito propuesta surge como respuesta un problema patrón contradicción detectada experimental shadow mode se prueba de forma acotada sin elevarse aún canon vigente validación se contrasta con evidencia práctica real cuando aplique con múltiples sabios revisión humana consolidación formal la norma se redacta versiona queda integrada al cuerpo vigente vigencia la norma entra en operación se considera aplicable según su ni
```

#### Bloque 4 (DRIVE_ONLY)
```
8 1 1 protocolo de deliberación multi sabio el panel multi sabio se convoca cuando la decisión es estratégica existe contradicción relevante el impacto es alto una sola fuente modelo no es suficiente entrada mínima requerida toda consulta multi sabio debe incluir problema exacto contexto mínimo objetivo de decisión restricción de tiempo costo criterio de salida esperado formato esperado de respuesta cada sabio debe devolver cuando sea posible postura principal fortalezas de esa postura riesgos d
```

#### Bloque 5 (DRIVE_ONLY)
```
consolidación formal estado en que una norma tiene redacción estable alcance definido justificación suficiente versión fecha aceptación dentro de su nivel normativo ver 6 7 crítico asunto que puede causar daño alto irreversibilidad compromiso de seguridad bloqueo central contradicción estructural ver 2 5
```

### 2. EPIA Fundacional v1.0

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (2339 tokens, 753 unicos)
- Dropbox: `EPIA_FUNDACIONAL_DBX.txt` (3648 tokens, 1039 unicos)
- Similaridad: **0.764** -> **DIFS SIGNIFICATIVAS**
- Tokens significativos solo en DRIVE (8): 2026-04-04, completos, cristaliza, deja, pasa, pendiente, previa, verse

- Tokens significativos solo en DROPBOX (286): abandonó, abierta, abre, absoluto, absorberlo, abstracción, abstracta, abstraerse, abstraída, accesorios, adquirió, agota, aislados, alterarse, alternativa, ambición, ambigüedad, ambos, ampliable, analiza, anthropic, aparece, apareció, aporta, arquitectónico-visionario, asignar, asociado, auditarse, auditoría, auxiliar ...

**Bloques grandes presentes en SOLO uno (>=30 tokens):**

#### Bloque 1 (DBX_ONLY)
```
capas las capas son niveles funcionales del ecosistema capa de visión capa de gobierno capa de orquestación capa de memoria capa de conectividad capa de ejecución capa de validación capa de expansión futura qué significa
```

#### Bloque 2 (DBX_ONLY)
```
destino final imaginado el destino final de es un ecosistema capaz de operar sobre las 10 dimensiones de poder luego extenderse hacia el entendido como la frontera de capacidades emergentes tecnologías hoy periféricas pero estratégicamente decisivas
```

#### Bloque 3 (DBX_ONLY)
```
distinción crítica modelo de manus claude anthropic qwen como motor interno de manus modelos los 6 sabios llamados externamente según necesidad esta distinción es obligatoria para evitar confundir el motor interno de una herramienta con el panel deliberativo del ecosistema
```

#### Bloque 4 (DBX_ONLY)
```
núcleo vs periferia núcleo de soberanía de integración memoria persistente orquestación multi-capacidad conectividad universal deliberación especializada periferia de herramientas concretas reemplazables proveedores específicos modelos puntuales conectores temporales exploraciones de frontera
```

#### Bloque 5 (DBX_ONLY)
```
jerarquía conceptual es más general en el plano arquitectónico-visionario es más específico en el plano normativo-operativo no son equivalentes sin el gobierna sin mapa de poder sin integra sin disciplina complementariedad real sin produce exuberancia caótica sin produce orden sin expansión el sistema total necesita ambos para no perder ambición estructural para no convertir esa ambición en desorden
```

### 3. Genealogia SOP/EPIA v2

- Drive: `GENEALOGIA_SOP_EPIA_v2_DRIVE.md` (750 tokens, 409 unicos)
- Dropbox: `GENEALOGIA_SOP_EPIA_DBX.txt` (750 tokens, 409 unicos)
- Similaridad: **1.000** -> **EQUIVALENTES**
- Tokens significativos solo en DRIVE (0): 

- Tokens significativos solo en DROPBOX (0): 

### 4. SOP+EPIA Reestructuracion 6 Sabios

- Drive: `SOP_EPIA_REESTRUCTURACION_DRIVE.md` (2650 tokens, 947 unicos)
- Dropbox: `SOP_EPIA_REESTRUCTURACION_DBX.md` (2650 tokens, 947 unicos)
- Similaridad: **1.000** -> **EQUIVALENTES**
- Tokens significativos solo en DRIVE (0): 

- Tokens significativos solo en DROPBOX (0): 

### 5. EPIA Fundacional (md vs md)

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (2339 tokens, 753 unicos)
- Dropbox: `EPIA_FUNDACIONAL_DBX.md` (3646 tokens, 1039 unicos)
- Similaridad: **0.764** -> **DIFS SIGNIFICATIVAS**
- Tokens significativos solo en DRIVE (7): completos, cristaliza, deja, pasa, pendiente, previa, verse

- Tokens significativos solo en DROPBOX (286): abandonó, abierta, abre, absoluto, absorberlo, abstracción, abstracta, abstraerse, abstraída, accesorios, adquirió, agota, aislados, alterarse, alternativa, ambición, ambigüedad, ambos, ampliable, analiza, anthropic, aparece, apareció, aporta, arquitectónico-visionario, asignar, asociado, auditarse, auditoría, auxiliar ...

**Bloques grandes presentes en SOLO uno (>=30 tokens):**

#### Bloque 1 (DBX_ONLY)
```
capas las capas son niveles funcionales del ecosistema capa de visión capa de gobierno capa de orquestación capa de memoria capa de conectividad capa de ejecución capa de validación capa de expansión futura qué significa
```

#### Bloque 2 (DBX_ONLY)
```
destino final imaginado el destino final de es un ecosistema capaz de operar sobre las 10 dimensiones de poder luego extenderse hacia el entendido como la frontera de capacidades emergentes tecnologías hoy periféricas pero estratégicamente decisivas
```

#### Bloque 3 (DBX_ONLY)
```
distinción crítica modelo de manus claude anthropic qwen como motor interno de manus modelos los 6 sabios llamados externamente según necesidad esta distinción es obligatoria para evitar confundir el motor interno de una herramienta con el panel deliberativo del ecosistema
```

#### Bloque 4 (DBX_ONLY)
```
núcleo vs periferia núcleo de soberanía de integración memoria persistente orquestación multi-capacidad conectividad universal deliberación especializada periferia de herramientas concretas reemplazables proveedores específicos modelos puntuales conectores temporales exploraciones de frontera
```

#### Bloque 5 (DBX_ONLY)
```
jerarquía conceptual es más general en el plano arquitectónico-visionario es más específico en el plano normativo-operativo no son equivalentes sin el gobierna sin mapa de poder sin integra sin disciplina complementariedad real sin produce exuberancia caótica sin produce orden sin expansión el sistema total necesita ambos para no perder ambición estructural para no convertir esa ambición en desorden
```

### 6. ENTREGABLE 2 SOP (md vs md)

- Drive: `ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md` (3998 tokens, 1168 unicos)
- Dropbox: `ENTREGABLE_2_SOP_DBX.md` (5202 tokens, 1368 unicos)
- Similaridad: **0.863** -> **DIFS NOTABLES**
- Tokens significativos solo en DRIVE (2): componente, esquema

- Tokens significativos solo en DROPBOX (196): abiertas, abiertos, accesible, aceptación, aceptada, aclaraciones, acotada, actores, además, afectada, afecte, alineación, altamente, altera, amplio, analítica, aplica, aplicable, aplique, aportar, aprobado, aprobar, aprobarse, aprobó, audita, auditable, aumenta, autorizados, bloquea, bloqueo ...

**Bloques grandes presentes en SOLO uno (>=30 tokens):**

#### Bloque 1 (DBX_ONLY)
```
2 5 glosario operativo cuantificable matriz de criticidad para evitar interpretaciones divergentes los siguientes términos se consideran operativamente definidos relevante un asunto es relevante cuando cumple al menos una de estas condiciones afecta doctrina arquitectura reglas impacta múltiples dominios agentes memorias modifica decisiones futuras altera seguridad costo trazabilidad validación requiere persistencia consolidación crítico un asunto es crítico cuando puede causar daño alto irrever
```

#### Bloque 2 (DBX_ONLY)
```
5 15 meta-principio de resolución de conflictos cuando dos principios constitucionales entren en tensión prevalecerá el siguiente orden de protección seguridad contención soberanía de memoria reversibilidad trazabilidad validación proporcional al riesgo eficiencia adaptativa regla la eficiencia nunca debe usarse para anular seguridad memoria reversibilidad trazabilidad en caso de conflicto no resuelto se activa confirmación n3 escalamiento humano
```

#### Bloque 3 (DBX_ONLY)
```
6 7 ciclo de vida de las normas toda norma debe recorrer un ciclo de vida explícito propuesta surge como respuesta un problema patrón contradicción detectada experimental shadow mode se prueba de forma acotada sin elevarse aún canon vigente validación se contrasta con evidencia práctica real cuando aplique con múltiples sabios revisión humana consolidación formal la norma se redacta versiona queda integrada al cuerpo vigente vigencia la norma entra en operación se considera aplicable según su ni
```

#### Bloque 4 (DBX_ONLY)
```
8 1 1 protocolo de deliberación multi sabio el panel multi sabio se convoca cuando la decisión es estratégica existe contradicción relevante el impacto es alto una sola fuente modelo no es suficiente entrada mínima requerida toda consulta multi sabio debe incluir problema exacto contexto mínimo objetivo de decisión restricción de tiempo costo criterio de salida esperado formato esperado de respuesta cada sabio debe devolver cuando sea posible postura principal fortalezas de esa postura riesgos d
```

#### Bloque 5 (DBX_ONLY)
```
consolidación formal estado en que una norma tiene redacción estable alcance definido justificación suficiente versión fecha aceptación dentro de su nivel normativo ver 6 7 crítico asunto que puede causar daño alto irreversibilidad compromiso de seguridad bloqueo central contradicción estructural ver 2 5
```
