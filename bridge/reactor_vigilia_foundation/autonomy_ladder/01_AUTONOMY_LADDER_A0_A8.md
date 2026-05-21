# 01 AUTONOMY LADDER A0-A8

## Definición Oficial de Niveles

La Escalera de Autonomía es el mecanismo de control de permisos para el Reactor de Vigilia. Define exactamente qué puede hacer un loop en función de su nivel máximo asignado.

### A0 — Observe
- **Permisos:** Solo observa, lee fuentes permitidas y produce señales.
- **Prohibiciones:** No escribe logs, no modifica estado, no crea archivos.
- **Ejemplo:** Escuchar un webhook entrante sin procesarlo.

### A1 — Analyze
- **Permisos:** Analiza y clasifica. Lee y escribe en su memoria temporal en RAM.
- **Prohibiciones:** No escribe artefactos persistentes en disco ni en el State Fabric.
- **Ejemplo:** Clasificar la urgencia de un ticket de soporte en memoria.

### A2 — Prepare Evidence
- **Permisos:** Prepara evidencia, tablas, mapas, findings y reportes draft. Puede escribir en el State Fabric.
- **Prohibiciones:** No crea artefactos persistentes fuera del State Fabric o directorios temporales.
- **Ejemplo:** Generar un `source_map.json` en memoria/State Fabric.

### A3 — Persistent Artifact
- **Permisos:** Puede crear artefactos persistentes no productivos en paths permitidos explícitamente. Debe dejar rastro en el Event Log.
- **Prohibiciones:** No puede proponer código para producción ni tocar entornos productivos.
- **Ejemplo:** Escribir un archivo `DOCTRINE_CANDIDATE` en el repositorio.

### A4 — Draft Branch / Draft PR Candidate
- **Permisos:** Puede preparar una rama lateral o un PR draft bajo un scope explícito. Requiere que el auditor no sea del mismo linaje que el ejecutor.
- **Prohibiciones:** No puede hacer merge ni aplicar cambios a `main`.
- **Ejemplo:** Abrir una rama `fix-login-bug` con código propuesto.

### A5 — Reversible Local Change
- **Permisos:** Puede producir cambios reversibles en un entorno aislado o local.
- **Prohibiciones:** No puede afectar producción ni datos de usuarios reales.
- **Ejemplo:** Modificar un archivo de configuración local para pruebas.

### A6 — Productive Action Proposal
- **Permisos:** Puede proponer una acción productiva (destructiva, pública o de impacto real), pero NO ejecutarla. Requiere decisión T1 visible.
- **Prohibiciones:** No puede ejecutar la acción propuesta.
- **Ejemplo:** Preparar un script de deployment y pedir aprobación T1.

### A7 — Productive Action with T1
- **Permisos:** Puede ejecutar una acción productiva **solo con firma T1 explícita**.
- **Prohibiciones:** No puede actuar sin la validación de T1.
- **Ejemplo:** Hacer push a `main` o ejecutar un script de migración de base de datos tras recibir el "GO" de T1.

### A8 — Self-Modification / Kernel Governance
- **Permisos:** Puede modificar el propio código del Monstruo, su arquitectura central o su configuración de seguridad.
- **Prohibiciones:** **Bloqueado por defecto.** Solo permitido en Sprints Magna firmados explícitamente por T1.
- **Ejemplo:** Reescribir el motor del Dispatcher.
