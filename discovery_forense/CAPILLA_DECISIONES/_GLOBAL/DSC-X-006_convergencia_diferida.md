---
id: DSC-X-006
proyecto: GLOBAL
tipo: patron_replicable
titulo: "Patrón Convergencia Diferida — proyectos del portfolio arrancan autónomos con infra compartida y convergen en momentos elegidos cuando ambos prueban PMF"
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:bridge/cowork_to_manus_REPORTE_ONBOARDING_2026-05-06.md
  - repo:docs/EL_MONSTRUO_APP_VISION_v1.md
cruza_con: [TODOS]
---

# Patrón Convergencia Diferida

## Decisión

Los proyectos del portfolio arrancan autónomos con su propio roadmap y mercado. Comparten infra crítica desde día 1 (Stripe checkout, Manus-Oauth, design tokens, observability). Definen API contracts de convergencia futura en su intake. La integración real con otros proyectos del portfolio ocurre en momentos elegidos cuando cada uno prueba PMF independiente — no por default ni por arquitectura forzada de día 1.

## Por qué

No forzar integración prematura: si un proyecto falla regulatoriamente o no encuentra demanda, no arrastra a los otros. Probar mercado por separado: cada empresa-hija valida su nicho sin depender de las demás. Convergencia se gana, no se asume. Reduce deuda técnica vs construcción de monólito multi-producto. Aplica a CIP × Marketplace × Interiorismo × Roche Bobois (eje principal), CIES × CIP, BioGuard × Vivir Sano × NIAS, y futuros.

## Implicaciones

Inventario v3 se mantiene como está (proyectos separados). Cap 10 v1.2 del documento de visión gana capa "Mapa de Ejes de Convergencia Futura". Pipeline E2E del Sprint 87 NUEVO gana paso pre-build: "Diseñar API contract de convergencia con otros proyectos del portfolio". Compartir infra ≠ fusión.

## Estado de validación

firme — fruto de iteración Cowork-Alfredo durante sesión 2026-05-06 cerrando conflicto §8.2 del reporte onboarding.
