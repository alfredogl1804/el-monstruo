# BIBLIA DE DOCKER v7.3

**Fecha de Actualización:** 30 de Abril de 2026

## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Nombre oficial</td><td>Docker, Inc.</td></tr>
<tr><td>Desarrollador</td><td>Docker, Inc.</td></tr>
<tr><td>País de Origen</td><td>Estados Unidos</td></tr>
<tr><td>Inversión y Financiamiento</td><td>Docker ha recaudado un total de $541 millones en 17 rondas de financiación hasta el 15 de abril de 2026. Las rondas incluyen 3 Seed, 3 Early-Stage y 11 Late-Stage. La ronda de financiación más grande fue una Serie D. La última ronda de financiación significativa fue una Serie C de $105 millones el 31 de marzo de 2022, valorando la compañía en $2.1 mil millones.</td></tr>
<tr><td>Modelo de Precios</td><td>Docker ofrece un modelo de precios escalonado:
<ul><li>**Personal:** $0 (para desarrolladores individuales, código abierto no comercial, estudiantes y educadores).</li><li>**Pro:** $11/usuario/mes (para profesionales individuales con características avanzadas).</li><li>**Team:** $16/usuario/mes (para equipos pequeños con herramientas colaborativas).</li><li>**Business:** $24/usuario/mes (para empresas con seguridad robusta, control y cumplimiento).</li></ul>
Además, ofrece Docker Hardened Images (DHI):
<ul><li>**Community:** Gratis (imágenes seguras y mínimas).</li><li>**Select:** Desde $5k/repositorio (seguridad de producción con soporte de cumplimiento).</li><li>**Enterprise:** Contactar para precios (controles de seguridad avanzados y personalización ilimitada).</td></tr>
<tr><td>Posicionamiento Estratégico</td><td>Docker se posiciona como una plataforma esencial para desarrolladores, simplificando la creación, el intercambio y la ejecución de aplicaciones en contenedores. Su estrategia se centra en la productividad del desarrollador, integraciones fluidas con la nube, cadenas de suministro de software bien arquitectadas y una experiencia moderna. Busca equilibrar la apertura con el control de nivel empresarial para un crecimiento sostenido.</td></tr>
<tr><td>Gráfico de Dependencias</td><td>Dockerfiles pueden ser visualizados como grafos de dependencias utilizando herramientas como `dockerfilegraph`, que emplea Graphviz para representar visualmente los procesos de construcción de Docker. Esto ayuda a entender las relaciones entre las etapas de construcción y las capas de la imagen.</td></tr>
<tr><td>Matriz de Compatibilidad</td><td>Docker es compatible con los principales sistemas operativos, incluyendo Linux (varias distribuciones como Red Hat Enterprise Linux) y Windows (Windows Server 2025, 2022, etc.). Las matrices de compatibilidad detallan las versiones mínimas del motor Docker requeridas para diferentes sistemas operativos y versiones de Docker Enterprise.</td></tr>
<tr><td>Acuerdos de Nivel de Servicio (SLOs)</td><td>Docker ofrece Acuerdos de Nivel de Servicio (SLAs) para sus servicios de suscripción y soporte. Los detalles específicos se encuentran en su "Docker Subscription Service Agreement" y en la página de "Availability", que cubre los procesos de soporte y los acuerdos de nivel de servicio. Los planes de pago incluyen diferentes tiempos de respuesta de soporte (ej. 5 días hábiles para Pro, 2 días para Team, 1 día para Business).</td></tr>
</table>

## L02 — GOBERNANZA Y MODELO DE CONFIANZA

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Licencia</td><td>Docker Desktop requiere una suscripción de pago por usuario para organizaciones con más de 250 empleados o más de $10 millones en ingresos anuales. Para uso personal, de código abierto no comercial, estudiantes y educadores, Docker Desktop es gratuito. Los Dockerfiles pueden tener licencias de código abierto como MIT, incluso si describen la instalación de software con otras licencias (ej. GPL).</td></tr>
<tr><td>Política de Privacidad</td><td>La Política de Privacidad de Docker (última actualización: 9 de enero de 2026) detalla la recopilación, uso y divulgación de información personal de los usuarios de sus sitios web y servicios. Recopila información de contacto requerida (nombre, empresa, dirección, teléfono, correo electrónico) e información de facturación. También utiliza herramientas de recopilación de información como cookies y balizas web para recopilar información de navegación. Docker cumple con regulaciones de privacidad como GDPR, CCPA, CPA, CTDPA, VCDPA, UCPA y el Marco de Privacidad APEC.</td></tr>
<tr><td>Cumplimiento y Certificaciones</td><td>Docker cumple con ISO/IEC 27001, los criterios de servicios de confianza SOC 2, el Estándar Arquitectónico de Nube Confiable de CSA y otros estándares aplicables. Docker anunció su certificación SOC 2 Tipo 2 y la certificación ISO 27001 el 4 de junio de 2024. También se adhiere al Marco de Privacidad de Datos (DPF) UE-EE. UU., la Extensión del Reino Unido al DPF UE-EE. UU. y el DPF Suiza-EE. UU.</td></tr>
<tr><td>Historial de Auditorías y Seguridad</td><td>Docker realiza auditorías regulares y ha obtenido la certificación SOC 2 Tipo 2 e ISO 27001, lo que demuestra un compromiso con la seguridad. Su política de privacidad menciona el uso de medidas de seguridad administrativas, técnicas y físicas para proteger los datos de los clientes.</td></tr>
<tr><td>Respuesta a Incidentes</td><td>Aunque la política de privacidad no detalla explícitamente un proceso de respuesta a incidentes, el cumplimiento con SOC 2 e ISO 27001 implica la existencia de procedimientos robustos para la gestión de incidentes de seguridad.</td></tr>
<tr><td>Matriz de Autoridad de Decisión</td><td>No se encontró una matriz de autoridad de decisión pública específica. Sin embargo, la estructura de liderazgo y la junta directiva de Docker (mencionadas en la Capa 1) son responsables de las decisiones estratégicas y operativas.</td></tr>
<tr><td>Política de Obsolescencia</td><td>No se encontró una política de obsolescencia explícita en la información pública disponible. Sin embargo, el soporte para versiones de Docker Desktop (hasta 6 meses más antiguas que la última) en planes de pago sugiere una política implícita de soporte de versiones.</td></tr>
</table>

## L03 — MODELO MENTAL Y MAESTRÍA

Docker revoluciona el desarrollo y despliegue de aplicaciones al introducir la **contenerización**, un enfoque que empaqueta software en unidades estandarizadas llamadas contenedores. Este modelo mental se centra en la portabilidad, la consistencia y el aislamiento, permitiendo a los desarrolladores construir, compartir y ejecutar aplicaciones de manera eficiente en cualquier entorno, desde el desarrollo local hasta la producción en la nube. La maestría en Docker implica comprender cómo estas abstracciones facilitan un ciclo de vida de desarrollo más ágil y confiable.

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Paradigma Central</td><td>**Contenerización:** Empaquetar aplicaciones y sus dependencias en unidades aisladas y portátiles (contenedores) que pueden ejecutarse de manera consistente en cualquier entorno.</td></tr>
<tr><td>Abstracciones Clave</td><td>
<ul>
<li>**Imágenes:** Plantillas inmutables que contienen el código de la aplicación, las bibliotecas, las dependencias y la configuración.</li>
<li>**Contenedores:** Instancias ejecutables de imágenes, aisladas del sistema operativo subyacente y de otros contenedores.</li>
<li>**Dockerfile:** Un script que define los pasos para construir una imagen Docker.</li>
<li>**Docker Hub/Registries:** Repositorios para almacenar y compartir imágenes Docker.</li>
<li>**Volúmenes:** Mecanismos para persistir datos generados por y utilizados por los contenedores.</li>
<li>**Redes:** Permiten la comunicación entre contenedores y con el mundo exterior.</li>
</ul>
</td></tr>
<tr><td>Patrones de Pensamiento Recomendados</td><td>
<ul>
<li>**Inmutabilidad:** Tratar los contenedores como inmutables; cualquier cambio requiere la creación de una nueva imagen.</li>
<li>**Microservicios:** Descomponer aplicaciones en servicios pequeños e independientes que se ejecutan en sus propios contenedores.</li>
<li>**Declarativo:** Definir el estado deseado de la aplicación y dejar que Docker lo gestione.</li>
<li>**Orquestación:** Utilizar herramientas como Kubernetes o Docker Swarm para gestionar y escalar contenedores en producción.</li>
<li>**Separación de preocupaciones:** Mantener el código y la configuración separados.</li>
</ul>
</td></tr>
<tr><td>Anti-patrones a Evitar</td><td>
<ul>
<li>**Contenedores monolíticos:** Empaquetar toda una aplicación monolítica en un solo contenedor, perdiendo los beneficios del aislamiento y la escalabilidad.</li>
<li>**Almacenamiento de datos persistentes dentro del contenedor:** Los contenedores son efímeros; los datos importantes deben almacenarse en volúmenes.</li>
<li>**Instalación manual de dependencias en tiempo de ejecución:** Todas las dependencias deben estar definidas en el Dockerfile para garantizar la reproducibilidad.</li>
<li>**Ejecutar múltiples procesos en un solo contenedor:** Un contenedor debe tener un solo propósito y ejecutar un solo proceso principal.</li>
<li>**No usar tags de imágenes:** No etiquetar las imágenes de forma significativa puede llevar a problemas de versionado y reproducibilidad.</li>
</ul>
</td></tr>
<tr><td>Curva de Aprendizaje</td><td>Moderada. Los conceptos básicos son accesibles para desarrolladores, pero la maestría en la optimización de Dockerfiles, la gestión de redes, el almacenamiento persistente y la orquestación (ej. Kubernetes) requiere una inversión de tiempo y experiencia práctica. La abundancia de documentación y recursos comunitarios facilita el aprendizaje.</td></tr>
</table>

## L04 — CAPACIDADES TÉCNICAS

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Capacidades Core</td><td>
<ul>
<li>**Contenerización de Aplicaciones:** Empaquetado de aplicaciones y sus dependencias en contenedores portátiles.</li>
<li>**Aislamiento de Procesos:** Ejecución de aplicaciones en entornos aislados del sistema operativo host.</li>
<li>**Gestión de Imágenes:** Creación, almacenamiento, distribución y versionado de imágenes Docker.</li>
<li>**Orquestación Básica:** Docker Compose para definir y ejecutar aplicaciones multi-contenedor.</li>
<li>**Redes de Contenedores:** Conectividad entre contenedores y con redes externas.</li>
<li>**Almacenamiento Persistente:** Gestión de volúmenes para datos de contenedores.</li>
<li>**Seguridad Básica:** Escaneo de vulnerabilidades en imágenes (Docker Scout), firma de imágenes.</li>
</ul>
</td></tr>
<tr><td>Capacidades Avanzadas</td><td>
<ul>
<li>**Docker Build Cloud:** Aceleración de compilaciones de imágenes en la nube.</li>
<li>**Testcontainers Cloud/Desktop:** Integración de pruebas con contenedores.</li>
<li>**Hardened Docker Desktop:** Versión de Docker Desktop con seguridad mejorada para entornos empresariales.</li>
<li>**Registro de Imágenes (Docker Hub/Registries privados):** Gestión avanzada de repositorios de imágenes.</li>
<li>**Gestión de Acceso a Imágenes y Registros:** Control de acceso basado en roles (RBAC) para imágenes y registros.</li>
<li>**SSO y SCIM:** Integración con sistemas de identidad empresariales para autenticación y aprovisionamiento de usuarios.</li>
<li>**Desktop Insights Dashboard:** Visibilidad sobre el uso de Docker Desktop en la organización.</li>
<li>**Enhanced Container Isolation (ECI):** Aislamiento mejorado de contenedores para mayor seguridad.</li>
</ul>
</td></tr>
<tr><td>Capacidades Emergentes (Abril 2026)</td><td>
<ul>
<li>**Depuración Asistida por IA:** Integración de herramientas de IA para facilitar la depuración de aplicaciones en contenedores.</li>
<li>**Soporte Expandido para Cargas de Trabajo No Linux:** Mejora continua del soporte para contenedores en entornos Windows y macOS.</li>
<li>**Optimización de Flujos de Trabajo de Desarrollo:** Nuevas características para reducir la "carga de trabajo del desarrollador" (developer toil) mediante la automatización y la mejora de la experiencia de usuario.</li>
<li>**Integración Profunda con IA/ML:** Facilidades para el despliegue y gestión de cargas de trabajo de inteligencia artificial y aprendizaje automático en contenedores.</li>
</ul>
</td></tr>
<tr><td>Limitaciones Técnicas Confirmadas</td><td>
<ul>
<li>**Aislamiento a nivel de SO:** Los contenedores comparten el kernel del sistema operativo host, lo que ofrece menos aislamiento que las máquinas virtuales.</li>
<li>**Complejidad de Orquestación a Gran Escala:** Aunque Docker Compose es útil para entornos pequeños, la orquestación de clústeres grandes requiere herramientas más robustas como Kubernetes.</li>
<li>**Curva de Aprendizaje para Conceptos Avanzados:** La gestión de redes complejas, almacenamiento distribuido y seguridad a nivel empresarial puede ser desafiante.</li>
<li>**Rendimiento de E/S en Volúmenes:** En ciertos escenarios, el rendimiento de E/S de los volúmenes puede ser una limitación.</li>
</ul>
</td></tr>
<tr><td>Roadmap Público</td><td>El roadmap público de Docker (disponible en GitHub: `github.com/docker/roadmap`) se centra en mejorar la productividad del desarrollador, la seguridad y la integración con la nube. Las áreas clave incluyen: Build Cloud, Testcontainers, Docker Scout, y mejoras en Docker Desktop. Para 2026, el enfoque incluye la reducción del "developer toil" a través de la depuración asistida por IA y la expansión del soporte para cargas de trabajo no Linux.</td></tr>
</table>

## L05 — DOMINIO TÉCNICO

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Stack Tecnológico</td><td>Docker está escrito principalmente en **Go** y utiliza características del kernel de Linux como **namespaces** (para aislamiento de procesos, redes, etc.) y **cgroups** (para gestión de recursos como CPU, memoria). También se apoya en **containerd** como un runtime de contenedores de bajo nivel.</td></tr>
<tr><td>Arquitectura Interna</td><td>Docker opera con una arquitectura cliente-servidor. Los componentes principales son:
<ul>
<li>**Docker Client:** La interfaz de línea de comandos (CLI) que permite a los usuarios interactuar con Docker.</li>
<li>**Docker Daemon (Engine):** Un servicio de fondo que gestiona los objetos de Docker (imágenes, contenedores, redes, volúmenes). Escucha las solicitudes de la API de Docker.</li>
<li>**Docker Registries (ej. Docker Hub):** Almacenan imágenes Docker. Docker Hub es el registro público predeterminado.</li>
<li>**Containerd:** Un runtime de contenedores que gestiona el ciclo de vida de los contenedores en el sistema operativo.</li>
<li>**runc:** Un runtime de contenedores de bajo nivel que se encarga de crear y ejecutar contenedores.</li>
</ul>
</td></tr>
<tr><td>Protocolos Soportados</td><td>Docker no implementa protocolos de aplicación específicos. En cambio, proporciona una capa de red que permite a los contenedores comunicarse utilizando cualquier protocolo estándar (HTTP/S, TCP, UDP, etc.) a través de la asignación de puertos y redes virtuales.</td></tr>
<tr><td>Formatos de Entrada/Salida</td><td>
<ul>
<li>**Entrada:** Dockerfiles (para definir la construcción de imágenes), archivos de configuración (ej. `docker-compose.yml`), imágenes Docker (para ejecutar contenedores).</li>
<li>**Salida:** Imágenes Docker (construidas a partir de Dockerfiles), contenedores en ejecución, logs de contenedores, volúmenes de datos.</li>
</ul>
</td></tr>
<tr><td>APIs Disponibles</td><td>
<ul>
<li>**Docker Engine API (REST API):** Permite la interacción programática con el Docker Daemon para gestionar imágenes, contenedores, redes y volúmenes.</li>
<li>**Docker Compose API:** Aunque no es una API REST independiente, Docker Compose utiliza la API del Engine para orquestar aplicaciones multi-contenedor.</li>
<li>**SDKs:** Docker proporciona SDKs para varios lenguajes de programación (Python, Go, Java, Node.js, etc.) que facilitan la interacción con la API de Docker Engine.</li>
</ul>
</td></tr>
</table>

## L06 — PLAYBOOKS OPERATIVOS

<table header-row="true">
<tr><td>**Caso de Uso**</td><td>**Pasos Exactos**</td><td>**Herramientas Necesarias**</td><td>**Tiempo Estimado**</td><td>**Resultado Esperado**</td></tr>
<tr><td>**1. Desarrollo Local Consistente**</td><td>
<ol>
<li>**Definir el entorno:** Crear un `Dockerfile` para la aplicación y un `docker-compose.yml` para definir los servicios (ej. base de datos, backend, frontend).</li>
<li>**Construir imágenes:** Ejecutar `docker-compose build` para construir las imágenes de los servicios.</li>
<li>**Levantar el entorno:** Ejecutar `docker-compose up` para iniciar todos los servicios en contenedores.</li>
<li>**Desarrollar y probar:** Trabajar en el código de la aplicación, con los cambios reflejados en el contenedor (usando volúmenes montados).</li>
<li>**Compartir el entorno:** Distribuir el `Dockerfile` y `docker-compose.yml` a otros desarrolladores para replicar el entorno.</li>
</ol>
</td><td>Docker Desktop, Docker Engine, Docker Compose, Editor de texto/IDE</td><td>1-2 horas (configuración inicial), minutos (uso diario)</td><td>Entorno de desarrollo idéntico para todos los desarrolladores, eliminando problemas de "funciona en mi máquina".</td></tr>
<tr><td>**2. Despliegue de Microservicios con Orquestación**</td><td>
<ol>
<li>**Contenerizar cada microservicio:** Crear un `Dockerfile` para cada microservicio.</li>
<li>**Definir la orquestación:** Utilizar un archivo de configuración de Kubernetes (ej. `deployment.yaml`, `service.yaml`) o Docker Compose (para entornos más pequeños) para definir cómo se despliegan y comunican los microservicios.</li>
<li>**Construir y publicar imágenes:** Construir las imágenes de Docker para cada microservicio y subirlas a un registro de contenedores (ej. Docker Hub, ECR).</li>
<li>**Desplegar en el clúster:** Aplicar los archivos de configuración de orquestación al clúster (ej. `kubectl apply -f .` para Kubernetes).</li>
<li>**Monitorear y escalar:** Utilizar las herramientas del orquestador para monitorear el estado de los servicios y escalar según la demanda.</li>
</ol>
</td><td>Docker Engine, Docker CLI, Kubernetes/Docker Swarm, `kubectl` (para Kubernetes), Registro de Contenedores</td><td>Horas a días (dependiendo de la complejidad), minutos (despliegues posteriores)</td><td>Aplicación distribuida compuesta por microservicios, desplegada y gestionada de forma escalable y resiliente.</td></tr>
<tr><td>**3. Pipeline de CI/CD con Docker**</td><td>
<ol>
<li>**Configurar el repositorio:** Asegurarse de que el código fuente de la aplicación esté en un sistema de control de versiones (ej. Git).</li>
<li>**Definir el Dockerfile:** Crear un `Dockerfile` para la aplicación.</li>
<li>**Configurar la herramienta de CI/CD:** Integrar Docker en la herramienta de CI/CD (ej. Jenkins, GitLab CI, GitHub Actions).</li>
<li>**Fase de Build:** La herramienta de CI/CD construye la imagen Docker a partir del `Dockerfile` tras cada commit.</li>
<li>**Fase de Test:** Ejecutar pruebas automatizadas dentro de un contenedor Docker.</li>
<li>**Fase de Push:** Si las pruebas pasan, la imagen se etiqueta y se sube a un registro de contenedores.</li>
<li>**Fase de Deploy:** La herramienta de CI/CD despliega la nueva imagen en el entorno de staging o producción.</li>
</ol>
</td><td>Docker Engine, Docker CLI, Herramienta de CI/CD (Jenkins, GitLab CI, GitHub Actions), Registro de Contenedores, Sistema de Control de Versiones (Git)</td><td>Horas (configuración inicial), minutos (ejecución por cada cambio)</td><td>Automatización del proceso de construcción, prueba y despliegue de aplicaciones, garantizando entregas rápidas y fiables.</td></tr>
</table>

## L07 — EVIDENCIA Y REPRODUCIBILIDAD

<table header-row="true">
<tr><td>**Benchmark**</td><td>**Score/Resultado**</td><td>**Fecha**</td><td>**Fuente**</td><td>**Comparativa**</td></tr>
<tr><td>Rendimiento de Contenedores Docker vs. VMs</td><td>Docker es generalmente más rápido y consume menos recursos que una virtualización completa de VM. Las VMs tardan minutos en arrancar y son órdenes de magnitud más grandes (en GB) que un contenedor equivalente.</td><td>Julio 2023</td><td>Backblaze Blog</td><td>VMware</td></tr>
<tr><td>Rendimiento de Inicio de Contenedores y Operaciones de Imagen (Docker vs. Podman)</td><td>Docker es 10-15% más rápido para el inicio de contenedores (150ms vs 180ms) y operaciones de imagen.</td><td>Diciembre 2025</td><td>Uptrace.dev</td><td>Podman</td></tr>
<tr><td>Rendimiento de Runtime (containerd vs. dockerd)</td><td>Containerd es generalmente más rápido que Docker, con un tiempo de ejecución de 0.07 segundos en comparación con los 0.13 segundos de Docker, debido a su arquitectura ligera.</td><td>Desconocido</td><td>Medium (norma-dev)</td><td>containerd</td></tr>
<tr><td>Métricas de Rendimiento de Contenedores (CPU, Memoria, E/S de Red)</td><td>`docker stats` proporciona un flujo de datos en vivo del uso de CPU, memoria, límites de memoria y métricas de E/S de red para contenedores en ejecución.</td><td>Desconocido</td><td>Docker Docs</td><td>N/A (monitoreo interno)</td></tr>
<tr><td>Evaluación de Rendimiento de Docker en Sistemas Operativos</td><td>Investigación sobre el rendimiento de los contenedores Docker en diferentes sistemas operativos.</td><td>2024</td><td>MDPI (M Sobieraj)</td><td>N/A (análisis de SO)</td></tr>
</table>

## L08 — ARQUITECTURA DE INTEGRACIÓN

<table header-row="true">
<tr><td>**Campo**</td><td>**Descripción**</td></tr>
<tr><td>Método de Integración</td><td>
<ul>
<li>**APIs REST:** La principal forma de interacción programática con el Docker Engine y Docker Hub.</li>
<li>**SDKs:** Bibliotecas cliente para diversos lenguajes que simplifican el uso de las APIs.</li>
<li>**Docker Compose:** Para definir y gestionar aplicaciones multi-contenedor, integrándose con el Docker Engine.</li>
<li>**Plugins y Extensiones:** Docker soporta un ecosistema de plugins para redes, volúmenes, etc., y extensiones para Docker Desktop.</li>
<li>**Integración con CI/CD:** Herramientas de CI/CD (Jenkins, GitLab CI, GitHub Actions) se integran con Docker para automatizar la construcción, prueba y despliegue de imágenes y contenedores.</li>
<li>**Testcontainers:** Librerías para pruebas de integración que utilizan contenedores Docker.</li>
</ul>
</td></tr>
<tr><td>Protocolo</td><td>
<ul>
<li>**HTTP/HTTPS:** Para la comunicación con la Docker Engine API y Docker Hub.</li>
<li>**TCP/UDP:** Para la comunicación de red entre contenedores y con servicios externos.</li>
<li>**Sockets Unix:** Para la comunicación local entre el cliente Docker y el daemon.</li>
</ul>
</td></tr>
<tr><td>Autenticación</td><td>
<ul>
<li>**Tokens de Autenticación:** Utilizados para acceder a Docker Hub y otros registros de contenedores.</li>
<li>**Credenciales de Usuario:** Nombre de usuario y contraseña para iniciar sesión en Docker Hub.</li>
<li>**SSO (Single Sign-On):** Para entornos empresariales, integración con proveedores de identidad.</li>
<li>**Tokens de Acceso Personal:** Para automatización y scripts.</li>
</ul>
</td></tr>
<tr><td>Latencia Típica</td><td>La latencia varía significativamente según el entorno (local vs. nube), la complejidad de la operación y la carga de la red. Las operaciones locales con el daemon suelen ser de milisegundos. Las interacciones con registros remotos pueden variar de decenas a cientos de milisegundos.</td></tr>
<tr><td>Límites de Rate</td><td>Docker Hub impone límites de tasa para las extracciones de imágenes (pulls) para usuarios anónimos y autenticados, que varían según el tipo de cuenta (ej. 100 pulls/hora para usuarios anónimos, ilimitado para planes de pago). La API del Docker Engine no tiene límites de tasa públicos explícitos, pero está sujeta a los recursos del host.</td></tr>
</table>

## L09 — VERIFICACIÓN Y PRUEBAS

<table header-row="true">
<tr><td>**Tipo de Test**</td><td>**Herramienta Recomendada**</td><td>**Criterio de Éxito**</td><td>**Frecuencia**</td></tr>
<tr><td>**Pruebas Unitarias**</td><td>Frameworks de prueba del lenguaje de programación (ej. JUnit para Java, Pytest para Python) ejecutados dentro de contenedores.</td><td>Todas las unidades de código funcionan según lo esperado; 100% de cobertura de pruebas unitarias (idealmente).</td><td>Con cada cambio de código; parte del pipeline de CI.</td></tr>
<tr><td>**Pruebas de Integración**</td><td>Testcontainers (para integrar bases de datos, colas de mensajes, etc. en contenedores), Docker Compose (para entornos multi-servicio).</td><td>Los componentes de la aplicación se comunican y funcionan correctamente juntos; la integración con servicios externos es exitosa.</td><td>Con cada cambio de código que afecte la integración; parte del pipeline de CI.</td></tr>
<tr><td>**Pruebas de Aceptación/End-to-End (E2E)**</td><td>Selenium, Cypress, Playwright (ejecutados en contenedores o contra aplicaciones en contenedores).</td><td>La aplicación completa funciona según los requisitos del usuario final; los flujos de usuario críticos son exitosos.</td><td>Antes de cada despliegue a staging/producción; parte del pipeline de CI/CD.</td></tr>
<tr><td>**Análisis de Seguridad de Imágenes**</td><td>Docker Scout, Snyk Container, Trivy, Clair.</td><td>Ausencia de vulnerabilidades críticas y de alta severidad; cumplimiento con políticas de seguridad definidas.</td><td>Con cada construcción de imagen; parte del pipeline de CI.</td></tr>
<tr><td>**Pruebas de Rendimiento y Carga**</td><td>JMeter, Locust, K6 (ejecutados en contenedores o contra aplicaciones en contenedores).</td><td>La aplicación cumple con los SLAs de rendimiento (latencia, throughput, uso de recursos) bajo carga esperada.</td><td>Periódicamente (ej. semanalmente, mensualmente) o antes de lanzamientos importantes.</td></tr>
<tr><td>**Pruebas de Conformidad/Cumplimiento**</td><td>Herramientas de auditoría específicas de la industria o regulaciones (ej. CIS Benchmarks para Docker).</td><td>El entorno Docker cumple con los estándares de seguridad y cumplimiento normativo.</td><td>Periódicamente; antes de auditorías externas.</td></tr>
</table>

## L10 — CICLO DE VIDA Y MIGRACIÓN

<table header-row="true">
<tr><td>**Versión**</td><td>**Fecha de Lanzamiento**</td><td>**Estado**</td><td>**Cambios Clave**</td><td>**Ruta de Migración**</td></tr>
<tr><td>**Docker Engine 29.x**</td><td>2026 (últimas actualizaciones)</td><td>Activo</td><td>Mejoras continuas en rendimiento, seguridad y experiencia del desarrollador; optimizaciones para Build Cloud y Scout.</td><td>Actualización directa desde versiones anteriores (ej. 28.x, 27.x) siguiendo la documentación oficial.</td></tr>
<tr><td>**Docker Engine 19.03**</td><td>22 de Julio de 2019</td><td>Fin de Vida (EOL) - 8 de Enero de 2021</td><td>Introducción de la API de plugins gestionados (cambios significativos respecto a 1.12).</td><td>Migración a versiones más recientes de Docker Engine, posiblemente requiriendo la desinstalación y reinstalación de plugins.</td></tr>
<tr><td>**Docker Desktop (última versión)**</td><td>Continuo (actualizaciones frecuentes)</td><td>Activo</td><td>Nuevas características para desarrolladores, integración con Docker Build Cloud, Testcontainers, Docker Scout, mejoras de seguridad.</td><td>Actualización a través de la aplicación Docker Desktop; versiones anteriores a 6 meses de la última no están disponibles para descarga.</td></tr>
<tr><td>**Estrategias de Migración de Contenedores**</td><td>N/A</td><td>N/A</td><td>N/A</td><td>
<ul>
<li>**Migración de Imágenes:** Exportar e importar imágenes entre hosts.</li>
<li>**Migración de Contenedores:** Detener, exportar e importar contenedores, asegurando la preservación de datos y configuraciones.</li>
<li>**Migración de Volúmenes:** Mover volúmenes de datos entre hosts.</li>
<li>**Migración con Herramientas:** Utilizar herramientas como Gordon para migrar Dockerfiles automáticamente.</li>
<li>**Consideraciones:** Asegurarse de que la aplicación sea compatible con Linux, gestionar el estado (preferiblemente sin estado), y configurar adecuadamente.</li>
</ul>
</td></tr>
</table>

## L11 — MARCO DE COMPETENCIA

<table header-row="true">
<tr><td>**Competidor Directo**</td><td>**Ventaja vs Competidor**</td><td>**Desventaja vs Competidor**</td><td>**Caso de Uso Donde Gana**</td></tr>
<tr><td>**Podman**</td><td>
<ul>
<li>Ecosistema más maduro y amplio.</li>
<li>Mayor popularidad y comunidad.</li>
<li>Mejor soporte para entornos legados.</li>
<li>Más rápido en operaciones de imagen y arranque de contenedores (según benchmarks de 2025).</li>
</ul>
</td><td>
<ul>
<li>Requiere daemon (dockerd), lo que puede ser un punto único de fallo y un riesgo de seguridad si se ejecuta como root.</li>
<li>Menos énfasis en seguridad por diseño (aunque ha mejorado).</li>
</ul>
</td><td>
<ul>
<li>Desarrollo local y equipos que valoran un ecosistema establecido y herramientas integradas.</li>
<li>Proyectos que requieren compatibilidad con un amplio rango de herramientas y servicios existentes.</li>
</ul>
</td></tr>
<tr><td>**Kubernetes**</td><td>
<ul>
<li>Docker es una plataforma de contenerización y runtime, mientras que Kubernetes es una plataforma de orquestación. No son competidores directos, sino complementarios. Docker crea y manipula imágenes, Kubernetes gestiona múltiples microservicios a escala.</li>
</ul>
</td><td>
<ul>
<li>Mayor complejidad y curva de aprendizaje.</li>
<li>Sobrecarga para proyectos pequeños o entornos de desarrollo simples.</li>
</ul>
</td><td>
<ul>
<li>Orquestación y gestión de clústeres de contenedores a gran escala en producción.</li>
<li>Despliegue de microservicios complejos y distribuidos.</li>
</ul>
</td></tr>
<tr><td>**LXC (Linux Containers)**</td><td>
<ul>
<li>Mayor facilidad de uso y abstracción para el desarrollador.</li>
<li>Ecosistema de herramientas más rico (Docker Compose, Docker Hub, etc.).</li>
<li>Mayor portabilidad de contenedores entre diferentes hosts.</li>
</ul>
</td><td>
<ul>
<li>Menor nivel de aislamiento que LXC puro en algunos aspectos.</li>
<li>Mayor abstracción puede ocultar detalles del sistema operativo subyacente.</li>
</ul>
</td><td>
<ul>
<li>Desarrollo y despliegue de aplicaciones modernas que requieren portabilidad y consistencia.</li>
<li>Equipos que buscan simplificar la gestión de dependencias y entornos.</li>
</ul>
</td></tr>
<tr><td>**Máquinas Virtuales (VMs)**</td><td>
<ul>
<li>Mucho más ligero y rápido en el arranque.</li>
<li>Menor consumo de recursos (CPU, RAM).</li>
<li>Mayor densidad de aplicaciones por host.</li>
<li>Mayor portabilidad y consistencia del entorno de aplicación.</li>
</ul>
</td><td>
<ul>
<li>Menor aislamiento de seguridad (comparten el kernel del host).</li>
<li>Menos adecuado para ejecutar sistemas operativos completos.</li>
</ul>
</td><td>
<ul>
<li>Ejecución de aplicaciones individuales o microservicios que requieren un entorno ligero y rápido.</li>
<li>Desarrollo y pruebas donde la consistencia del entorno es clave.</li>
</ul>
</td></tr>
</table>

## L12 — CAPA DE INYECCIÓN DE IA (AI INJECTION LAYER)

<table header-row="true">
<tr><td>**Capacidad de IA**</td><td>**Modelo Subyacente**</td><td>**Nivel de Control**</td><td>**Personalización Posible**</td></tr>
<tr><td>**Asistente de IA (Gordon)**</td><td>Modelo de lenguaje grande (LLM) propietario de Docker, entrenado en documentación y bases de código de Docker.</td><td>Alto. Gordon es un agente de IA integrado en Docker Desktop que ayuda con tareas específicas de Docker, como depuración de contenedores, escritura de Dockerfiles y gestión de imágenes.</td><td>Limitada a la interacción a través de prompts. Los usuarios pueden guiar a Gordon con sus preguntas y comandos para obtener asistencia contextual.</td></tr>
<tr><td>**Contenerización para ML/IA**</td><td>N/A (Docker es la plataforma, no el modelo).</td><td>Alto. Los desarrolladores tienen control total sobre los modelos de ML/IA que empaquetan y ejecutan en contenedores.</td><td>Completa. Los usuarios pueden contenerizar cualquier modelo de ML/IA, framework (TensorFlow, PyTorch), y sus dependencias, permitiendo una personalización total del entorno de ejecución y del modelo.</td></tr>
<tr><td>**Integración con Herramientas de IA**</td><td>N/A (Docker facilita la integración, no es la herramienta de IA).</td><td>Medio a Alto. Docker facilita la integración de diversas herramientas y plataformas de IA/ML al proporcionar un entorno consistente y reproducible para su ejecución.</td><td>Depende de la herramienta de IA específica. Docker permite a los desarrolladores definir entornos personalizados para sus herramientas de IA.</td></tr>
<tr><td>**Depuración Asistida por IA**</td><td>Modelos de IA internos de Docker para análisis de logs y código.</td><td>Medio. La IA asiste en la identificación de problemas, pero la resolución final y el control recaen en el desarrollador.</td><td>Limitada a la configuración de las herramientas de depuración y la interpretación de las sugerencias de la IA.</td></tr>
</table>

## L13 — RENDIMIENTO REALISTA Y EXPERIENCIA COMUNITARIA

<table header-row="true">
<tr><td>**Métrica**</td><td>**Valor Reportado por Comunidad**</td><td>**Fuente**</td><td>**Fecha**</td></tr>
<tr><td>**Consistencia del Entorno**</td><td>Altamente valorado por su capacidad para crear entornos idénticos en diferentes sistemas, reduciendo significativamente los problemas de despliegue.</td><td>Reseñas de usuarios en G2.com, Capterra.com</td><td>2026</td></tr>
<tr><td>**Rendimiento de CPU y Memoria**</td><td>Los usuarios monitorean activamente el uso de CPU y memoria de los contenedores usando `docker stats` y extensiones de Docker Desktop para identificar cuellos de botella.</td><td>Foros de Docker, blogs técnicos (ej. Last9.io)</td><td>2025-2026</td></tr>
<tr><td>**Velocidad de Arranque de Contenedores**</td><td>Generalmente percibido como rápido, con benchmarks que muestran tiempos de arranque de contenedores en el orden de los milisegundos (ej. 150ms vs 180ms de Podman).</td><td>Uptrace.dev (benchmarks de 2025)</td><td>Diciembre 2025</td></tr>
<tr><td>**Problemas de Rendimiento (I/O)**</td><td>Algunos usuarios reportan que el rendimiento de I/O puede ser un cuello de botella en ciertos escenarios, especialmente con volúmenes montados.</td><td>Foros de Docker, Stack Overflow</td><td>Continuo</td></tr>
<tr><td>**Lentitud en `docker pull` (ej. Singapur)**</td><td>Usuarios en ciertas regiones geográficas (ej. Singapur) reportan lentitud en las operaciones de `docker pull`.</td><td>Reseñas de usuarios en Capterra.com</td><td>2026</td></tr>
<tr><td>**Adopción**</td><td>Docker ha superado el 92% de adopción entre ingenieros, siendo la herramienta de desarrollo más utilizada.</td><td>LinkedIn (Manjunath Janardhan)</td><td>2026</td></tr>
<tr><td>**Seguridad (CIS Benchmarks)**</td><td>La comunidad utiliza y contribuye a herramientas como Docker Bench for Security para verificar las mejores prácticas de seguridad en despliegues de contenedores.</td><td>CIS Security, GitHub (docker/docker-bench-security)</td><td>Continuo</td></tr>
</table>

## L14 — ECONOMÍA OPERATIVA Y ESTRATEGIA GTM

<table header-row="true">
<tr><td>**Plan**</td><td>**Precio**</td><td>**Límites**</td><td>**Ideal Para**</td><td>**ROI Estimado**</td></tr>
<tr><td>**Personal**</td><td>$0/mes</td><td>1 usuario, 1 repo Scout, 100 pulls/hr en Docker Hub, 1 repo privado.</td><td>Desarrolladores individuales, proyectos de código abierto no comerciales, estudiantes y educadores.</td><td>Ahorro de costos al eliminar la necesidad de licencias para uso personal y educativo.</td></tr>
<tr><td>**Pro**</td><td>$11/usuario/mes</td><td>1 usuario, 2 repos Scout, pulls ilimitados en Docker Hub, 200 minutos de Build Cloud, 100 minutos de Testcontainers Cloud.</td><td>Profesionales individuales que requieren características avanzadas y recursos adicionales.</td><td>Mejora de la productividad individual y reducción del tiempo de desarrollo.</td></tr>
<tr><td>**Team**</td><td>$16/usuario/mes</td><td>Hasta 100 usuarios, repos Scout ilimitados, pulls ilimitados en Docker Hub, repos privados ilimitados, 500 minutos de Build Cloud, 500 minutos de Testcontainers Cloud, 10 tokens de acceso a la organización.</td><td>Equipos pequeños que necesitan herramientas colaborativas y gestión centralizada.</td><td>Aumento de la eficiencia del equipo, colaboración mejorada y reducción de errores de entorno.</td></tr>
<tr><td>**Business**</td><td>$24/usuario/mes</td><td>Usuarios ilimitados, repos Scout ilimitados, pulls ilimitados en Docker Hub, repos privados ilimitados, 1,500 minutos de Build Cloud, 1,500 minutos de Testcontainers Cloud, 100 tokens de acceso a la organización, organizaciones ilimitadas en Docker Hub.</td><td>Grandes empresas que buscan seguridad robusta, control, cumplimiento y soporte premium.</td><td>ROI del 126% en tres años (según estudio de impacto económico de Docker Business), reducción de costos operativos y de seguridad, aceleración de la entrega de software.</td></tr>
<tr><td>**Docker Hardened Images (DHI) - Select**</td><td>Desde $5k/repositorio</td><td>Seguridad de producción con soporte de cumplimiento, variantes FIPS/STIG, correcciones de CVE críticas < 7 días.</td><td>Organizaciones con requisitos de seguridad y cumplimiento estrictos.</td><td>Reducción de riesgos de seguridad, cumplimiento normativo y ahorro de tiempo en la gestión de vulnerabilidades.</td></tr>
<tr><td>**Estrategia Go-to-Market (GTM)**</td><td>Docker emplea una estrategia GTM híbrida que combina un modelo freemium con ofertas empresariales. Se enfoca en la productividad del desarrollador (developer-first platform) y en la integración con el ecosistema de herramientas existentes. La estrategia incluye: 
<ul>
<li>**Product-Led Growth:** Ofrecer planes de bajo costo y autoservicio para desarrolladores, activando su base de usuarios masiva para luego ofrecer productos premium.</li>
<li>**Enfoque en el Valor Empresarial:** Destacar el impacto económico (ROI, ahorro de costos) de Docker Business para atraer a grandes organizaciones.</li>
<li>**Innovación Continua:** Invertir en nuevas características como Build Cloud, Testcontainers y Docker Scout para mantener la relevancia y competitividad.</li>
<li>**Ecosistema de Socios:** Colaborar con socios para ampliar el alcance y la integración de Docker.</li>
</ul>
</td><td>N/A</td><td>N/A</td><td>N/A</td></tr>
</table>

## L15 — BENCHMARKING EMPÍRICO Y RED TEAMING

<table header-row="true">
<tr><td>**Escenario de Test**</td><td>**Resultado**</td><td>**Fortaleza Identificada**</td><td>**Debilidad Identificada**</td></tr>
<tr><td>**Evaluación de Rendimiento (Docker vs. VM vs. Bare Metal)**</td><td>Los contenedores Docker muestran un rendimiento cercano al bare metal y superior a las máquinas virtuales en muchas cargas de trabajo, especialmente en el arranque y el consumo de recursos.</td><td>Eficiencia de recursos, rapidez de inicio, menor sobrecarga.</td><td>Puede haber una ligera sobrecarga de CPU en comparación con la ejecución directa en VM para algunas cargas de trabajo intensivas.</td></tr>
<tr><td>**Rendimiento de Almacenamiento de Docker**</td><td>La configuración del almacenamiento de Docker es compleja y la elección de la solución de almacenamiento impacta significativamente el rendimiento.</td><td>Flexibilidad en la elección de backends de almacenamiento.</td><td>La complejidad de la configuración puede llevar a un rendimiento subóptimo si no se gestiona correctamente.</td></tr>
<tr><td>**Rendimiento de Arranque de Contenedores**</td><td>El tiempo de arranque de los contenedores está dominado por la sobrecarga del runtime, no por el tamaño de la imagen.</td><td>Arranque rápido de contenedores, incluso con imágenes grandes.</td><td>La optimización del runtime es crucial para reducir aún más los tiempos de inicio.</td></tr>
<tr><td>**Rendimiento de GPU Passthrough en Docker para IA/ML**</td><td>Comparación del rendimiento de GPU entre entornos nativos y Docker para cargas de trabajo de IA/ML, mostrando que Docker puede mantener un rendimiento comparable.</td><td>Capacidad para ejecutar cargas de trabajo de IA/ML intensivas en GPU dentro de contenedores con buen rendimiento.</td><td>Posibles pequeñas diferencias de rendimiento en comparación con el entorno nativo, que requieren optimización.</td></tr>
<tr><td>**Red Teaming: Escenarios de Escape de Contenedores**</td><td>Los escenarios de escape de contenedores son posibles si no se siguen las mejores prácticas de seguridad (ej. ejecutar contenedores como root, montar sockets de Docker, configuraciones de capacidades inseguras).</td><td>Aislamiento por defecto relativamente seguro si se siguen las mejores prácticas.</td><td>Vulnerabilidades del kernel del host, configuraciones inseguras de contenedores, imágenes vulnerables.</td></tr>
<tr><td>**Red Teaming: Construcción de Laboratorios de Red Teaming con Docker**</td><td>Docker se utiliza para crear entornos aislados y reproducibles para simular ataques, configurar infraestructuras C2 (Command and Control) y probar defensas.</td><td>Facilidad para crear y destruir entornos de prueba, reproducibilidad de escenarios de ataque.</td><td>Requiere un buen conocimiento de seguridad de contenedores para evitar comprometer el host.</td></tr>
<tr><td>**Benchmarking de Seguridad (CIS Docker Benchmark)**</td><td>Herramientas como Docker Bench for Security evalúan la configuración de Docker contra las mejores prácticas de seguridad del CIS.</td><td>Disponibilidad de herramientas y guías para evaluar y mejorar la postura de seguridad.</td><td>La seguridad no es automática; requiere configuración y monitoreo activo.</td></tr>
</table>
