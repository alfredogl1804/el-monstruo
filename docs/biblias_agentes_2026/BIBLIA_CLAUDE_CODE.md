# Biblia de Implementación: Claude Code (Anthropic)

**Fecha de Lanzamiento:** Febrero 2026 (Research Preview) / Abril 2026 (v2.1.126)
**Versión:** v2.1.126
**Arquitectura Principal:** Agente de terminal con orquestación paralela de sub-agentes y arquitectura de memoria de tres capas.

## 1. Visión General y Diferenciador Único

Claude Code es un agente de codificación autónomo basado en terminal que interactúa directamente con el sistema de archivos local. Su diferenciador técnico más importante es su **arquitectura de memoria de tres capas** (revelada en un leak de código fuente) y su capacidad para **orquestar sub-agentes en paralelo** utilizando un patrón de "Split-and-Merge" (Dividir y Fusionar).

A diferencia de los asistentes de codificación basados en IDE (como Copilot o Cursor) que dependen del contexto del editor, Claude Code opera a nivel de sistema operativo, ejecutando comandos, leyendo archivos y coordinando equipos de agentes para resolver problemas de ingeniería de software de horizonte largo.

## 2. Arquitectura Técnica: Memoria de Tres Capas

El mayor desafío para los agentes de codificación es mantener el contexto a través de sesiones largas y bases de código masivas. Claude Code resuelve esto con tres mecanismos distintos:

### 2.1. Capa 1: Memoria Persistente (`memory.md`)
Claude Code utiliza un archivo markdown simple y en texto plano (`memory.md`) en el directorio del proyecto como su almacén duradero.
-   **Qué almacena:** Decisiones arquitectónicas, convenciones del proyecto, restricciones conocidas y contexto previo.
-   **Por qué Markdown:** Es inspeccionable (los humanos pueden leerlo y corregirlo), persistente (sobrevive a reinicios), portátil y controlable por versiones (git). Esto hace que la memoria del agente sea auditable y confiable.

### 2.2. Capa 2: Búsqueda Basada en Grep (Orientación a Corto Plazo)
Para navegar por la base de código en tiempo real sin saturar la ventana de contexto, Claude Code utiliza herramientas de búsqueda basadas en `grep` (y utilidades similares como `ripgrep` o `ast-grep`).
-   **Funcionamiento:** En lugar de leer archivos completos a ciegas, el agente formula consultas de búsqueda para encontrar definiciones de funciones, usos de clases o patrones específicos, recuperando solo los fragmentos relevantes.

### 2.3. Capa 3: El Daemon Chyros (Proactividad en Segundo Plano)
Aunque no se lanzó en las primeras versiones, el código fuente reveló referencias a un proceso en segundo plano llamado "Chyros".
-   **Propósito:** Indexar la base de código, monitorear cambios en los archivos y pre-computar el contexto de forma asíncrona, permitiendo que el agente tenga respuestas casi instantáneas sobre el estado del proyecto sin tener que buscar activamente en cada turno.

## 3. Orquestación de Sub-Agentes: Patrón Split-and-Merge

Claude Code soporta un modelo de orquestador donde un agente padre genera sub-agentes y los ejecuta en paralelo (hasta 10 sub-agentes simultáneos por orquestador).

1.  **Split (Dividir):** El orquestador analiza una tarea compleja (ej. refactorizar 5 archivos) y crea un sub-agente independiente para cada subtarea. Cada sub-agente recibe su propio prompt de sistema, herramientas y un contexto aislado.
2.  **Ejecución Paralela:** Los sub-agentes operan simultáneamente. Si un sub-agente encuentra un error (ej. una prueba falla), intenta corregirlo de forma autónoma dentro de su propio bucle de retroalimentación (Feedback Loop) ejecutando código en un sandbox.
3.  **Merge (Fusionar):** Una vez que todos los sub-agentes terminan, el orquestador recopila los resultados, resuelve cualquier conflicto (ej. cambios superpuestos en el mismo archivo) y presenta el resultado final.

## 4. Lecciones para el Monstruo

La arquitectura de Claude Code proporciona directrices claras para mejorar las capacidades de codificación del Monstruo:

1.  **Implementar `memory.md`:** El Monstruo debe adoptar inmediatamente el patrón de escribir un archivo `memory.md` (o `AGENTS.md`) en la raíz de cualquier proyecto en el que trabaje. Debe leer este archivo al inicio de cada sesión y actualizarlo con decisiones clave. La transparencia de un archivo de texto es superior a las bases de datos vectoriales opacas para la colaboración humano-agente.
2.  **Búsqueda Activa sobre Lectura Pasiva:** En lugar de intentar leer archivos enteros o depender de que el usuario proporcione el contexto, el Monstruo debe usar herramientas de búsqueda en el sistema de archivos (`grep`, `find`) de manera proactiva para localizar el código relevante antes de intentar modificarlo.
3.  **Orquestación Paralela Real:** Para tareas que involucran múltiples archivos independientes, el Monstruo debe evolucionar su herramienta `WideResearchTool` (o crear una `ParallelCodingTool`) para lanzar sub-agentes que modifiquen archivos simultáneamente, reduciendo drásticamente el tiempo total de ejecución.

---
*Referencias:*
[1] MindStudio Blog: What Is the Anthropic Claude Code Source Code Leak? Three-Layer Memory Architecture Explained (Abril 2026)
[2] MindStudio Blog: Claude Code Split-and-Merge Pattern: How Sub-Agents Run in Parallel (Abril 2026)
