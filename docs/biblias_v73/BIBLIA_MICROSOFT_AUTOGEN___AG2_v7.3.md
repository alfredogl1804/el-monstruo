# BIBLIA DE MICROSOFT_AUTOGEN___AG2 v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>AG2 (anteriormente AutoGen)</td></tr>
<tr><td>Desarrollador</td><td>AG2.ai (creadores originales de AutoGen)</td></tr>
<tr><td>País de Origen</td><td>No especificado, pero con raíces en la investigación de Microsoft.</td></tr>
<tr><td>Inversión y Financiamiento</td><td>No disponible públicamente.</td></tr>
<tr><td>Modelo de Precios</td><td>Open source en su núcleo; soluciones empresariales a escala (Request Access).</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Plataforma de inteligencia multi-agente de código abierto para construir, orquestar y evolucionar sistemas de agentes de IA como fuerza de trabajo de IA. Se posiciona como un sistema operativo de IA agéntico (AgentOS) para construir, orquestar y desplegar sistemas de IA multi-agente [1].</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Depende de modelos de lenguaje grandes (LLMs) como OpenAI, Google ADK, y frameworks como LangChain para la interoperabilidad [1].</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con diversos LLMs y frameworks de IA.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>No disponibles públicamente para la versión open source.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>Open-source (detalles específicos de la licencia no encontrados, pero se asume una licencia permisiva común para proyectos de este tipo, como MIT o Apache 2.0) [1].</td></tr>
<tr><td>Política de Privacidad</td><td>No disponible públicamente para el framework open source; se aplicaría a soluciones empresariales específicas [1].</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>No especificado para el framework open source.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>No disponible públicamente.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>No disponible públicamente.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>Comunidad de desarrolladores para el proyecto open source; equipo de AG2.ai para la dirección estratégica y soluciones empresariales.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No disponible públicamente.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

AG2 promueve un **paradigma de construcción de sistemas, no de prompts**, donde la inteligencia multi-agente se orquesta a escala. Se enfoca en la creación de un tiempo de ejecución universal donde agentes especializados actúan como un equipo cohesivo, eliminando los silogismos entre "islas de inteligencia" [1]. El dominio de AG2 implica comprender cómo los agentes de IA pueden colaborar y comunicarse para resolver tareas complejas de manera autónoma o con intervención humana. La clave es diseñar flujos de trabajo agénticos deterministas y dinámicos para procesos de negocio y la investigación en colaboración multi-agente [1].

<table header-row="true">
<tr><td>Paradigma Central</td><td>Construcción de sistemas multi-agente, no prompts. Orquestación de agentes de IA como una fuerza de trabajo cohesiva.</td></tr>
<tr><td>Abstracciones Clave</td><td>Agentes, conversaciones entre agentes, flujos de trabajo agénticos, AgentOS.</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Pensamiento sistémico, diseño de interacciones entre agentes, identificación de roles y responsabilidades de agentes, iteración y refinamiento de flujos de trabajo.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Tratar a los agentes como cajas negras, depender excesivamente de un solo agente, ignorar la coordinación y comunicación entre agentes, no definir claramente los objetivos y criterios de éxito.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada para desarrolladores familiarizados con IA y programación; requiere comprensión de conceptos de sistemas multi-agente y orquestación.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>Construcción de agentes de IA, facilitación de la cooperación entre múltiples agentes, orquestación de sistemas multi-agente, interoperabilidad con frameworks como Google ADK, OpenAI, LangChain [1].</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Gestión unificada del estado ("shared brain") a través de ciclos de vida de tareas, protocolos estandarizados (A2A y MCPs) con seguridad empresarial integrada, coordinación multiplataforma para ensamblar equipos dinámicos de personas especializadas [1].</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Se espera una mayor integración con sistemas empresariales existentes, mejoras en la auditoría de decisiones y trazabilidad, y optimización del rendimiento para despliegues a gran escala.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>La complejidad de la orquestación multi-agente puede escalar rápidamente; la depuración de interacciones complejas entre agentes puede ser un desafío.</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap se centra en la evolución de AgentOS para construir, orquestar y desplegar sistemas de IA multi-agente a escala [1].</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Python (principalmente), posiblemente otros lenguajes para integraciones específicas. Utiliza LLMs y frameworks de IA externos.</td></tr>
<tr><td>Arquitectura Interna</td><td>Basada en un sistema operativo agéntico (AgentOS) que proporciona un tiempo de ejecución universal para agentes especializados.</td></tr>
<tr><td>Protocolos Soportados</td><td>A2A (Agent-to-Agent), MCPs (Model Context Protocols) [1].</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>Depende de los agentes y LLMs integrados, pero generalmente texto, JSON, y otros formatos de datos estructurados.</td></tr>
<tr><td>APIs Disponibles</td><td>API para la creación y gestión de agentes, API para la orquestación de flujos de trabajo multi-agente.</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Automatización de un proceso de soporte al cliente.</td></tr>
<tr><td>Pasos Exactos</td><td>1. Agente de recepción clasifica la consulta del cliente. 2. Agente de conocimiento busca soluciones en la base de datos. 3. Agente de comunicación interactúa con el cliente para recopilar más información o proporcionar una solución. 4. Agente de escalada interviene si la solución no es satisfactoria.</td></tr>
<tr><td>Herramientas Necesarias</td><td>AG2 AgentOS, LLM (ej. GPT-4), base de datos de conocimiento, sistema de ticketing.</td></tr>
<tr><td>Tiempo Estimado</td><td>Variable, desde minutos hasta horas, dependiendo de la complejidad del caso.</td></tr>
<tr><td>Resultado Esperado</td><td>Resolución eficiente de consultas de clientes, reducción del tiempo de respuesta, mejora de la satisfacción del cliente.</td></tr>
<tr><td>Caso de Uso</td><td>Generación de código y pruebas.</td></tr>
<tr><td>Pasos Exactos</td><td>1. Agente de planificación descompone la tarea de desarrollo. 2. Agente de codificación genera el código. 3. Agente de pruebas escribe y ejecuta pruebas unitarias. 4. Agente de depuración identifica y corrige errores.</td></tr>
<tr><td>Herramientas Necesarias</td><td>AG2 AgentOS, LLM (ej. Claude 3 Opus), IDE, framework de pruebas.</td></tr>
<tr><td>Tiempo Estimado</td><td>Horas a días, dependiendo de la complejidad del módulo.</td></tr>
<tr><td>Resultado Esperado</td><td>Código funcional y bien probado, reducción del ciclo de desarrollo.</td></tr>
<tr><td>Caso de Uso</td><td>Análisis de mercado y generación de informes.</td></tr>
<tr><td>Pasos Exactos</td><td>1. Agente de recopilación de datos extrae información de diversas fuentes (noticias, redes sociales, informes). 2. Agente de análisis procesa y sintetiza los datos. 3. Agente de redacción genera un informe estructurado. 4. Agente de visualización crea gráficos y tablas.</td></tr>
<tr><td>Herramientas Necesarias</td><td>AG2 AgentOS, LLM, APIs de datos de mercado, herramientas de visualización.</td></tr>
<tr><td>Tiempo Estimado</td><td>Días a semanas, dependiendo de la profundidad del análisis.</td></tr>
<tr><td>Resultado Esperado</td><td>Informes de mercado completos y perspicaces, apoyo a la toma de decisiones estratégicas.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>Rendimiento en tareas de colaboración multi-agente.</td></tr>
<tr><td>Score/Resultado</td><td>No hay benchmarks estandarizados públicamente disponibles para AG2 específicamente, pero se espera un rendimiento comparable o superior a AutoGen en tareas de orquestación de agentes [1].</td></tr>
<tr><td>Fecha</td><td>Abril 2026.</td></tr>
<tr><td>Fuente</td><td>Observaciones de la comunidad y declaraciones de los desarrolladores de AG2.ai [1].</td></tr>
<tr><td>Comparativa</td><td>AutoGen (Microsoft), LangChain, CrewAI.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>APIs, SDKs, conectores directos.</td></tr>
<tr><td>Protocolo</td><td>HTTP/HTTPS, A2A, MCPs.</td></tr>
<tr><td>Autenticación</td><td>Tokens API, OAuth (dependiendo del servicio integrado).</td></tr>
<tr><td>Latencia Típica</td><td>Variable, depende de la complejidad de la tarea y los servicios externos.</td></tr>
<tr><td>Límites de Rate</td><td>Depende de los límites de los servicios externos integrados (ej. OpenAI API).</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>Pruebas unitarias de agentes individuales.</td></tr>
<tr><td>Herramienta Recomendada</td><td>Pytest, unittest.</td></tr>
<tr><td>Criterio de Éxito</td><td>El agente realiza su tarea específica correctamente y maneja excepciones.</td></tr>
<tr><td>Frecuencia</td><td>Durante el desarrollo y antes de cada despliegue.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de integración de flujos de trabajo multi-agente.</td></tr>
<tr><td>Herramienta Recomendada</td><td>Frameworks de pruebas personalizados, simulaciones.</td></tr>
<tr><td>Criterio de Éxito</td><td>El sistema multi-agente completa la tarea de extremo a extremo según lo esperado.</td></tr>
<tr><td>Frecuencia</td><td>Antes de cada despliegue importante.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de rendimiento y escalabilidad.</td></tr>
<tr><td>Herramienta Recomendada</td><td>Herramientas de benchmarking, pruebas de carga.</td></tr>
<tr><td>Criterio de Éxito</td><td>El sistema mantiene el rendimiento bajo carga y escala eficientemente.</td></tr>
<tr><td>Frecuencia</td><td>Periódicamente y antes de despliegues a gran escala.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>v0.1 (versión inicial de AG2 como proyecto independiente)</td></tr>
<tr><td>Fecha de Lanzamiento</td><td>Noviembre de 2024 (fecha de la bifurcación de AutoGen) [1].</td></tr>
<tr><td>Estado</td><td>Activo, en desarrollo continuo.</td></tr>
<tr><td>Cambios Clave</td><td>Separación de la base de código original de AutoGen, enfoque en AgentOS y orquestación multi-agente.</td></tr>
<tr><td>Ruta de Migración</td><td>Para usuarios de AutoGen, la migración a AG2 implica la adaptación a la nueva base de código y las filosofías de diseño de AG2.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>Microsoft AutoGen.</td></tr>
<tr><td>Ventaja vs Competidor</td><td>AG2 se posiciona como una evolución de AutoGen, con un enfoque más amplio en la orquestación de sistemas multi-agente y un AgentOS universal [1].</td></tr>
<tr><td>Desventaja vs Competidor</td><td>Menor respaldo corporativo directo de Microsoft en comparación con AutoGen.</td></tr>
<tr><td>Caso de Uso Donde Gana</td><td>Proyectos que requieren una orquestación multi-agente más flexible y un AgentOS abierto.</td></tr>
<tr><td>Competidor Directo</td><td>LangChain.</td></tr>
<tr><td>Ventaja vs Competidor</td><td>AG2 se enfoca más en la colaboración y orquestación de agentes autónomos, mientras que LangChain se centra en la construcción de cadenas de prompts y componentes de LLM.</td></tr>
<tr><td>Desventaja vs Competidor</td><td>LangChain tiene una comunidad más grande y una adopción más amplia en ciertos casos de uso.</td></tr>
<tr><td>Caso de Uso Donde Gana</td><td>Sistemas complejos donde la interacción y la autonomía de múltiples agentes son críticas.</td></tr>
<tr><td>Competidor Directo</td><td>CrewAI.</td></tr>
<tr><td>Ventaja vs Competidor</td><td>AG2 ofrece una infraestructura más fundamental a través de su AgentOS, permitiendo una mayor personalización y control sobre la orquestación.</td></tr>
<tr><td>Desventaja vs Competidor</td><td>CrewAI puede ser más rápido para prototipar flujos de trabajo de agentes simples.</td></tr>
<tr><td>Caso de Uso Donde Gana</td><td>Desarrollo de sistemas multi-agente a medida con requisitos de escalabilidad y seguridad.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>Orquestación de agentes de IA, colaboración multi-agente, toma de decisiones autónoma.</td></tr>
<tr><td>Modelo Subyacente</td><td>Utiliza diversos LLMs (ej. GPT-4, Claude 3, Gemini) y otros modelos de IA como componentes.</td></tr>
<tr><td>Nivel de Control</td><td>Alto nivel de control sobre la definición de agentes, sus roles, sus capacidades y sus interacciones.</td></tr>
<tr><td>Personalización Posible</td><td>Extensa personalización de agentes, flujos de trabajo, modelos de IA utilizados y protocolos de comunicación.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Eficiencia en la resolución de tareas complejas.</td></tr>
<tr><td>Valor Reportado por Comunidad</td><td>Se reporta una mejora significativa en la automatización de tareas y la productividad [1].</td></tr>
<tr><td>Fuente</td><td>Testimonios de usuarios y estudios de caso publicados por AG2.ai [1].</td></tr>
<tr><td>Fecha</td><td>Abril 2026.</td></tr>
<tr><td>Métrica</td><td>Facilidad de uso y curva de aprendizaje.</td></tr>
<tr><td>Valor Reportado por Comunidad</td><td>Considerado moderado, requiere familiaridad con conceptos de IA y programación.</td></tr>
<tr><td>Fuente</td><td>Discusiones en foros y comunidades de desarrolladores.</td></tr>
<tr><td>Fecha</td><td>Abril 2026.</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Open Source Core con soluciones empresariales y soporte.</td></tr>
<tr><td>Precio</td><td>Gratuito para el uso open source; precios basados en suscripción o licencias para soluciones empresariales.</td></tr>
<tr><td>Límites</td><td>Versión open source puede tener limitaciones en escalabilidad y soporte; soluciones empresariales ofrecen mayores capacidades.</td></tr>
<tr><td>Ideal Para</td><td>Desarrolladores, investigadores, empresas que buscan construir sistemas multi-agente personalizados y escalables.</td></tr>
<tr><td>ROI Estimado</td><td>Reducción de costos operativos, aumento de la productividad, aceleración del desarrollo de IA.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Resistencia a ataques de inyección de prompts en agentes.</td></tr>
<tr><td>Resultado</td><td>La robustez depende de la implementación específica de los agentes y los LLMs subyacentes.</td></tr>
<tr><td>Fortaleza Identificada</td><td>La arquitectura modular permite implementar capas de seguridad y validación en cada agente.</td></tr>
<tr><td>Debilidad Identificada</td><td>Vulnerabilidades heredadas de los LLMs subyacentes pueden persistir si no se mitigan activamente.</td></tr>
<tr><td>Escenario de Test</td><td>Comportamiento inesperado o emergente en interacciones multi-agente.</td></tr>
<tr><td>Resultado</td><td>Posibilidad de comportamientos emergentes no deseados en sistemas complejos.</td></tr>
<tr><td>Fortaleza Identificada</td><td>La capacidad de orquestación permite definir reglas y restricciones para guiar las interacciones.</td></tr>
<tr><td>Debilidad Identificada</td><td>La depuración de comportamientos emergentes puede ser compleja debido a la naturaleza distribuida del sistema.</td></tr>
</table>

### Referencias
[1] AG2.ai. (n.d.). *AG2: Build Systems, Not Prompts | Open-Source Multi-Agent AI Framework*. Recuperado de https://ag2.ai/