---
id: DSC-MB-003
proyecto: MENA-BADUY
tipo: patron_replicable
titulo: "Metodología validada de barrido cruzado para inteligencia: scrape→Drive (corpus)→Notion (índice operativo)→S3 (evidencia/raw). Replicable a cualquier proyecto investigativo."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:discovery_forense/REPORTE_FORENSE_MAGNA.md
cruza_con: ["ninguno"]
---

# Patrón barrido cruzado Drive+Notion+S3

## Decisión

Se establece como estándar el patrón de barrido cruzado para proyectos investigativos. El flujo de datos es: 1) Scrape inicial de fuentes, 2) Almacenamiento del corpus documental en Google Drive para procesamiento, 3) Creación de un índice operativo y estructurado en Notion para gestión y consulta, y 4) Respaldo de evidencia cruda (raw) en Amazon S3 para inmutabilidad y auditoría.

## Por qué

Este patrón garantiza la integridad de la evidencia (S3), facilita el análisis colaborativo y procesamiento de documentos (Drive), y proporciona una interfaz estructurada y ágil para la toma de decisiones y seguimiento operativo (Notion). Separa claramente el almacenamiento inmutable del espacio de trabajo activo.

## Implicaciones

Cualquier nuevo proyecto investigativo en el ecosistema debe implementar esta arquitectura de tres capas. Requiere mantener integraciones activas y sincronizadas entre las herramientas de scraping, Drive, Notion y S3.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)