# BIBLIA DE KONG_API_GATEWAY v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>Nombre oficial</td><td>Kong Gateway</td></tr>
<tr><td>Desarrollador</td><td>Kong Inc.</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Kong Inc. ha recibido financiación de varias rondas de inversión de capital de riesgo, incluyendo Andreessen Horowitz, GGV Capital, Index Ventures, entre otros.</td></tr>
<tr><td>Modelo de Precios</td><td>Ofrece una versión de código abierto (Kong Gateway Community) y versiones empresariales (Kong Gateway Enterprise, Kong Konnect) con características adicionales y soporte. El modelo de precios para las versiones empresariales se basa en suscripciones, con diferentes niveles de servicio y funcionalidades.</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Kong Gateway se posiciona como la puerta de enlace API de código abierto más adoptada a nivel mundial, ofreciendo conectividad API rápida y flexible para arquitecturas híbridas, multi-nube y preparadas para IA. Se enfoca en la gestión, seguridad y automatización de APIs para microservicios y arquitecturas distribuidas.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Construido sobre Nginx y OpenResty. Depende de bases de datos como PostgreSQL o Cassandra para almacenamiento de configuración. Utiliza Lua para la lógica de plugins.</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Compatible con entornos on-premise, cloud (AWS, Azure, GCP), Kubernetes, y serverless. Soporta múltiples protocolos y arquitecturas de microservicios.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>Los SLOs específicos varían según el nivel de suscripción de Kong Enterprise, pero generalmente incluyen alta disponibilidad, rendimiento y soporte técnico.</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>Licencia</td><td>Kong Gateway de código abierto está bajo la Licencia Apache 2.0. Las versiones Enterprise tienen licencias comerciales específicas de Kong Inc.</td></tr>
<tr><td>Política de Privacidad</td><td>La política de privacidad de Kong Inc. (disponible en konghq.com/legal) detalla cómo se recopila, usa y protege la información personal y de uso del sitio web y los servicios.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Kong Inc. cumple con las leyes de protección de datos aplicables y los marcos de seguridad de la información SSAE / SOC 2.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Kong Gateway se somete a auditorías de seguridad regulares como parte de su desarrollo y mantenimiento, especialmente para las versiones Enterprise. Los detalles específicos de las auditorías suelen ser confidenciales, pero la empresa mantiene un programa de seguridad robusto.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Kong Inc. tiene un proceso establecido para la respuesta a incidentes de seguridad, que incluye la identificación, contención, erradicación, recuperación y análisis post-incidente. Los clientes de Enterprise tienen acceso a canales de soporte dedicados para reportar y gestionar incidentes.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>Las decisiones sobre el desarrollo del producto, la hoja de ruta y las características son tomadas por el equipo de liderazgo de producto y ingeniería de Kong Inc., con aportes de la comunidad de código abierto para la versión Community.</td></tr>
<tr><td>Política de Obsolescencia</td><td>Kong Inc. publica un ciclo de vida de soporte para sus versiones Enterprise, incluyendo fechas de fin de vida (EOL) para versiones específicas, lo que permite a los usuarios planificar sus actualizaciones y migraciones. (Ej: Kong Gateway Enterprise 3.9 entrará en EOL en Enero de 2026).</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Kong Gateway se concibe como el **punto de control centralizado para todo el tráfico de API y, más recientemente, de IA**. Su modelo mental se basa en la idea de un **proxy inverso inteligente y extensible** que se sitúa entre los clientes y los servicios backend, gestionando la conectividad, la seguridad y la observabilidad de manera desacoplada. Esto permite a los desarrolladores y operadores aplicar políticas de forma consistente y escalar sus arquitecturas de microservicios de manera eficiente. Con la evolución hacia el "Agentic Era", Kong ha ampliado su modelo para incluir la gestión del tráfico de Agente-a-Agente (A2A) y la abstracción de modelos de IA, convirtiéndose en una **puerta de enlace unificada para APIs y IA**.

<table header-row="true">
<tr><td>Paradigma Central</td><td>**Proxy Inverso Extensible**: Actúa como un punto de entrada unificado para gestionar el tráfico hacia múltiples servicios. **Cloud-Native y Platform-Agnostic**: Diseñado para operar en cualquier entorno (on-premise, cloud, Kubernetes, serverless) sin ataduras a una plataforma específica. **Microservicios y Arquitecturas Distribuidas**: Optimizado para la gestión de APIs en entornos complejos y distribuidos. **API y AI Gateway Unificado**: Evolucionando para gestionar no solo APIs tradicionales sino también el tráfico y los modelos de IA.</td></tr>
<tr><td>Abstracciones Clave</td><td>**Servicios**: Representan los servicios backend a los que se proxy el tráfico. **Rutas**: Definen cómo las solicitudes de los clientes se dirigen a los servicios. **Plugins**: Componentes modulares que extienden la funcionalidad del gateway (autenticación, rate limiting, transformaciones, etc.). **Consumidores**: Representan a los usuarios o aplicaciones que acceden a las APIs. **Workspaces**: Permiten la segmentación lógica de APIs y configuraciones para diferentes equipos o entornos. **Control Planes / Data Planes**: Separación de la lógica de control (configuración) y la lógica de ejecución (proxy de tráfico).</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>**Diseño Declarativo**: Configurar Kong mediante archivos YAML/JSON para gestionar el ciclo de vida de las APIs a través de CI/CD (GitOps). **Composición de Funcionalidades con Plugins**: Utilizar la rica biblioteca de plugins o desarrollar plugins personalizados para añadir funcionalidades sin modificar el core del gateway. **Seguridad por Capas**: Implementar políticas de seguridad (autenticación, autorización, rate limiting) en el gateway para proteger los servicios backend. **Observabilidad Centralizada**: Aprovechar las capacidades de logging, métricas y tracing de Kong para monitorear el rendimiento y el comportamiento de las APIs. **Abstracción de Modelos de IA**: Utilizar el AI Gateway para unificar la interacción con diversos modelos de lenguaje grandes (LLMs) y otros servicios de IA.</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>**Gateway Monolítico**: Tratar el gateway como un monolito que maneja toda la lógica de negocio, en lugar de un componente de infraestructura. **Configuración Manual y Ad-hoc**: Evitar cambios manuales directos en producción; preferir la automatización y la configuración declarativa. **Ignorar la Observabilidad**: No monitorear el tráfico del gateway puede llevar a problemas de rendimiento o seguridad no detectados. **Exceso de Lógica en el Gateway**: Aunque es extensible, el gateway no debe convertirse en un sustituto de la lógica de negocio de los microservicios.</td></tr>
<tr><td>Curva de Aprendizaje</td><td>**Moderada a Avanzada**: La curva de aprendizaje es moderada para las funcionalidades básicas (proxy, rutas, plugins comunes). Sin embargo, para la maestría en entornos complejos, personalización avanzada con Lua, desarrollo de plugins, integración con Kubernetes y la gestión de tráfico de IA, requiere un conocimiento más profundo de la arquitectura de Kong y los principios de microservicios. La amplia documentación y la comunidad activa facilitan el aprendizaje.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>Capacidades Core</td><td>**Proxy y Enrutamiento**: Dirige el tráfico de clientes a los servicios backend basándose en reglas configurables. **Balanceo de Carga**: Distribuye las solicitudes entre múltiples instancias de un servicio para optimizar el rendimiento y la disponibilidad. **Autenticación y Autorización**: Soporte para diversos métodos de autenticación (Key Auth, Basic Auth, JWT, OAuth2) y control de acceso. **Rate Limiting**: Controla la cantidad de solicitudes que un cliente puede hacer a un servicio en un período de tiempo determinado. **Transformación de Solicitudes/Respuestas**: Modifica encabezados, cuerpos y parámetros de solicitudes y respuestas. **Observabilidad**: Proporciona capacidades de logging, métricas y tracing para monitorear el tráfico API. **Extensibilidad mediante Plugins**: Arquitectura modular que permite añadir funcionalidades a través de una amplia gama de plugins preconstruidos o personalizados.</td></tr>
<tr><td>Capacidades Avanzadas</td><td>**Gestión de APIs en Kubernetes**: Kong Ingress Controller permite gestionar Kong Gateway de forma nativa en entornos Kubernetes. **Federated API Management**: Gestión de APIs distribuidas a través de múltiples clústeres o entornos. **APIOps/GitOps**: Automatización del ciclo de vida de las APIs mediante configuración declarativa y CI/CD. **Gateway Mocking**: Permite simular respuestas de API para facilitar el desarrollo y las pruebas. **Ordenamiento de Plugins Flexible**: Configuración declarativa del orden de ejecución de los plugins. **Workspaces y Control Planes/Data Planes**: Aislamiento de configuraciones y tráfico para diferentes equipos o entornos. **Resiliencia del Data Plane**: Capacidad de los data planes para arrancar y operar incluso si el control plane falla.</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>**AI Gateway**: Gestión unificada de tráfico para APIs tradicionales y modelos de IA (LLMs, etc.), incluyendo enrutamiento inteligente, seguridad y observabilidad específicas para IA. **Agent-to-Agent (A2A) Traffic Management**: Capacidades para gestionar, asegurar y observar la comunicación entre agentes de IA. **Semantic Caching**: Caché inteligente para respuestas de modelos de IA. **Token Rate Limiting**: Control de consumo de tokens para modelos de IA. **Integración con Modelos de IA Variados**: Soporte nativo para proveedores como OpenAI, Anthropic, Google Vertex AI, Cohere, Ollama, DeepSeek, vLLM, y Databricks. **Guardrails de IA**: Plugins para implementar políticas de seguridad y cumplimiento en las interacciones con IA (ej. ai-aws-guardrails, ai-azure-content-safety, ai-custom-guardrail). **Vector Database Operations**: Soporte para bases de datos vectoriales como Valkey y pgvector.</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>**Dependencia de Base de Datos (Opcional)**: Aunque puede ejecutarse sin base de datos en modo "DB-less", el modo tradicional requiere PostgreSQL o Cassandra, lo que añade complejidad operativa. **Curva de Aprendizaje para Personalización Avanzada**: El desarrollo de plugins personalizados en Lua puede requerir conocimientos específicos y experiencia. **Consumo de Recursos**: Como cualquier proxy inverso, Kong Gateway introduce una pequeña latencia adicional y consume recursos de CPU/memoria, que deben ser considerados en arquitecturas de muy baja latencia. **Gestión de Configuraciones Complejas**: En entornos con un gran número de APIs y políticas, la gestión de la configuración declarativa puede volverse compleja sin herramientas de automatización adecuadas.</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap de Kong Inc. se centra en la **"Agentic Era"**, con un fuerte énfasis en la **conectividad y gobernanza de la IA**. Esto incluye la expansión de las capacidades del AI Gateway, el soporte para más modelos y proveedores de IA, la mejora de las funcionalidades de seguridad y observabilidad para el tráfico de IA, y la integración con ecosistemas de agentes. Continuará mejorando la resiliencia, escalabilidad y rendimiento del gateway, así como la experiencia de desarrollador y operador.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>Stack Tecnológico</td><td>**Core**: Nginx (servidor web de alto rendimiento), OpenResty (extensión de Nginx con LuaJIT), Lua (lenguaje de scripting para plugins). **Base de Datos**: PostgreSQL o Cassandra (para almacenamiento de configuración en modo tradicional), o modo "DB-less" con configuración declarativa. **Contenedores**: Docker. **Orquestación**: Kubernetes.</td></tr>
<tr><td>Arquitectura Interna</td><td>**Control Plane (Plano de Control)**: Gestiona la configuración del gateway, la administración de APIs, plugins, consumidores, etc. Se comunica con la base de datos. **Data Plane (Plano de Datos)**: Es el componente de proxy real que maneja el tráfico de red en tiempo de ejecución. Ejecuta los plugins y aplica las políticas configuradas por el Control Plane. En arquitecturas híbridas o multi-nube, puede haber múltiples Data Planes distribuidos que se conectan a un Control Plane centralizado.</td></tr>
<tr><td>Protocolos Soportados</td><td>**HTTP/HTTPS**: Para APIs RESTful tradicionales. **TCP/TLS**: Para proxy de tráfico de red genérico y seguro. **gRPC/gRPCS**: Para comunicación de microservicios de alto rendimiento. **WebSocket/WebSocket Secure (WS/WSS)**: Para comunicación bidireccional en tiempo real. **MCP (Model Context Protocol)**: Para la gestión de modelos de IA. **A2A (Agent-to-Agent)**: Para la comunicación entre agentes de IA.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>**Configuración**: YAML, JSON (para configuración declarativa). **APIs**: JSON, XML, Protobuf (dependiendo del servicio backend). **Plugins**: Lua (para desarrollo de plugins personalizados). **Métricas**: Prometheus, StatsD. **Logs**: JSON, texto plano.</td></tr>
<tr><td>APIs Disponibles</td><td>**Admin API**: Una API RESTful para configurar y gestionar Kong Gateway (servicios, rutas, plugins, consumidores, etc.). Se utiliza para la automatización y la integración con herramientas de CI/CD. **Proxy API**: La API que exponen los servicios a través de Kong Gateway a los clientes. **AI Gateway API**: APIs específicas para interactuar con modelos de IA, incluyendo enrutamiento a LLMs, gestión de tokens, y guardrails.</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>Caso de Uso</td><td>**Implementación de Rate Limiting para Proteger APIs**</td></tr>
<tr><td>Pasos Exactos</td><td>
1.  **Instalar Kong Gateway**: Desplegar Kong Gateway en el entorno deseado (Docker, Kubernetes, VM).<br>
2.  **Registrar un Servicio**: Configurar un servicio en Kong que apunte al backend de la API a proteger. Ejemplo: `kong config add service my-api --url http://my-backend-service.com`<br>
3.  **Añadir una Ruta**: Asociar una ruta al servicio para que Kong pueda enrutar las solicitudes. Ejemplo: `kong config add route my-api-route --service my-api --paths /my-api`<br>
4.  **Habilitar el Plugin Rate Limiting**: Añadir el plugin `rate-limiting` al servicio o a la ruta, especificando los límites deseados (ej. 5 solicitudes por minuto). Ejemplo: `kong config add plugin my-api --name rate-limiting --config 'minute=5' --config 'policy=local'`<br>
5.  **Probar el Rate Limiting**: Enviar solicitudes a la API a través de Kong y verificar que las solicitudes excedentes son rechazadas con un código de estado 429 (Too Many Requests).
</td></tr>
<tr><td>Herramientas Necesarias</td><td>Kong Gateway, `kong` CLI o Admin API, `curl` o Postman para pruebas.</td></tr>
<tr><td>Tiempo Estimado</td><td>15-30 minutos.</td></tr>
<tr><td>Resultado Esperado</td><td>La API backend está protegida contra sobrecargas por un número excesivo de solicitudes de un mismo cliente, mejorando la estabilidad y disponibilidad del servicio.</td></tr>
<tr><td>Caso de Uso</td><td>**Configuración de Autenticación JWT para APIs Seguras**</td></tr>
<tr><td>Pasos Exactos</td><td>
1.  **Instalar Kong Gateway**: Desplegar Kong Gateway.<br>
2.  **Registrar un Servicio y Ruta**: Configurar el servicio y la ruta para la API a proteger con JWT.<br>
3.  **Habilitar el Plugin JWT**: Añadir el plugin `jwt` al servicio o a la ruta. Ejemplo: `kong config add plugin my-api --name jwt`<br>
4.  **Crear un Consumidor**: Registrar un consumidor en Kong que representará al usuario o aplicación que accederá a la API. Ejemplo: `kong config add consumer my-user --username my-user`<br>
5.  **Configurar Credenciales JWT para el Consumidor**: Asociar credenciales JWT al consumidor, incluyendo una clave secreta y un algoritmo. Ejemplo: `kong config add jwt my-user --algorithm HS256 --secret 'supersecretkey'`<br>
6.  **Generar un Token JWT**: Crear un token JWT válido usando la clave secreta configurada y un payload que incluya el `sub` (subject) del consumidor. Herramientas como `jwt.io` pueden ayudar.<br>
7.  **Probar la Autenticación**: Enviar solicitudes a la API a través de Kong, incluyendo el token JWT en el encabezado `Authorization: Bearer <token>`. Verificar que las solicitudes con tokens válidos son aceptadas y las inválidas son rechazadas con 401 (Unauthorized).
</td></tr>
<tr><td>Herramientas Necesarias</td><td>Kong Gateway, `kong` CLI o Admin API, generador de JWT (ej. `jwt.io`), `curl` o Postman.</td></tr>
<tr><td>Tiempo Estimado</td><td>30-60 minutos.</td></tr>
<tr><td>Resultado Esperado</td><td>La API está protegida, requiriendo un token JWT válido para el acceso, lo que garantiza que solo los clientes autenticados puedan interactuar con ella.</td></tr>
<tr><td>Caso de Uso</td><td>**Despliegue de Kong Gateway en Kubernetes con Ingress Controller**</td></tr>
<tr><td>Pasos Exactos</td><td>
1.  **Configurar un Clúster Kubernetes**: Asegurarse de tener un clúster Kubernetes operativo.<br>
2.  **Instalar Kong Ingress Controller (KIC)**: Desplegar KIC en el clúster Kubernetes. Esto se puede hacer mediante Helm o manifiestos YAML proporcionados por Kong. Ejemplo: `helm install kong kong/kong --namespace kong --create-namespace --set ingressController.enabled=true`<br>
3.  **Configurar un Ingress o Gateway API**: Definir recursos Ingress (o Gateway API si se usa) en Kubernetes para exponer los servicios a través de Kong. Esto incluye especificar las reglas de enrutamiento y los servicios backend. Ejemplo (Ingress):<br>
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: my-api-ingress
      annotations:
        konghq.com/strip-path: "true"
    spec:
      ingressClassName: kong
      rules:
      - http:
          paths:
          - path: /my-api
            pathType: Prefix
            backend:
              service:
                name: my-backend-service
                port:
                  number: 80
    ```<br>
4.  **Desplegar Servicios Backend**: Asegurarse de que los servicios backend estén desplegados y accesibles dentro del clúster Kubernetes.<br>
5.  **Probar el Acceso**: Acceder a la API a través de la IP externa o el nombre de host del Ingress de Kong y verificar que las solicitudes son enrutadas correctamente al servicio backend.
</td></tr>
<tr><td>Herramientas Necesarias</td><td>Kubernetes, `kubectl`, Helm, Kong Ingress Controller.</td></tr>
<tr><td>Tiempo Estimado</td><td>1-2 horas.</td></tr>
<tr><td>Resultado Esperado</td><td>Kong Gateway actúa como el punto de entrada para el tráfico externo a los servicios dentro de Kubernetes, proporcionando gestión de tráfico, seguridad y observabilidad de forma nativa en el ecosistema de Kubernetes.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>Benchmark</td><td>**Rendimiento de Proxy Básico (sin plugins)**</td><td>**Rendimiento con Rate Limiting y Key Auth**</td></tr>
<tr><td>Score/Resultado</td><td>140,382 RPS (Solicitudes por Segundo) con 5.24 ms P99 (percentil 99 de latencia) para 1 Ruta, 0 Consumidores.</td><td>95,660.8 RPS con 9.05 ms P99 para 100 Rutas, 100 Consumidores.</td></tr>
<tr><td>Fecha</td><td>Febrero 2024 (para Kong Gateway 3.6.x, los resultados se publican para cada versión menor subsiguiente).</td><td>Febrero 2024.</td></tr>
<tr><td>Fuente</td><td>[Kong Gateway performance testing benchmarks](https://developer.konghq.com/gateway/performance/benchmarks/)</td><td>[Kong Gateway performance testing benchmarks](https://developer.konghq.com/gateway/performance/benchmarks/)</td></tr>
<tr><td>Comparativa</td><td>Demuestra la alta capacidad de rendimiento de Kong Gateway en su configuración más básica, superando a menudo a otras soluciones en pruebas de throughput.</td><td>Muestra el impacto en el rendimiento al aplicar políticas de seguridad y control de tráfico, manteniendo aún un alto rendimiento y baja latencia para escenarios empresariales complejos.</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>Método de Integración</td><td>**Proxy Inverso**: Kong se sitúa como un proxy inverso entre los clientes y los servicios backend. **Plugins**: La funcionalidad se extiende y personaliza mediante plugins que se insertan en el flujo de solicitudes/respuestas. **Admin API**: Integración programática para la gestión y configuración de Kong. **Kubernetes Ingress Controller**: Integración nativa con Kubernetes para la gestión de tráfico.</td></tr>
<tr><td>Protocolo</td><td>**HTTP/HTTPS**: Para APIs RESTful. **TCP/TLS**: Para tráfico genérico. **gRPC/gRPCS**: Para microservicios. **WebSocket/WSS**: Para comunicación en tiempo real. **MCP (Model Context Protocol)**: Para la gestión de modelos de IA. **A2A (Agent-to-Agent)**: Para la comunicación entre agentes de IA.</td></tr>
<tr><td>Autenticación</td><td>**Key Auth**: Autenticación basada en claves API. **Basic Auth**: Autenticación HTTP básica. **JWT (JSON Web Token)**: Autenticación basada en tokens web JSON. **OAuth 2.0**: Soporte para el framework de autorización OAuth 2.0. **OpenID Connect**: Capacidad de autenticación basada en OIDC. **SAML**: Soporte para autenticación SAML. **LDAP**: Integración con directorios LDAP. **mTLS**: Autenticación mutua TLS.</td></tr>
<tr><td>Latencia Típica</td><td>**Baja**: En configuraciones básicas sin plugins, la latencia P99 puede ser tan baja como 5.24 ms (para 140,382 RPS). Con plugins de seguridad y rate limiting, puede aumentar ligeramente, pero se mantiene en rangos de un solo dígito de milisegundos (ej. 9.05 ms P99 para 95,660.8 RPS con rate limiting y key auth).</td></tr>
<tr><td>Límites de Rate</td><td>**Configurables por Plugin**: Los límites de rate se implementan a través del plugin `rate-limiting`, que permite configurar límites por segundo, minuto, hora, día, mes o año, y por diferentes criterios (IP, consumidor, credencial, etc.).</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>Tipo de Test</td><td>**Pruebas de Rendimiento y Carga**</td></tr>
<tr><td>Herramienta Recomendada</td><td>**K6**: Herramienta de código abierto para pruebas de carga y rendimiento. Kong proporciona un [public test suite](https://github.com/Kong/kong-gateway-performance-benchmark) que utiliza K6 para sus benchmarks.</td></tr>
<tr><td>Criterio de Éxito</td><td>Mantener un alto rendimiento (RPS) y baja latencia (P99) bajo cargas esperadas y picos de tráfico, según los benchmarks publicados por Kong y los requisitos específicos del servicio. Por ejemplo, P99 < 10ms para el 99% de las solicitudes.</td></tr>
<tr><td>Frecuencia</td><td>Regularmente, especialmente antes de cada despliegue importante o actualización de versión de Kong Gateway, y periódicamente (ej. mensual o trimestral) para monitorear la degradación del rendimiento.</td></tr>
<tr><td>Tipo de Test</td><td>**Pruebas Funcionales de API**</td></tr>
<tr><td>Herramienta Recomendada</td><td>**Postman / Insomnia**: Herramientas populares para probar endpoints de API, incluyendo la validación de solicitudes, respuestas, encabezados y códigos de estado.</td></tr>
<tr><td>Criterio de Éxito</td><td>Todas las APIs enrutadas a través de Kong Gateway responden correctamente según sus especificaciones, aplicando las políticas configuradas (autenticación, rate limiting, transformación) de manera esperada.</td></tr>
<tr><td>Frecuencia</td><td>Como parte del ciclo de desarrollo continuo (CI/CD) para cada cambio en la configuración de Kong o en los servicios backend.</td></tr>
<tr><td>Tipo de Test</td><td>**Pruebas de Seguridad**</td></tr>
<tr><td>Herramienta Recomendada</td><td>**OWASP ZAP / Burp Suite**: Para pruebas de penetración y escaneo de vulnerabilidades. **Herramientas de prueba de autenticación/autorización**: Para validar la correcta aplicación de políticas de seguridad.</td></tr>
<tr><td>Criterio de Éxito</td><td>Las políticas de seguridad (autenticación, autorización, rate limiting, WAF) se aplican correctamente, protegiendo las APIs contra accesos no autorizados, ataques de inyección, denegación de servicio, etc.</td></tr>
<tr><td>Frecuencia</td><td>Periódicamente (ej. anualmente) y después de cambios significativos en la configuración de seguridad o la introducción de nuevas APIs.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>Versión</td><td>**3.14.0.2**</td><td>**3.14.0.1**</td><td>**3.14.0.0**</td><td>**3.9.1 (Enterprise)**</td></tr>
<tr><td>Fecha de Lanzamiento</td><td>28 de Abril de 2026</td><td>10 de Abril de 2026</td><td>7 de Abril de 2026</td><td>4 de Junio de 2025</td></tr>
<tr><td>Estado</td><td>Activa, última versión de parche.</td><td>Activa.</td><td>Activa.</td><td>Activa, pero la versión 3.9 de Enterprise entrará en EOL en Enero de 2026.</td></tr>
<tr><td>Cambios Clave</td><td>Correcciones de errores en plugins de IA (ai-transformers, ai-mcp-oauth2, ai-mcp-proxy, ai-proxy-advanced), clustering, core y Kong Manager. Actualizaciones de dependencias.</td><td>Corrección de error en el plugin openid-connect.</td><td>Cambios importantes: `hide_credentials` por defecto a `true` en plugins de autenticación, `tls_certificate_verify` por defecto a `true` en core, `ssl_verify` por defecto a `on` en oauth2 y Redis Partials. Deprecación de `parse-request` en ai-rate-limiting-advanced. Nuevas características en plugins de IA (soporte para GCP OAuth, tokenizer de bytes, metadatos de modelo), vectordb (Valkey), y soporte WebSocket en acl.</td></tr>
<tr><td>Ruta de Migración</td><td>Las actualizaciones entre versiones de parche (ej. 3.14.0.1 a 3.14.0.2) suelen ser directas. Las actualizaciones entre versiones menores (ej. 3.13 a 3.14) pueden requerir atención a los cambios importantes y deprecaciones documentadas en el changelog. Kong Inc. recomienda seguir las guías de actualización para cada versión. Para migraciones de Kong Open Source a Kong Enterprise o Kong Konnect, existen guías específicas para facilitar la transición, aprovechando la compatibilidad de configuración declarativa.</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>Competidor Directo</td><td>**Google Apigee**</td><td>**AWS API Gateway**</td><td>**Tyk**</td><td>**Nginx (como proxy inverso)**</td></tr>
<tr><td>Ventaja vs Competidor</td><td>**Flexibilidad y Agnosticismo de Plataforma**: Kong es más ligero y agnóstico a la nube, con despliegue flexible en cualquier entorno (on-prem, multi-cloud, Kubernetes). Apigee está más ligado al ecosistema de Google Cloud. **Open Source Core**: La versión de código abierto de Kong permite mayor personalización y control. **Rendimiento**: Kong a menudo demuestra un rendimiento superior en throughput y latencia en benchmarks específicos.</td><td>**Control y Personalización**: Kong ofrece mayor control sobre la configuración y la extensibilidad a través de plugins. AWS API Gateway es un servicio gestionado con menos opciones de personalización profunda. **Multi-cloud/Híbrido**: Kong está diseñado para entornos híbridos y multi-nube, mientras que AWS API Gateway es específico de AWS.</td><td>**Rendimiento y Escalabilidad**: Kong ha demostrado un rendimiento superior en varios benchmarks. **Ecosistema y Comunidad**: Kong tiene una comunidad de código abierto más grande y un ecosistema de plugins más maduro.</td><td>**Funcionalidades de Gestión de API**: Kong, construido sobre Nginx, añade una capa completa de gestión de API (autenticación, rate limiting, observabilidad, etc.) que Nginx por sí solo no ofrece. **Extensibilidad**: La arquitectura de plugins de Kong facilita la adición de funcionalidades sin modificar el core.</td></tr>
<tr><td>Desventaja vs Competidor</td><td>**Complejidad Operativa**: Apigee ofrece una solución más "llave en mano" con menos complejidad operativa para la gestión completa del ciclo de vida de la API. **Funcionalidades de Monetización y Portal de Desarrolladores**: Apigee tiene funcionalidades más robustas y maduras para monetización y portales de desarrolladores.</td><td>**Servicio Gestionado**: AWS API Gateway es un servicio completamente gestionado, lo que reduce la carga operativa. **Integración Nativa con AWS**: Integración profunda con otros servicios de AWS.</td><td>**Menor Reconocimiento de Marca**: Tyk tiene una cuota de mercado y reconocimiento de marca ligeramente menor que Kong.</td><td>**Falta de Características de API Gateway**: Nginx es un excelente proxy inverso, pero carece de las características específicas de un API Gateway, lo que requiere configuración manual y desarrollo para replicar las funcionalidades de Kong.</td></tr>
<tr><td>Caso de Uso Donde Gana</td><td>**Arquitecturas Híbridas y Multi-nube**: Cuando se requiere una gestión de API consistente en entornos distribuidos y heterogéneos. **Alta Personalización y Extensibilidad**: Para organizaciones que necesitan adaptar el gateway a requisitos muy específicos mediante plugins personalizados. **Entornos Kubernetes Nativos**: Kong Ingress Controller ofrece una integración profunda y eficiente con Kubernetes.</td><td>**Control Total y Flexibilidad de Despliegue**: Cuando la organización necesita control total sobre la infraestructura del gateway y la flexibilidad para desplegarlo en cualquier lugar. **Evitar Vendor Lock-in**: Para evitar la dependencia de un único proveedor de nube.</td><td>**Proyectos de Código Abierto y Comunidades Fuertes**: Para equipos que valoran un fuerte soporte de la comunidad y la flexibilidad del código abierto.</td><td>**Gestión Integral de Microservicios**: Cuando se necesita una solución completa para la gestión, seguridad y observabilidad de APIs en una arquitectura de microservicios.</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>Capacidad de IA</td><td>**AI Gateway Unificado**: Actúa como un proxy para el conectividad de IA, permitiendo la gestión centralizada de LLMs y otros servicios de IA. **Enrutamiento Inteligente**: Dirige las solicitudes a los modelos de IA más apropiados. **Seguridad y Gobernanza de IA**: Aplica políticas de seguridad, autenticación y autorización al tráfico de IA. **Observabilidad de IA**: Monitorea el consumo de IA, el uso de herramientas, el gasto de tokens y el rendimiento de los modelos. **Optimización de Costos**: Controla y optimiza el uso y costo de la IA con modelos de consumo predictivos y limitación de tokens. **Guardrails de IA**: Implementa políticas de seguridad y cumplimiento para las interacciones con IA. **Semantic Caching**: Caché inteligente para respuestas de modelos de IA. **Agent-to-Agent (A2A) Traffic Management**: Gestión de la comunicación entre agentes de IA.</td></tr>
<tr><td>Modelo Subyacente</td><td>Kong AI Gateway es agnóstico al modelo y al proveedor. Soporta una amplia gama de modelos de lenguaje grandes (LLMs) y otros servicios de IA de proveedores como **OpenAI, Anthropic, Google Vertex AI, Cohere, Ollama, DeepSeek, vLLM, y Databricks**. También soporta la integración con **Amazon Bedrock** y el **Model Context Protocol (MCP)**.</td></tr>
<tr><td>Nivel de Control</td><td>**Alto**: Kong AI Gateway ofrece un control granular sobre el tráfico de IA. Permite a los usuarios definir reglas de enrutamiento, aplicar políticas de seguridad (autenticación, autorización, rate limiting de tokens), transformar solicitudes/respuestas, y monitorear el rendimiento y el costo. Los plugins de IA proporcionan una extensibilidad significativa para adaptar el comportamiento del gateway a necesidades específicas.</td></tr>
<tr><td>Personalización Posible</td><td>**Extensa**: La personalización se logra principalmente a través de los plugins de IA de Kong. Se pueden desarrollar plugins personalizados utilizando el Plugin Development Kit (PDK) de Kong para implementar lógica de negocio específica, integraciones con sistemas internos, o guardrails de IA a medida. La configuración declarativa permite adaptar el comportamiento del gateway a través de archivos YAML/JSON, facilitando la integración con flujos de CI/CD.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>Métrica</td><td>**Rendimiento (RPS)**</td><td>**Latencia (P99)**</td><td>**Escalabilidad**</td><td>**Consumo de Recursos**</td><td>**Experiencia General**</td></tr>
<tr><td>Valor Reportado por Comunidad</td><td>**Alto**: Usuarios y benchmarks de terceros a menudo reportan un alto rendimiento, con cifras que superan las 100,000 RPS en configuraciones optimizadas. Por ejemplo, un benchmark de GigaOm de junio de 2025 encontró que Kong "sobresale en throughput y rendimiento general" [1].</td><td>**Bajo**: La latencia P99 se mantiene en rangos bajos de milisegundos, incluso con plugins habilitados. Los benchmarks de Kong para la versión 3.6.x muestran P99 de 5.24 ms para proxy básico y 9.05 ms con rate limiting y key auth [2].</td><td>**Excelente**: Ampliamente reconocido por su capacidad de escalar horizontalmente para manejar grandes volúmenes de tráfico API. La arquitectura de control plane/data plane facilita la escalabilidad.</td><td>**Eficiente**: Aunque consume más CPU y memoria que soluciones más ligeras como KrakenD en algunos escenarios de alta concurrencia, su rendimiento general justifica el consumo para la mayoría de los casos de uso [3].</td><td>**Positiva**: La comunidad valora su flexibilidad, extensibilidad a través de plugins, y su capacidad para gestionar APIs en entornos complejos de microservicios y multi-nube. Es considerado un "fit fuerte para gestionar APIs en entornos de producción" [4].</td></tr>
<tr><td>Fuente</td><td>[1] GigaOm Benchmark: Kong API Gateway (Junio 2025); [2] Kong Gateway performance testing benchmarks (Febrero 2024); [3] Kong and KrakenD API Gateway Performance Under High Concurrency (Medium); [4] Kong Gateway Pros and Cons | User Likes & Dislikes - G2</td><td>[2] Kong Gateway performance testing benchmarks (Febrero 2024)</td><td>Gartner Peer Insights, G2 Reviews, Reddit discussions.</td><td>[3] Kong and KrakenD API Gateway Performance Under High Concurrency (Medium)</td><td>Gartner Peer Insights, G2 Reviews, Stack Overflow, Reddit.</td></tr>
<tr><td>Fecha</td><td>Junio 2025, Febrero 2024, Varios.</td><td>Febrero 2024.</td><td>Varios (continuo).</td><td>Varios.</td><td>Varios (continuo).</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>Plan</td><td>**Kong Gateway Community (Open Source)**</td><td>**Kong Gateway Enterprise**</td><td>**Kong Konnect (SaaS)**</td></tr>
<tr><td>Precio</td><td>Gratuito (código abierto).</td><td>Basado en suscripción anual, con precios que varían desde aproximadamente $30,000-$50,000 para despliegues pequeños hasta seis cifras para implementaciones empresariales grandes. El costo puede depender del número de nodos, servicios o APIs gestionadas.</td></tr>
<tr><td>Límites</td><td>Funcionalidades básicas de API Gateway. Requiere autogestión y soporte comunitario.</td><td>Incluye funcionalidades avanzadas, plugins empresariales, soporte técnico 24/7, Kong Manager (GUI), Developer Portal y Analytics. Los límites de uso (ej. número de servicios) pueden estar sujetos al contrato de suscripción.</td></tr>
<tr><td>Ideal Para</td><td>Pequeñas y medianas empresas, startups, desarrolladores individuales, o proyectos que requieren un control total y personalización, y que tienen la capacidad de autogestionar el soporte y la operación.</td><td>Grandes empresas y organizaciones con requisitos de seguridad, rendimiento y escalabilidad críticos, que necesitan soporte empresarial, funcionalidades avanzadas y herramientas de gestión integradas.</td><td>Empresas que buscan una solución de gestión de API completamente gestionada, con la flexibilidad de desplegar Data Planes en sus propias infraestructuras (híbrido) y la simplicidad de una plataforma SaaS para el Control Plane. Ideal para equipos que priorizan la velocidad y la reducción de la carga operativa.</td></tr>
<tr><td>ROI Estimado</td><td>**Alto (en términos de costo inicial)**: No hay costo de licencia, pero requiere inversión en recursos humanos para implementación, mantenimiento y soporte. El ROI se maximiza en proyectos donde la personalización y el control son clave.</td><td>**Moderado a Alto**: El ROI se justifica por la reducción del tiempo de comercialización de las APIs, la mejora de la seguridad, la escalabilidad y la eficiencia operativa. La inversión en soporte y funcionalidades avanzadas se traduce en menor riesgo y mayor productividad.</td><td>**Alto (en términos de agilidad y reducción de la carga operativa)**: Permite a las empresas centrarse en el desarrollo de sus APIs en lugar de la gestión de la infraestructura. La visibilidad de costos por consumo ayuda a optimizar el gasto.</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>Escenario de Test</td><td>**Pruebas de Carga Extrema y Estabilidad**</td><td>**Análisis de Vulnerabilidades y Ataques de Inyección**</td><td>**Evaluación de Políticas de Autenticación/Autorización**</td><td>**Red Teaming en Entornos de Producción**</td></tr>
<tr><td>Resultado</td><td>Kong Gateway demuestra un alto rendimiento y estabilidad bajo cargas extremas, con la capacidad de manejar cientos de miles de solicitudes por segundo (RPS) y mantener una baja latencia P99, incluso con plugins habilitados. Sin embargo, en percentiles muy altos (ej. P99.9), la latencia puede aumentar significativamente en comparación con soluciones más ligeras o Nginx puro.</td><td>Se han identificado y mitigado vulnerabilidades comunes de API (ej. inyección SQL, XSS) a través de la configuración de plugins de seguridad y WAF. La configuración por defecto de Kong es robusta, pero las malas configuraciones pueden exponer el gateway a riesgos.</td><td>Las políticas de autenticación (JWT, OAuth2) y autorización (ACL) se validan para asegurar que solo los usuarios y aplicaciones autorizados puedan acceder a los recursos protegidos. Se verifica la resistencia a ataques de fuerza bruta y el manejo de tokens inválidos o expirados.</td><td>Simulaciones de ataques avanzados (ej. escalada de privilegios, bypass de políticas, exfiltración de datos) han demostrado la efectividad de las defensas de Kong cuando está correctamente configurado. Se han identificado áreas de mejora en la monitorización de anomalías y la respuesta automatizada a incidentes.</td></tr>
<tr><td>Fortaleza Identificada</td><td>**Rendimiento Bruto y Escalabilidad**: Capacidad para manejar grandes volúmenes de tráfico de manera eficiente. **Extensibilidad para Optimización**: Los plugins permiten optimizar el rendimiento para casos de uso específicos.</td><td>**Rica Biblioteca de Plugins de Seguridad**: Facilita la implementación de controles de seguridad robustos. **Flexibilidad de Configuración**: Permite adaptar las defensas a las necesidades específicas.</td><td>**Soporte Amplio para Estándares de Seguridad**: Integración con JWT, OAuth2, OIDC, etc. **Control Granular**: Posibilidad de aplicar políticas a nivel de servicio, ruta o consumidor.</td><td>**Arquitectura Desacoplada (CP/DP)**: Aísla el plano de datos de posibles compromisos del plano de control. **Capacidades de Observabilidad**: Facilita la detección de actividades sospechosas.</td></tr>
<tr><td>Debilidad Identificada</td><td>**Latencia en Percentiles Muy Altos**: Puede ser un factor limitante para aplicaciones que requieren latencias extremadamente bajas en todos los percentiles. **Consumo de Recursos**: Puede ser mayor que el de soluciones más minimalistas.</td><td>**Riesgo de Mala Configuración**: Una configuración incorrecta o incompleta puede anular las protecciones de seguridad. **Dependencia de Plugins de Terceros**: La seguridad puede depender de la calidad y el mantenimiento de plugins externos.</td><td>**Complejidad de Implementación**: La configuración de políticas de autorización complejas puede ser un desafío. **Gestión de Claves y Secretos**: Requiere una gestión segura de credenciales y claves.</td><td>**Detección de Amenazas Avanzadas**: Puede requerir integración con soluciones SIEM/SOAR externas para una detección y respuesta más sofisticada. **Actualizaciones y Parches**: La falta de aplicación oportuna de parches puede introducir vulnerabilidades.</td></tr>
</table>

## Referencias

[1] GigaOm. (2025, Junio 5). *GigaOm Benchmark: Kong API Gateway*. Recuperado de [https://portal.gigaom.com/report/gigaom-benchmark-kong-api-gateway-2](https://portal.gigaom.com/report/gigaom-benchmark-kong-api-gateway-2)
[2] Kong Inc. (2024, Febrero 26). *Kong Gateway performance testing benchmarks*. Recuperado de [https://developer.konghq.com/gateway/performance/benchmarks/](https://developer.konghq.com/gateway/performance/benchmarks/)
[3] Çakıcı, Z. (2025, Junio 10). *API Gateway Performance Benchmark*. Medium. Recuperado de [https://medium.com/code-beyond/api-gateway-performance-benchmark-407500194c76](https://medium.com/code-beyond/api-gateway-performance-benchmark-407500194c76)
[4] G2. *Kong Gateway Reviews & Ratings*. Recuperado de [https://www.g2.com/products/kong-gateway/reviews?qs=pros-and-cons](https://www.g2.com/products/kong-gateway/reviews?qs=pros-and-cons)
