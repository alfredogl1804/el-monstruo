<!-- lint_strict -->
# T1-MAGNA-001 — Paradigma de Interfaz del Monstruo — FIRMADA

**Tipo:** Decisión T1 Magna — FIRMADA
**Origen:** `T1_MAGNA_001_PARADIGMA_INTERFAZ_PARA_FIRMA.md` (Manus B, 2026-05-26)
**Estado:** Enforced (firmada T1)
**Firma:** Alfredo Góngora (T1 magna) — dada verbalmente en sesión Cowork 2026-05-27, transcrita por Cowork T2-A para ratificación. T1 puede revocar.

---

## Decisión firmada

```yaml
decision_t1_magna_001:
  paradigma_ganador: C   # Híbrido formal con jerarquía clara
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  transcrito_por: Cowork T2-A (firma verbal T1 en sesión, pendiente ratificación)
  justificacion_corta: >
    Captura la visión "la interfaz del Monstruo es que no hay interfaz; las
    pantallas se invocan, no se muestran" PERO con red de seguridad. La
    invocación (voz + WhatsApp + ambient + Smart Rendering) es el modo
    principal; las pantallas sobreviven solo como backstops mínimos con
    propósito (Daily 5). Elegida sobre Acto 2 puro por reversibilidad (si el
    ambient falla, hay rescate), entrada a mercado LATAM vía WhatsApp (72% no
    abre apps nuevas), y porque las 6 capas comerciales viven sobre transport
    agnóstico que el híbrido soporta nativamente.
  sprints_a_cancelar:
    - MOBILE_2_COCKPIT
    - MOBILE_3_COCKPIT
    - MOBILE_4_COCKPIT
    - MOBILE_5_COCKPIT
    - TOGGLE_DAILY_COCKPIT
    - PORTFOLIO_EMPRESAS_HIJAS_UI   # reemplazado por SMART_RENDERING_CAPABILITY
  sprints_a_diferir:
    - COCKPIT_1   # diferido hasta validar que Daily 5 no es suficiente
    - COCKPIT_2
    - COCKPIT_3
  sprints_a_reactivar_si_fallo:
    - COCKPIT_1   # reactivar si Daily 5 demuestra ser insuficiente en 60d
    - COCKPIT_2
    - COCKPIT_3
  fecha_revision_60_dias: 2026-07-26
```

---

## Regla de oro canonizada (Opción C)

| Tipo de tarea | Transport principal | Pantalla backstop |
|---|---|---|
| Diálogo, preguntas, tareas conversacionales | WhatsApp + Voice | NO |
| Estado del día, qué hay que hacer | Voice + Notification | Daily 5 (minimal) |
| Auditar / configurar / power features | Invocación on-demand | Vista densa invocada (no navegada) |
| Confidente (sensible, deep link) | Voice + WhatsApp DM | Modo Confidente UI sin nombre |
| Catastros (4 dominios persistidos) | Smart Rendering invocado | Vista de catastro on-demand, efímera |

**Principio:** invocación primaria (pull del usuario o push efímero del kernel) → la superficie aparece por intención, hace su trabajo, se disuelve. La navegación persistente NO es la cara del Monstruo. Alineado con Objetivo #3 ("un chat, un input, sin menús infinitos, sin configuración visible") + Objetivo #2 (Apple/Tesla = interfaz que desaparece).

---

## Orden de ejecución desbloqueado (prioridad C)

1. `MOBILE_REALIGNMENT_001` — ✅ ejecutado (PR #114), cimiento/theme
2. `WHATSAPP_GATEWAY_P0` + `VOICE_BRAND_ELEVENLABS` — transport conversacional principal
3. `LISTENING_AMBIENT_CAPABILITY` — kill switch verbal
4. `MOBILE_0_SMP` + `CAPABILITY_VAULT_SOBERANO`
5. `DAILY_5_SUPERFICIES` — única pantalla del Acto 1 que sobrevive (backstop)
6. `MODO_CONFIDENTE_UI` — deep link silencioso
7. `SMART_RENDERING_CAPABILITY` — composición sobre los 4 Catastros
8. 6 capas transversales comerciales (Sprint 91.14: CAPA_VENTAS, SEO, ADS, TENDENCIAS, OPS, FINANZAS)

---

## Consecuencias post-firma (a ejecutar)

1. **Manus B** regenera el Tablero de Campaña: cancelados → halo gris; priorizados C → P0.
2. **Cowork T2-A** audita esta firma y cierra `CONTRADICTIONS_MAP.md` CONTRA-001 (+ CONTRA-002, CONTRA-005) como resueltos.
3. Se desbloquean los 18+ sprints según orden C.
4. Revisión a 60 días (2026-07-26): ¿Daily 5 suficiente? Si no → reactivar COCKPIT_1/2/3.

## Relación con análisis previo

- `bridge/cowork_CRUCE_SPRINTS_FLUTTER_x_15_OBJETIVOS_2026_05_27.md` (Cowork) = subset Flutter de esta decisión (los 4 sprints mobile_2-5). T1-MAGNA-001 es el backlog completo (18+ sprints incl. WhatsApp/Voice/Listening/capabilities). El cruce queda **subsumido** por este documento; su conclusión (mobile_2-5 mueren) es consistente con C.
- **NO se redacta DSC-MO-012:** esta firma T1-MAGNA-001 ES la canon del paradigma. Un DSC paralelo sería duplicación (DSC-G-004).

## Drift menor anotado

El §6 del doc PARA_FIRMA referenciaba "T1-MAGNA-005 = WhatsApp Gateway P0", pero el `T1-MAGNA-005` real del repo ya es Forja Shadow→Enforce (FIRMADA Opción D, 2026-05-27). Colisión de numeración en la serie T1-MAGNA — limpiar en pase de mantenimiento de la Capilla, no bloquea esta firma.

---

**Transcrito por:** Cowork (Arquitecto T2-A), 2026-05-27 — para ratificación T1.
