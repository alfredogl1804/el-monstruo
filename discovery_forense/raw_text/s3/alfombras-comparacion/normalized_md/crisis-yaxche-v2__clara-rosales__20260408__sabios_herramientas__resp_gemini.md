# Herramientas para Crisis — Gemini

¡Excelente! Estamos ante una crisis de nivel ROJO EMERGENTE con un plazo crítico de 48-72 horas. La Operación YAXCHÉ requiere velocidad, precisión y una orquestación inteligente de nuestros recursos. Como estratega especializado en Latinoamérica, entiendo que la percepción pública y la respuesta inmediata son cruciales. Aquí mis recomendaciones concretas y accionables para maximizar el plan de Clara Rosales:

---

### 1. HERRAMIENTAS DE ALTO IMPACTO

Estas herramientas serán el núcleo de nuestra respuesta, permitiéndonos actuar con rapidez y eficacia.

*   **GPT-5.4 (IA LLM)**
    *   **Qué haría exactamente:** Será el cerebro central. Generará borradores de comunicados de prensa, discursos, guiones para videos, contenido para redes sociales, respuestas a preguntas frecuentes (FAQs), y análisis de escenarios. También puede sintetizar informes de monitoreo y proponer líneas argumentales para el reencuadre.
    *   **En qué fase del plan se usaría:** Todas las fases, pero crítica en **Respuesta inmediata (0-6h)** y **Plan táctico (24-72h)** para la generación rápida de contenido.
    *   **Cómo se integraría operativamente:** Integrado con Notion para la gestión de contenido, con Gmail/Outlook para el envío de comunicados, y con Asana para la asignación de tareas de revisión y publicación. Podría recibir inputs directamente de Perplexity o Mentionlytics vía Zapier.
    *   **Impacto estimado:** **ALTO**. Su capacidad de orquestación y síntesis es insustituible para una respuesta ágil y coherente.

*   **Mentionlytics (APIs de Datos/Monitoreo)**
    *   **Qué haría exactamente:** Proporcionará monitoreo en tiempo real de menciones en redes sociales, noticias, blogs y foros. Identificará tendencias, sentimientos (positivo/negativo/neutro), influencers clave, focos de desinformación y la propagación de la narrativa. Nos permitirá medir la efectividad de nuestras acciones y detectar nuevas amenazas.
    *   **En qué fase del plan se usaría:** **Monitoreo continuo**, pero esencial desde la **Respuesta inmediata (0-6h)** para entender la magnitud y dirección de la crisis.
    *   **Cómo se integraría operativamente:** Configurado para enviar alertas a través de Zapier (ej. a un canal de Slack o Telegram, o directamente a Asana/Notion) cuando se detecten picos de menciones negativas o nuevos actores. Sus reportes serían analizados por Claude Opus y GPT-5.4.
    *   **Impacto estimado:** **ALTO**. Sin monitoreo, estamos ciegos. Es la base para cualquier toma de decisión informada.

*   **Perplexity Sonar (IA LLM)**
    *   **Qué haría exactamente:** Realizará búsquedas web en tiempo real con citas para verificar hechos, investigar antecedentes de Carlos Koyoc Uribe, rastrear el origen de las acusaciones, y obtener información actualizada sobre la iniciativa de VIH. Es nuestra herramienta de inteligencia de campo rápida.
    *   **En qué fase del plan se usaría:** Crítica en **Respuesta inmediata (0-6h)** para contextualizar las acusaciones y en **Plan táctico (24-72h)** para preparar la denuncia legal y la rueda de prensa.
    *   **Cómo se integraría operativamente:** Usado por el equipo de investigación para validar información. Sus hallazgos se documentarían en Notion y se usarían como input para GPT-5.4 y Claude Opus para refinar narrativas y argumentos legales.
    *   **Impacto estimado:** **ALTO**. La velocidad en la verificación de datos y la obtención de inteligencia es clave para contrarrestar la desinformación.

*   **HeyGen (APIs de Media/Generación)**
    *   **Qué haría exactamente:** Creará el video de respuesta inmediata de Clara. Utilizaremos avatares IA para generar un mensaje profesional, conciso y con el tono adecuado, sin la presión de una grabación tradicional. Esto nos permite un control total sobre el mensaje y una producción extremadamente rápida. *Importante: El avatar debe ser 100% fiel a la imagen y voz de Clara para evitar rechazo. Si no se logra esto, esta herramienta pasaría a un impacto medio y se priorizaría un video grabado tradicionalmente.*
    *   **En qué fase del plan se usaría:** **Respuesta inmediata (0-6h)**. Es el primer punto de contacto visual de Clara.
    *   **Cómo se integraría operativamente:** GPT-5.4 generaría el guion. ElevenLabs clonaría la voz de Clara (si es viable y convincente) o usaría una voz profesional. HeyGen ensamblaría el video. El resultado se subiría a las redes sociales (Instagram, etc.) y a la landing page en Vercel.
    *   **Impacto estimado:** **ALTO** (si la calidad es indistinguible de la realidad y el mensaje es auténtico). **MEDIO** (si se percibe como "IA" y genera desconfianza).

*   **Notion (MCPs Configurados)**
    *   **Qué haría exactamente:** Servirá como nuestro "War Room Digital". Centralizará toda la información: plan de crisis detallado, análisis de la situación (inputs de Mentionlytics/Perplexity), borradores de comunicados, FAQs, argumentos clave, registro de decisiones, contactos de medios, y seguimiento legal.
    *   **En qué fase del plan se usaría:** Todas las fases, como eje central de colaboración y documentación.
    *   **Cómo se integraría operativamente:** El equipo trabajará en tiempo real en Notion. Recibirá alertas de Zapier, documentos generados por GPT-5.4, y análisis de Claude Opus. Se vinculará con Asana para las tareas específicas.
    *   **Impacto estimado:** **ALTO**. Es la columna vertebral de la organización y la memoria institucional de la crisis.

*   **Zapier (MCPs Configurados)**
    *   **Qué haría exactamente:** Actuará como el pegamento de automatización. Conectará Mentionlytics a Notion/Asana para alertas, enviará borradores de GPT-5.4 a Gmail para revisión, o activará notificaciones en Google Calendar para reuniones urgentes.
    *   **En qué fase del plan se usaría:** Todas las fases, facilitando la velocidad y reduciendo la carga manual.
    *   **Cómo se integraría operativamente:** Configurado con múltiples "Zaps" para crear un flujo de trabajo sinérgico entre las herramientas de monitoreo, análisis, gestión y comunicación.
    *   **Impacto estimado:** **ALTO**. La automatización es clave para ganar la ventana crítica de 48-72 horas.

*   **Vercel (MCPs Configurados)**
    *   **Qué haría exactamente:** Desplegará una "landing page" de transparencia. Aquí se publicarán los comunicados oficiales, el video de Clara, un FAQ actualizado sobre las acusaciones y la iniciativa de VIH, enlaces a documentos legales (la denuncia), y testimonios de apoyo (si aplica). Será el punto de referencia oficial.
    *   **En qué fase del plan se usaría:** **Plan táctico (24-72h)** para la carta abierta y denuncia, y **Reencuadre (7-30 días)** para consolidar la narrativa.
    *   **Cómo se integraría operativamente:** El contenido generado por GPT-5.4 y revisado en Notion se publicaría aquí. Los enlaces a esta página se compartirían en redes sociales (Instagram) y en comunicados de prensa (Gmail/Outlook).
    *   **Impacto estimado:** **ALTO**. Un punto centralizado de información oficial es vital para controlar la narrativa y ofrecer transparencia.

---

### 2. CADENA DE EJECUCIÓN: SISTEMA DE GUERRA INTEGRADO

Diseñemos una cadena de ejecución para la fase crítica, enfocada en la detección, análisis y respuesta.

**Flujo: Detección Rápida y Respuesta Coherente a Nueva Acusación/Escalada**

1.  **Detección (Mentionlytics + Perplexity Sonar):**
    *   **Mentionlytics** detecta un nuevo pico de menciones negativas, un hashtag emergente o una nueva acusación específica sobre Clara Rosales (ej. un medio local publica un "nuevo dato" de Carlos Koyoc Uribe).
    *   **Perplexity Sonar** realiza una búsqueda inmediata para verificar la fuente, el contexto y los antecedentes de la nueva información/acusación, extrayendo citas relevantes.

2.  **Alerta y Recopilación (Zapier + Notion):**
    *   **Zapier** se activa por la alerta de Mentionlytics.
    *   **Zapier** crea una nueva entrada de "Incidente Crítico" en **Notion**, incluyendo los datos de Mentionlytics y los hallazgos iniciales de Perplexity Sonar. Asigna automáticamente una tarea de "Análisis Urgente" en **Asana** al equipo de estrategia, con un plazo de 30 minutos.

3.  **Análisis Profundo y Estrategia (Claude Opus 4.6 + GPT-5.4):**
    *   El equipo copia la nueva información y el contexto de Notion a **Claude Opus 4.6** para un análisis crítico profundo: ¿Cuáles son las vulnerabilidades? ¿Cómo se conecta con las acusaciones existentes? ¿Qué contra-argumentos podemos construir? ¿Cuál es el riesgo legal?
    *   Simultáneamente, la información se envía a **GPT-5.4** para que, basándose en el análisis de Claude, proponga 3-5 opciones de respuesta inmediata (ej. borrador de tweet, declaración corta, línea argumental para una aparición).

4.  **Generación de Contenido y Aprobación (GPT-5.4 + Notion + Gmail/Outlook):**
    *   Una vez seleccionada la línea de respuesta, **GPT-5.4** genera el contenido detallado (ej. borrador de comunicado de prensa, guion para un video corto, 3 publicaciones para redes sociales).
    *   Este contenido se guarda en **Notion** para revisión y aprobación por el equipo legal y Clara.
    *   Si es un comunicado de prensa, **Zapier** lo envía desde Notion a una cuenta de **Gmail/Outlook** preconfigurada para su distribución a medios, una vez aprobado.

5.  **Publicación y Difusión (Instagram + Vercel + ElevenLabs/HeyGen):**
    *   El contenido aprobado se publica directamente en las redes sociales de Clara (ej. **Instagram**).
    *   Si se requiere un audio o video, **ElevenLabs** (para audio) o **HeyGen** (para video) se usarían para generar el material final a partir del guion de GPT-5.4.
    *   La **landing page en Vercel** se actualiza con la nueva declaración oficial o FAQ.

6.  **Monitoreo Continuo y Ajuste (Mentionlytics + Zapier):**
    *   **Mentionlytics** continúa monitoreando la respuesta a nuestras acciones, cerrando el ciclo.
    *   **Zapier** alerta nuevamente si la crisis escala o si surgen nuevas narrativas, reiniciando el proceso.

Este sistema garantiza una respuesta rápida, informada y coordinada, minimizando los tiempos de reacción y maximizando la coherencia del mensaje.

---

### 3. HERRAMIENTAS SUBUTILIZADAS QUE PODRÍAN DAR UNA VENTAJA INESPERADA

*   **SecurityTrails (APIs de Datos/Monitoreo)**
    *   **Ventaja inesperada:** Aunque no es una herramienta de comunicación directa, SecurityTrails puede ser invaluable para la inteligencia de contrainformación. Nos permitiría investigar el dominio y la infraestructura web de los medios o plataformas que difunden las acusaciones más virulentas. ¿Quién está detrás de ellos? ¿Hay patrones en sus registros DNS o WHOIS que los vinculen a intereses políticos específicos o a la oposición? ¿Hay un patrón de comportamiento en sus servidores que indique un ataque coordinado?
    *   **Uso en crisis:** En la fase de **Contraataque (Día 3-7)**, podría revelar vínculos ocultos o debilidades en la estructura de los atacantes que podríamos usar para desacreditar la fuente de la información, no solo la información misma. Podría ser el "dato del PAN-Kanasín" pero desde una perspectiva de infraestructura digital.

*   **Grok 4.20 (IA LLM)**
    *   **Ventaja inesperada:** Su capacidad para "ángulos no obvios" es perfecta para la fase de **Contraataque (Día 3-7)** y **Reencuadre (7-30 días)**. Cuando las respuestas convencionales se agotan o no son suficientes, Grok puede ayudarnos a pensar fuera de la caja. ¿Qué narrativa completamente inesperada podría cambiar la conversación? ¿Cómo podemos girar la polémica del VIH de una manera que nadie espera, convirtiéndola en una fortaleza sorprendente? Esto requiere supervisión humana muy estricta, pero puede generar ideas disruptivas.
    *   **Uso en crisis:** Brainstorming de estrategias de contraataque o reencuadre que otras IAs más "convencionales" no considerarían.

*   **manus-analyze-video (Herramientas Nativas del Sandbox)**
    *   **Ventaja inesperada:** Si los oponentes o Carlos Koyoc Uribe publican videos (entrevistas, declaraciones, etc.), esta herramienta puede analizar el contenido, el tono, las palabras clave, y el sentimiento de manera automatizada. Puede identificar rápidamente los puntos clave de su ataque, quiénes aparecen, y cómo se están posicionando.
    *   **Uso en crisis:** En la fase de **Monitoreo continuo** y preparación del **Contraataque**, nos permite desglosar rápidamente los mensajes audiovisuales del adversario para identificar debilidades o contradicciones.

---

### 4. STACK MÍNIMO VIABLE (5 herramientas)

Si solo pudiéramos elegir 5 herramientas, estas serían las más esenciales para mantener la operación en marcha y responder a la crisis:

1.  **GPT-5.4 (IA LLM):** El cerebro central. Generación de contenido, análisis estratégico, síntesis de información. Sin ella, la velocidad de respuesta se reduciría drásticamente y la coherencia del mensaje sería difícil de mantener.
2.  **Mentionlytics (APIs de Datos/Monitoreo):** Los ojos y oídos. Monitoreo en tiempo real es absolutamente crítico para saber qué está pasando, dónde y cómo. Sin esto, cualquier estrategia sería un disparo al aire.
3.  **Notion (MCPs Configurados):** El War Room. Centraliza la información, la colaboración y la toma de decisiones. Es indispensable para que el equipo trabaje de manera coordinada y tenga acceso a la misma información vital.
4.  **Zapier (MCPs Configurados):** El pegamento de la automatización. Conectaría Mentionlytics a Notion/Asana y a GPT-5.4, permitiendo que la información fluya y las acciones se disparen automáticamente. Es la clave para la velocidad en una crisis de 48-72 horas.
5.  **Perplexity Sonar (IA LLM):** La inteligencia rápida. Para verificar hechos, investigar acusaciones y obtener información en tiempo real. Es crucial para refutar la desinformación y construir una defensa sólida basada en datos.

Este stack permite monitorear, analizar, generar contenido, coordinar al equipo y automatizar tareas esenciales, cubriendo los pilares fundamentales de la gestión de crisis.

---

### 5. RIESGOS DE USO Y HERRAMIENTAS A EVITAR

Es tan importante saber qué usar como qué no usar, o cuándo usarlo con extrema precaución.

*   **HeyGen / Novita AI (Video con avatares IA / Video AI generativo) para la propia Clara Rosales:**
    *   **Riesgo:** Si el avatar no es 100% convincente y natural, o si se detecta que el video es generado por IA, esto podría ser **extremadamente contraproducente**. En Latinoamérica, la autenticidad y la cercanía son muy valoradas. Un video "falso" o "robotizado" de la propia Clara en un momento de crisis grave (acusaciones de narcotráfico) destruiría la confianza y generaría la percepción de que está ocultando algo o no es lo suficientemente valiente para dar la cara.
    *   **Recomendación:** Usar solo si la calidad es indistinguible de un video real y si se puede justificar su uso (ej. "problemas técnicos" o "rapidez por la urgencia"). De lo contrario, es preferible un video grabado tradicionalmente (incluso si es menos "profesional" en la producción) para los mensajes directos de Clara. Podría usarse para videos explicativos de la iniciativa de VIH con un narrador, pero no para la respuesta directa de Clara a las acusaciones.

*   **Grok 4.20 (IA LLM) sin supervisión humana estricta:**
    *   **Riesgo:** Su capacidad para "ángulos no obvios" puede llevar a ideas brillantes, pero también a sugerencias irresponsables, éticamente cuestionables o culturalmente insensibles. En una crisis de nivel ROJO, un error en la estrategia puede ser fatal.
    *   **Recomendación:** Usarlo exclusivamente para brainstorming interno y siempre con un equipo de estrategas experimentados que filtren y validen cada idea antes de considerarla. Nunca permitir que Grok genere contenido directamente para publicación sin revisión humana profunda.

*   **Filtrar dato del PAN-Kanasín vía terceros (Fase 3: Contraataque):**
    *   **Riesgo (no de una herramienta específica, sino de la acción):** Si bien es parte del plan, la ejecución de esta fase debe ser extremadamente cautelosa. Usar herramientas como GPT-5.4 o Claude Opus para *generar* información falsa o engañosa para filtrar es ilegal, antiético y podría desatar una crisis aún mayor si se descubre.
    *   **Recomendación:** Las IAs deben usarse para *analizar información existente* (obtenida quizás vía SecurityTrails o Perplexity), *identificar puntos débiles* en la narrativa del oponente, y *formular cómo presentar esa información verificada* a terceros de manera estratégica. Nunca para fabricar datos. La fuente del "dato" debe ser real y verificable, aunque su filtración sea estratégica.

*   **Herramientas no aplicables (Meshy AI, Fashn AI, Keepa, Have I Been Pwned, Best Buy, PayPal, RevenueCat):**
    *   **Riesgo:** Desperdicio de tiempo y recursos del equipo de crisis en un momento crítico.
    *   **Recomendación:** Ignorarlas por completo. Su funcionalidad no tiene ninguna utilidad en este contexto de crisis política.

---

La Operación YAXCHÉ exige una ejecución impecable. Con estas herramientas y un equipo bien coordinado, tenemos la capacidad de controlar la narrativa y proteger la reputación de Clara Rosales Montiel. ¡Manos a la obra!