# Veredicto Sabio — Perplexity Sonar T2-B
**DSC bajo audit:** DSC-G-013 DRAFT — "DB↔Repo Coherence Gate"
**Fecha:** 2026-05-18
**Rol del Sabio:** auditor externo web/mercado (browsing tiempo real)
**Veredicto binario:** 🟡 **CON CAVEAT**

---

## 1. ¿El patrón "DB↔Repo drift" es problema reconocido en literatura técnica reciente?

**Sí.**

- **Liquibase** define "database/schema drift" como cambios de schema fuera del proceso gobernado de migraciones, causados por hotfixes, parches no versionados o procesos inconsistentes, con riesgos de pérdida de datos, compliance, seguridad y costo. Fuente: [Liquibase — Detect and Prevent Database Schema Drift](https://www.liquibase.com/blog/database-drift).
- **Redgate/Flyway** define drift como diferencias entre dos representaciones de DB que dicen tener la misma versión de schema, incluyendo cambios out-of-band y cambios en scripts versionados después del deploy. Fuente: [Redgate Flyway — How to Detect Database Drift using Flyway Snapshots](https://www.red-gate.com/hub/product-learning/flyway/how-to-detect-database-drift-using-flyway-snapshots/).
- El spec DSC-G-013 identifica el mismo patrón en tres capas: repo↔`schema_migrations`, código↔CHECK constraints y planning↔realidad. Fuente: [DSC-G-013 draft](https://github.com/alfredogl1804/el-monstruo/blob/main/discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-013_db_repo_coherence_gate_DRAFT.md).

## 2. ¿Qué herramientas/frameworks existentes resuelven este gate?

- **Atlas**: cubre más que §4.2 Nivel A. Ofrece GitHub Actions para `migrate/lint`, `migrate/apply`, `migrate/test`, `migrate/autorebase`, `schema/lint`, `schema/plan` y monitoreo de schema. También detecta cambios destructivos, historial no reproducible y conflictos por migraciones concurrentes. Fuente: [Atlas GitHub Actions](https://atlasgo.io/integrations/github-actions).
- **Flyway Enterprise**: resuelve drift DB↔snapshot/repo con `check -drift`, comparando snapshots, live DBs o migraciones aplicadas, y genera artefactos JSON/HTML de diferencias. Fuente: [Redgate Flyway](https://www.red-gate.com/hub/product-learning/flyway/how-to-detect-database-drift-using-flyway-snapshots/).
- **Liquibase**: resuelve detección de drift mediante `liquibase diff --format=json`, drift reports, snapshots y automatización CI/CD. Fuente: [Liquibase](https://www.liquibase.com/blog/database-drift).
- **SQLFluff/dbt**: sirve para lint/render de SQL y dbt macros, pero no resuelve por sí solo drift runtime DB↔repo↔`schema_migrations`. Fuente: [SQLFluff dbt templater](https://docs.sqlfluff.com/en/stable/configuration/templating/dbt.html).

**Comparación contra §4.2:** la propuesta de DSC-G-013 es correcta como gate ligero específico de El Monstruo, pero Atlas/Flyway/Liquibase cubren mejor replayability, snapshots, drift reports, cambios destructivos y migraciones concurrentes.

## 3. Mejores prácticas para `schema_migrations` multi-agente que faltan en el spec

- **Snapshots inmutables post-migrate**: Flyway recomienda capturar snapshot después de migración exitosa, versionarlo y comparar target DB contra snapshot esperado antes de deploy. Fuente: [Redgate Flyway](https://www.red-gate.com/hub/product-learning/flyway/how-to-detect-database-drift-using-flyway-snapshots/).
- **Migration replayability test**: Atlas valida que el historial de migraciones pueda reproducirse desde cualquier punto, no solo que el número siguiente sea correcto. Fuente: [Atlas GitHub Actions](https://atlasgo.io/integrations/github-actions).
- **Protección contra concurrent migrations**: Atlas detecta cambios de historial por migraciones concurrentes y tiene `migrate/autorebase` para arreglar conflictos de `atlas.sum`. Fuente: [Atlas GitHub Actions](https://atlasgo.io/integrations/github-actions).
- **Diff JSON machine-readable en CI**: Liquibase recomienda drift diff en JSON para contar diferencias, priorizar y bloquear CI si afecta objetos críticos. Fuente: [Liquibase](https://www.liquibase.com/blog/database-drift).
- **Rollback/resolve workflow**: Flyway documenta tres salidas ante drift: revertir, ignorar irrelevantes o incorporar cambios a source control con nueva migración. Fuente: [Redgate Flyway](https://www.red-gate.com/hub/product-learning/flyway/how-to-detect-database-drift-using-flyway-snapshots/).

## 4. Veredicto binario

🟡 **CON CAVEAT**.

El gate es real y necesario: Liquibase, Flyway y Atlas validan que DB↔repo drift es un problema reconocido. Caveat: §4.2 debe incorporar snapshots, replayability, diff JSON, protección de concurrencia y rollback workflow; si no, queda como grep disciplinario, no gate robusto.

---

**Recibido por:** Cowork T2-A
**Status:** documentado verbatim para anti-Memento. Integración de ajustes pendiente de decisión T1 + veredicto GPT-5.5.
