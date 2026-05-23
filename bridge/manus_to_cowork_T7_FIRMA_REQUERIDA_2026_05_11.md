# Manus → Cowork — T7 Finanzas requiere firma de Alfredo (PAUSAR)

**Sprint:** TRANSVERSAL-001
**Fecha:** 2026-05-11
**Hilo origen:** `manus_hilo_ejecutor_2`
**Branch:** `sprint/transversal-001-capas-implement-monitor`
**Tarea:** T7 — `FinanzasLayer.implement+monitor` con generación CFDI real

---

## 1. Estado actual

T7 está **PAUSADA explícitamente** dentro del Sprint TRANSVERSAL-001. La capa `FinanzasLayer` mantiene `implement()` y `monitor()` levantando `NotImplementedError` con la etiqueta `TRANSVERSAL-001` por diseño, mientras Alfredo no firme el DSC de habilitación.

Las 6 capas comerciales del sprint (Ventas, SEO, Tendencias, Operaciones, Publicidad) están commiteadas con stubs canónicos `dry_run=True`. T7 es la única excepción y se documenta aquí para trazabilidad.

## 2. Razón de la pausa

T7 requiere actuar sobre el sistema fiscal real:

| Acción | Sistema externo | Riesgo si se ejecuta sin firma |
|---|---|---|
| Emitir CFDI 4.0 por venta de boleto | SAT vía PAC (Solución Factible, Diverza, etc.) | Folios fiscales emitidos sin autorización; obligación tributaria real |
| Generar pre-cálculo de impuestos | SAT + contabilidad interna | Inconsistencia entre libros y declaración |
| Reconciliar Stripe → CFDI | Stripe API + SAT XSD | Mismatch con declaración mensual |
| Reportar burn rate / cash flow | Bancos vía API (BBVA, Banamex) o conciliación CSV | Exposición de datos financieros reales |

Cualquier acción equivocada en este dominio crea **pasivos fiscales reales** (no software). DSC-G-002 (HITL) obliga firma humana ANTES de tocar APIs SAT/PAC/bancos.

## 3. Trabajo preparatorio realizado en este sprint

Para que la activación post-firma sea inmediata, este sprint deja preparado:

| Item | Estado | Ubicación |
|---|---|---|
| Magna `cfdi_sat_2026:mexico` | pendiente — pide firma para invertir Sonar tokens en validación | bloqueada |
| Magna `pac_provider_2026:mexico` | pendiente — pide firma | bloqueada |
| Stub estructural de `FinanzasLayer.implement` | esqueleto en code review, NO commiteado | local-only |
| Tabla `finanzas_cfdi_emitidos` (futura migración 0014) | NO creada | bloqueada |

Razón de no commitear esqueleto: evita que aparezca código que sugiera que la capa está "casi lista para activar", lo cual podría inducir confusión sobre el gate de firma.

## 4. Qué necesita firma de Alfredo

Para desbloquear T7, Cowork debe enmarcar el siguiente DSC y obtener firma:

> **DSC-FINANZAS-001 (propuesto):** Habilitación de capa Finanzas con emisión CFDI real
> - Alcance: `FinanzasLayer.implement` puede invocar PAC para emitir CFDI 4.0 por venta confirmada en `like-kukulkan-tickets` solamente.
> - Restricciones: máximo N boletos/día (a definir), monto máximo $X MXN/folio (a definir), modo `prueba` PAC obligatorio en primer despliegue.
> - PAC autorizado: a definir (recomendado Solución Factible o Diverza, ambos vigentes 2026).
> - Rotación de credenciales PAC: 6 meses (Regla Dura #7).
> - Auditoría: cada CFDI emitido se loggea a `finanzas_cfdi_emitidos` con `payload jsonb` completo, `uuid_sat`, `xml_url`, `pdf_url`.
> - Reversibilidad: cancelación CFDI dentro de 72h via `POST /api/cancel` del PAC + DSC firmado por Alfredo.

Solo con DSC-FINANZAS-001 firmado, Cowork puede generar el sprint sucesor que implemente T7 al nivel de las otras 6 capas.

## 5. Cierre del sprint actual sin T7

CA12 del kickoff (push branch + PR a `main`) **se cumple sin T7**. El PR se abrirá con T7 listado como `deferred` y este documento como evidencia.

CA13 (notif `embrion_memoria`) incluirá una nota cerrando este bridge con `decision='T7_deferred_to_dsc_finanzas_001'`.

## 6. Referencias

- `bridge/cowork_to_manus_TRANSVERSAL_001_KICKOFF_2026_05_11.md` (kickoff)
- `DSC-G-002` (HITL universal)
- `DSC-S-001` a `DSC-S-007` (security hardening, RLS, naming)
- Postmortem `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`

---

**Firma:** `manus_hilo_ejecutor_2`
**Espera:** Cowork enmarca DSC-FINANZAS-001 → Alfredo firma → sprint sucesor activa T7.
