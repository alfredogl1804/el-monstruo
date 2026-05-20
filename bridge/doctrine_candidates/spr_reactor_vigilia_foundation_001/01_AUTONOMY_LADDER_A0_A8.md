# 01 AUTONOMY LADDER A0-A8

## Estado
- SPRINT_CANDIDATE_R0
- DOCTRINE_CANDIDATE

## Concepto
El comportamiento autónomo requiere límites explícitos codificables. La escalera de autonomía define qué puede hacer un loop sin solicitar firma T1.

## Niveles de Autonomía

| Nivel | Nombre | Permisos | Ejemplo de Acción |
|---|---|---|---|
| **A0** | Observador | Solo lectura. No escribe logs ni estado. | Leer un webhook entrante. |
| **A1** | Analista | Lee y escribe en su memoria temporal. | Clasificar un ticket de soporte. |
| **A2** | Preparador | Prepara evidencia y la deposita en el State Fabric. | Generar un source_map.json. |
| **A3** | Creador DRAFT | Crea artefactos no productivos (documentos, schemas). | Escribir un DOCTRINE_CANDIDATE. |
| **A4** | Propositor de Código | Escribe código pero no lo integra a main. | Abrir una rama lateral o PR en GitHub. |
| **A5** | Ejecutor Reversible | Ejecuta acciones que pueden deshacerse con 1 clic. | Crear una tarea en Asana; subir archivo a Drive. |
| **A6** | Propositor Productivo | Propone acción productiva destructiva/pública. Requiere firma T1. | Preparar un deployment; redactar un tweet. |
| **A7** | Ejecutor Productivo | Ejecuta acción productiva *después* de firma T1. | Hacer push a main; disparar CI/CD. |
| **A8** | Modificador de Núcleo | Modifica el propio código del Monstruo. | **BLOQUEADO.** Solo permitido en Sprints Magna. |

## Reglas de Implementación
1. Todo Loop Contract debe declarar su `max_autonomy_level` al nacer.
2. Si un loop intenta una acción superior a su nivel, el Dispatcher rechaza la acción y registra una violación de seguridad.
3. El Reactor de Vigilia (tareas propias) opera por defecto en A3 (crea drafts/evidencia). Nunca opera en A7 sin T1.
