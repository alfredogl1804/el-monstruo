# BIBLIA DE PORTKEY v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>Portkey AI</td></tr>
<tr><td>Desarrollador</td><td>Portkey AI Software India Private Limited</td></tr>
<tr><td>País de Origen</td><td>India</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Inicialmente financiado por inversores de capital de riesgo. Adquirido por Palo Alto Networks en abril de 2026. Detalles específicos de rondas de financiación previas a la adquisición se encuentran en plataformas como Crunchbase y Pitchbook.</td></tr>
<tr><td>Modelo de Precios</td><td>Basado en el uso (logs registrados, retención de datos). Ofrece un nivel gratuito y planes de pago escalonados con sobrecargos por uso adicional. Precios detallados disponibles en portkey.ai/pricing.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Plataforma de infraestructura de IA lista para producción, plano de control unificado para IA en producción, puerta de enlace de IA (AI Gateway) para constructores de Gen AI. Se enfoca en la gestión, monitoreo y optimización de despliegues de modelos de lenguaje grandes (LLM).</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Depende de proveedores de modelos de lenguaje grandes (LLM) como OpenAI, Anthropic, Google, Meta, Mistral, etc., así como de plataformas de nube (AWS, Azure, GCP) para despliegue y escalabilidad. También se integra con herramientas de desarrollo y CI/CD.</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con más de 250 modelos de IA de más de 40 proveedores (incluyendo OpenAI GPT-4, Claude, Gemini, Llama, Mistral). Soporta más de 50 guardrails de IA. Integración con OpenAI-like APIs.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>Como plataforma de infraestructura crítica, Portkey ofrece SLOs empresariales que garantizan alta disponibilidad, baja latencia y rendimiento consistente. Los detalles específicos varían según el contrato empresarial, pero típicamente incluyen garantías de tiempo de actividad (ej. 99.9%), rendimiento de API y soporte técnico.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>Portkey AI Gateway es de código abierto (disponible en GitHub). Las ofertas de plataforma empresarial tienen términos de licencia comercial.</td></tr>
<tr><td>Política de Privacidad</td><td>Disponible en portkey.ai/privacy-policy. Detalla la recopilación, uso y protección de datos personales, así como los derechos de privacidad del usuario.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Cumple con estándares de seguridad y privacidad como SOC2 Tipo 2, ISO 27001, GDPR y HIPAA (para el plan Enterprise). Ofrece BAA Signing para cumplimientos.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Auditorías de seguridad regulares para mantener las certificaciones. Todos los datos en tránsito hacia y desde Portkey AI están cifrados usando TLS 1.2 o superior. Cifrado AES-256 para datos en reposo.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Implementa procesos de respuesta a incidentes para abordar rápidamente cualquier brecha de seguridad o problema de datos. Los detalles específicos del proceso están documentados internamente y se comunican a los clientes empresariales según sea necesario.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>La autoridad de decisión sobre la plataforma y las características de seguridad recae en el equipo de liderazgo de producto y seguridad de Portkey AI, con aportes de los equipos de ingeniería y cumplimiento. Tras la adquisición, Palo Alto Networks influye en las decisiones estratégicas de seguridad.</td></tr>
<tr><td>Política de Obsolescencia</td><td>Portkey se compromete a mantener la compatibilidad con versiones anteriores y a proporcionar avisos claros y oportunos sobre la obsolescencia de características o APIs. Los detalles específicos se comunican a través de la documentación y los canales de soporte.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Portkey AI se concibe como el "plano de control unificado" o "puerta de enlace" (Gateway) para aplicaciones de Inteligencia Artificial Generativa. Su modelo mental se basa en abstraer la complejidad de interactuar con múltiples proveedores de LLMs, proporcionando una capa intermedia que maneja el enrutamiento, la observabilidad, la seguridad (guardrails) y la gestión de prompts. Para dominar Portkey, los desarrolladores deben pensar en términos de "políticas de enrutamiento" y "tuberías de observabilidad" en lugar de llamadas directas a APIs de modelos específicos.

<table header-row="true">
<tr><td>Paradigma Central</td><td>Middleware de IA / AI Gateway. Actúa como un proxy inteligente entre la aplicación del usuario y los proveedores de modelos de IA.</td></tr>
<tr><td>Abstracciones Clave</td><td>Virtual Keys (claves virtuales para gestionar acceso a proveedores), Configs (configuraciones de enrutamiento y fallbacks), Guardrails (reglas de validación de entrada/salida), Traces (trazas de observabilidad).</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>Diseñar para la resiliencia (usar fallbacks y reintentos automáticos), centralizar la gestión de prompts, desacoplar la lógica de la aplicación de los proveedores de LLM específicos.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>Hardcodear claves de API de proveedores directamente en el código de la aplicación, ignorar la observabilidad en producción, depender de un solo proveedor de LLM sin configurar fallbacks.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada. La integración básica (cambiar la URL base de la API) es muy rápida (minutos). Dominar características avanzadas como enrutamiento complejo, guardrails personalizados y análisis de observabilidad requiere más tiempo y comprensión de la arquitectura de la plataforma.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>AI Gateway (enrutamiento a 250+ LLMs), Balanceo de Carga, Fallbacks Automáticos, Caching, Observabilidad (registro de requests/responses, costos, rendimiento), Guardrails (seguridad, cumplimiento), Gestión de Prompts.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>Virtual Keys para gestión de acceso, Control de Acceso basado en Roles (RBAC), Anonymizer de PII, Hosting gestionado en VPC, SSO con Okta Auth, Análisis de costos por caso de uso, Network Level Guardrails, Integración con plataformas de MLOps y observabilidad (ej. Arize Phoenix).</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>Agent Gateway (gobernanza, observabilidad y control para agentes de IA), soporte para más de 1600 modelos de lenguaje, visión, audio e imagen, integración mejorada con Prisma AIRS Platform de Palo Alto Networks para seguridad avanzada.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>La complejidad de la configuración de guardrails y políticas de enrutamiento puede requerir experiencia. El rendimiento puede depender de la latencia de los proveedores de LLM subyacentes. La personalización profunda de ciertos aspectos puede requerir soluciones a medida.</td></tr>
<tr><td>Roadmap Público</td><td>Continuar expandiendo el soporte de modelos y proveedores de IA. Mejorar las capacidades de Agent Gateway. Profundizar la integración con soluciones de seguridad empresarial (como Prisma AIRS). Mejorar las herramientas de optimización de costos y rendimiento. Desarrollar características para la gestión de modelos multimodales.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>Principalmente TypeScript para el desarrollo del AI Gateway (conocido por su rendimiento y flexibilidad). Utiliza tecnologías de nube para escalabilidad y despliegue.</td></tr>
<tr><td>Arquitectura Interna</td><td>Funciona como una capa de middleware (AI Gateway) entre las aplicaciones del usuario y los proveedores de LLM. Emplea una arquitectura distribuida para manejar el enrutamiento, balanceo de carga, caching y observabilidad. El Gateway es de código abierto.</td></tr>
<tr><td>Protocolos Soportados</td><td>Principalmente HTTP/S para las llamadas a la API. Soporta OIDC para Single Sign-On (SSO) en planes empresariales.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>JSON para las solicitudes y respuestas de la API. Compatible con los formatos de entrada/salida de los diversos modelos de LLM a los que se conecta.</td></tr>
<tr><td>APIs Disponibles</td><td>Inference API (para interactuar con LLMs a través del Gateway), Management APIs (para configurar el Gateway, gestionar claves virtuales, guardrails, etc.). SDKs oficiales para Python y Node.js, y compatible con librerías de OpenAI Python/Node.js.</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>Gestión Centralizada de Prompts y Observabilidad de Costos</td><td>Pasos Exactos</td><td>1. Integrar el AI Gateway de Portkey en la aplicación existente (cambiando la URL base de la API). 2. Centralizar todos los prompts en el Prompt Engineering Studio de Portkey. 3. Configurar tags y metadatos para cada caso de uso. 4. Monitorear el panel de observabilidad de Portkey para rastrear el uso, el rendimiento y los costos por caso de uso.</td><td>Herramientas Necesarias</td><td>Portkey AI Gateway, Portkey Prompt Engineering Studio, Panel de Observabilidad de Portkey.</td><td>Tiempo Estimado</td><td>Configuración inicial: 1-2 horas. Monitoreo continuo: Diario/Semanal.</td><td>Resultado Esperado</td><td>Visibilidad completa sobre el uso de LLM, optimización de costos, gestión eficiente de prompts y mejora continua del rendimiento.</td></tr>
<tr><td>Caso de Uso</td><td>Implementación de Balanceo de Carga y Fallbacks para Resiliencia</td><td>Pasos Exactos</td><td>1. Configurar múltiples proveedores de LLM en Portkey. 2. Definir políticas de balanceo de carga (ej. round-robin, latencia mínima) entre los proveedores. 3. Establecer reglas de fallback automático a un proveedor o modelo alternativo en caso de fallos (ej. errores de API, timeouts). 4. Probar los escenarios de fallo para asegurar la resiliencia.</td><td>Herramientas Necesarias</td><td>Portkey AI Gateway, Configuración de Fallbacks y Balanceo de Carga de Portkey.</td><td>Tiempo Estimado</td><td>2-4 horas.</td><td>Resultado Esperado</td><td>Alta disponibilidad de la aplicación de IA, reducción del tiempo de inactividad, mejora de la experiencia del usuario frente a interrupciones del proveedor.</td></tr>
<tr><td>Caso de Uso</td><td>A/B Testing de Prompts y Modelos para Optimización</td><td>Pasos Exactos</td><td>1. Definir dos o más variantes de prompts o modelos a probar en el Prompt Engineering Studio de Portkey. 2. Configurar el AI Gateway para enrutar un porcentaje del tráfico a cada variante (ej. 50/50). 3. Recopilar métricas de rendimiento (ej. latencia, costo, calidad de respuesta) para cada variante a través del panel de observabilidad. 4. Analizar los resultados para identificar la variante con mejor rendimiento.</td><td>Herramientas Necesarias</td><td>Portkey Prompt Engineering Studio, Portkey AI Gateway, Panel de Observabilidad de Portkey.</td><td>Tiempo Estimado</td><td>Configuración: 1-2 horas. Duración del test: Días/Semanas (dependiendo del tráfico). Análisis: 1-2 horas.</td><td>Resultado Esperado</td><td>Optimización de la calidad de las respuestas de LLM, reducción de costos, mejora del rendimiento de la aplicación de IA.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>Latencia del AI Gateway</td><td>Score/Resultado</td><td>~3ms de latencia a 250 RPS por pod, escalable linealmente.</td><td>Fecha</td><td>Febrero 2026</td><td>Fuente</td><td>TrueFoundry vs Portkey: Choosing the Best AI Gateway</td><td>Comparativa</td><td>Comparado favorablemente con LiteLLM y Kong AI Gateway en benchmarks de rendimiento.</td></tr>
<tr><td>Benchmark</td><td>Uptime</td><td>Score/Resultado</td><td>99.9999% (reclamado para opciones comerciales)</td><td>Fecha</td><td>Desconocida (afirmación general)</td><td>Fuente</td><td>AI Gateway Comparison 2026: LiteLLM vs Portkey vs Kong vs 5 More</td><td>Comparativa</td><td>Considerado una de las opciones comerciales más fuertes para fiabilidad gestionada.</td></tr>
<tr><td>Benchmark</td><td>Optimización de Costos</td><td>Score/Resultado</td><td>Reducción significativa de costos mediante caching y enrutamiento inteligente.</td><td>Fecha</td><td>Octubre 2025</td><td>Fuente</td><td>Why I Chose Portkey's AI gateway for Managing Multiple AI Providers</td><td>Comparativa</td><td>Permite a los usuarios encontrar el modelo óptimo para cada paso de procesamiento, mejorando la eficiencia.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>SDKs oficiales (Python, Node.js), compatible con OpenAI SDK (mediante cambio de URL base), REST API directa. Integración con frameworks de agentes populares y SDKs.</td></tr>
<tr><td>Protocolo</td><td>Principalmente HTTP/S para la comunicación con el Gateway y los proveedores de LLM.</td></tr>
<tr><td>Autenticación</td><td>Token-based authentication para acceso a la API de Portkey. Soporte para Single Sign-On (SSO) vía OIDC en planes empresariales. Las claves de API de los proveedores de LLM se gestionan de forma segura a través de Virtual Keys.</td></tr>
<tr><td>Latencia Típica</td><td>~3ms de latencia adicional introducida por el Gateway (a 250 RPS por pod), con un enfoque en minimizar el impacto en el rendimiento general.</td></tr>
<tr><td>Límites de Rate</td><td>Portkey permite a los usuarios configurar límites de rate personalizados para sus aplicaciones y para cada proveedor de LLM. Los límites de rate inherentes de los proveedores de LLM subyacentes se gestionan y se pueden configurar fallbacks para mitigar su impacto.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>A/B Testing de Prompts y Modelos</td><td>Herramienta Recomendada</td><td>Portkey Prompt Engineering Studio, Portkey AI Gateway, Panel de Observabilidad de Portkey.</td><td>Criterio de Éxito</td><td>Mejora en métricas clave como latencia, costo, calidad de respuesta o tasa de éxito de la tarea.</td><td>Frecuencia</td><td>Según sea necesario para optimización continua de prompts y evaluación de nuevos modelos.</td></tr>
<tr><td>Tipo de Test</td><td>Canary Testing</td><td>Herramienta Recomendada</td><td>Portkey AI Gateway.</td><td>Criterio de Éxito</td><td>El nuevo modelo o prompt no introduce regresiones o degradaciones significativas en el rendimiento o la experiencia del usuario.</td><td>Frecuencia</td><td>Al desplegar nuevas versiones de modelos o prompts en producción.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de Resiliencia (Fallbacks)</td><td>Herramienta Recomendada</td><td>Portkey AI Gateway.</td><td>Criterio de Éxito</td><td>La aplicación continúa funcionando sin interrupciones o con degradación mínima ante fallos de proveedores de LLM.</td><td>Frecuencia</td><td>Periódicamente y después de cambios significativos en la configuración del Gateway o de los proveedores.</td></tr>
<tr><td>Tipo de Test</td><td>Pruebas de Integración MCP</td><td>Herramienta Recomendada</td><td>Portkey-AI/hoot (herramienta de testing MCP).</td><td>Criterio de Éxito</td><td>Comunicación exitosa y consistente con los servidores MCP, depuración eficiente de interacciones.</td><td>Frecuencia</td><td>Durante el desarrollo y la integración de nuevos agentes o herramientas MCP.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>AI Gateway (Open Source)</td><td>Fecha de Lanzamiento</td><td>Marzo 2026 (open-source)</td><td>Estado</td><td>Activo, en desarrollo continuo</td><td>Cambios Clave</td><td>Lanzamiento como proyecto de código abierto, integración con más de 1600 modelos, soporte para MCP.</td><td>Ruta de Migración</td><td>Para usuarios de versiones anteriores o propietarios, la migración implica la adopción del código abierto y la configuración de las nuevas características.</td></tr>
<tr><td>Versión</td><td>Portkey Python SDK v0.1.44</td><td>Fecha de Lanzamiento</td><td>Abril 2026 (estable)</td><td>Estado</td><td>Activo, estable</td><td>Cambios Clave</td><td>Versión estable con mejoras en la facilidad de uso para construir aplicaciones de IA listas para producción.</td><td>Ruta de Migración</td><td>Actualización de paquetes a través de pip para versiones anteriores del SDK.</td></tr>
<tr><td>Versión</td><td>Portkey Enterprise (general)</td><td>Fecha de Lanzamiento</td><td>Continuo (actualizaciones mensuales/trimestrales)</td><td>Estado</td><td>Activo, con soporte empresarial</td><td>Cambios Clave</td><td>Adición de soporte para Workload Identity Federation (AWS-GCP), nuevas variables de entorno, mejoras en la interfaz de usuario y soporte para nuevos modelos de LLM.</td><td>Ruta de Migración</td><td>Actualizaciones gestionadas por el equipo de Portkey para clientes empresariales, con guías de migración para cambios mayores.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>LiteLLM</td><td>Ventaja vs Competidor</td><td>Portkey ofrece una plataforma más robusta y completa para operaciones de IA en producción, con observabilidad avanzada, gestión de prompts y guardrails integrados. Mayor enfoque en la preparación empresarial.</td><td>Desventaja vs Competidor</td><td>LiteLLM puede ser más ligero y fácil de configurar para casos de uso más simples o prototipos. Algunos usuarios han reportado que Portkey puede ser más costoso para ciertas configuraciones empresariales (ej. residencia de datos en la UE, SSO).</td><td>Caso de Uso Donde Gana</td><td>Equipos que necesitan una plataforma de producción con gobernanza, observabilidad profunda y fiabilidad gestionada para despliegues de IA a escala empresarial.</td></tr>
<tr><td>Competidor Directo</td><td>Kong AI Gateway</td><td>Ventaja vs Competidor</td><td>Portkey está diseñado específicamente para flujos de trabajo de aplicaciones LLM, ofreciendo características nativas como gestión de prompts, guardrails y observabilidad de IA.</td><td>Desventaja vs Competidor</td><td>Kong AI Gateway, siendo una solución más general de API Gateway, ha mostrado menor latencia en algunos benchmarks (65% menor que Portkey en ciertas condiciones).</td><td>Caso de Uso Donde Gana</td><td>Empresas que buscan una solución especializada en IA con un control granular sobre los LLMs y una experiencia de desarrollo optimizada para Gen AI.</td></tr>
<tr><td>Competidor Directo</td><td>Cloudflare AI Gateway</td><td>Ventaja vs Competidor</td><td>Portkey ofrece un conjunto de características más amplio y profundo para la gestión de LLMs, incluyendo balanceo de carga, fallbacks, caching y un estudio de ingeniería de prompts.</td><td>Desventaja vs Competidor</td><td>Cloudflare AI Gateway puede ser más rápido de configurar para usuarios que ya están en el ecosistema de Cloudflare.</td><td>Caso de Uso Donde Gana</td><td>Desarrolladores y empresas que requieren un control más sofisticado y una plataforma dedicada para la gestión y optimización de sus aplicaciones de IA.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>AI Gateway para LLMs</td><td>Modelo Subyacente</td><td>Actúa como proxy para más de 250 modelos de IA de más de 40 proveedores (ej. OpenAI GPT-4, Claude, Gemini, Llama, Mistral).</td><td>Nivel de Control</td><td>Alto. Permite enrutamiento condicional, balanceo de carga, fallbacks, caching, y aplicación de guardrails a nivel de gateway.</td><td>Personalización Posible</td><td>Extensa. Configuración de guardrails personalizados, gestión de prompts, A/B testing de modelos y prompts, y optimización de costos.</td></tr>
<tr><td>Capacidad de IA</td><td>Guardrails de Seguridad</td><td>Modelo Subyacente</td><td>Módulos de seguridad integrados en el Gateway, incluyendo detección de inyección de prompts, exposición de datos sensibles y otras amenazas de seguridad de IA.</td><td>Nivel de Control</td><td>Alto. Más de 60 guardrails predefinidos y la capacidad de crear reglas personalizadas para filtrar, corregir o enrutar solicitudes de LLM.</td><td>Personalización Posible</td><td>Definición de reglas personalizadas para la detección y mitigación de amenazas, configuración de umbrales y acciones automáticas.</td></tr>
<tr><td>Capacidad de IA</td><td>Gestión de Prompts</td><td>Modelo Subyacente</td><td>No se basa en un modelo de IA subyacente para la gestión de prompts, sino en una interfaz y herramientas para organizar, versionar y desplegar prompts.</td><td>Nivel de Control</td><td>Alto. Permite la centralización, versionado y despliegue de prompts a través del Prompt Engineering Studio.</td><td>Personalización Posible</td><td>Creación de plantillas de prompts, variables, y la capacidad de realizar A/B testing para optimizar su efectividad.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>Uptime</td><td>Valor Reportado por Comunidad</td><td>99.99% - 99.9999% (afirmaciones de SLA empresarial)</td><td>Fuente</td><td>TrueFoundry, Palo Alto Networks (comunicados de prensa y blogs)</td><td>Fecha</td><td>Febrero 2026, Abril 2026</td></tr>
<tr><td>Métrica</td><td>Latencia Adicional del Gateway</td><td>Valor Reportado por Comunidad</td><td>20-40ms de sobrecarga de latencia (TrueFoundry), ~3ms a 250 RPS por pod (benchmarks).</td><td>Fuente</td><td>TrueFoundry, Kong AI Gateway Benchmark</td><td>Fecha</td><td>Febrero 2026, Julio 2025</td></tr>
<tr><td>Métrica</td><td>Facilidad de Integración</td><td>Valor Reportado por Comunidad</td><td>Muy fácil y rápida integración (ej. "2 líneas de código").</td><td>Fuente</td><td>G2 Reviews, AWS Marketplace Reviews</td><td>Fecha</td><td>2026 (continuo)</td></tr>
<tr><td>Métrica</td><td>Visibilidad y Control (Observabilidad)</td><td>Valor Reportado por Comunidad</td><td>Gran visibilidad y control sobre las operaciones de IA, incluyendo costos y rendimiento.</td><td>Fuente</td><td>G2 Reviews, AWS Marketplace Reviews</td><td>Fecha</td><td>2026 (continuo)</td></tr>
<tr><td>Métrica</td><td>Gestión de Costos</td><td>Valor Reportado por Comunidad</td><td>Ayuda a reducir costos mediante optimización y monitoreo.</td><td>Fuente</td><td>Portkey.ai (testimonios de clientes)</td><td>Fecha</td><td>2026 (continuo)</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>Desarrollador (Gratuito)</td><td>Precio</td><td>Gratis</td><td>Límites</td><td>10k logs registrados por mes.</td><td>Ideal Para</td><td>Prototipos, desarrollo inicial, proyectos personales.</td><td>ROI Estimado</td><td>Ahorro de tiempo en configuración y monitoreo, acceso a funcionalidades básicas de Gateway.</td></tr>
<tr><td>Plan</td><td>Pro</td><td>Precio</td><td>Basado en el uso (ej. $9 por cada 100k requests adicionales después del límite base).</td><td>Límites</td><td>Más allá de los 10k logs, con sobrecargos. Retención de logs de 30 días, retención de trazas de 90 días.</td><td>Ideal Para</td><td>Startups, equipos pequeños que escalan, aplicaciones con volúmenes moderados.</td><td>ROI Estimado</td><td>Optimización de costos de LLM, mejora de la fiabilidad, observabilidad detallada para la toma de decisiones.</td></tr>
<tr><td>Plan</td><td>Enterprise</td><td>Precio</td><td>Personalizado (típicamente $2,000-$10,000+/mes)</td><td>Límites</td><td>Negociados según volumen, retención, modelo de despliegue y nivel de soporte. Incluye características avanzadas como SOC2, ISO27001, GDPR, HIPAA Compliance.</td><td>Ideal Para</td><td>Grandes empresas con necesidades complejas de cumplimiento, seguridad y escalabilidad.</td><td>ROI Estimado</td><td>Reducción de riesgos de seguridad y cumplimiento, gestión eficiente de costos a gran escala, alta disponibilidad y soporte dedicado.</td></tr>
<tr><td>Plan</td><td>Límites de Rate y Presupuesto</td><td>Precio</td><td>Incluido en los planes</td><td>Límites</td><td>Configurables por el usuario (costo-basado en USD o token-basado). Mínimo de $1 o 100 tokens.</td><td>Ideal Para</td><td>Controlar el gasto y prevenir el uso excesivo de APIs de LLM.</td><td>ROI Estimado</td><td>Prevención de gastos inesperados, gestión proactiva de recursos.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>Ataque de Inyección de Prompts</td><td>Resultado</td><td>Detección y mitigación exitosa del ataque.</td><td>Fortaleza Identificada</td><td>Capacidad robusta de los guardrails de Portkey para identificar y bloquear prompts maliciosos o que intentan eludir las instrucciones del sistema.</td><td>Debilidad Identificada</td><td>La efectividad depende de la configuración y actualización continua de los guardrails; nuevos vectores de ataque pueden requerir ajustes.</td></tr>
<tr><td>Escenario de Test</td><td>Exfiltración de Datos Sensibles (PII)</td><td>Resultado</td><td>Prevención de la exfiltración de datos sensibles.</td><td>Fortaleza Identificada</td><td>Funcionalidad de anonimización de PII y controles de acceso basados en roles (RBAC) que limitan la exposición de datos.</td><td>Debilidad Identificada</td><td>Requiere una configuración adecuada de las políticas de anonimización y una identificación precisa de los datos sensibles.</td></tr>
<tr><td>Escenario de Test</td><td>Denegación de Servicio (DoS) a través de LLM</td><td>Resultado</td><td>Manejo de picos de tráfico y prevención de sobrecarga del proveedor de LLM.</td><td>Fortaleza Identificada</td><td>Balanceo de carga, límites de rate y caching del AI Gateway que protegen contra el uso excesivo y ataques DoS.</td><td>Debilidad Identificada</td><td>La capacidad de resistir ataques a gran escala puede depender de la infraestructura subyacente y la configuración de escalabilidad.</td></tr>
<tr><td>Escenario de Test</td><td>Desviación del Comportamiento del Agente de IA</td><td>Resultado</td><td>El Agent Gateway mantiene el comportamiento deseado del agente.</td><td>Fortaleza Identificada</td><td>Las capacidades de gobernanza y observabilidad del Agent Gateway permiten monitorear y controlar el comportamiento de los agentes de IA.</td><td>Debilidad Identilidad</td><td>La complejidad de los agentes de IA puede introducir nuevos desafíos en la detección de desviaciones sutiles.</td></tr>
</table>
