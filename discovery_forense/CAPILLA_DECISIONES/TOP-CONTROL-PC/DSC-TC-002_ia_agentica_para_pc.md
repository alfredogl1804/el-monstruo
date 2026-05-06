---
id: DSC-TC-002
proyecto: TOP-CONTROL-PC
tipo: restriccion_dura
titulo: "Top Control PC opera localmente en el PC del usuario con privilegios completos. Soberanía total: no SaaS dependiente, modelos locales preferidos donde se pueda."
estado: firme
fecha: 2026-05-06
fuentes:
  - drive:roadmap_v3_top_control_pc.md
cruza_con: ["ninguno"]
---

# IA agéntica para PC

## Decisión

Top Control PC debe operar localmente en el equipo del usuario con privilegios completos. Se establece una soberanía total sobre los datos y la ejecución, eliminando la dependencia de plataformas SaaS de terceros. Se prioriza el uso de modelos de IA locales siempre que sea técnicamente viable para garantizar la privacidad y el control absoluto del entorno.

## Por qué

Para asegurar la privacidad, seguridad y autonomía del usuario. Al operar localmente con privilegios completos, la IA puede interactuar profundamente con el sistema operativo sin exponer datos sensibles a la nube, cumpliendo con el principio de soberanía total y evitando bloqueos por parte de proveedores externos.

## Implicaciones

Requiere hardware capaz de ejecutar modelos locales eficientemente. Limita el uso de APIs externas que requieran enviar datos del usuario. El diseño de la arquitectura debe contemplar la gestión de permisos locales y la seguridad del sistema anfitrión.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)