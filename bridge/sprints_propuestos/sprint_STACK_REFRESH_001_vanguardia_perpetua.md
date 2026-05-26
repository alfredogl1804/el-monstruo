<!-- lint_strict -->
# Sprint STACK-REFRESH-001 — Vanguardia Perpetua

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #6 (Vanguardia Perpetua) + #5 (Validación Tiempo Real) + #14 (Guardián de los Objetivos)
**Capa Transversal:** C7 (Resiliencia Agéntica) — variante interna del Monstruo
**Bloqueos:** ninguno técnico
**Resultado esperado:** El stack tecnológico del Monstruo y de cada empresa hija se mantiene en la vanguardia automáticamente, no por inspección manual ocasional.

---

## 0. Procedencia

OM-06 v3.0 (`docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` sección "Vanguardia Perpetua") establece que el stack debe estar siempre al día. Hoy esto se materializa solo como skill `anti-autoboicot` que recuerda al agente validar versiones antes de escribir código. Esto es reactivo, no proactivo.

Auditoría 2026-05-26: 0 sprints en backlog cubren OM-06 ejecutivamente.

---

## 1. Audit pre-sprint

Lo que existe en el ecosistema actual operando como vanguardia parcial: el skill `anti-autoboicot` opera reactivamente cuando un agente está por escribir código, el skill `validacion-tiempo-real` consulta Perplexity para verificar versiones, y el skill `el-monstruo-armero` mantiene un catálogo investigado de herramientas listas para usar. Sin embargo, ninguno de estos opera de forma autónoma sin que un agente externo los invoque.

Lo que falta es un sistema activo: un job perpetuo que escanea el stack canónico del Monstruo y de cada empresa hija, detecta versiones obsoletas, vulnerabilidades, mejores alternativas emergentes, y propone refreshes con evidencia. Sin esto, el ecosistema se va degradando silenciosamente hasta que un incidente lo revela.

---

## 2. Tareas (Scope mínimo viable)

El sprint propone una capability `stack_refresh` con los siguientes módulos:

**Módulo de inventario.** Cada componente del stack canónico (Supabase, Railway, modelos LLM, frameworks frontend, librerías core) se cataloga en una tabla `stack_inventory` con columnas para versión actual, fecha de última verificación, fuente de verdad oficial, y nivel de criticidad. El catálogo se hidrata automáticamente desde `package.json`, `requirements.txt`, `pnpm-lock.yaml` y archivos de configuración de cada repo del ecosistema.

**Módulo de scan.** Un job semanal compara cada versión catalogada contra la versión más reciente publicada por el upstream oficial, usando Perplexity Sonar Reasoning Pro como validador en tiempo real. Para cada componente que tenga una versión más reciente, se calcula una métrica de gap: cuántas versiones de retraso, qué tipo de cambios incluye (security, breaking, feature), y cuál es la severidad combinada.

**Módulo de alertas.** Cuando un componente tiene gap crítico (CVE conocido, breaking change relevante, o más de 3 versiones de retraso), se dispara una alerta al Embrión Daddy del proyecto correspondiente. La alerta incluye evidencia textual del upstream, propuesta de upgrade y estimación de esfuerzo.

**Módulo de propuestas.** Para cada alerta, el sistema propone un sprint de upgrade con scope, riesgos y plan de rollback. La decisión final siempre es HITL en tier Owner. El propósito es que el humano tenga visibilidad estructurada, no que se aplique upgrade automático sin su firma.

**Módulo de discovery de alternativas.** Adicional al refresh de versiones, el módulo escanea el horizonte de herramientas emergentes en cada categoría (LLMs, frameworks, plataformas) y reporta candidatos que superan a los actuales en benchmarks objetivos. Esto materializa la cláusula "vanguardia perpetua" más allá de solo mantener actualizado lo que ya existe.

**Módulo de integración con OM-04.** Cada vez que se ejecuta un upgrade y el sistema detecta un error post-upgrade, se persiste como caso en `error_memory` con la lección extraída, para que la próxima decisión de upgrade considere ese histórico. Esto cierra el loop entre OM-06 y OM-04.

---

## 3. Dependencias

Este sprint depende de Perplexity Sonar (ya disponible vía `SONAR_API_KEY`), de la tabla `error_memory` del Monstruo (ya existe), del schema de Supabase para `stack_inventory` (a crear), y de la conexión al endpoint `/v1/genome/now` del Sprint 91 que ya provee inventario base de repos y servicios.

---

## 4. Criterios de Cierre y Métricas de Éxito

El éxito se mide en tres dimensiones. Primero, cobertura: al menos el 95% de los componentes del stack canónico están en `stack_inventory` con verificación menor a 30 días. Segundo, frescura: ningún componente operando con CVE crítico permanece vulnerable más de 7 días. Tercero, descubrimiento: al menos una alternativa emergente se evalúa formalmente cada trimestre por categoría.

---

## 5. Anti-doctrina

No se debe ejecutar upgrade automático sin firma del Owner, porque un upgrade puede romper integraciones invisibles. No se debe consultar entrenamiento del LLM para versiones porque por definición está desactualizado. No se debe perseguir vanguardia que sacrifique estabilidad sin medir el costo. No se debe alertar sobre componentes con gap menor (1 versión patch) salvo que el changelog reporte security fix.

---

## 6. Notas de canonización

Este sprint se inyecta como `Estado: Propuesto — Canonizado sin ejecutar`. Aparece en el Tablero de Campaña como nodo del distrito `backlog_canonizado` con `paradigm: vanguardia_perpetua`. Su status se promueve a `EJECUCION` cuando aparezca un commit a `kernel/stack_refresh/` o cuando se cree la tabla `stack_inventory` en migraciones SQL.

Firmado: **Manus B — 2026-05-26**
Auditor pendiente: Cowork (T2)
