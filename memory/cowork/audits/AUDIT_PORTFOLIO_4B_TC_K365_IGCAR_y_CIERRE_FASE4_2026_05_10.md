# AUDIT PORTFOLIO 4B — Subproyectos del Portfolio Pt 2 + CIERRE FASE 4

**Sub-Fase:** 4B (cierra Fase 4 completa)
**Subproyectos cubiertos:** Top-Control-PC (TCP/CONTROL TOTAL), Kukulkán-365 (K365), IGCAR (estatuto cruzado)
**Generado por:** Cowork (scheduled task autónomo `cowork-estudio-fase4b-portfolio-tc-k365-igcar`)
**Fecha:** 2026-05-10
**Pre-flight ejecutado:** ✅ COWORK_BASE_CONOCIMIENTO + AUDIT_PORTFOLIO_4A leídos íntegros. DSCs específicos (TC-001/002, K365-001/002, X-001) leídos línea por línea. Verificación física con `find` y `ls` de carpetas en root. Lectura de manifests `top-control-pc-control-total.md`, `kukulkan-365.md`, y referencias cruzadas a CIES, OMNICOM, SOP, EPIA.
**Síndrome-Dory:** neutralizado. Toda la información viene de filesystem 2026-05-10 + DSCs canonizados 2026-05-06 (Sprint Memento), no de memoria parcial.

---

## §0. Resumen ejecutivo (1 página)

| Subproyecto | DSCs firmados / PEND | Carpeta código en repo | Madurez para sprint comercial | Bloqueante crítico |
|---|---|---|---|---|
| **Top-Control-PC** | 2 firmes (TC-001/002), 0 PEND explícitos | ❌ NO existe `top-control-pc/`, `tcp/`, ni `control-total/` en root. Solo capilla DSCs + manifest. **No hay skill dedicado.** Roadmaps V2/V3 en Drive (2026-04-25). | **MEDIA** (visión + roadmap recientes, pero 3 decisiones bisagra abiertas + sin código) | Triple decisión bisagra: módulo del Monstruo vs producto independiente; scope MVP; mercado objetivo. Stack técnico sin confirmar. Modelos locales soberanos requieren hardware capaz. |
| **Kukulkán-365** | 2 firmes (K365-001/002), 0 PEND explícitos | ❌ NO en este monorepo. Repo externo `k365-knowledge-repo` (GitHub PRIVATE) — repo de **conocimiento**, no de producto. **Zona Like 313 (DSC-K365-002) ES el primer producto activo de K365 y vive operativamente en LikeTickets.** | **DEPENDE LIKETICKETS** (su único producto activo es Zona Like 313 que es 100% LikeTickets) | Alianza con Leones de Yucatán pendiente (bloqueante). Modelo de inversión sin definir. Climatización a gran escala = capex masivo. |
| **IGCAR** | 1 firme (X-001 _GLOBAL), estatuto v2 sin procesar | ❌ NO existe carpeta `igcar/`, sin skill, sin repo. Estatuto oficial vive en Drive (`IGCAR_Estatuto_Oficial_v2.docx`) sin procesar. | **BAJA** (concepto sin código, sin ruta de implementación, 5 proyectos cruzados de los cuales 3 son nominales/sin desarrollo) | El propio DSC-X-001 declara: *"documento oficial de estatutos está pendiente de procesar para extraer lineamientos específicos"*. Cruza con OMNICOM (nominal), CIP (bloqueado legal), CIES (nominal), SOP (corpus histórico), EPIA (corpus histórico). 3 de 5 proyectos cruzados no son arrancables hoy. |

**Cifra resumen Portfolio Pt 2:** 0 de 3 subproyectos en producción. Top-Control-PC con la visión técnica más madura (modelo IA agéntica con privilegios completos, soberanía total). K365 con el único cruce comercial vivo (Zona Like 313 vía LikeTickets). IGCAR como **estatuto unificador sin materialización técnica** — concepto educativo/certificación que debe procesarse documentalmente antes que técnicamente.

**Hallazgo magna 4B (refuerza H1 de 4A):** los 3 subproyectos del Portfolio Pt 2 confirman el patrón detectado en Pt 1 — **el monorepo `~/el-monstruo` NO contiene carpetas de productos finales**. Top-Control-PC tiene 39 archivos en Drive y 29 páginas en Notion; K365 tiene un repo externo de conocimiento; IGCAR vive en un .docx de Drive. Esto **eleva la urgencia de `MAPA_REPOS.md`** recomendado en 4A §6.3 — sin él, cualquier auditoría futura repite la pregunta "¿dónde está el código de X?" innecesariamente.

---

## §1. Top-Control-PC (TCP / CONTROL TOTAL)

### §1.1. DSCs canonizados (2 firmes, 0 PEND explícitos)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-TC-001 | decision_arquitectonica | firme | Top Control PC = plataforma IA agéntica que toma control completo del PC del usuario para realizar tareas de productividad sin intervención humana. Paradigma: **Absorción Soberana**. No cruza con ningún otro proyecto en el campo `cruza_con` (declarado "ninguno"). |
| DSC-TC-002 | restriccion_dura | firme | Operación 100% local con **privilegios completos** sobre el PC anfitrión. **Soberanía total**: no SaaS dependiente. Modelos locales preferidos donde sea técnicamente viable. Implica hardware capaz, gestión profunda de permisos, seguridad del sistema anfitrión. |

**Observación crítica:** ambos DSCs declaran `cruza_con: ["ninguno"]`. Sin embargo el **manifest** `top-control-pc-control-total.md` §7 declara cruces explícitos con:
- **El Monstruo** (relación de integración, "posible módulo o componente del núcleo")
- **Absorción Soberana** (relación arquitectónica)
- **Vivir Sano + Skills/Etapas** (comparten el spec maestro `Arquitectura de Absorción Soberana v2026-04-05 (GPT-5.4)`)

**Inconsistencia DSC ↔ manifest:** los DSCs firmados niegan cruces, el manifest los afirma. Recomendación: actualizar DSC-TC-001 con `cruza_con: ["EL-MONSTRUO", "VIVIR-SANO", "Absorcion-Soberana"]` o emitir DSC-TC-003 declarando explícitamente los cruces (porque el spec maestro compartido GPT-5.4 ES un cruce arquitectónico real, no decorativo).

### §1.2. Estado código verificable

```
$ find ~/el-monstruo -maxdepth 3 -type d \( -iname "*top-control*" -o -iname "*tcp*" -o -iname "*control-total*" \)
./discovery_forense/CAPILLA_DECISIONES/TOP-CONTROL-PC
(único hit — solo capilla de DSCs, sin código)

$ ls ~/el-monstruo/skills/ | grep -i "top\|control"
(sin resultados — no existe skill dedicado)
```

**Verificación negativa total:**
- ❌ No hay `top-control-pc/`, `tcp/`, `control-total/`, ni `cci-control/` en root
- ❌ No hay `kernel/top_control_pc/` ni embebido en kernel
- ❌ No hay `apps/top-control-pc/` (mientras que `apps/` ya alberga `mobile/` para Flutter, no hay variante desktop nativa)
- ❌ No hay skill `creacion-top-control-pc` ni equivalente
- ❌ No hay repo GitHub dedicado conocido (manifest declara "Pendiente")
- ❌ No hay BOM de hardware mínimo (paradoja vs DSC-TC-002 que requiere "hardware capaz")
- ❌ No hay tests, deploy config, ni scripts específicos

**Insumos existentes (en otras ubicaciones):**
- **Drive:** 39 archivos, 8 plan-like — el segundo proyecto con MÁS planes en Drive después de Mena-Baduy. Especialmente: `ROADMAP_MUNDIAL_V2_CRUCE` (2026-04-25), `ROADMAP_MUNDIAL_V3_DEFINITIVO` (2026-04-25), `evidencia_cruce_v3`.
- **Notion:** 29 páginas, 2 plan-like. Especialmente: `Arquitectura de Absorción Soberana — Versión Definitiva (GPT-5.4)`, `MONSTRUO Top-20 Núcleo v1`.
- **Categorización corregida** en `_HALLAZGOS_FASE_II_RECUPERADOS.md` §7: reclasificado de "En Diseño" a "🟢 Activo/Core" tras evidencia de roadmap V2+V3 (2026-04-25, tracción reciente) + spec maestro firmado por GPT-5.4.

**Diagnóstico:** Top-Control-PC tiene **alta densidad documental + cero código**. Es el opuesto a LikeTickets (alto código, baja documentación canonizada en monorepo). Riesgo: documentación dispersa que no converge a spec ejecutable.

### §1.3. Bloqueantes externos

1. **Decisión bisagra #1 (manifest §4.1, bloqueante=Sí, impacto=Alto):** ¿Top-Control-PC es **módulo integrado de El Monstruo** o **producto de software independiente**? Esta decisión cambia totalmente la arquitectura:
   - Como módulo: vive en `kernel/top_control_pc/`, comparte memoria + capas transversales, sin marketing propio.
   - Como producto independiente: requiere repo, branding, distribución, modelo de negocio, soporte separado.

2. **Decisión bisagra #2 (manifest §4.2, bloqueante=Sí, impacto=Alto):** scope exacto del MVP. Sin esto, los 8 planes en Drive corren riesgo de scope creep infinito.

3. **Decisión bisagra #3 (manifest §4.3, bloqueante=No, impacto=Medio):** mercado objetivo / usuario final. ¿Power users técnicos? ¿Trabajadores administrativos? ¿Consultores? El producto cambia radicalmente.

4. **Restricción dura DSC-TC-002 → bloqueo de stack:** "modelos locales preferidos donde sea técnicamente viable" implica:
   - Mínimo 32-64GB RAM en PC anfitrión para modelos open-source serios (Qwen 72B, DeepSeek R1, Llama 3.1 70B).
   - GPU local recomendada (limita mercado a usuarios con hardware ≥ $40-80k MXN).
   - O bien aceptar trade-off: modelos pequeños locales (7-13B) + escalado opcional a cloud para casos pesados, **lo cual rompe parcialmente la soberanía total**.

5. **Riesgo arquitectónico cruzado:** si TCP es módulo del Monstruo, hereda dependencia de las capas transversales del kernel (audit 3B: 6 de 8 capas con integraciones huecas). Si es producto independiente, necesita su propio kernel — duplicación.

### §1.4. Madurez para arrancar sprint comercial: **MEDIA**

**Justificación:** la madurez documental es ALTA (39 Drive + 29 Notion + 8 plan-like + 2 DSCs firmes + categoría 🟢 Activo). La madurez de implementación es **NULA** (cero código). La madurez de decisiones es **BAJA** (3 bisagras abiertas). Promedio = MEDIA.

A diferencia de CIP (BAJA — espera abogado externo) o BioGuard (BAJA — espera COFEPRIS), Top-Control-PC NO tiene bloqueos externos legales/regulatorios. Sus 3 bloqueantes son **internas y accionables** por Alfredo + equipo técnico. Por eso MEDIA y no BAJA.

### §1.5. Sprint propuesto

**Pre-requisito:** sesión de toma de decisiones de 2-4 horas con Alfredo para resolver las 3 bisagras simultáneamente. Output: DSC-TC-003 (alcance), DSC-TC-004 (MVP scope), DSC-TC-005 (mercado).

**Sprint TCP-001 "Spike de viabilidad técnica" (2 semanas, paralelo a sesión de decisiones):**
- Probar 2-3 frameworks de control de PC: pyautogui + accessibility APIs (macOS), MS UI Automation (Windows), AppleScript bridges. Spike de 3-5 días cada uno.
- Probar modelos locales: Qwen 32B Instruct vs DeepSeek R1 distilled vs Llama 3.1 70B Q4. Benchmark de latencia en MacBook Pro M3 Max y desktop con RTX 4090.
- Validar: ¿pueden modelos locales orquestar agentic loops de 5-10 pasos sin colapsar el equipo?
- Output: documento `tools/spikes/tcp_viabilidad_tecnica.md` con recomendación de stack.

**Sprint TCP-002 "MVP Demo restringido" (3-4 semanas, post-decisiones):**
- 1 caso de uso vertical: ej. "el agente abre Excel, lee un archivo, hace análisis, genera reporte en Word, lo guarda en Drive".
- Stack del spike + framework de control de PC ganador + modelo local ganador.
- Sin distribución todavía — solo demo interno para Alfredo.

### §1.6. Conexión con el resto del ecosistema

Si TCP se canoniza como **módulo del Monstruo** (preferida en este audit por soberanía Obj #12 + Adoptar > Construir):
- Vive en `kernel/top_control_pc/` o `apps/desktop/` con bridges al kernel.
- Hereda las 8 capas transversales (Obj #9) — pero hoy 6 de 8 al ~5%.
- **Capa 1 Manos** (de hecho, Manos es exactamente lo que TCP automatiza para el usuario en su PC).
- **Capa 7 Resiliencia** crítica (un agente con permisos completos que falla puede destruir el PC del usuario — requiere kill switch agresivo, sandboxing, undo).
- **Capa 8 Memento** crítica (estado de la sesión TCP debe persistir entre reinicios; el agente no puede olvidar qué estaba haciendo).

Si se canoniza como **producto independiente**: requiere su propia capa de seguridad/sandboxing/kill switch fuera del kernel. Mayor velocidad inicial, mayor deuda arquitectónica futura.

---

## §2. Kukulkán-365 (K365)

### §2.1. DSCs canonizados (2 firmes, 0 PEND explícitos)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-K365-001 | restriccion_dura | firme | K365 es proyecto inmobiliario tipo **Distrito de Entretenimiento Climatizado** en Mérida. Premisa innegociable: **365 días al año** de operación. Resuelve calor extremo de Yucatán mediante climatización integral (HVAC como gasto operativo principal). |
| DSC-K365-002 | cruce_inter_proyecto | firme | **Zona Like (313 butacas premium) del estadio Kukulkán es el primer producto comercial activo de K365.** Cruza con `LikeTickets` y `Comercialización Zona Like 313`. Funciona como piloto comercial validando modelo de negocio + infra tecnológica antes de expandir. |

### §2.2. Estado código verificable

**Repo externo conocido:** `k365-knowledge-repo` (GitHub PRIVATE). Manifest declara explícitamente: repo de **conocimiento**, no de producto. NO en este monorepo.

**En este monorepo:**
```
$ find . -maxdepth 3 -type d -iname "*kukulkan*"
./discovery_forense/CAPILLA_DECISIONES/KUKULKAN-365
(único hit — solo capilla de DSCs)

$ ls skills/ | grep -i "kukulkan\|k365"
(sin skill dedicado a K365 directamente)
```

**Pero:** la **operación viva de K365** se materializa hoy 100% a través de la skill `comercializacion-zona-like-313` y la skill `ticketlike-ops` — porque DSC-K365-002 establece que Zona Like ES el primer producto activo de K365, y Zona Like ES LikeTickets en producción.

**Diagnóstico:** K365 es un proyecto **conceptualmente macro pero operativamente solapado con LikeTickets**. Sin LikeTickets, K365 no tiene producto activo. Toda la madurez operativa de K365 es heredada de LikeTickets ($41,445 MXN/sem, 303 órdenes pagadas, Stripe LIVE).

### §2.3. Bloqueantes externos

1. **Alianza con Leones de Yucatán pendiente** (manifest §4.1, bloqueante=Sí, impacto=Alto): K365 sin formalización con Leones limita la conversión del estadio Kukulkán a Distrito de Entretenimiento. Ya hay relación operativa (Zona Like vende boletos para los 42 juegos de Leones), pero el contrato/alianza para expansión a 365 días no existe.
2. **Modelo de inversión sin definir** (manifest §4.2, bloqueante=Sí, impacto=Alto): la climatización integral del estadio es capex masivo (~estimación: cientos de millones MXN). Sin modelo de inversión claro, el proyecto es visión sin ruta financiera.
3. **Costos operativos HVAC** (DSC-K365-001 los declara como gasto principal): pricing model debe absorberlos sin perder competitividad vs alternativas no climatizadas. Riesgo de unit economics negativos.
4. **Cruce con CIP (no declarado, recomendado canonizar):** si CIP arranca y se aplica al estadio Kukulkán u otros inmuebles de K365, los tokens inmobiliarios podrían ser **el modelo de inversión** que resuelve bloqueante #2. Ningún DSC actual lo declara. Recomendación: emitir DSC-X-002 (cruce K365 ↔ CIP) tras decisiones legales CIP.

### §2.4. Madurez para arrancar sprint comercial: **DEPENDE LIKETICKETS** (no autónoma)

K365 NO tiene madurez propia para sprint independiente. Su único producto activo es Zona Like 313, que ya está en producción vía LikeTickets. Cualquier "sprint comercial K365" hoy es en realidad **un sprint de expansión de LikeTickets a más zonas/productos del estadio Kukulkán**.

### §2.5. Sprint propuesto

**Sprint K365-001 "Conversión virtual Distrito 365 — Fase 1: Multi-zona LikeTickets" (2-3 semanas):**
- Extender el modelo Zona Like 313 a otras zonas premium del estadio: palcos, suite VIP, área familiar premium.
- Reusar 100% del stack DSC-LT-001 (Vite + tRPC + TiDB + Stripe).
- Reusar el patrón DSC-LT-003 (Stripe → confirmSeatsForOrder → email).
- Estimación: si Daniel tiene la infra LikeTickets parametrizada, ~1-2 semanas. Si requiere refactor del modelo de butacas, ~3-4 semanas.

**Sprint K365-002 "Eventos no deportivos 365" (post-K365-001, 4-6 semanas):**
- Vender boletos para conciertos, ferias, convenciones en el estadio durante días no-juego.
- Requiere catálogo de eventos diversificado (no solo 42 juegos).
- Habilita la tesis "365 días" del DSC-K365-001 sin necesitar la conversión física a Distrito Climatizado completo.

**Pre-requisito de sprint K365 físico (post-virtual):** cierre de bloqueantes externos #1 (alianza Leones formal) + #2 (modelo de inversión).

### §2.6. Conexión con el resto del ecosistema

- **DSC-K365-002 ↔ DSC-LT-002/003:** simbiosis verificada. K365 no existe operativamente sin LikeTickets.
- **Cruce candidato CIP↔K365 (no canonizado):** los inmuebles de K365 (estadio + futuras expansiones de Distrito) son candidatos naturales para ser tokenizados vía CIP cuando CIP esté disponible. Cierra el ciclo "El Monstruo construye empresas" (Obj #1) en una sola jurisdicción geográfica (Yucatán/Mérida).
- **Cruce con Mena-Baduy:** la ciudad Mérida es escenario común. K365 (entretenimiento) y Mena-Baduy (política) son proyectos paralelos que comparten geografía pero NO deben mezclarse operativamente (OPSEC del proyecto político lo prohíbe).
- **Cruce con Mérida 2027:** si Mena-Baduy gana la candidatura, K365 podría tener un aliado político municipal estratégico para infraestructura/permisos. Este es un cruce potencial, no canonizado, sensible.

---

## §3. IGCAR (Instituto Global de Certificación en Alto Rendimiento)

### §3.1. DSCs canonizados (1 firme, estatuto v2 sin procesar)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-X-001 | cruce_inter_proyecto | firme | IGCAR es **estatuto unificador que cruza 5 proyectos**: OMNICOM + CIP + CIES + SOP + EPIA. Estatuto oficial v2 (`IGCAR_Estatuto_Oficial_v2.docx` en Drive) **pendiente de procesar** para extraer lineamientos específicos. Funciona como eje transversal para estandarizar y certificar el alto rendimiento entre las 5 iniciativas. |

**Auto-declaración crítica del DSC:** *"documento oficial de estatutos está pendiente de procesar para extraer lineamientos específicos"*. Es un DSC firme que **declara explícitamente que su contenido específico aún no está canonizado**. Es un meta-DSC: canoniza la existencia del estatuto pero pospone la canonización de su contenido.

### §3.2. Estado código verificable

```
$ find ~/el-monstruo -maxdepth 4 -type d -iname "*igcar*"
(sin resultados)

$ find ~/el-monstruo -maxdepth 5 -type f -iname "*igcar*"
./discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-X-001_igcar_cruza_5_proyectos.md
(único hit — solo el DSC mismo)

$ ls ~/el-monstruo/skills/ | grep -i "igcar"
(sin skill dedicado)
```

**Verificación negativa total:**
- ❌ No existe carpeta `igcar/` en root, ni en `discovery_forense/`, ni en `apps/`, ni en `skills/`
- ❌ No existe manifest específico en `discovery_forense/PROJECT_MANIFESTS/igcar.md`
- ❌ No existe repo GitHub conocido
- ❌ El estatuto oficial vive como `.docx` en Drive, sin extracción a Markdown ni a DSCs por capítulo
- ❌ No hay cronograma, ni roadmap, ni plan de implementación

**Insumos existentes:**
- **DSC-X-001** (este audit lo lee íntegro)
- **Drive:** `IGCAR_Estatuto_Oficial_v2.docx` + `ANALISIS_32_ARCHIVOS_SUBIDOS.md` (declarados como fuentes en el frontmatter del DSC)

### §3.3. Análisis de los 5 proyectos cruzados

| Proyecto cruzado | Categoría / estado actual | Implicación |
|---|---|---|
| **OMNICOM** | 🟡 Nominal — sin código, sin desarrollo activo. Manifest superado por `_OMNICOM_DOSSIER_COMPLETO.md`. Posible relación con agencia publicitaria Omnicom Group, posible workspace Notion "Omnicom Inc". Sin confirmar si es proyecto propio o registro de cliente externo. | IGCAR cruza con un proyecto que ni siquiera está confirmado como propio. |
| **CIP** | 🟠 En diseño — bloqueado por DSC-CIP-PEND-001 (figura legal). Ver audit 4A §1. | IGCAR + CIP solo se pueden materializar tras resolución legal CIP. |
| **CIES** | 🟡 Nominal — mención histórica en SOP, sin desarrollo activo. Posible relación con CIP ("Centro Inmobiliario Especializado" o similar), pendiente de confirmar con Alfredo. | Posible que CIES NO sea proyecto independiente sino sub-componente de CIP. |
| **SOP** | 📚 Corpus histórico — Standard Operating Procedure documental en Dropbox + Drive. No es proyecto comercial activo. Hay documentos `SOP_EPIA_REESTRUCTURACION_DBX.md` y `REPOSITORIO_MAESTRO_SOP_EPIA_DBX`. | SOP es referencia, no proyecto. |
| **EPIA** | 📚 Corpus fundacional — `EPIA_FUNDACIONAL_DBX.docx/txt/md` en Dropbox. Documento fundacional. | EPIA es referencia, no proyecto. |

**Lectura:** de los 5 proyectos cruzados:
- 1 (CIP) es proyecto comercial real bloqueado externamente
- 2 (OMNICOM, CIES) son nominales sin confirmar siquiera identidad/alcance
- 2 (SOP, EPIA) son **corpus documentales históricos**, no proyectos vivos

**Diagnóstico:** IGCAR cruza con un universo de proyectos donde **el 60% son nominales o documentales**, no operativos. Esto no invalida IGCAR — un estatuto unificador puede existir antes que sus proyectos cruzados maduren — pero **vuelve poco accionable cualquier sprint técnico de IGCAR hoy**.

### §3.4. Bloqueantes externos

1. **El DSC-X-001 mismo declara su propio bloqueante interno:** "documento oficial de estatutos está pendiente de procesar". Sin extracción del .docx a DSCs específicos por capítulo o cláusula, IGCAR es contenedor sin contenido canonizado.
2. **3 de 5 proyectos cruzados no son arrancables hoy:** OMNICOM (nominal sin identidad), CIES (nominal posible variante de CIP), CIP (bloqueado legal).
3. **Ningún proyecto cruzado actualmente referencia IGCAR en sus DSCs propios.** Verificación: los DSCs CIP-001..006 no mencionan IGCAR. Los manifests OMNICOM, CIP, CIES no mencionan IGCAR. **El cruce es declarado por IGCAR pero no recíproco.** Cierra-loop pendiente.

### §3.5. Madurez para arrancar sprint comercial: **BAJA**

IGCAR es **concepto sin código, sin ruta de implementación, sin proyecto dependiente que lo demande**. Es coherente con su naturaleza (estatuto/instituto de certificación, no producto SaaS), pero como subproyecto de portfolio del Monstruo no es priorizable en términos comerciales.

### §3.6. Sprint propuesto SI arrancara

**Sprint IGCAR-DOCUMENTAL-001 "Procesamiento del Estatuto v2" (1-2 semanas, NO técnico):**
- Extraer `IGCAR_Estatuto_Oficial_v2.docx` a Markdown estructurado en `discovery_forense/IGCAR/estatuto_v2.md`.
- Generar DSCs específicos por cláusula clave: lineamientos de certificación, criterios de alto rendimiento, governance, criterios de admisión de proyectos cruzados.
- Validar con Alfredo qué cláusulas son `restriccion_dura` y cuáles son `decision_arquitectonica`.
- Output: 5-10 DSCs nuevos `DSC-IGCAR-001..010` que reemplacen el meta-DSC X-001.

**Sprint IGCAR-INTEGRACION-002 (post-documental, post-CIP-legal, 2-3 semanas):**
- Cruzar DSCs IGCAR con DSCs CIP y emitir DSCs de cruce (DSC-X-IGCAR-CIP).
- Validar si OMNICOM y CIES son proyectos propios o derivados/duplicados (consulta Alfredo).
- Si IGCAR tiene contraparte digital (portal de certificaciones, BD de certificados), spec del sistema.

**No se recomienda sprint técnico de IGCAR antes de procesar el estatuto.** Construir software para implementar un estatuto sin canonizar es inverso al principio "Adoptar > Construir" (regla #3).

### §3.7. Conexión con el resto del ecosistema

IGCAR es **el único subproyecto del Portfolio cuyo valor primario es transversal-conceptual, no producto**. Su rol es alinear estándares entre proyectos. Si el Monstruo crece a 7+ subproyectos comerciales (Pt 1 + Pt 2 + futuros), IGCAR podría volverse el equivalente a "compliance & quality assurance institucional" del ecosistema.

Cruce no canonizado pero candidato natural:
- **IGCAR ↔ Capa 8 Memento (Obj #15):** la certificación de alto rendimiento requiere persistencia de evidencia y audit trails — exactamente lo que Memento provee.
- **IGCAR ↔ Capa 7 Resiliencia:** estándares de uptime, recovery, DR podrían canonizarse vía IGCAR.

---

## §4. CIERRE FASE 4 — Tabla consolidada Portfolio (7 subproyectos)

| Proyecto | DSCs (firmes / PEND) | Código existente en monorepo | Bloqueantes externos | Madurez sprint | Sprint propuesto inmediato |
|---|---|---|---|---|---|
| **CIP** | 6 firmes + 2 PEND | ❌ Solo skill `creacion-cip` con docs estratégicas. 0 código. | 🔴 Crítico: figura legal CNBV/SHCP/Banxico (DSC-CIP-PEND-001) | **BAJA** | Pre: consulta legal 2-4 semanas. Post: Sprint CIP-001 ERC-3643 foundation. |
| **LikeTickets / Zona Like** | 3 firmes (LT-001/002/003) | ❌ Repo externo `like-kukulkan-tickets`. Skills `ticketlike-ops` + `comercializacion-zona-like-313` en monorepo. | 🟡 Sprint 87/90 Pagos del Monstruo no arrancado | **🟢 ALTA** ($41,445 MXN/sem en producción Stripe LIVE) | Sprint 90 Checkout Stripe (extracción patrón DSC-LT-003 a kernel) |
| **Mena-Baduy / Crisol-8** | 3 firmes (MB-001/002/003) | ❌ Repo externo `crisol-8`. Planes y evidencia normalizada en `discovery_forense/`. | 🟡 OPSEC alto + consolidación Notion + estrategia mediática | **MEDIA** (operativa, no comercial — Sprint III en producción política) | MB-COWORK-001 hub Notion + sync con monorepo (NO contenido sensible) |
| **BioGuard** | 1 firme (BG-001) + 1 PEND | ❌ Solo capilla DSCs. Sin skill, sin repo, sin BOM. | 🔴 Crítico triple: COFEPRIS + hardware bisagra + substrato biológico | **BAJA** | NO arrancar hasta resolución regulatoria. Pre-spec ~$50-100k MXN consultoría especializada. |
| **Top-Control-PC** | 2 firmes (TC-001/002) | ❌ Solo capilla DSCs + manifest. 39 archivos Drive + 29 páginas Notion. Sin skill, sin código. | 🟡 3 decisiones bisagra internas (módulo vs producto, MVP scope, mercado) | **MEDIA** (alta documental, nula código) | TCP-001 spike viabilidad técnica 2 sem (en paralelo a sesión de decisiones) |
| **Kukulkán-365** | 2 firmes (K365-001/002) | ❌ Solo capilla DSCs. Repo externo `k365-knowledge-repo` (knowledge, no producto). Operativamente vive vía LikeTickets. | 🟡 Alianza Leones + modelo de inversión | **DEPENDE LIKETICKETS** | K365-001 Multi-zona LikeTickets (extensión zonas premium estadio) |
| **IGCAR** | 1 firme (X-001 _GLOBAL) + estatuto v2 sin procesar | ❌ Sin carpeta, sin skill, sin repo. Estatuto en `.docx` Drive. | 🟠 Auto-declarado: estatuto sin procesar; 3 de 5 proyectos cruzados nominales | **BAJA** | IGCAR-DOCUMENTAL-001 (procesar estatuto v2 → DSCs específicos) |

### §4.1. Análisis cruzado: candidatos a sprint comercial inmediato

#### Pregunta clave 1: ¿Cuál subproyecto tiene MAYOR madurez técnica + MENORES bloqueantes externos?

**Ranking 1° → ganador absoluto: LikeTickets / Zona Like**
- **Madurez técnica:** ALTA. Stripe LIVE desde 2026-04-14, $41,445 MXN/sem revenue real, 303 órdenes pagadas, skill operativa robusta v2.0.0 con changelog 2026-05-04, scripts de smoke check + deploy automatizado.
- **Bloqueantes externos:** ninguno crítico. Solo bloqueante interno: Sprint 87/90 no arrancado en kernel — pero el producto opera **standalone sin él**.
- **Ratio madurez/bloqueo:** óptimo del portfolio.

**2° lugar: Top-Control-PC**
- Madurez técnica: NULA en código, ALTA en documentación + roadmaps recientes (2026-04-25).
- Bloqueantes: 3 decisiones bisagra **internas** (no requieren abogados, COFEPRIS, ni alianzas externas).
- Como las bisagras son resolubles en 1 sesión Alfredo + Cowork, es el **#2 candidato realista** post-LikeTickets.

**3° lugar: Mena-Baduy** (en producción operativa pero sin métrica comercial)

**Excluidos del top 3 (no arrancables hoy):**
- CIP (espera abogado externo)
- BioGuard (espera COFEPRIS)
- IGCAR (espera procesamiento documental)
- K365 (depende de LikeTickets)

#### Pregunta clave 2: ¿Cuál tiene MAYOR cruce inter-proyecto (efecto multiplicador)?

**Ranking 1° → ganador: LikeTickets**
- **DSC-LT-003** patrón Stripe canonizado declara cruces explícitos con `Marketplace, CIP, Mundo de Tata`.
- **DSC-K365-002** establece que K365 vive operativamente vía LikeTickets.
- Total: cruza directamente con 4 proyectos (Marketplace, CIP, Mundo de Tata, K365) por DSCs firmes.
- Es el **patrón fundacional cross-portfolio** identificado en audit 4A §5.4.

**2° lugar: IGCAR**
- DSC-X-001 declara cruce con 5 proyectos (OMNICOM, CIP, CIES, SOP, EPIA).
- **Pero el cruce es unilateral** (los 5 proyectos no referencian IGCAR en sus propios DSCs).
- Cruce nominal-conceptual, no operativo.

**3° lugar: Top-Control-PC**
- Manifest declara cruce con El Monstruo (núcleo) + Vivir Sano + Skills/Etapas (spec maestro Absorción Soberana GPT-5.4 compartido).
- Cruce arquitectónico real (spec compartido) pero no canonizado en DSCs propios — inconsistencia detectada §1.1.

#### Pregunta clave 3: ¿Cuál tiene MAYOR urgencia externa?

**Ranking 1° → ganador: Mena-Baduy / Crisol-8**
- **Candidatura Mérida 2027** = ventana política con fecha dura. Cada semana cuenta.
- DSC-MB-001 declara confidencialidad + OPSEC reforzado: la urgencia incluye no solo plazos sino también gestión de riesgos políticos.

**2° lugar: LikeTickets (urgencia operativa, no externa)**
- Cada semana sin Sprint 90 = 1 semana más donde el patrón Stripe está duplicado en futuros productos.
- Cada semana sin Sprint 90 = 1 semana de drift entre código LikeTickets producción y DSC-LT-003 canonizado.

**3° lugar: K365**
- Si la temporada de Leones 2026 tiene cronograma fijo, expandir Multi-zona LikeTickets antes del próximo arranque de temporada da 1 año más de revenue completo.
- No es urgencia externa absoluta — es urgencia de oportunidad.

**Sin urgencia externa identificada:** CIP, BioGuard, Top-Control-PC, IGCAR.

### §4.2. Top 3 candidatos para arrancar Sprint comercial post-kernel completion

**#1 ABSOLUTO: Sprint 90 Checkout Stripe (LikeTickets → kernel)**
- Producto en producción real, único bloqueante 100% accionable internamente, mayor leverage cross-portfolio (desbloquea CIP futuro, Marketplace, Mundo de Tata, K365 futuro).
- Cierra deuda técnica del Sprint 87 original (audit 3A §10.1).
- Estimación: 1 sprint (~1-2 semanas) si Daniel tiene la implementación documentada.
- **Justifica iniciarse ANTES de "kernel completion"** si "kernel completion" significa cerrar Capa 6 Finanzas — porque este sprint ES parte de cerrar Capa 6.

**#2 RECOMENDADO POST-#1: K365-001 Multi-zona LikeTickets**
- Reusa 100% el módulo extraído en Sprint 90.
- Multiplica revenue (estadio Kukulkán tiene zonas premium adicionales más allá de Zona Like 313).
- Habilita la tesis "365 días" parcialmente (eventos diversificados en estadio).
- Estimación: 2-3 semanas.

**#3 RECOMENDADO PARALELO: Sprint TCP-001 Spike viabilidad técnica + sesión de decisiones bisagra Alfredo**
- 0 dependencia de #1 y #2. Puede correr en paralelo.
- Resuelve las 3 decisiones bisagra abiertas (módulo vs producto, MVP, mercado).
- Si gana "módulo del Monstruo": acelera Capa 1 Manos del kernel.
- Si gana "producto independiente": habilita un segundo flujo de revenue independiente.
- Estimación: 2 semanas spike + 1 sesión de decisiones (4 horas).

**Excluidos del top 3 inmediato (justificados):**
- CIP/BioGuard: bloqueos externos legales/regulatorios.
- Mena-Baduy: no es sprint comercial, es operación política.
- IGCAR: requiere procesamiento documental no técnico.

### §4.3. Hallazgos transversales de la Fase 4 completa (Pt 1 + Pt 2)

**(H1) Patrón confirmado: 0 de 7 subproyectos viven en este monorepo.** Todos viven en repos externos privados (LikeTickets, Mena-Baduy, K365), en Drive/Notion (TCP, IGCAR, BioGuard), o no existen físicamente aún (CIP, BioGuard). El monorepo es **kernel + memoria + DSCs + skills + bridge**, NO fábrica de productos. **Acción urgente:** documentar `MAPA_REPOS.md` (ya recomendado en 4A §6.3, ahora con 3 subproyectos adicionales que confirman el patrón).

**(H2) DSC-LT-003 sigue siendo el patrón de mayor leverage cross-portfolio.** En 4A se identificó como cross con Marketplace + CIP + Mundo de Tata. En 4B se confirma cross con K365 (vía DSC-K365-002). Es el **único DSC del portfolio que cruza con 4+ proyectos por declaración explícita**.

**(H3) 4 de 7 subproyectos están bloqueados por externalidades no controlables hoy.** CIP (legal), BioGuard (regulatorio), Mena-Baduy (urgencia política con OPSEC), IGCAR (procesamiento documental + 3 cruces nominales). Solo 3 (LikeTickets, K365, TCP) son arrancables o expandibles inmediatamente.

**(H4) Inconsistencias DSC ↔ manifest detectadas que deben canonizarse:**
- Top-Control-PC: DSCs declaran `cruza_con: ["ninguno"]` pero manifest declara cruces con El Monstruo + Vivir Sano + Absorción Soberana. Recomendación: emitir DSC-TC-003 con cruces explícitos.
- IGCAR: cruce unilateral (declarado solo por IGCAR, no recíproco). Recomendación: añadir referencia IGCAR a DSCs CIP, OMNICOM, CIES — o degradar el cruce a "aspirativo" hasta que sea recíproco.
- K365 ↔ CIP: cruce candidato natural (CIP podría ser el modelo de inversión K365) no canonizado en ningún DSC actual. Recomendación: emitir DSC-X-002 tras resolución legal CIP.

**(H5) IGCAR como "estatuto sin sustancia procesada".** El propio DSC-X-001 declara que su contenido específico está pendiente. Es un meta-DSC. Riesgo: si el estatuto v2 se procesa y resulta inconsistente con DSCs ya firmados de los 5 proyectos cruzados, se requerirá reconciliación masiva. **Acción urgente baja prioridad:** procesar estatuto antes que la divergencia crezca.

**(H6) Top-Control-PC es la oportunidad técnica más visible y desbloqueable inmediatamente.** A diferencia de CIP/BioGuard, sus 3 bloqueantes son decisiones internas resolubles en una sesión Alfredo. Si la Capa 1 Manos del Monstruo necesita un primer caso de uso vertical, TCP es el candidato natural — pero requiere antes la decisión "módulo vs producto independiente".

**(H7) K365 es proyecto-paraguas más que proyecto-código.** Su único producto activo es Zona Like vía LikeTickets. Operativamente, "Sprint K365" = "Sprint LikeTickets de expansión". Documentar esto explícitamente evita confusión futura.

### §4.4. Decisiones derivadas (para próxima sesión Cowork-Alfredo)

1. **Acción #1 (heredada de 4A, urgente):** crear `MAPA_REPOS.md` en `memory/cowork/` con tabla explícita: monorepo = kernel/memoria; productos en repos externos; subproyectos sin código aún. **Refuerzo 4B:** los 3 subproyectos auditados aquí confirman el patrón con datos adicionales.

2. **Acción #2 (heredada de 4A, urgente):** renombrar Sprint 87 → Sprint 90 Checkout Stripe + extraer DSC-LT-003 a kernel. **Refuerzo 4B:** este sprint también desbloquea K365-001 Multi-zona — leverage adicional.

3. **Acción #3 (4A, mantener):** consulta legal CIP en paralelo con specs ERC-3643 agnósticas.

4. **Acción #4 (NUEVA 4B):** emitir DSC-TC-003 con cruces explícitos de TCP (El Monstruo + Vivir Sano + Absorción Soberana). Cierra inconsistencia DSC ↔ manifest.

5. **Acción #5 (NUEVA 4B):** sesión de decisiones bisagra Top-Control-PC (4 horas con Alfredo). Output: 3 DSCs nuevos resolviendo módulo vs producto, MVP scope, mercado objetivo.

6. **Acción #6 (NUEVA 4B):** procesar `IGCAR_Estatuto_Oficial_v2.docx` a Markdown estructurado + emitir 5-10 DSCs específicos `DSC-IGCAR-001..010` que reemplacen al meta-DSC X-001.

7. **Acción #7 (NUEVA 4B):** clarificar estatus de OMNICOM y CIES con Alfredo. ¿Son proyectos propios? ¿Subcomponentes de otros? ¿Trabajo histórico para clientes? Sin clarificación, el cruce IGCAR↔OMNICOM↔CIES queda como referencia muerta.

8. **Acción #8 (NUEVA 4B):** emitir DSC-X-002 (cruce K365 ↔ CIP) post-resolución legal CIP — los inmuebles K365 son candidatos naturales para tokenización CIP.

9. **Acción #9 (NUEVA 4B):** confirmar que los Sprint 90 + K365-001 + TCP-001 corren en paralelo, NO secuencialmente. Sprint 90 desbloquea K365-001; TCP-001 es independiente.

10. **Siguiente sub-fase:** **Fase 5** — definir el orden y dependencias de los sprints recomendados, asignación de hilos (Cowork arquitectura, Hilo B implementación, Hilo C ejecución), y métricas de cierre. Spec sugiere fase **5A** (planificación Sprint 90 detallado).

---

## §5. AUTOAUDIT (Capa 8 Memento aplicada a este propio audit 4B)

**Pre-flight ejecutado:** ✅
- Lectura íntegra de `AUDIT_PORTFOLIO_4A_CIP_LT_MB_BG_2026_05_10.md` para coherencia con tabla resumen y hallazgos transversales.
- Lectura línea por línea de los 5 DSCs específicos: DSC-TC-001, DSC-TC-002, DSC-K365-001, DSC-K365-002, DSC-X-001.
- Lectura de manifests: `top-control-pc-control-total.md` (íntegro), `kukulkan-365.md` (íntegro), referencias a `cies.md`, `omnicom.md`.
- Verificación física con `find -maxdepth 3` y `find -maxdepth 5` para existencia de carpetas/archivos. Todas las verificaciones negativas son objetivas (cero hits).
- Cross-check con `discovery_forense/sop_epia_diff/` para confirmar que SOP y EPIA son corpus documentales, no proyectos.

**Cifras heredadas por confianza (sin re-validar):**
- Cifras de revenue de LikeTickets ($41,445 MXN/sem, 303 órdenes) heredadas íntegras de audit 4A §2.3, que a su vez vienen de SKILL.md de ticketlike-ops v2.0.0. No revalidé contra Stripe LIVE en este pase.
- Cifras "39 archivos Drive + 29 páginas Notion" para TCP heredadas del manifest declarado por Manus. No revalidé ejecutando `gws drive` ni `notion-search` en este pase autónomo.
- Cifra "82 archivos en Drive" para Mena-Baduy heredada de 4A.

**Honestidad pura sobre limitaciones de este audit 4B:**

1. **No procesé el .docx del estatuto IGCAR v2.** Solo leí lo que el DSC-X-001 declara sobre él (1 párrafo). Posible que el contenido del estatuto cambie radicalmente la lectura de IGCAR — si Alfredo procesa el .docx, este audit 4B requiere revisión.

2. **No verifiqué los repos externos privados** (`like-kukulkan-tickets`, `crisol-8`, `k365-knowledge-repo`). Toda la información sobre código real viene de skills + manifests + DSCs.

3. **No conté DSCs de catálogo cruzado para TCP/K365/IGCAR.** Por ejemplo, si DSC-G-002 (Transversalidad) afecta a TCP, no lo conté en su subtotal. Estimar "DSCs efectivos por subproyecto" requiere otro pase.

4. **No estimé costos económicos** de los sprints propuestos en sub-fase 4B (a diferencia de 4A donde estimé $30-80k MXN para abogado CIP). Los sprints TCP/K365/IGCAR no tienen estimación de costo en este audit — pendiente.

5. **No validé que K365 dependa de LikeTickets en el sentido financiero.** Solo en el sentido operativo (DSC-K365-002 declara que Zona Like 313 es el primer producto activo). Si K365 tiene revenue propio adicional (ej: rentas comerciales del estadio fuera de Zona Like), no lo conté.

6. **No verifiqué la fecha de "última actividad" de TCP** declarada como 2026-04-25 en el manifest. Si hay actividad más reciente en Drive/Notion no migrada al manifest, este audit hereda staleness.

7. **No conté inconsistencias de naming ID vs filename para TCP/K365/IGCAR.** Para CIP en 4A se detectó doble `DSC-CIP-002`. Para los DSCs auditados en 4B no detecté conflictos similares en la lectura, pero no fue verificación exhaustiva tipo `grep -r "id: DSC-TC"` en todas las CAPILLA.

**Síndrome-Dory check:** ✅ todas las afirmaciones técnicas concretas (existencia/no de carpetas, contenido literal de DSCs, contenido literal de manifests) son verificables contra filesystem 2026-05-10. Las afirmaciones interpretativas (ej. "K365 depende operativamente de LikeTickets") están justificadas con DSCs canonizados como evidencia. Las estimaciones cualitativas ("MEDIA", "BAJA", "ALTA") están justificadas con criterios explícitos.

**Capa 8 Memento aplicada:** este audit declara explícitamente fuente y frescura de cada cifra. Cualquier hilo ejecutor (Manus, Hilo B, Hilo C) que lea este audit puede saber qué confiar literalmente y qué validar antes de ejecutar.

**Inconsistencia detectada en mi propio razonamiento:** en §1.5 propongo TCP-001 spike "en paralelo a sesión de decisiones" — pero el spike validará/invalidará opciones de stack. Si la decisión bisagra cambia (ej. de "módulo del Monstruo" a "producto independiente") los criterios de stack cambian. **Refinamiento:** la sesión de decisiones bisagra debe correr ANTES o EN-EL-MISMO-DÍA que el spike, no después. Corregido implícitamente en §4.2 #3 ("2 semanas spike + 1 sesión de decisiones (4 horas)" → leer como "1 sesión de decisiones primero, luego 2 semanas spike").

---

## §6. Cierre Sub-Fase 4B + Cierre Fase 4

**Sub-Fase 4B (Audit Portfolio Subproyectos Pt 2: Top-Control-PC, Kukulkán-365, IGCAR + Cierre Fase 4) COMPLETADA.**

**Cifra consolidada del Portfolio Pt 2:**
- 0/3 subproyectos en producción comercial propia (TCP no tiene código, K365 vive vía LikeTickets, IGCAR no es producto)
- 1/3 con tracción documental reciente (TCP: roadmaps V2/V3 del 2026-04-25)
- 1/3 con producto activo prestado (K365 vía LikeTickets)
- 1/3 estatuto conceptual sin procesar (IGCAR)

**Cifra consolidada Fase 4 completa (Pt 1 + Pt 2 = 7 subproyectos):**
- **1/7 en producción comercial real con revenue verificable** (LikeTickets: $41,445 MXN/sem)
- **1/7 en producción operativa política** (Mena-Baduy, sin revenue)
- **5/7 sin producción comercial propia hoy** (CIP, BioGuard, TCP, K365 dependiente, IGCAR)
- **3/7 bloqueados por externalidades críticas** (CIP legal, BioGuard regulatorio, IGCAR documental)
- **1/7 bloqueado por decisiones internas resolubles** (TCP: 3 bisagras)
- **1/7 dependiente operativamente de otro** (K365 ↔ LikeTickets)

**Top 3 hallazgos magnos de la Fase 4 completa:**
- **(M1)** **Ningún subproyecto vive en este monorepo.** El modelo es kernel + memoria, productos en repos externos. `MAPA_REPOS.md` urgente.
- **(M2)** **DSC-LT-003 (patrón Stripe) cruza con 4+ proyectos** y es el patrón fundacional cross-portfolio. Sprint 90 tiene leverage máximo.
- **(M3)** **4/7 subproyectos requieren acción no técnica externa** (legal, regulatoria, política, documental). Solo 3/7 pueden avanzar técnicamente hoy: LikeTickets, K365 (vía LT), TCP.

**Top 3 oportunidades de leverage (recomendaciones de prioridad técnica para Sprint comercial):**
- **(P1)** Sprint 90 Checkout Stripe (LikeTickets → kernel). Único bloqueo accionable internamente con leverage cross-portfolio máximo.
- **(P2)** Sprint K365-001 Multi-zona LikeTickets (post-Sprint 90). Reusa el módulo extraído + multiplica revenue.
- **(P3)** Sprint TCP-001 Spike viabilidad técnica + sesión de decisiones bisagra (paralelo a P1, P2). Independiente.

**Acciones legales/documentales en paralelo (no técnicas, NO bloquean P1-P3):**
- Consulta legal CIP (2-4 semanas, $30-80k MXN).
- Procesamiento estatuto IGCAR v2 → DSCs específicos (1-2 semanas).
- Clarificación de OMNICOM y CIES con Alfredo.
- Consultoría regulatoria BioGuard (~$50-100k MXN, opcional).

**Siguiente sub-fase recomendada:** **Fase 5A — Planificación detallada del Sprint 90** (Checkout Stripe → kernel) como primer sprint comercial del portfolio post-Fase 4. Incluir: spec del módulo extraído, contrato de eventos emitidos, plan de migración de LikeTickets para usar el módulo extraído sin downtime, tests con Stripe `sk_test`, documentación del patrón en `docs/patterns/STRIPE_CHECKOUT_PATTERN.md`.

**Archivos generados Fase 4:**
- `audits/AUDIT_PORTFOLIO_4A_CIP_LT_MB_BG_2026_05_10.md` (35 KB, 4 subproyectos)
- `audits/AUDIT_PORTFOLIO_4B_TC_K365_IGCAR_y_CIERRE_FASE4_2026_05_10.md` (este archivo, 3 subproyectos + cierre Fase 4)

**Total Fase 4:** 2 archivos en `audits/`, 7 subproyectos auditados con verificación física de filesystem, 5 hallazgos magnos transversales, 9 acciones derivadas para próxima sesión Cowork-Alfredo, 3 candidatos priorizados para Sprint comercial post-kernel completion.

---

*Generado por Cowork (scheduled task autónomo `cowork-estudio-fase4b-portfolio-tc-k365-igcar`) aplicando Capa 8 Memento al propio proceso de auditoría. Todo en español. Verificado contra filesystem 2026-05-10. Síndrome-Dory neutralizado. Coherente con audit 4A 2026-05-10. v1.0 — 2026-05-10.*
