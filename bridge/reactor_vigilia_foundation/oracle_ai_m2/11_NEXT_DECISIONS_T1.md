# Decisiones T1 Pendientes Post-M2

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

La ejecución exitosa de las sondas M2 genera evidencia empírica (`REALTIME_VERIFIED`), pero por diseño arquitectónico, M2 no toma decisiones sobre cómo usar esa evidencia.

Las siguientes decisiones requieren la intervención y aprobación de T1 (Alfredo Góngora):

## 1. Autorización de Reclasificación de Riesgo
**Decisión:** ¿Se autoriza el inicio de `SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001`?
**Contexto:** Este sprint tomará el overlay generado por M2 y, para las capacidades que ahora son `REALTIME_VERIFIED`, evaluará si su `risk_class` debe elevarse de R0 a niveles superiores (R1-R4) según la superficie de ataque real confirmada.

## 2. Automatización del Oráculo (Daemon/Scheduler)
**Decisión:** ¿Se autoriza la creación de un scheduler (cron/daemon) R0 para ejecutar el Oráculo M2 periódicamente?
**Contexto:** Actualmente M2 se ejecutó como un script finito (one-shot). Para que El Monstruo tenga "vigilia", M2 debe correr en background (ej. cada 24 horas) para detectar si un proveedor se cae o lanza un nuevo modelo. ¿Se implementa vía `manus-config schedule` o un script en una VM persistente?

## 3. Proveedores Obligatorios vs. Opcionales
**Decisión:** De los 6 proveedores probados, ¿cuáles son considerados críticos (core) para la operación del Monstruo y cuáles son opcionales?
**Contexto:** Si un proveedor opcional falla, M2 puede simplemente reportarlo. Si un proveedor crítico falla (ej. OpenAI), ¿debería M2 emitir una alerta de emergencia (Blocker) al Dispatcher?

## 4. Presupuesto Recurrente
**Decisión:** ¿Cuál es el presupuesto mensual en USD autorizado para las sondas de verificación empírica del Oráculo M2?
**Contexto:** Este sprint usó un hard cap de $5.00 USD por corrida. Si se automatiza para correr diariamente, el presupuesto debe definirse formalmente.

## 5. Integración con el Catastro General
**Decisión:** ¿Los outputs de M2 (modelos detectados, capacidades verificadas) deben alimentar un Catastro General en Supabase, o deben permanecer como artifacts locales (JSON) consumidos solo por los loops internos de Vigilia?
**Contexto:** Actualmente todo se guarda en JSONs locales en el sandbox/repo. Moverlos a Supabase implica abrir el plano de datos y requiere diseño de RLS.
