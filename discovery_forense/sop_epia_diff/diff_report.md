# Diff semántico SOP/EPIA — Drive (.md) vs Dropbox (.docx/.md)

**Fecha:** 2026-05-05
**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)
**Método:** normalización (whitespace, BOM, line endings) + SHA256 + SequenceMatcher

## Resumen ejecutivo

| # | Par | Drive bytes | DBX bytes | SHA Drive | SHA DBX | Similaridad | Estado |
|---|---|---|---|---|---|---|---|
| 1 | SOP — Documento Fundacional Maestro v1.2 | 43321 | 31216 | `0464cabe583ed2f6` | `19f2b377da41beec` | 0.248 | DOCUMENTOS DISTINTOS |
| 2 | EPIA — Documento Fundacional Maestro v1.0 | 19373 | 28404 | `07499d44322b9f0c` | `502838fee3a820e3` | 0.197 | DOCUMENTOS DISTINTOS |
| 3 | Genealogía Evolutiva SOP/EPIA v2 | 6472 | 6028 | `13238a738e2918f6` | `cfe83920e7429d41` | 0.188 | DOCUMENTOS DISTINTOS |
| 4 | SOP+EPIA Reestructuración 6 Sabios (Abr 2026) | 20785 | 20785 | `3c8daa1cdbbc621b` | `3c8daa1cdbbc621b` | 1.000 | IDENTICOS |
| 5 | EPIA Documento Fundacional (md vs md) | 19373 | 30383 | `07499d44322b9f0c` | `715af8f2f95ec77e` | 0.663 | DIFERENCIAS SIGNIFICATIVAS |
| 6 | ENTREGABLE 2 SOP (md vs md) | 33484 | 43321 | `3fd70775b4976967` | `0464cabe583ed2f6` | 0.866 | DIFERENCIAS MENORES |

## Detalle por par

### 1. SOP — Documento Fundacional Maestro v1.2

- Drive: `SOP_v1.2_DRIVE.md` (43321 bytes, normalizado: 43059)
- Dropbox: `ENTREGABLE_2_SOP_DBX.txt` (31216 bytes, normalizado: 31126)
- SHA Drive: `0464cabe583ed2f6` | SHA Dropbox: `19f2b377da41beec`
- Similaridad: **0.248** (DOCUMENTOS DISTINTOS)

**Primeras diferencias detectadas:**

#### Diff bloque 1 (replace)
```diff
- DRIVE: # ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP
+ DBX:   ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP
+ DBX:   SOP — DOCUMENTO FUNDACIONAL MAESTRO
+ DBX:   0. Portada de control
```

#### Diff bloque 2 (replace)
```diff
- DRIVE: # SOP — DOCUMENTO FUNDACIONAL MAESTRO
+ DBX:   Versión:1.0 compilada
```

#### Diff bloque 3 (replace)
```diff
- DRIVE: ## 0. Portada de control
+ DBX:   Estado:Canónico consolidado
```

#### Diff bloque 4 (replace)
```diff
- DRIVE: **Nombre oficial del documento:**
- DRIVE: SOP — Documento Fundacional Maestro
+ DBX:   Fecha:2026-04-04
```

#### Diff bloque 5 (replace)
```diff
- DRIVE: **Versión:**
- DRIVE: 1.2 compilada — con 6 cambios de auditoría + pulido fino editorial
+ DBX:   Alcance:Gobernanza integral del ecosistema operativo, documental, decisional y técnico que sostiene la operación de El Monstruo y de sus dominios derivados.
```

### 2. EPIA — Documento Fundacional Maestro v1.0

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (19373 bytes, normalizado: 19163)
- Dropbox: `EPIA_FUNDACIONAL_DBX.txt` (28404 bytes, normalizado: 28362)
- SHA Drive: `07499d44322b9f0c` | SHA Dropbox: `502838fee3a820e3`
- Similaridad: **0.197** (DOCUMENTOS DISTINTOS)

**Primeras diferencias detectadas:**

#### Diff bloque 1 (replace)
```diff
- DRIVE: # EPIA — DOCUMENTO FUNDACIONAL MAESTRO
+ DBX:   EPIA — DOCUMENTO FUNDACIONAL MAESTRO
+ DBX:   0. Portada de control
+ DBX:   Nombre oficial: EPIA — Ecosistema de IAs ExternasVersión: 1.0Estado: Canónico consolidadoFecha: 2026-04-04Alcance: Marco fundacional, arquitectónico y visionario para definir qué integra el ecosistema
```

#### Diff bloque 2 (replace)
```diff
- DRIVE: ## 0. Portada de control
- DRIVE: 
- DRIVE: **Nombre oficial:** EPIA — Ecosistema de IAs Externas
+ DBX:   1. Resumen ejecutivo
+ DBX:   EPIA es el nombre de una apuesta estructural: construir un ecosistema soberano de inteligencias externas, conectadas, orquestadas y acumulativas, capaz de superar las limitaciones de una sola IA, una 
```

#### Diff bloque 3 (replace)
```diff
- DRIVE: Su tesis es simple y radical: **la inteligencia útil no debe residir en un modelo aislado, sino en un ecosistema interoperable de cerebros, brazos ejecutores, memoria persistente, protocolos de contex
+ DBX:   Su tesis es simple y radical: la inteligencia útil no debe residir en un modelo aislado, sino en un ecosistema interoperable de cerebros, brazos ejecutores, memoria persistente, protocolos de contexto
```

#### Diff bloque 4 (replace)
```diff
- DRIVE: - **EPIA define el mapa del poder**: qué capacidades importan, qué capas deben existir, qué se integra y con qué propósito.
- DRIVE: - **SOP define el gobierno**: cómo se decide, cómo se valida, cómo se limita, cómo se detiene y cómo se opera sin caos.
+ DBX:   EPIA define el mapa del poder: qué capacidades importan, qué capas deben existir, qué se integra y con qué propósito.
+ DBX:   SOP define el gobierno: cómo se decide, cómo se valida, cómo se limita, cómo se detiene y cómo se opera sin caos.
```

#### Diff bloque 5 (replace)
```diff
- DRIVE: - **EPIA es la doctrina arquitectónica general.**
- DRIVE: - **El Monstruo es su implementación concreta en abril de 2026.**
+ DBX:   EPIA es la doctrina arquitectónica general.
+ DBX:   El Monstruo es su implementación concreta en abril de 2026.
```

### 3. Genealogía Evolutiva SOP/EPIA v2

- Drive: `GENEALOGIA_SOP_EPIA_v2_DRIVE.md` (6472 bytes, normalizado: 6413)
- Dropbox: `GENEALOGIA_SOP_EPIA_DBX.txt` (6028 bytes, normalizado: 6020)
- SHA Drive: `13238a738e2918f6` | SHA Dropbox: `cfe83920e7429d41`
- Similaridad: **0.188** (DOCUMENTOS DISTINTOS)

**Primeras diferencias detectadas:**

#### Diff bloque 1 (replace)
```diff
- DRIVE: # Genealogía Evolutiva del Ecosistema SOP y EPIA
- DRIVE: 
- DRIVE: **Fecha de actualización:** 2026-04-06
+ DBX:   Genealogía Evolutiva del Ecosistema SOP y EPIA
+ DBX:   Fecha de actualización: 2026-04-06
+ DBX:   Corpus base: 98 archivos (66 originales + 32 históricos subidos)
```

#### Diff bloque 2 (replace)
```diff
- DRIVE: ---
+ DBX:   1. Evolución del SOP (Standard Operating Procedure)
+ DBX:   El SOP es la constitución operativa del sistema. Ha evolucionado de ser una lista de trucos y reglas para prompts, a convertirse en un framework completo de gobernanza con "Policy-as-Code".
```

#### Diff bloque 3 (replace)
```diff
- DRIVE: ## 1. Evolución del SOP (Standard Operating Procedure)
+ DBX:   Generación 0: Los Cimientos (Pre-Septiembre 2025)
+ DBX:   Documentos clave: Documento_Maestro_SOP.md, Mandato_Maestro_SOP.pdf
+ DBX:   Conceptos introducidos:
```

#### Diff bloque 4 (replace)
```diff
- DRIVE: El SOP es la **constitución operativa** del sistema. Ha evolucionado de ser una lista de trucos y reglas para prompts, a convertirse en un framework completo de gobernanza con "Policy-as-Code".
+ DBX:   Generación 1: La Capa de Persistencia (Septiembre 2025)
+ DBX:   Documentos clave: RespaldoSOP13desep25.md
+ DBX:   Conceptos introducidos:
```

#### Diff bloque 5 (replace)
```diff
- DRIVE: ### Generación 0: Los Cimientos (Pre-Septiembre 2025)
- DRIVE: * **Documentos clave:** `Documento_Maestro_SOP.md`, `Mandato_Maestro_SOP.pdf`
- DRIVE: * **Conceptos introducidos:**
+ DBX:   Generación 2: El Roadmap Estratégico (Octubre 2025)
+ DBX:   Documentos clave: Plan_Implementacion_SOP_v3.pdf
+ DBX:   Conceptos introducidos:
```

### 4. SOP+EPIA Reestructuración 6 Sabios (Abr 2026)

- Drive: `SOP_EPIA_REESTRUCTURACION_DRIVE.md` (20785 bytes, normalizado: 20785)
- Dropbox: `SOP_EPIA_REESTRUCTURACION_DBX.md` (20785 bytes, normalizado: 20785)
- SHA Drive: `3c8daa1cdbbc621b` | SHA Dropbox: `3c8daa1cdbbc621b`
- Similaridad: **1.000** (IDENTICOS)

### 5. EPIA Documento Fundacional (md vs md)

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (19373 bytes, normalizado: 19163)
- Dropbox: `EPIA_FUNDACIONAL_DBX.md` (30383 bytes, normalizado: 30239)
- SHA Drive: `07499d44322b9f0c` | SHA Dropbox: `715af8f2f95ec77e`
- Similaridad: **0.663** (DIFERENCIAS SIGNIFICATIVAS)

**Primeras diferencias detectadas:**

#### Diff bloque 1 (insert)
```diff
+ DBX:   ### Qué significa “capas”
+ DBX:   Las capas son niveles funcionales del ecosistema:
+ DBX:   - capa de visión,
```

#### Diff bloque 2 (insert)
```diff
+ DBX:   ### Destino final imaginado
+ DBX:   El destino final de EPIA es un ecosistema capaz de operar sobre las **10 Dimensiones de Poder**, y luego extenderse hacia el **DEEP SPECTRUM**, entendido como la frontera de capacidades emergentes y t
+ DBX:   
```

#### Diff bloque 3 (replace)
```diff
- DRIVE: Como visión canónica de expansión, EPIA reconoce diez grandes dimensiones de poder:
+ DBX:   Como visión canónica de expansión, EPIA reconoce diez grandes dimensiones de poder. Su formulación exacta podrá refinarse, pero su espíritu es estable:
+ DBX:   
```

#### Diff bloque 4 (replace)
```diff
- DRIVE: **DEEP SPECTRUM** representa la expansión futura hacia capacidades y tecnologías emergentes:
+ DBX:   **DEEP SPECTRUM** es la visión de frontera. Representa la expansión futura hacia tecnologías y dominios que hoy son exploratorios pero mañana pueden ser estructurales:
```

#### Diff bloque 5 (insert)
```diff
+ DBX:   EPIA no exige que todo eso exista hoy. Exige que el ecosistema esté diseñado para poder absorberlo mañana.
+ DBX:   
```

### 6. ENTREGABLE 2 SOP (md vs md)

- Drive: `ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md` (33484 bytes, normalizado: 33255)
- Dropbox: `ENTREGABLE_2_SOP_DBX.md` (43321 bytes, normalizado: 43059)
- SHA Drive: `3fd70775b4976967` | SHA Dropbox: `0464cabe583ed2f6`
- Similaridad: **0.866** (DIFERENCIAS MENORES)

**Primeras diferencias detectadas:**

#### Diff bloque 1 (replace)
```diff
- DRIVE: 1.0 compilada
+ DBX:   1.2 compilada — con 6 cambios de auditoría + pulido fino editorial
```

#### Diff bloque 2 (insert)
```diff
+ DBX:   ### 2.5 Glosario operativo cuantificable y matriz de criticidad
+ DBX:   
+ DBX:   Para evitar interpretaciones divergentes, los siguientes términos se consideran operativamente definidos:
```

#### Diff bloque 3 (replace)
```diff
- DRIVE: El humano conserva soberanía, pero no debe cargar manualmente toda la consistencia del sistema.
+ DBX:   El humano conserva soberanía final, pero no debe cargar manualmente la consistencia cotidiana del sistema.
```

#### Diff bloque 4 (replace)
```diff
- DRIVE: ### 5.5 Seguridad Mental y Operativa
+ DBX:   ### 5.5 Seguridad cognitiva y operativa
```

#### Diff bloque 5 (insert)
```diff
+ DBX:   ### 5.15 Meta-principio de resolución de conflictos
+ DBX:   
+ DBX:   Cuando dos principios constitucionales entren en tensión, prevalecerá el siguiente orden de protección:
```
