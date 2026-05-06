# SOP+EPIA — REESTRUCTURACIÓN Y EVOLUCIÓN (Abril 2026)

## 1. Diagnóstico de Consenso

El consenso entre los 6 Sabios es nítido: el ecosistema SOP+EPIA alcanzó una **madurez doctrinal alta** y una **madurez ejecutable aún insuficiente**. En otras palabras, ya existe una constitución operativa seria, con principios sólidos, jerarquía normativa, separación razonable entre visión, gobierno y operación, y una preocupación poco común por memoria, trazabilidad, validación proporcional al riesgo, reversibilidad y contención. Ese es el principal activo del corpus actual.

Sin embargo, casi todos coinciden en que el sistema todavía no es una gobernanza plenamente operacionalizada. La doctrina ya habla en lenguaje de kernel, policy-as-code, observabilidad, context packets, validadores, kill-switches, sub-SOPs y contratos entre capas; pero la implementación real aún depende en gran medida de documentos, disciplina humana y sesiones efímeras de LLM. La crítica más dura, formulada con distintos matices por varios Sabios, es que existe una **brecha estructural entre lo que el sistema declara ser y lo que hoy puede ejecutar**.

También hay consenso en que el corpus sufre de **inflación documental e histórica**. La evolución del sistema fue intelectualmente fértil, pero dejó una órbita de conceptos, ramas, marcos intermedios, metáforas y artefactos pre-canónicos que ya no deben seguir compitiendo por autoridad. La genealogía aporta valor como memoria institucional, pero no puede seguir operando como canon disperso.

Otro hallazgo compartido es que la separación entre **EPIA** y **SOP** es correcta en teoría, pero todavía insuficientemente fijada en términos operativos. EPIA debe describir arquitectura, capacidades, capas y contratos sistémicos; SOP debe gobernar conducta, decisión, validación, memoria y límites operativos. Esa frontera aún necesita endurecerse.

Finalmente, emerge un consenso estratégico: los próximos 90 días no deben dedicarse a producir más filosofía, sino a **comprimir el canon, formalizar el kernel, instrumentar métricas y someter el sistema a tensión real**. La prioridad ya no es pensar mejor el sistema, sino hacerlo funcionar bajo evidencia.

### Tabla 1. Síntesis de consenso por dimensión

| Dimensión | Consenso principal |
|---|---|
| Madurez doctrinal | Alta; el corpus ya tiene constitución, principios y taxonomía robusta |
| Madurez ejecutable | Media-baja; faltan artefactos técnicos y runtime real |
| Estado documental | Exceso de dispersión, duplicidad y residuos históricos |
| Separación de capas | Bien resuelta conceptualmente, incompleta en contratos operativos |
| Memoria y trazabilidad | Bien priorizadas doctrinalmente, débilmente implementadas |
| Validación y control | Correctos en teoría, poco instrumentados en la práctica |
| Prioridad inmediata | Dejar de expandir doctrina y cerrar la brecha hacia ejecución medible |

---

## 2. Gaps Críticos Identificados

El primer gap crítico, señalado de manera casi unánime, es la **brecha doctrina-implementación**. SOP+EPIA ya define un destino claro de gobernanza ejecutable, pero aún opera mayormente como gobernanza textual avanzada. Persisten componentes estructurales sin materialización técnica suficiente: `truth.yaml` o equivalente, `context_packet.schema.json`, `decision_record.schema.json`, kernel formal, validadores, observabilidad, inventario gobernado de conectores, protocolo técnico de contención y mecanismos reales de kill-switch.

El segundo gap es la **ausencia de un flujo de valor end-to-end canónico**. No basta con tener principios, reglas y matrices; el sistema necesita mostrar claramente cómo entra un problema, cómo se clasifica, qué validación aplica, qué decisión se toma, cómo se registra, cómo se ejecuta y cómo se audita. Hoy ese recorrido existe de forma fragmentaria, no como experiencia operacional única.

El tercer gap es la **falta de evidencia operativa**. Varios Sabios subrayaron que el sistema tiene muy pocos ejemplos canónicos de uso real: no hay un Governance Operations Log consolidado, no hay suficientes Decision Records completos, no hay historial visible de excepciones, activaciones de kill-switch o confirmaciones N3 que permitan demostrar que la gobernanza ya está viva en producción. La doctrina se autoexplica bien, pero todavía se autoevidencia poco.

El cuarto gap es la **inflación normativa y cognitiva**. El corpus, en su forma acumulada, corre el riesgo de violar su propio principio de seguridad cognitiva. Hay demasiados principios, reglas, marcos heredados, capas, protocolos y conceptos orbitando a la vez. La reestructuración debe reducir carga cognitiva, consolidar nombres y eliminar solapamientos.

El quinto gap es la **debilidad del contrato EPIA↔SOP**. Aunque el reparto conceptual está claro, aún no existe un contrato suficientemente canónico que precise qué produce EPIA, qué consume SOP, qué evento activa qué regla, y qué artefactos son arquitectónicos versus operativos versus técnicos.

El sexto gap es la **debilidad de la memoria soberana**. El corpus insiste correctamente en memoria, consolidación y anti-amnesia, pero todavía no cuenta con una implementación mínima y soberana que no dependa de la memoria efímera del hilo. La memoria debe vivir en repositorios versionados, artefactos estructurados y registros auditables.

El séptimo gap es la **falta de institucionalización de sub-SOPs**. Los sub-SOPs por dominio están declarados como necesidad, pero aún no están formalizados con plantilla única, registro canónico, estatus de vigencia y pilotos controlados suficientes. En este punto, varios Sabios coinciden además en que la rama operativa histórica más cercana a producción real no debe despreciarse, sino absorberse como evidencia y patrón de diseño.

### Tabla 2. Gaps críticos y nivel de consenso

| Gap crítico | Nivel de consenso | Impacto |
|---|---|---|
| Brecha entre doctrina y ejecución | Muy alto | Crítico |
| Falta de artefactos técnicos ejecutables | Muy alto | Crítico |
| Exceso de documentos y conceptos heredados | Muy alto | Alto |
| Contrato EPIA↔SOP insuficiente | Alto | Alto |
| Falta de métricas y evidencia de uso real | Muy alto | Crítico |
| Ausencia de runtime / orquestación real | Alto | Alto |
| Memoria soberana no implementada | Alto | Alto |
| Sub-SOPs no institucionalizados | Alto | Alto |

### Conceptos históricos que conviene rescatar formalmente

No todo lo antiguo debe eliminarse. Hay varios conceptos heredados que, según la sabiduría acumulada, deben ser rescatados e integrados dentro del nuevo canon con nombre, función y ubicación clara:

| Concepto histórico | Acción recomendada | Nuevo lugar canónico |
|---|---|---|
| PAU / Mandato Maestro | Rescatar como ciclo de aprendizaje institucional | SOP Operativo + Governance Operations Log |
| MCV | Rescatar como protocolo de cambio controlado | SOP Operativo + repositorio Git / PR workflow |
| RuleMint | Rescatar su disciplina de creación de reglas | SOP Kernel Spec + proceso de gobierno de cambios |
| AutoFooter KPI | Rescatar como obligación de propuesta con métricas | SOP Operativo |
| Rama operativa Gen 3.5 | Absorber como caso real / patrón de Sub-SOP | Registro de Sub-SOPs + anexos de referencia |
| Cost-guardrails / gateway artifacts | Reutilizar como semillas de Policy-as-Code | Policy Registry / repositorio técnico |

---

## 3. Arquitectura Documental Definitiva

La arquitectura definitiva debe resolver simultáneamente cuatro problemas: exceso de documentos, mezcla de capas, falta de ejecutabilidad y debilidad de trazabilidad. La solución no es agregar más piezas sueltas, sino **reducir, jerarquizar, versionar y separar con disciplina**.

Se propone una arquitectura definitiva de **9 artefactos canónicos** organizados en **4 niveles**, complementados por un **repositorio técnico ejecutable**. Esta propuesta sintetiza la compresión documental defendida por los Sabios 1 y 2, incorpora la exigencia de runtime y machine-readability enfatizada por los Sabios 3 y 4, y conserva la claridad jerárquica señalada por el Sabio 6.

### Principio rector de diseño documental

Todo artefacto del sistema deberá pertenecer exclusivamente a una de estas categorías:

| Categoría | Función |
|---|---|
| Identidad | Explicar qué es el sistema y por qué existe |
| Constitución | Definir principios, límites, jerarquía normativa y contratos soberanos |
| Operación | Explicar cómo se trabaja, decide, valida, registra y mejora |
| Ejecución | Traducir la doctrina a artefactos legibles por máquina y operables por runtime |

Si un documento mezcla dos o más categorías sin necesidad explícita, deberá dividirse o deprecarse.

### Arquitectura definitiva propuesta

#### Nivel 0 — Identidad

| Documento | Propósito | Observación |
|---|---|---|
| `Carta_Fundacional_EPIA_SOP_v1.0.md` | Explicar la tesis central del ecosistema, su propósito, límites y valor | Documento corto, de entrada, máximo 3–5 páginas |

#### Nivel 1 — Constitución

| Documento | Propósito | Observación |
|---|---|---|
| `EPIA_Arquitectonica_v1.0.md` | Definir capas, capacidades, roles sistémicos, interoperabilidad y contrato EPIA↔SOP | EPIA deja de absorber reglas operativas |
| `SOP_Constitucional_v1.0.md` | Definir principios no negociables, taxonomía normativa, meta-principio de conflicto y límites soberanos | Debe comprimirse respecto al corpus actual |

#### Nivel 2 — Operación

| Documento | Propósito | Observación |
|---|---|---|
| `SOP_Operativo_General_v1.0.md` | Describir el flujo de valor: entrada, clasificación, validación, decisión, registro, ejecución, revisión, excepciones | Reescrito por flujo, no por acumulación temática |
| `Protocolo_Investigacion_MDC_v1.0.md` | Formalizar el protocolo de investigación como subordinado al SOP Operativo | Sale del canon difuso |
| `SubSOP_Template_Maestro_v1.0.md` | Plantilla única obligatoria para dominios | Norma editorial y operativa |
| `Registro_Canonico_SubSOPs_v1.0.md` | Catálogo vivo de sub-SOPs vigentes, experimentales, deprecados y faltantes | Debe incluir estado y responsable |

#### Nivel 3 — Ejecución y Gobernanza Ejecutable

| Documento / artefacto | Propósito | Formato sugerido |
|---|---|---|
| `SOP_Kernel_Spec_v0.1.md` | Definir entidades formales, estados, eventos, severidades, excepciones y contratos | Markdown técnico |
| `Governance_Metrics_Standard_v1.0.md` | Definir métricas canónicas y criterios de medición | Markdown |
| `Governance_Operations_Log_v0.x` | Registrar decisiones, excepciones, contradicciones, kill-switches y aprendizajes | Markdown + CSV/SQLite si aplica |

### Repositorio técnico obligatorio

Además del canon documental, la reestructuración exige un repositorio técnico versionado que concentre la dimensión ejecutable del sistema.

#### Estructura recomendada del repositorio

| Ruta / artefacto | Función |
|---|---|
| `core/sop_rules.yaml` | Reglas legibles por máquina |
| `core/truth.md` o `core/truth.yaml` | Estado soberano mínimo |
| `schemas/context_packet.schema.json` | Esquema de handoff y memoria mínima |
| `schemas/decision_record.schema.json` | Esquema de decisión auditable |
| `policies/validator_n3.rego` o equivalente | Política inicial de validación crítica |
| `capabilities/api_registry.yaml` | Inventario gobernado de conectores, APIs y MCPs |
| `ops/decision_records/` | Registros vivos de decisiones |
| `ops/sub-sops/` | Sub-SOPs vigentes |
| `telemetry/` | Logs, métricas y eventos de control |

### Qué se fusiona

| Elemento actual | Acción |
|---|---|
| SOP fundacional sobredimensionado | Se divide en `SOP_Constitucional` y `SOP_Operativo_General` |
| Resúmenes ejecutivos EPIA + SOP | Se condensan en la `Carta_Fundacional_EPIA_SOP` |
| RuleMint, MCV, AutoFooter KPI | Se integran en SOP Operativo + Kernel + proceso de gobierno de cambios |
| Artefactos técnicos dispersos de generaciones previas | Se absorben en repositorio técnico y Policy Registry |

### Qué se separa

| Elemento | Acción |
|---|---|
| MDC / investigación | Se convierte en protocolo subordinado, no en doctrina transversal difusa |
| Inventarios dinámicos de herramientas y conectores | Salen del canon fundacional y pasan al repositorio / manual vivo |
| Casos operativos por dominio | Salen del cuerpo general y se formalizan como Sub-SOPs |

### Qué se depreca

| Tipo de artefacto | Criterio |
|---|---|
| Documentos históricos redundantes | Se archivan si no aportan una regla o caso único |
| Metáforas sin enforcement operativo | Se eliminan del canon activo |
| Placeholders `[TECH-PENDING]` sin plan | Se reemplazan por backlog con fecha y dueño |
| Versiones paralelas con autoridad ambigua | Se archivan o integran formalmente |

---

## 4. Roadmap de Evolución a 90 Días

El roadmap debe convertir la reestructuración en ejecución verificable. La meta del trimestre no es “terminar de pensar el sistema”, sino **hacer que la gobernanza crítica sea parcialmente ejecutable, medible y auditable**. Se propone un plan de 90 días dividido en cuatro fases.

### Objetivo del trimestre

Al día 90, el ecosistema debe haber logrado al menos lo siguiente:

1. Canon documental comprimido y sin ambigüedad jerárquica.
2. Kernel inicial formalizado.
3. Memoria mínima soberana implementada.
4. Registro real de decisiones y excepciones.
5. Al menos 2–3 sub-SOPs piloto operando bajo reglas comunes.
6. Dashboard mínimo con métricas de uso y fricción.
7. Primer runtime o integración mínima que reduzca dependencia del copiado manual de contexto.

### Fase 1 — Compresión canónica y partición (Días 1–15)

| Fecha objetivo | Entregable | Resultado esperado |
|---|---|---|
| Día 5 | `Carta_Fundacional_EPIA_SOP_v1.0.md` | Identidad clara del sistema |
| Día 10 | `SOP_Constitucional_v1.0.md` | Núcleo no negociable comprimido |
| Día 12 | `EPIA_Arquitectonica_v1.0.md` | Capas y contrato EPIA↔SOP definidos |
| Día 15 | `SOP_Operativo_General_v1.0.md` estructura base | Flujo de valor unificado |

**Criterio de éxito de la fase:** el corpus deja de estar organizado por genealogía y pasa a estar organizado por función.

### Fase 2 — Formalización del kernel y memoria soberana (Días 16–30)

| Fecha objetivo | Entregable | Resultado esperado |
|---|---|---|
| Día 18 | `SOP_Kernel_Spec_v0.1.md` | Entidades formales definidas |
| Día 22 | `schemas/context_packet.schema.json` | Handoff mínimo estructurado |
| Día 25 | `schemas/decision_record.schema.json` | Decisiones registrables de forma consistente |
| Día 28 | `core/truth.md` o `truth.yaml` | Estado soberano mínimo operativo |
| Día 30 | `Governance_Operations_Log_v0.x` abierto | Toda decisión relevante empieza a registrarse |

**Criterio de éxito de la fase:** el sistema ya no depende solo de memoria textual difusa para gobernarse.

### Fase 3 — Instrumentación mínima y pilotos (Días 31–60)

| Fecha objetivo | Entregable | Resultado esperado |
|---|---|---|
| Día 35 | `SubSOP_Template_Maestro_v1.0.md` | Plantilla única obligatoria |
| Día 40 | `Registro_Canonico_SubSOPs_v1.0.md` | Estado de dominios visible |
| Día 45 | `capabilities/api_registry.yaml` | Inventario gobernado de conectores |
| Día 50 | Sub-SOP piloto 1: Automatización | Dominio real bajo canon nuevo |
| Día 55 | Sub-SOP piloto 2: Investigación Estratégica / OSINT | Segundo dominio bajo prueba |
| Día 60 | Validador inicial N3 / workflow equivalente | Primera política ejecutable |

**Criterio de éxito de la fase:** al menos 5 decisiones reales del backlog deben procesarse de extremo a extremo bajo el nuevo flujo y quedar registradas.

### Fase 4 — Runtime mínimo, métricas y auditoría (Días 61–90)

| Fecha objetivo | Entregable | Resultado esperado |
|---|---|---|
| Día 70 | Inyección automática de `truth` + reglas en flujo de trabajo mínimo | Menor dependencia del pegado manual |
| Día 75 | Dashboard mínimo de gobernanza | Métricas semanales visibles |
| Día 80 | Mecanismo inicial de contención / kill-switch técnico | Control real sobre un brazo o flujo piloto |
| Día 85 | Auditoría de uso real | Evidencia de qué reglas sirvieron y cuáles no |
| Día 90 | Informe de poda y consolidación | Reglas no usadas se deprecán o justifican |

### Métricas canónicas del trimestre

Se recomienda comenzar con un set reducido pero suficiente de métricas, evitando sobreinstrumentación prematura.

| Métrica | Definición | Meta inicial |
|---|---|---|
| % de decisiones relevantes con Decision Record completo | Decisiones registradas / decisiones relevantes tomadas | >70% al día 90 |
| % de decisiones críticas con Context Packet válido | Casos críticos con contexto estructurado | >80% al día 90 |
| Contradicciones abiertas > 7 días | Número de conflictos doctrinales sin resolver | Tendencia descendente |
| % de proyectos activos con Sub-SOP mínimo | Cobertura de operación especializada | >60% al día 90 |
| Governance overhead por flujo | Tiempo de gobernanza / tiempo total del flujo | Medir y reducir |
| Ratio API vs GUI fallback | Tareas resueltas vía integración frente a interfaz manual | Tendencia a mayor integración |
| % de automatizaciones con rollback declarado | Flujos con reversibilidad explícita | >80% en pilotos |
| Tasa de inyección automática de reglas | Interacciones con contexto cargado automáticamente | >50% al día 90, con rumbo a 95% |

### Tabla de prioridades ejecutivas

| Prioridad | Decisión |
|---|---|
| P1 | Comprimir el canon y fijar jerarquía |
| P1 | Abrir Governance Operations Log desde el día 1 |
| P1 | Implementar Context Packet y Decision Record |
| P1 | Formalizar 2–3 sub-SOPs reales |
| P2 | Construir validador N3 mínimo |
| P2 | Crear inventario gobernado de conectores |
| P2 | Iniciar runtime / inyección automática de reglas |
| P3 | Expandir métricas, observabilidad y contención avanzada |

---

## 5. Veredictos de los 6 Sabios

| Sabio | Veredicto |
|---|---|
| GPT-5.4 | Deja de expandir el corpus: divide el canon, formaliza el kernel y conviértelo en gobernanza ejecutable medible. |
| Claude Opus 4.6 | El SOP es una constitución brillante que aún no ha sido sometida a juicio real: úsala, mídela y elimina lo que no sobreviva al contacto con la realidad. |
| Gemini 3.1 Pro | Deja de escribir leyes para un fantasma; construye el servidor, inyecta las reglas en código y obliga al sistema a ejecutar bajo gravedad técnica real. |
| Grok 4.20 | Deja de perfeccionar la constitución de un imperio documental y construye de una vez la máquina operativa. |
| Perplexity Sonar | No emitió juicio sustantivo por falta de base externa relevante; su silencio refuerza que esta reestructuración debe fundarse en criterio interno y evidencia operativa propia. |
| DeepSeek R1 | La doctrina ya está completa; ahora debe convertirse en el kernel ejecutable que orquesta y limita activamente a sus propios agentes. |

---

## 6. Conclusión Final

La reestructuración de SOP+EPIA no debe entenderse como una nueva iteración documental, sino como un **cambio de régimen**. El sistema ya no necesita más expansión conceptual; necesita compresión, depuración, formalización y prueba bajo condiciones reales. La conclusión consolidada de los Sabios es inequívoca: el ecosistema ya ganó el derecho a dejar de pensarse como borrador intelectual y empezar a exigirse como sistema operativo.

La arquitectura definitiva propuesta responde a esa necesidad. Reduce el canon a un conjunto jerárquico claro, separa identidad, constitución, operación y ejecución, rescata lo valioso de generaciones previas sin permitir que compitan con el canon vigente, y traslada la ambición de policy-as-code desde la retórica hacia artefactos concretos: schemas, registros, reglas legibles por máquina, inventarios gobernados, logs y validadores.

El criterio rector de los próximos 90 días será simple: **todo lo importante debe poder leerse, ejecutarse, registrarse y auditarse**. Lo que no pueda hacer esas cuatro cosas pertenece al histórico, no al núcleo vivo del sistema.

En consecuencia, la prioridad institucional inmediata es esta:

1. **Partir el canon actual y fijar autoridad documental.**
2. **Abrir el registro real de gobernanza desde el primer día.**
3. **Formalizar el kernel mínimo y la memoria soberana mínima.**
4. **Poner en operación sub-SOPs piloto con evidencia real.**
5. **Medir fricción, uso, contradicción y ejecutabilidad.**
6. **Podar sin sentimentalismo todo lo que no aporte valor comprobable.**

El destino correcto de SOP+EPIA no es ser una biblioteca admirable. Es convertirse en una **gobernanza viva, ejecutable y verificable**, capaz de limitar, coordinar y mejorar sistemas inteligentes sin depender exclusivamente de memoria humana, disciplina manual o brillantez contextual momentánea.

**Veredicto final de reestructuración:** el canon se comprime, el kernel se formaliza, la operación se registra y la máquina empieza, por fin, a existir.