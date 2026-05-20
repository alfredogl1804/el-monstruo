# Visión — Oracle Risk Classification

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

## El Principio Rector

> **Antes de aumentar potencia, aumentar clasificación.**
> Antes de conectar APIs reales, establecer el riesgo.
> Antes de orquestar, definir la autonomía requerida.
> Antes de avanzar a M2, auditar el riesgo.

El Oráculo de IAs (SPR-EMBRION-PERITO-LOOP-001) demostró la capacidad de proponer un catálogo de capacidades emergentes. El Loop Auditor (SPR-LOOP-AUDITOR-001) validó este catálogo pero detectó un gap crítico: las capacidades carecían de una clasificación de riesgo individual (`risk_class`) y los sprints carecían de un nivel de autonomía requerido (`required_autonomy_level`).

Este sprint no busca mejorar el catálogo mediante investigación externa. Su único propósito es **convertir los outputs del Oráculo en artefactos gobernables por riesgo**.

## La Necesidad de un Overlay

Para mantener la inmutabilidad de la evidencia histórica, el catálogo original del Oráculo (`v0`) no debe ser modificado destructivamente. En su lugar, este sprint introduce el concepto de **Risk Classification Overlay**. 

Un overlay es una capa de metadatos estructurados que se superpone al catálogo original para producir una versión anotada (`v0_1`). Esto preserva el linaje de los datos: el Oráculo propuso `v0`, y el proceso de clasificación de riesgo generó `v0_1`.

## Criterios de Clasificación No Sesgados

La clasificación de riesgo debe basarse estrictamente en la **superficie de acción**, no en la marca o proveedor del modelo de IA. Las preguntas fundamentales son:
- ¿Qué lee? (Datos públicos vs. Datos privados de Alfredo)
- ¿Qué escribe? (Reportes vs. Código fuente)
- ¿Qué ejecuta? (Ninguna acción vs. Modificación del kernel)
- ¿Qué cuesta? (Tokens locales vs. Llamadas API costosas)

Si un modelo open-source propone modificar el kernel, su riesgo es `R5`. Si el modelo propietario más avanzado solo propone leer un documento público, su riesgo operativo es `R1`. El riesgo deriva de la acción, no del actor.
