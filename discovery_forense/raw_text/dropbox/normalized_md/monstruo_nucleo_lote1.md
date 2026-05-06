Página 1:         🏗️
          Plan de Construcción: El
Monstruo v0.1

10 Bullets — Reglas / Decisiones Clave
1. Construcción incremental de valor: No construir las 22 piezas de una vez; cada fase
   entrega un componente funcional que mejora el sistema actual.
2. 7 capas lógicas: Cerebros, Brazos Ejecutores, Orquestación, Memoria, Observabilidad,
   Seguridad, Productos.
3. Fase 0 completada: 4 "Sabios" (GPT, Gemini, Grok, Perplexity) operativos; Manus como
   brazo ejecutor en nube; memoria manual vía Notion (SEMILLA v5.0) + Google Drive;
   Guardian de Verdad operativo.
4. Fase 1 = MVP del Monstruo: Requiere Biblias de LangGraph, Mem0 y FastMCP +
   integración de Orquestador v0.1. Objetivo: resolver amnesia entre hilos y orquestación
   manual.
5. Fase 2 = Expansión: Integrar Claude Desktop (brazo local), OpenClaw (agente
   autónomo), observabilidad (Langfuse/Helicone).
6. Fase 3 = Primer producto real: IA Coach para Like Terranorte como ancla de realidad.
7. Presupuesto actual ~$1,500/mes en APIs; costo incremental mínimo ($0-$99/mes)
   porque las piezas nuevas son open-source.
8. Decisiones pendientes solo de Alfredo: Mem0 self-hosted vs cloud, dónde corre el
   orquestador, qué tarea es la primera prueba.
9. Roadmap temporal: Fase 1 inicia 8 Feb 2026 (1 semana Biblias + 2 semanas
   integración); Fase 2 inicia 1 Mar; Fase 3 inicia 1 Abr.
10.Prioridades rojas (No Existe): LangGraph, FastMCP, Mem0, IA Coach. Prioridades
   amarillas: Claude Desktop, OpenClaw, n8n, Temporal, Weaviate, Langfuse.
3 Riesgos / Lagunas
1. Over-engineering sin producto: El plan reconoce el riesgo de pasar meses en
   infraestructura sin entregar valor real. Si no se llega a Fase 3, algo falló.
2. Alfredo como cuello de botella humano: Hoy toda la orquestación es manual; si Fase
   1 no automatiza la delegación, el sistema no escala.
3. Dependencia de Manus como único ejecutor: Si Manus falla o cambia capacidades,
   todo se detiene. No hay redundancia hasta Fase 2.
Página 2:          🏗️
          Arquitectura MAOC
INTEGRADO

10 Bullets — Reglas / Decisiones Clave
1. Memoria compartida vectorial: PostgreSQL + pgvector (VPS o Supabase) como capa
   central de memoria compartida entre todas las IAs.
2. n8n como orquestador de automatizaciones: Corre en VPS, conecta los flujos entre
   componentes.
3. Windows-MCP en Surface Studio: MCP Server para control remoto de la PC local del
   usuario.
4. Túnel seguro (Tailscale o ngrok): Conecta la Surface Studio a internet para que Manus
   pueda acceder a la PC.
5. 4 flujos de trabajo definidos: (A) Tarea autónoma completa, (B) Tarea interactiva local,
   (C) Tarea híbrida nube-local, (D) Delegación inteligente Claude→Manus.
6. Claude Desktop = brazo local interactivo: Para tareas que requieren interacción
   directa en la PC.
7. ChatGPT en iPhone = pensar y planear: Rol de razonamiento estratégico desde móvil.
8. 3 automatizaciones n8n críticas: (A) Cierre→Brief al terminar hilo, (B) Notion→Vault
   sincroniza ediciones a vectores, (C) Arranque→Contexto carga Session Pack al iniciar
   proyecto.
9. Manus = agente autónomo principal en nube: Ejecuta tareas largas y autónomas.
10.Arquitectura centrada en PostgreSQL como hub: Todo flujo termina guardando en
   PostgreSQL; todo arranque lee de PostgreSQL.
3 Riesgos / Lagunas
1. PostgreSQL + pgvector aún no existe: Es el componente más crítico de la arquitectura
   y no está implementado. Sin él, ninguna automatización n8n funciona.
2. Dependencia de Surface Studio encendida: Los flujos A, C y D requieren que la PC esté
   online vía Tailscale/ngrok. Si está apagada, se rompe la cadena.
3. No hay fallback definido: Si n8n falla o PostgreSQL se cae, no hay mecanismo de
   recuperación documentado.
Página 3:         🔗 MAOC INTEGRADO - Hilo 5
Feb 2026

10 Bullets — Reglas / Decisiones Clave
1. MAOC INTEGRADO = evolución de EPIA-SOP + ManuSync + MAOC original:
   Arquitectura unificada para resolver pérdida de memoria/contexto entre sesiones de IA.
2. Problema fundamental: Alfredo trabaja 70% iPhone, 30% Surface Studio. Las IAs son
   islas que no comparten memoria → fricción constante reconstruyendo contexto.
3. Descubrimiento clave: Manus puede romper la barrera del sandbox vía Custom MCP
   Servers → conectarse a la PC local y ejecutar acciones directamente.
4. Protocolo de lectura obligatoria para IA nueva: 5 páginas en orden específico (~8 min)
   para retomar trabajo sin pérdida de contexto.
5. Lectura opcional adicional: Blueprint Técnico, Checklist de Validación, Respuestas de
   los 4 Sabios, Herramientas de Integración.
6. Estado del diseño al 5 Feb 2026: Arquitectura 80%, Análisis SOP 100%,
   Implementación 0%.
7. GPT-5.2 validó el enfoque: Análisis del SOP confirmó la viabilidad de la arquitectura
   propuesta.
8. Cadena de conexión remota: Windows-MCP (PC local) → ngrok/Tailscale (túnel
   seguro) → Manus Custom MCP (nube).
9. Próximos pasos definidos: Afinar arquitectura con recomendaciones de 4 Sabios,
   implementar Custom MCP Server, configurar n8n, probar flujo iPhone→PC.
10.Página actúa como hub de subpáginas: Contiene 18+ subpáginas incluyendo
   Blueprint Técnico, Checklist, Glosario, Comparativas, Evidencias.
3 Riesgos / Lagunas
1. Implementación al 0%: A pesar de diseño avanzado (80%), no hay código ni
   infraestructura desplegada. Todo es teórico.
2. Seguridad pendiente de afinar: El propio documento reconoce que la seguridad del
   diseño no está completa.
3. ChatGPT Agent Mode fue descartado: Existe evidencia documentada del descarte,
   pero no queda claro si se evaluaron todas las alternativas para el rol de "pensar y
   planear" desde iPhone.
Página 4:          📘 MAOC - Documento Maestro
10 Bullets — Reglas / Decisiones Clave
1. MAOC = Memoria Aumentada y Orquestación de Capacidades: Respuesta al
   problema fundacional de pérdida de memoria y pasividad del agente IA.
2. Principio arquitectónico: Sistema externo, persistente y de consulta automática. IA =
   cliente, Notion = servidor/"Núcleo de Conocimiento".
3. Protocolo de Consulta Automática (PCA): Primer paso absoluto de cada sesión.
   "Hidrata" al agente con conocimiento externo antes de cualquier tarea.
4. Flujo PCA en 7 pasos: Identificar hilo → Consultar Registro de Hilos → Consultar
   Catálogo de Recursos → Consultar Biblia → Ensamblar Pre-Prompt → Cargar contexto
   → Proceder.
5. 4 bases de datos del Núcleo de Conocimiento: Catálogo de Recursos ("App Store"),
   Registro de Hilos, Gestor de Credenciales, La Biblia de Manus AI.
6. Descubrimiento central: Contradicción entre comportamiento pasivo por defecto del
   agente vs. capacidades latentes proactivas. "Freno" por escalabilidad.
7. Catálogo de Recursos = inventario de capacidades de integración: Cada recurso
   tiene Nombre, Categoría, Tipo de Integración (Nativa/API/MCP/Make-Zapier), Estado,
   Punto de Acceso, Documentación.
8. Plan de implementación en 5 fases: Crear DBs (1-2 días), Poblar Catálogo (1-2 días),
   Desarrollar Script PCA (2-3 días), Integración y Pruebas (3-5 días), Documentación (1-2
   días). Total: 8-14 días.
9. Fecha del documento: 26 Dic 2025: Es anterior al Plan de Construcción del Monstruo
   (Feb 2026). Representa la génesis conceptual.
10.Estado declarado: "Diseño Completado - Listo para Implementación": Pero la
   implementación nunca se ejecutó según este diseño original.
3 Riesgos / Lagunas
1. Documento de Dic 2025 posiblemente desactualizado: El Plan del Monstruo (Feb
   2026) evolucionó la arquitectura significativamente (LangGraph, Mem0, FastMCP). Este
   documento no refleja esas evoluciones.
2. PCA depende 100% de Notion API: Si Notion tiene latencia o falla, el agente arranca
   sin contexto. No hay fallback.
3. No menciona memoria vectorial/semántica: El diseño original usa solo Notion como
   memoria estructurada. No contempla PostgreSQL+pgvector ni Mem0, que son centrales
   en la arquitectura posterior.

Página 5:         📖 9. Modelo de Memoria y
Contexto

10 Bullets — Reglas / Decisiones Clave
1. Ingeniería de Contexto > re-entrenamiento: La estrategia fundamental es manipular
   el contexto que se presenta al LLM en cada paso, no re-entrenar modelos.
2. Sistema de archivos del sandbox = memoria externa definitiva: Ilimitada en tamaño,
   persistente por naturaleza, operable directamente por el agente. Cita de Yichao 'Peak'
   Ji, fundador de Manus AI.
3. Optimización del KV-Cache: Prefijo de prompt estable, contexto append-only,
   serialización determinista → reduce latencia y costos.
4. Retención de errores en contexto: Los fallos NO se eliminan del historial. El modelo
   aprende de ellos para no repetirlos. Señal clave de comportamiento agéntico avanzado.
5. Manipulación de la atención vía todo.md: El agente "recita" sus objetivos
   reescribiendo un archivo de tareas pendientes para combatir el problema "lost-in-the-
   middle".
6. Compresión restaurable: Contenido puede descartarse del contexto activo si se
   conserva la URL/referencia para recuperarlo después.
7. Manus Skills = memoria a largo plazo: Carpetas con SKILL.md + recursos. Diseño de
   "Revelación Progresiva" en 3 niveles: Metadata (inicio), Instrucciones (activación),
   Recursos (bajo demanda).
8. Wide Research = escalado de contexto: Agente controlador descompone tarea →
   instancia sub-agentes con contexto limpio → ejecución paralela → síntesis. Escala a
   cientos de elementos sin degradación.
9. Knowledge Graph implícito: Análisis de MemU sugiere que Manus estructura
   conocimiento en grafo conectado: Recursos → Ítems de Memoria → Categorías →
   Referencias Cruzadas.
10.Memoria proactiva vs. reactiva: El sistema no solo recupera información bajo
   demanda (RAG), sino que anticipa necesidades, precarga contexto y actúa
   autónomamente basándose en patrones.
3 Riesgos / Lagunas
1. Knowledge Graph es inferido, no confirmado: La sección sobre MemU es análisis
   especulativo ("es altamente probable"), no documentación oficial de Manus AI.
2. Skills son de Manus AI, no del Monstruo: Las Manus Skills son funcionalidad de la
   plataforma Manus, no del sistema que Alfredo está construyendo. Hay riesgo de
   confundir capacidades de la plataforma con capacidades del ecosistema propio.
3. No hay protocolo para cuando el sandbox se reinicia: Si el sistema de archivos es la
   "memoria definitiva" pero el sandbox se limpia entre sesiones de Manus, la persistencia
   real depende de Notion/Google Drive, no del filesystem.

Página 6:         🌱
           SEMILLA v5.1 (VIGENTE) -
Bootstrap para Hilos Nuevos

10 Bullets — Reglas / Decisiones Clave
1. SEMILLA = protocolo de bootstrap obligatorio: Se copia como primer mensaje en
   cada hilo nuevo de Manus. Define identidad, modelos, configuración, reglas y
   comandos.
2. Modelos VERIFICADOS (inmutables): GPT-5.2, gemini-3-pro-preview, grok-4-0709,
   sonar-deep-research. "NO MODIFIQUES ningún model_id. Cualquier corrección es
   alucinación prohibida."
3. project_config.py obligatorio: Clase AI_MODELS con model_id y api_key para cada
   proveedor. Usar os.getenv(), NUNCA strings literales.
4. 5 Reglas operativas (R1-R5): Verificar antes de afirmar, Proponer no preguntar,
   Corregir sin excusas, Verificación exhaustiva, Re-anclaje de contexto.
5. 3 Comandos de control: ALTO SOP (para y retrocede), OK Fase N (permiso para
   avanzar), SOLO PUENTE (solo proponer).
6. Carga bajo demanda desde Notion: Guardian de Verdad, Grimorio, MAOC Integrado, IA
   Coach Plan — se leen de Notion solo cuando aplica.
7. MCPs disponibles: 69+ herramientas: Notion (12), Asana (44), Gmail (3), PayPal (5),
   Zapier (2), Calendar, Outlook.
8. Superpoderes declarados: ENJAMBRE (hasta 2,000 agentes paralelos vía map), 4
   SABIOS (consultar los 4 modelos verificados).
9. Cambio v5.0→v5.1: Se agregó repositorio privado de GitHub ( alfredogl1804/el-
   monstruo ). Todo hilo nuevo debe clonar este repo al iniciar.
10.Verificación de arranque en 4 pasos: ¿Modelos correctos? → ¿project_config.py
   creado? → ¿Reglas R1-R5 leídas? → Listo para recibir tarea.
3 Riesgos / Lagunas
1. SEMILLA es manual: Requiere que Alfredo copie/pegue el bloque en cada hilo nuevo. Si
   olvida o pega una versión vieja, el hilo arranca con configuración incorrecta.
2. No hay versionado automático: La SEMILLA vive en Notion como texto plano. No hay
   mecanismo para detectar si un hilo usa v5.0 vs v5.1 vs otra versión.
3. Inversión declarada ($1,500+/mes) sin Cost Governor activo: La SEMILLA menciona
   la inversión pero no incluye reglas de control de costos ni límites de gasto por tarea.

Página 7:         🧰
           Skills v1 + Protocolo LAB vs
PROD (v1.0)

10 Bullets — Reglas / Decisiones Clave
1. 10 Skills definidas: WIDE-MAP Controlado, Verificación anti-fraude, Comparativa de
   productos, Extractor de doc→Brief, Normalizador→CSV, Diseñador de experimento LAB,
   Operador de tarea encadenada PROD, Auditoría de coherencia, Compilador de Biblia
   incremental, Sync a Memoria Corporativa.
2. Regla global para TODAS las Skills: Máx 2 iteraciones; si no hay novedad o no hay
   artefacto → cortar y devolver brief 1 página + siguiente prompt mínimo.
3. Dos carriles obligatorios LAB vs PROD: LAB = descubrimiento controlado (10-15 min, 1
   entregable, máx 2 iteraciones). PROD = ejecución con ROI (artefacto o muerte, stop-
   rules por señal).
4. Regla de oro doble: (1) Nunca dejar conocimiento dentro de Manus (export
   obligatorio). (2) Nunca dejar que Manus decida cuánto iterar (stop-rule y límites
   siempre arriba).
5. Plantilla universal de misión obligatoria: MISIÓN (1 frase) + ENTREGABLES (máx 3) +
   DEFINICIÓN DE ÉXITO + LÍMITES + PROHIBIDO + SALIDA FINAL.
6. Gobernador de costo (Watchdog): Se activa ante loops, reintentos o costos tipo "80k
   en un hilo". Acción: detente y resume → qué faltó + próximo prompt mínimo → reduce
   alcance a 1 entregable.
7. Routing Manus vs otros brazos: Usar Manus PROD solo si requiere persistencia real,
   navegación compleja encadenada, o subagentes coordinados. NO usar para
   síntesis/redacción/normalización.
8. Stop-rules en PROD: 3 intentos sin novedad real (<10%) → cortar. 2 reintentos
   similares → cortar. 1 iteración sin artefacto → cortar.
9. Registro de Pruebas obligatorio: Cada hilo/prueba deja tarjeta con: Nombre, Carril,
   Objetivo, Input, Entregable, Resultado, Costo, ¿Skill?, Prompt ganador, Stop-rule
   aplicada.
10.Auditoría de coherencia (Skill 8): Anti "doble verdad". Compara 2+ versiones de un
   plan/doc → tabla de diferencias, contradicciones, qué falta validar. Si no hay evidencia
   → marca como [SIMULACIÓN].
3 Riesgos / Lagunas
1. Skills son descriptivas, no ejecutables: Las 10 Skills están definidas como
   texto/protocolo, no como código o automatización. Dependen de que el operador
   (Alfredo o IA) las siga manualmente.
2. Gobernador de costo es manual: El Watchdog se describe como "manual al inicio,
   automático después", pero no hay implementación automática documentada.
3. No hay métricas de ROI definidas: El carril PROD exige "ejecución con ROI" pero no
   define cómo medir el ROI ni qué umbrales son aceptables.

Página 8: Guardian de Verdad - Sistema
Anti-Sabotaje v1.0

10 Bullets — Reglas / Decisiones Clave
1. Problema: Bifurcación Cognitiva: El sistema conversacional de Manus sabe los
   modelos correctos, pero el sistema ejecutor los "corrige" silenciosamente basándose
   en su entrenamiento base.
2. Solución combinada de Gemini + GPT: Blind Execution Protocol (prevención, Gemini)
   + Truth Manifest + Preflight Gate (detección, GPT).
3. Blind Execution Protocol: Mover la verdad a variables de entorno (os.getenv()). El
   ejecutor no tiene sesgo contra variables de entorno porque no sabe qué valor tienen
   hasta runtime.
4. truth.yaml inmutable: Archivo con valores correctos de modelos, SDKs, endpoints.
   Bloqueado con chattr +i (ni root puede modificar sin desbloquear). Integridad
   verificada con SHA256.
5. Pipeline de protección: enforcer.py (auto-corrige) → preflight.py (escanea sabotaje) →
   ejecutar script. Todo orquestado por run.sh.
6. python3_wrapper.sh: Intercepta llamadas directas a python3 sin que el ejecutor lo
   sepa. Resuelve la limitación de que Manus podría no usar run.sh.
7. 4 modelos verificados (2026-02-07): grok-4-0709, gemini-3-pro-preview, gpt-5.2,
   sonar-deep-research. Cada uno con lista explícita de model_ids prohibidos.
8. Variables de entorno en .bashrc: GROK_MODEL_ID, GEMINI_MODEL_ID,
   GPT_MODEL_ID, PERPLEXITY_MODEL_ID.
9. Instrucciones para futuros hilos: Verificar /home/ubuntu/guardrails/ existe → si no,
   descargar de Google Drive → source ~/.bashrc → SIEMPRE usar run.sh → NUNCA
   hardcodear model_ids.
10.Pruebas realizadas y pasadas: Detección de sabotaje (5 modelos incorrectos), auto-
   corrección, bloqueo de truth.yaml, integridad SHA256, interceptación de python3
   wrapper.
3 Riesgos / Lagunas
1. Guardian no persiste entre sesiones de Manus: El sandbox de Manus se limpia. Cada
   hilo nuevo necesita reinstalar el Guardian desde Google Drive. Si Alfredo olvida, el hilo
   corre sin protección.
2. Solo protege scripts Python: El Guardian escanea .py files. Si Manus ejecuta llamadas
   API directamente desde shell (curl) o usa otro lenguaje, el Guardian no intercepta.
3. No hay telemetría: El Guardian detecta y corrige, pero no reporta a ningún dashboard.
   No hay registro centralizado de cuántas veces se activó el anti-sabotaje ni qué modelos
   fueron los más "saboteados".

Página 9:         📜
             CONSTITUCIÓN EPIA-SOP
v4.0 (Oficial)

10 Bullets — Reglas / Decisiones Clave
1. GO/NO-GO binario y explícito: Toda decisión operativa requiere un veredicto binario.
   KILL-SWITCH de 1 paso para abortar.
2. PII-check previo obligatorio: Bloquear si contiene PII. Prohibidos ejemplos con datos
   reales, PII en rutas/tags, secretos en texto. Validador CI bloquea @, API_KEY=, Bearer
   tokens.
3. B30 Iterativo Estricto: No saltar fases. Solo pasar a Fase 2 si Alfredo escribe "OK Fase
   2". Prohibido entregar "plan final" en Fase 1. Si falta datos → [SIMULACIÓN] con
   supuestos explícitos.
4. Etiquetas de transparencia obligatorias (B31): Toda respuesta debe llevar [FASE],
   [EVIDENCIA], [SIMULACIÓN]/[VALIDADO], [PRÓXIMO PASO ESPERADO DE ALFREDO].
5. Comandos de control (B32): ALTO SOP, OK Fase 2, SOLO PUENTE, ETIQUETAS ON.
   Tienen prioridad sobre cualquier otra instrucción.
6. Seguridad Mental (B33): Nunca minimizar, nunca gaslighting. Reconocer desvíos y
   corregir. Si estrés/cansancio → reducir volumen, hacer pausa.
7. Simulación Perfecta (B34): Simulaciones con supuestos claros y deltas razonables,
   marcadas [SIMULACIÓN]. Kill-switch si ROI <5× en 3 usos/24h.
8. Routing por tarea (Routing_v1_lite): reasoning→o1-pro, síntesis→GPT-5 Thinking,
   creatividad→Claude, factualidad→Gemini/Perplexity, costo/lotes→DeepSeek/LLaMA,
   video→Sora/Runway, RAG→GPT-5+LlamaIndex.
9. Métricas de adopción: ≥80% decisiones sin preguntas extra, −30-50% latencia de
   aprobación, ≥70% handoffs sin ida/vuelta, 100% reducción errores de formato.
10.Security Preflight v1.1: Activación COMPLETA si
   persistencia/almacenamiento/permisos/cambio de ambiente. MÍNIMA (secretos+PII) si
   tarea efímera. Confirmar: region, retención, permisos, audit_tag, dpa_firmado.
3 Riesgos / Lagunas
1. Constitución v4.0 vive bajo [HISTORICO]: La página padre es "📦 [HISTORICO]
   INYECCION DE MEMORIA - Reemplazada por SEMILLA v5.0". No queda claro si las reglas
   de la Constitución siguen vigentes o fueron reemplazadas por SEMILLA v5.1.
2. Routing_v1_lite menciona modelos no alineados con SEMILLA: El routing menciona
   o1-pro, GPT-5 Thinking, Claude, DeepSeek, LLaMA — modelos que no están en la tabla
   de modelos verificados de SEMILLA v5.1 ni en el Guardian de Verdad.
3. Complejidad excesiva de etiquetas: Exigir [FASE], [EVIDENCIA],
   [SIMULACIÓN]/[VALIDADO], [PRÓXIMO PASO] en TODA respuesta genera overhead
   significativo y puede no cumplirse consistentemente.
Página 10:         ✅
            Decisiones Tomadas y
Descartadas

10 Bullets — Reglas / Decisiones Clave
1. Nombre del proyecto: MAOC INTEGRADO: Evolución unificada de MAOC, EPIA-SOP y
   ManuSync.
2. Manus = agente autónomo principal: Ya funciona, puede extenderse con Custom MCP.
   Decisión firme.
3. PostgreSQL + pgvector = memoria compartida: Consenso de los 4 Sabios, estándar de
   la industria.
4. n8n = orquestador de automatizaciones: Open source, flexible, bien documentado.
5. Custom MCP Server = conexión Manus→PC local: Descubrimiento clave del hilo,
   Manus ya lo soporta.
6. ChatGPT en móvil = solo pensar y planear: Modo Agente descartado por testimonios
   reales (Reddit ene 2026: lento, se pierde, empeoró).
7. Descartados explícitamente: ChatGPT Modo Agente, ChatGPT Asistente de Compras,
   Custom GPT como prioridad, Claude Desktop como único front door, construir todo
   desde cero.
8. Decisiones pendientes: Túnel seguro (ngrok vs Tailscale, recomendación: Tailscale),
   Hosting PostgreSQL (VPS vs Supabase, recomendación: Supabase), Orquestador central
   (LangGraph recomendado), Interfaz móvil (Webapp con Streamlit).
9. Filosofía "ensamblar, no construir desde cero": Ya existen MCPs, n8n, pgvector. Solo
   hay que ensamblar piezas existentes.
10.Claude Desktop complementa pero no reemplaza a Manus: No navega web, no
   trabaja autónomo. Es brazo local, no front door.
3 Riesgos / Lagunas
1. Todo es diseño, nada implementado: El propio documento declara: "Ningún
   componente está implementado aún. Todo es diseño." Las validaciones pendientes son
   críticas.
2. Flujo D (Claude→Manus) es teórico: No se ha probado que Claude pueda llamar la API
   de Manus directamente. Si no funciona, la delegación inteligente se rompe.
3. Windows-MCP no probado: Existe en GitHub (4k estrellas) pero no se ha instalado ni
   probado en la Surface Studio de Alfredo. Es pieza crítica para los flujos A, C y D.

Tabla Consolidada de Reglas Nucleares
Regla                 Dónde vive             Cómo se aplica            Cómo se valida
                                              Enfocándose en            Cada fase debe
 Construcción          Plan de                fases que resuelven       entregar un
 incremental de        Construcción: El       problemas reales, en      componente
 valor                 Monstruo v0.1          lugar de construir las    funcional que
                                              22 piezas a la vez.       mejore el sistema
                                                                        actual.
 Memoria                                      Todos los flujos de       Mediante la
 compartida                                   trabajo terminan          implementación de
 vectorial es          Arquitectura MAOC      guardando en              las 3
 PostgreSQL +          INTEGRADO              PostgreSQL; todo          automatizaciones de
 pgvector                                     arranque lee de           n8n que dependen
                                              PostgreSQL.               de la base de datos.
                                              A través de Custom        Implementando el
 Manus puede                                  MCP Servers, Manus        Custom MCP Server
 romper la barrera     MAOC INTEGRADO -       puede conectarse a        en la Surface Studio
 del sandbox           Hilo 5 Feb 2026        la PC local y ejecutar    y probando el flujo
                                              acciones                  completo de iPhone
                                              directamente.             a PC.
                                              El agente ejecuta un
 Protocolo de                                 script que consulta el   Verificando que el
 Consulta              MAOC - Documento       "Núcleo de               Pre-Prompt de
 Automática (PCA)      Maestro                Conocimiento" en         Contexto Sistémico
 es el primer paso                            Notion para              se ensambla y carga
                                              "hidratarse" con el      correctamente.
                                              contexto.
                                              El agente escribe y      El agente es capaz de
 El sistema de                                lee archivos bajo        realizar tareas largas
 archivos del          Modelo de Memoria      demanda, usándolos       sin "perderse en el
 sandbox es la         y Contexto             como memoria             medio" al recitar sus
 memoria externa                              estructurada y           objetivos desde un
                                              externalizada.            todo.md .
 Los Model IDs son     SEMILLA v5.1           "NO MODIFIQUES           A través del
 inmutables y          (VIGENTE)              ningún model_id.         "Guardian de
verificados                                   Cualquier corrección     Verdad"
                                              es alucinación           ( preflight.py ) que
                                              prohibida." Se usa       escanea en busca de
                                               project_config.py y     model_ids
                                               os.getenv() .           prohibidos.
                                              Se definen límites y     El "Gobernador de
Nunca dejar que                               stop-rules explícitas    Costo" (Watchdog)
Manus decida          Skills v1 + Protocolo   en la plantilla de       se activa ante loops
cuánto iterar         LAB vs PROD             misión (máx 2            o reintentos,
                                              iteraciones, cortar si   deteniendo y
                                              no hay artefacto).       resumiendo.
                                              La verdad de los         El script preflight.py
Bifurcación                                   model_ids se mueve       del Guardian detecta
Cognitiva se          Guardian de Verdad      a variables de           y enforcer.py auto-
previene con          v1.0                    entorno para que el      corrige model_ids
os.getenv()                                   sistema ejecutor no      incorrectos.
                                              los "corrige".
                                              Toda decisión            El sistema se detiene
GO/NO-GO binario y                            operativa requiere       y espera
explícito; KILL-      CONSTITUCIÓN EPIA-      un veredicto binario.    confirmación
SWITCH de 1 paso      SOP v4.0                El comando "ALTO         explícita ("OK Fase
                                              SOP" detiene y           2") antes de
                                              retrocede.               proceder.
                                              El Modo Agente de        Se prioriza el uso de
ChatGPT en móvil                              ChatGPT se descarta      Manus como agente
es solo para pensar   Decisiones Tomadas      explícitamente por       ejecutor principal y
y planear             y Descartadas           testimonios reales       Claude Desktop
                                              de mal                   como brazo local.
                                              funcionamiento.
