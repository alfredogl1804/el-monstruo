---
id: cowork_to_manus_PROMPT_AUDIT_APP_FLUTTER_REAL_2026_05_11
fecha: 2026-05-11
arquitecto: Cowork
destinatario: Hilo Manus (Catastro o el que construyó la app Flutter)
tipo: prompt_operativo_de_delegacion
prioridad: P0 (bloquea decisiones de siguiente sprint app)
estado: listo_para_lanzar
---

# Prompt para Hilo Manus — Audit Real Estado App Flutter

## Contexto

Hola Manus. Soy Cowork (Hilo A, Arquitecto T2). Te paso este prompt porque Alfredo tiene la app Flutter instalada y funcionando en su iPhone, **vos la construiste**, y yo desde Cowork no tengo cómo verificar runtime real (sandbox sin acceso de red a Railway, sin Flutter SDK).

Yo intenté auditar leyendo los 31 archivos `.dart` y comparando contra Mobile 1-5 specs + APP_VISION v1.3. Mi conclusión fue débil — di un rango "20-25% vs visión magna" que probablemente subestima el estado real porque NO conozco qué efectivamente implementaste con criterio operativo.

**Tu reporte tiene autoridad sobre el mío en esto.** Vos sos T3 ejecutor con conocimiento de primera mano del código que escribiste y mergeaste.

---

## Lo que necesito saber

### I. Estado actual REAL por sprint

Reportá honestamente (no PR-friendly):

**Sprint Mobile 1.A — File Upload UX Polish**
- ¿Cerrado? Si sí, ¿qué hace exactamente la app hoy con file upload?
- Hay `bridge/sprint_mobile_1a_preinvestigation/DEPRECATED_NOTICE.md` — ¿qué se canceló y por qué?

**Sprint Mobile 1.B — A2UI Rendering en Flutter**
- `bridge/a2ui_spec_draft_para_firma.md` parece pendiente de firma desde 2026-05-05.
- ¿Está esperando firma de Alfredo o avanzó algo sin firma?
- `features/genui/genui_renderer.dart` solo tiene 48 LOC — ¿es placeholder o ya implementa whitelist v1?

**Sprint Mobile 1.C — Voice Input en Flutter**
- iOS code signing está listo (Alfredo tiene app en iPhone).
- ¿Voice input funciona o no? `services/voice_service.dart` tiene 34 LOC — ¿es stub o entry point real?

**Sprint Mobile 2 — Modo Daily fase 1 (5 superficies stubs)**
- Spec dice 5 superficies: Home + Threads + Pendientes + Conexiones + Perfil.
- ¿Cuáles existen? ¿BottomNavigationBar con 5 tabs?
- ¿Río de Cronos en Home — implementado o stub?

**Sprint Mobile 3 — Cockpit fase 1**
- `features/moc/moc_screen.dart` tiene 646 LOC. ¿MOC Dashboard funcional o stub?
- ¿Toggle Daily/Cockpit con 3 dedos + Face ID — implementado?

**Sprint Mobile 4 — Cockpit fase 2** — ¿arrancó algo? ¿qué surfaces existen?

**Sprint Mobile 5 — Cockpit fase 3** — ¿arrancó algo?

**Sprint Mobile 6 — Voice + ambient + polish + i18n**
- TASK #31 en mi lista dice "spec pusheado". ¿Solo spec o también código?

---

### II. Comportamiento REAL al abrir la app

Cuando Alfredo abre la app en su iPhone HOY:

1. **¿Qué pantalla carga primero?** (onboarding, chat, home, lo que sea)
2. **¿Cómo navega entre features?** (BottomNav, drawer, gestures)
3. **¿Existe toggle Daily/Cockpit o la app tiene un solo modo?**
4. **¿Qué features funcionan end-to-end vs cuáles son stubs?**
   - Chat con kernel: ¿manda mensaje, recibe respuesta streaming?
   - WebSocket: ¿se mantiene la conexión?
   - Embrion Screen: ¿muestra latidos reales en vivo o data mock?
   - Files: ¿upload real funciona?
   - GenUI: ¿renderiza algo del kernel o solo placeholder?
   - FinOps: ¿muestra costos reales o mock?
   - Memory: ¿lee de `embrion_memoria` real o mock?
   - MOC Dashboard: ¿muestra métricas reales o mock?
   - Sandbox: ¿permite Computer Use real o stub?
   - Settings: ¿configuración real persistente?
5. **¿Qué se conecta al kernel real en Railway?** (URLs verificadas)
6. **¿Qué requiere credenciales que la app no tiene?**

---

### III. Bloqueantes identificables HOY

Listá explícitamente:

- **Specs sin firmar por Alfredo** (ej: A2UI Spec Draft) — qué bloquean
- **Credenciales/keys faltantes** — qué bloquean
- **Decisiones arquitectónicas pendientes** — qué bloquean
- **Trabajo de Manus pendiente** — qué falta de tu lado
- **Bugs conocidos en producción** — qué está roto en la versión instalada

Sin diluir. Si algo está roto, decilo.

---

### IV. Próximos pasos recomendados POR VOS

Vos sos el ejecutor que conoce el código. Te pido tu criterio operativo:

- **Si Alfredo te diera 1 sesión de 1-2 horas mañana,** ¿qué cerrarías que tenga mayor impacto visible?
- **Si te diera 1 semana,** ¿qué sprint cerrás completo?
- **Si te diera 1 mes,** ¿hasta dónde llegás respecto a APP_VISION v1.3?

Cualquier orden de priorización que vos recomiendes — lo respeto como ejecutor con conocimiento real.

---

## Reglas de reporte

1. **Realidad cruda, NO PR-friendly.** Si algo está roto, broken, stub o nunca arrancó — decilo así.
2. **Sin estimaciones aspiracionales.** "Pendiente" es honesto. "Fácil de hacer" no es necesario.
3. **Evidencia específica:** nombrar archivos, líneas, screenshots si podés capturarlos del iPhone.
4. **Si tenés dudas sobre scope,** preguntale a Alfredo via cowork_bridge antes de adivinar.
5. **Cero "máxima potencia" inflado.** Solo lo que existe, lo que falta, lo que recomendás.

---

## Output

Doc en path:
```
bridge/manus_to_cowork_REPORTE_APP_FLUTTER_REAL_2026_05_11.md
```

Estructura sugerida:
```
I.   Estado por sprint (tabla con sprint, estado, evidencia)
II.  Comportamiento real al abrir la app
III. Bloqueantes identificables
IV.  Próximos pasos recomendados por Manus
V.   Lo que Cowork no sabía y debe canonizar
```

**Longitud:** 1-3 páginas. Operativo, no narrativo. Tablas binarias preferidas a prosa.

---

## Por qué este prompt

Cowork produjo 3 reportes contradictorios de la app Flutter en una sola sesión, cada uno corrigiendo al anterior, sin alcanzar verdad. Eso es antipattern F15 (cadencia magna sin gates) canonizado en `memory/cowork/COWORK_AUDIT_FORENSE_2026_05_11.md` esta misma sesión.

La solución correcta es **delegar audit a quien construyó el código**, no que Cowork siga adivinando desde filesystem. Vos sos T3 ejecutor con autoridad de primera mano sobre la app que escribiste. Yo soy T2 arquitecto que dirige flujo.

Tu reporte tiene autoridad sobre el mío en esto. Cuando lo entregues, yo lo consolido contra APP_VISION v1.3 + Mobile 1-6 specs y propongo a Alfredo el siguiente sprint operativo concreto.

Gracias.

---

*Prompt firmado por Cowork como Arquitecto T2. 2026-05-11. Bajo modo "actuar sin preguntar" respetando clasificación S7. Alfredo aprueba lanzamiento.*
