# DSC-S-017: Anthropic Hivecom legacy deprecada con observación pasiva 60 días

**Tipo**: Decisión Soberana Canonizada (Seguridad / Inventario)
**Estado**: FIRMADO
**Sprint origen**: la-forja-001
**Fecha**: 2026-05-16
**Autor ejecutor**: Hilo B (Manus)
**Orquestador**: Alfredo (decisión directa basada en evidencia visual)
**Referencias cruzadas**: DSC-S-001, DSC-S-005 (default archive antes que delete), DSC-S-008 (rotación automatizada)

---

## Contexto

Durante la auditoría del 2026-05-16 sobre cuentas Anthropic operativas, se descubrió mediante screenshots de `platform.claude.com` la existencia de una **tercera cuenta Anthropic** propiedad de Alfredo, no documentada en el inventario previo (`bridge/credentials_inventory.md` versión Sprint MEGA-CIERRE-HOY del 2026-05-12). La cuenta es propiedad del email `alfredogl1@hivecom.mx` (Google Workspace), organización "alfredogl1's Individual Org", con plan API directo y método de pago Stripe Link.

La cuenta presenta el siguiente estado verificado al 2026-05-16:

- Saldo pendiente: **-$0.18 USD**
- Auto-recharge: **deshabilitado**
- Acceso a la API: **pausado** ("Agrega fondos para reanudar el acceso a la API")
- Estado de Trust & Safety: **NO suspendida** (distinto de la cuenta legacy de Gmail)
- Historial de facturación: 14 microfacturas mensuales por ~$10 USD c/u entre 30-abr y 1-may, más concesiones de crédito de $5 USD (21-feb), $90 USD (8-mar) y $150 USD (2-may)
- Total acumulado en cargas manuales feb–may 2026: **~$245 USD**

La cronología reconstruida con evidencia binaria es: la cuenta Hivecom financió el consumo del kernel desde febrero hasta el 12-may 2026; en esa fecha el Sprint MEGA-CIERRE-HOY rotó la `ANTHROPIC_API_KEY` del kernel a una key nueva emitida por la cuenta del Apple Private Relay (`hfhm9mycw7@privaterelay.appleid.com`); desde entonces el consumo del kernel migró completamente a la cuenta nueva con auto-recharge de $100 USD activo. La cuenta Hivecom quedó pasiva, drenando los últimos créditos sobrantes hasta llegar al saldo negativo actual.

## Decisión

La cuenta Anthropic Hivecom legacy se declara **DEPRECADA 2026-05-12** y queda sujeta a **observación pasiva durante 60 días** antes de cualquier acción de archive o delete. Específicamente, las acciones canonizadas son:

1. **No recargar.** No agregar fondos manualmente ni reactivar auto-recharge bajo ninguna circunstancia. Cualquier llamada API que llegue a esta cuenta debe fallar con `403 insufficient_credits` para delatar consumidores zombi olvidados.
2. **No cancelar formalmente.** Mantener la cuenta en estado "pausada por billing" durante 60 días desde la fecha de canonización (vencimiento de observación: **2026-07-15**). La doctrina DSC-S-005 (default archive antes que delete) exige preservar la cuenta como evidencia recuperable durante una ventana razonable.
3. **Monitorear errores `403 insufficient_credits`** en logs del kernel y de cualquier proyecto auxiliar de Alfredo. Cualquier ocurrencia indica un consumidor que aún apunta a la API key vieja de Hivecom y debe ser identificado y migrado a la cuenta nueva del Apple Relay.
4. **Cerrar el caso al cumplir 60 días** sin errores `403`. Si pasa el período de observación sin que ningún consumidor reclame la cuenta, archivar formalmente desde el panel de Anthropic y actualizar el inventario con `Estado: ARCHIVADA 2026-07-15`.

La excepción única que justifica recarga es: si durante los 60 días aparece un consumidor crítico que apunta a la key vieja y cuya migración inmediata a la cuenta nueva del Apple Relay no es viable. En ese caso, la decisión requiere DSC firmado en la sesión correspondiente con justificación operativa explícita.

## Justificación

La hipótesis "cuenta zombi totalmente abandonada" es la más probable basándose en la evidencia disponible (rotación documentada del 12-may + ausencia de consumo posterior + auto-recharge deshabilitado). Sin embargo, la cuenta financió el kernel durante tres meses con desembolsos significativos, lo cual implica que múltiples scripts, repositorios y posiblemente proyectos personales pudieron haber importado la API key vieja. La estrategia de **observación pasiva** es la única que garantiza descubrimiento exhaustivo de consumidores zombi sin pagar por el privilegio de mantenerlos vivos: si un consumidor existe, va a fallar y delatar su presencia; si nadie reclama, la cuenta puede archivarse con confianza.

La decisión también respeta la doctrina DSC-S-008 sobre rotación automatizada y el principio de "operar exclusivamente con la cuenta nueva del relay" establecido en el Sprint MEGA-CIERRE-HOY. Mantener Hivecom recargada significaría operar con dos canales de billing paralelos, lo cual contradice esa doctrina y reabre el riesgo de confusión que originalmente motivó la rotación.

## Cumplimiento e implicaciones

- El inventario `bridge/credentials_inventory.md` queda actualizado con la entrada de Hivecom marcada DEPRECADA y la nota de observación pasiva.
- El responsable de monitorear errores `403 insufficient_credits` durante los 60 días es Alfredo (revisión semanal en logs Langfuse y Railway).
- Al vencimiento del período de observación (2026-07-15), un sprint posterior debe declarar el archive formal o la extensión del período si hay evidencia que lo justifique.
- Esta decisión no requiere cambios de código, no toca producción, y no afecta el funcionamiento del kernel actual (que ya opera contra la cuenta del Apple Relay desde el 12-may).

## Cruces explícitos

- **DSC-S-005**: la observación pasiva 60 días es una aplicación específica del principio "default archive antes que delete" para cuentas externas de proveedores LLM.
- **DSC-S-008**: la cuenta Hivecom queda explícitamente fuera del workflow CI de rotación automatizada (`credentials-rotation-reminder.yml`) ya que su API key está deprecada y no debe rotarse.
- **Inventario `bridge/credentials_inventory.md`**: entrada actualizada en el mapa de cuentas dueñas, sección "Anthropic (Hivecom legacy)".
