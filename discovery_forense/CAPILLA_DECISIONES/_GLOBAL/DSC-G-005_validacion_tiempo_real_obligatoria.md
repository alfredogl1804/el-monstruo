---
id: DSC-G-005
proyecto: GLOBAL
tipo: antipatron
titulo: "Modelos IA, versiones de software, frameworks deben verificarse contra realidad presente, no asumir desde training. Anti-Dory + Anti-Autoboicot."
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:validacion-tiempo-real
  - skill:anti-autoboicot
cruza_con: ["todos"]
---

# Validación en tiempo real obligatoria, nunca solo entrenamiento

## Decisión

Es obligatorio validar en tiempo real las versiones de modelos IA, software, frameworks y APIs contra la realidad presente. Queda estrictamente prohibido asumir versiones o configuraciones basándose únicamente en los datos de entrenamiento del modelo. Se debe aplicar el protocolo Anti-Autoboicot y Anti-Dory antes de escribir código, configuraciones o dependencias.

## Por qué

Los modelos de IA tienen un corte de conocimiento que vuelve obsoleta la información sobre versiones y herramientas. Depender del entrenamiento genera código roto, dependencias inexistentes y fallos de despliegue (autoboicot), comprometiendo la integridad del ecosistema.

## Implicaciones

Afecta a todos los proyectos del ecosistema. Obliga a ejecutar búsquedas en tiempo real o consultar documentación actualizada antes de definir arquitecturas, escribir dependencias o invocar APIs.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)