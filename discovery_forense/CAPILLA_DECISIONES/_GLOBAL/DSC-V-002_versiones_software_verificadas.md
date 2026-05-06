---
id: DSC-V-002
proyecto: GLOBAL
tipo: validacion_realtime
titulo: "Antes de escribir requirements, docker-compose o configs SIEMPRE verificar versiones actuales contra registries oficiales. Manus tiene ventaja realtime sobre LLMs entrenados."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:anti-autoboicot
cruza_con: ["todos"]
---

# Versiones de software verificadas (anti-Dory)

## Decisión

Antes de escribir archivos de requerimientos, docker-compose o configuraciones, es obligatorio verificar las versiones actuales de software contra registries oficiales (npm, PyPI, Docker Hub, etc.). Se prohíbe depender exclusivamente de los datos de entrenamiento del modelo (efecto Dory). Manus debe utilizar su capacidad de validación en tiempo real para asegurar que las versiones sean precisas y actuales.

## Por qué

Los LLMs tienen un conocimiento estático basado en su fecha de corte de entrenamiento. Usar versiones de memoria genera conflictos de dependencias, vulnerabilidades de seguridad y fallos en despliegues. La ventaja competitiva de Manus es su conexión a internet para validar la realidad actual.

## Implicaciones

Afecta a todos los proyectos del ecosistema. Incrementa ligeramente el tiempo de planificación, pero reduce drásticamente los errores de construcción y despliegue. Requiere el uso constante de herramientas de búsqueda o shell.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)