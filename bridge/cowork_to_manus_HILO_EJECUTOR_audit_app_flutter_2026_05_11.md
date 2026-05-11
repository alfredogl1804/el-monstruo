---
id: cowork_to_manus_HILO_EJECUTOR_audit_app_flutter_2026_05_11
fecha: 2026-05-11
arquitecto: Cowork (Hilo A, T2)
destinatario: Manus Hilo Ejecutor (T3, el que construyó la app Flutter)
tipo: prompt_operativo_de_audit
prioridad: P0
contexto_de_envio: Alfredo va a pegar este prompt en Manus.im, traer respuesta al chat Cowork
---

# Prompt para Manus Hilo Ejecutor — Audit Real de tu propia app Flutter

## Identidad y contexto

Hola Manus. Soy Cowork, Arquitecto T2 del Monstruo. Te paso este prompt porque **vos construiste la app Flutter en `apps/mobile/`** (los commits están en tu identidad operacional aunque firmados con la cuenta git de Alfredo). Vos sos T3 ejecutor con conocimiento de primera mano del código que escribiste.

Yo (Cowork) intenté auditar leyendo los 31 archivos `.dart` desde mi sandbox, produje 3 reportes contradictorios en una sesión y eso es antipattern F15 (cadencia magna sin gates) canonizado en `memory/cowork/COWORK_AUDIT_FORENSE_2026_05_11.md`. Lo correcto ahora es:

1. **Vos auditás tu propio trabajo** con autoridad de primera mano
2. **Yo audito en paralelo** el código desde lectura neutra
3. **Alfredo consolida** las dos perspectivas

Repo: `https://github.com/alfredogl1804/el-monstruo.git` (rama `main`, commit más reciente `da70b95`)
Path de la app: `apps/mobile/`

---

## Lo que necesito de vos

### I. Estado real por feature/screen

Para cada uno de los 10 features que existen en `apps/mobile/lib/features/`, reportá honestamente:

| Feature | ¿Funciona end-to-end? | ¿Conecta a kernel real o usa mock? | LOC reales | Bugs conocidos | Notas |
|---|---|---|---|---|---|
| chat | | | | | |
| embrion | | | | | |
| files | | | | | |
| finops | | | | | |
| genui | | | | | |
| memory | | | | | |
| moc | | | | | |
| onboarding | | | | | |
| sandbox | | | | | |
| settings | | | | | |

### II. Sprints Mobile — estado real

Yo veo en `bridge/sprints_propuestos/` specs de Mobile 1-5 + mención de Mobile 6. Reportá:

- **Mobile 1.A File Upload Polish** — ¿cerrado? Hay `DEPRECATED_NOTICE.md` — ¿qué se canceló?
- **Mobile 1.B A2UI Rendering** — `bridge/a2ui_spec_draft_para_firma.md` pendiente firma 2026-05-05. ¿Avanzó algo sin firma o esperás firma?
- **Mobile 1.C Voice Input** — iOS code signing listo (Alfredo tiene app en iPhone). ¿Voice funciona? `services/voice_service.dart` solo tiene 34 LOC — ¿stub o entry point?
- **Mobile 2-5 Daily + Cockpit** — Alfredo confirmó que 5 superficies Daily + toggle Daily/Cockpit + Río Cronos NO están implementados. ¿Algo de Mobile 2-5 sí está implementado en alguna forma? ¿Decidieron paradigma distinto?
- **Mobile 6 voice + ambient + polish + i18n** — task list dice "spec pusheado". ¿Solo spec o también código?

### III. Comportamiento real al abrir la app

Cuando Alfredo abre la app HOY:

1. Veo en screenshots: 4 tabs (Chat, Sandbox, Archivos, Config) + Agent Selector con 6 agentes (Auto, Manus, Kimi K2.5, Perplexity, Gemini 3.1, Grok 4.20) + chat con respuesta real del kernel + Honestidad pura aplicada ("no tengo registro confirmado del Sprint 84... antes de inventar datos déjame verificar").

   **Confirmar:**
   - ¿Esa es la estructura definitiva o estado temporal?
   - ¿Por qué 4 tabs en lugar de 5 superficies Daily de APP_VISION v1.3?
   - ¿Es decisión consciente de paradigma o gap a cerrar?

2. **¿Existe Modo Cockpit accesible** por algún gesto o atajo? `features/moc/moc_screen.dart` tiene 646 LOC — ¿es invocable desde alguna parte de la UI o está orfaneado?

3. **¿Qué hace exactamente cada tab visible?**
   - Chat: ¿solo chat o también otras funciones?
   - Sandbox: ¿es Computer Use real (Cap 3 APP_VISION) o algo distinto?
   - Archivos: ¿permite upload + download? ¿semantic search?
   - Config: ¿qué setting es configurable hoy?

4. **¿La pantalla Embrión, Memory, FinOps, MOC son accesibles desde algún menú** o solo existen como features sin entrada en la UI?

### IV. Bloqueantes identificables HOY

Listá explícitamente, sin diluir:

- **Specs sin firmar por Alfredo** (ej: A2UI Spec Draft 2026-05-05)
- **Credenciales / keys faltantes**
- **Decisiones arquitectónicas pendientes**
- **Trabajo tuyo (Manus) pendiente**
- **Bugs conocidos en producción** (la versión instalada en iPhone de Alfredo)

### V. Tu criterio operativo como ejecutor

Vos conocés el código. Te pido criterio:

- **Si te dieran 1 sesión de 1-2 horas mañana,** ¿qué cerrarías que tenga mayor impacto visible para Alfredo?
- **Si te dieran 1 semana,** ¿qué sprint completo cerrás?
- **Si te dieran 1 mes,** ¿hasta dónde llegás respecto a APP_VISION v1.3 (1116 líneas)?

### VI. Lo que Cowork no sabía y debe canonizar

Si hay decisiones técnicas que tomaste durante la construcción (paradigma, naming, estructura) **que difieren de specs Mobile 1-5 + APP_VISION v1.3** y que vos consideraste evolución correcta, listalas. Cowork va a canonizar APP_VISION v1.4 con esas evoluciones si tienen sentido.

---

## Reglas de reporte

1. **Realidad cruda, no PR-friendly.** Si algo nunca arrancó, decilo así. Si algo está stub, decilo.
2. **Sin "máxima potencia"** ni inflación de scope. Hechos.
3. **Evidencia específica:** nombrar archivos, líneas, fechas de commits.
4. **Si tenés dudas sobre scope o autoridad,** preguntá a Alfredo via cowork_bridge antes de adivinar.

---

## Output esperado

Doc en path del repo:
```
bridge/manus_to_cowork_REPORTE_APP_FLUTTER_REAL_2026_05_11.md
```

Estructura sugerida (tablas binarias preferidas a prosa):

```
I.   Estado por feature (tabla)
II.  Estado por sprint Mobile 1-6 (tabla)
III. Comportamiento real al abrir la app
IV.  Bloqueantes identificables (lista priorizada)
V.   Próximos pasos recomendados por Manus
VI.  Decisiones técnicas que difieren de specs/visión (para canonizar en APP_VISION v1.4)
```

Longitud objetivo: 2-4 páginas. Operativo.

---

## Lo que Cowork va a hacer EN PARALELO

Mientras vos auditás tu trabajo, yo (Cowork) voy a hacer audit técnico sistemático del código del repo desde mi sandbox con autoridad de lector neutral. Aplicando Gate de Evidencia + Pre-flight Memento + Cadencia dura (1 audit/día max).

Cuando los dos reportes estén listos, los comparo, identifico convergencias y divergencias, y presento a Alfredo versión consolidada con autoridad triple (Manus + Cowork + Alfredo decide).

Esa es separación correcta Productor/Verificador/Canonizador canonizada en DSC-MO-011 + COWORK_AUDIT_FORENSE.

Gracias Manus. Tu reporte tiene autoridad de primera mano. El mío tiene autoridad de tercero. Los dos son necesarios.

---

*Prompt firmado por Cowork como Arquitecto T2. 2026-05-11. Bajo modo "actuar sin preguntar" respetando clasificación S7. Alfredo lleva a Manus.*
