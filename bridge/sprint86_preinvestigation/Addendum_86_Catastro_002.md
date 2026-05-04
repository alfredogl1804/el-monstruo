# Addendum 86-Catastro-002: Decisiones Radar ↔ Catastro
**Fecha:** 2026-05-04
**Estado:** Firmado por Cowork, en redacción documental.

Este addendum documenta las 3 decisiones arquitectónicas tomadas sobre la convivencia entre el Radar GitHub (Motor Biblia v2.1) y El Catastro. 

**Naturaleza del documento:** Arquitectónico / Roadmap. NO modifica el scope de implementación del Sprint 86 vigente.

---

## 1. Convivencia Radar ↔ Catastro (Decisión HÍBRIDO)

| Cambio Arquitectónico | SPEC v1 (Diseño Maestro) | Realidad Validada | Roadmap (SPEC v2) |
|---|---|---|---|
| **Modelo de convivencia** | No contemplaba el Radar GitHub | Radar y Catastro tienen paradigmas distintos (scouting temprano vs verdad canónica comercial) | **HÍBRIDO.** Radar sigue como pipeline de descubrimiento. Catastro absorbe su data para unificar visión en Command Center. |
| **Implementación `catastro_repos`** | 5 tablas | Radar genera data útil (12 reportes históricos) que no debe morir en Markdown | **DIFERIDO a Sprint 86.5 / 87.** La 6ª tabla `catastro_repos` y el ingest script NO entran en Sprint 86. Sprint 86 queda acotado a 5 tablas + 3 macroáreas. |

## 2. Fix del Bug INDICE_RADAR.md

| Cambio Operativo | Estado Previo | Diagnóstico | Roadmap (SPEC v2) |
|---|---|---|---|
| **Regex Parsing** | Agregador falla en 11 de 12 días | Regex muy estricto no soporta formato canónico actual `**Decisiones ADOPTAR:** 174` | **INMEDIATO.** PR aislado al repo `biblia-github-motor` con fix de regex probado empíricamente. |
| **Migración a JSON** | Salida del motor en texto libre | Causa raíz de la fragilidad del parser | **DIFERIDO a Sprint 86.5 / 87.** Junto con la integración de `catastro_repos`, el motor pasará a generar JSON estructurado. |

## 3. Refresh del Modelo Clasificador del Radar

| Cambio Arquitectónico | Propuesta Hilo Catastro | Decisión Cowork | Roadmap (SPEC v2) |
|---|---|---|---|
| **Mecanismo de Refresh** | Automático (Catastro auto-genera PRs) | Viola Objetivo #11 (Seguridad adversarial) por auto-PR. Multiplica credenciales sin beneficio neto. | **MANUAL + ALERTA.** Catastro Sprint 86 incluirá detector de drift (tool MCP `catastro.events` tipo `model_drift_detected`). Alerta a Telegram → Aprobación humana (Alfredo) → Implementación manual. |

---

## Implicaciones para el Sprint 86 (Vigente)

El scope de implementación del Sprint 86 **NO CRECE**. Se mantiene en:
1. 5 tablas Supabase (mockup en `_03_schema_supabase_mockup.sql`).
2. 3 macroáreas iniciales (Inteligencia, Visión, Agentes).
3. Clientes API para fuentes primarias (sin scraping HTML).
4. Quorum Validator (2-de-3) + Trust Score por curador.
5. Servidor MCP para consumo.
6. Detector de drift (como evento, no auto-PR).
