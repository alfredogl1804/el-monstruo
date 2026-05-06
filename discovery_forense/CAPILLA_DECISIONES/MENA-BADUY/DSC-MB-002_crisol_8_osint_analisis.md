---
id: DSC-MB-002
proyecto: MENA-BADUY
tipo: decision_arquitectonica
titulo: "Crisol-8 plataforma de OSINT + análisis estratégico para campaña Mérida 2027"
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:discovery_forense/CRISOL_PLANS/
cruza_con: [ninguno]
---

# Crisol-8 es OSINT + análisis

## Decisión

Crisol-8 se establece como la plataforma central de OSINT y análisis estratégico para la campaña Mérida 2027. La arquitectura se basa en un stack compuesto por scrapers en Python para recolección de datos, Notion como índice estructurado, Google Drive para el almacenamiento del corpus documental y Amazon S3 para la preservación inmutable de evidencia.

## Por qué

Se requiere una separación clara entre recolección automatizada, organización colaborativa y preservación segura. Esta estructura garantiza trazabilidad, acceso rápido para el equipo y protección contra pérdida o alteración de evidencia digital crítica durante la campaña.

## Implicaciones

Los equipos deben estandarizar flujos hacia Notion y Drive. Toda nueva fuente de datos debe integrarse vía scrapers en Python y respaldar evidencia cruda en S3 antes de su procesamiento.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)