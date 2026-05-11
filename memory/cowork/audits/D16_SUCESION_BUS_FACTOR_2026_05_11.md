---
id: D16_SUCESION_BUS_FACTOR_2026_05_11
dimension: 16
nombre: Sucesión / Bus Factor / Continuidad del Fundador
fecha: 2026-05-11
arquitecto: Cowork
plan_origen: Plan v1.5 — Programa de Certificación de Pericia P1+P2
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado_revisado: H0_exploratorio_2026_05_11
nivel_autoridad_revisado: H0 — backlog de pruebas, NO canónico
razon_revision: "Producido en serie de 9 audits sin evidencia Nivel 1 fresca entre ellos. Inventario de mitigaciones útil. Porcentaje sin rúbrica. Ver CORRECTIVO_ARQUITECTONICO_2026_05_11.md."
cruza_con:
  - D7_GOBERNANZA_RACI_2026_05_11 (GAP G-04, G-08)
  - D12_SEGURIDAD_ADVERSARIAL_2026_05_11 (P0-1 falsificación de identidad)
  - D13_DATOS_MEMORIA_2026_05_11 (Capa M9 memoria humana, GAP M-08)
  - D18_SRE_RESILIENCIA_2026_05_11
  - Objetivo Maestro #12 (Soberanía)
  - Objetivo Maestro #14 (Guardian de los Objetivos)
  - Objetivo Maestro #15 (Memoria Soberana)
  - DSC-MO-006 (Par bicéfalo)
  - DSC-MO-007 (Failover 3 capas)
estado: firme
---

# Dimensión 16 — Sucesión / Bus Factor / Continuidad del Fundador

## Marco

Esta dimensión audita **qué pasa con el Monstruo si Alfredo desaparece**. No es paranoia — es ingeniería de continuidad. "Desaparece" tiene gradientes: 24h sin acceso, 1 semana de vacaciones, 1 mes enfermo, fallecimiento. Cada gradiente exige respuestas distintas.

El Objetivo #12 (Soberanía) exige independencia de proveedores. Pero la soberanía también significa: el proyecto no depende del estado fisiológico de un único humano para sobrevivir.

**Principio fundacional:** Si el proyecto requiere a Alfredo para cualquier decisión P0, entonces el proyecto es Alfredo, no el Monstruo. La construcción del Monstruo es precisamente la construcción de una entidad que sobreviva al fundador — en sus principios, su doctrina, su capacidad operacional.

**Frase orientadora:**

> *"Un proyecto soberano sobrevive a su fundador con dignidad. Si no puede, no es soberano — es una extensión del fundador."*

---

## Inventario de dependencias del fundador (Alfredo)

### D-FUND-1: Decisiones P0 / Magna

**Hoy:** Alfredo es único aprobador.

**Si Alfredo no está:**
- 24h: tolerable, decisiones se acumulan
- 1 semana: arquitectura paraliza, Cowork no puede canonizar
- 1 mes: sistema entra en deriva, embrión sigue corriendo sin guardián
- Permanente: doctrina queda congelada al estado del último día

**🔴 Bus factor 1 absoluto.**

### D-FUND-2: Credenciales y secretos

**Hoy:**
- Bitwarden (verificar) en posesión exclusiva de Alfredo
- Tokens de Railway, Supabase, OpenAI, Anthropic, Telegram, GitHub
- Acceso a cuenta de banco que paga los costos operativos

**Si Alfredo no está:**
- 24h: sistema sigue corriendo
- 1 semana: si una key vence, no hay quien rote
- 1 mes: facturas no se pagan, providers suspenden
- Permanente: sistema muere por starvation de recursos

**🔴 No hay break-glass procedure.**

### D-FUND-3: Conocimiento tácito (memoria humana — Capa M9)

**Hoy:**
- Historia del proyecto, contexto de decisiones, relaciones, prioridades
- Razones detrás de cosas no documentadas
- Capacidad de evaluar si Cowork está alucinando vs lúcido

**Si Alfredo no está:**
- Cowork pierde su validador externo
- Sin Alfredo, Cowork puede confirmar sesgos sin contraste humano
- 8 Sabios pueden ser invocados, pero sin guardián que pondere sus respuestas

**🔴 Sin captura sistemática. Tribal knowledge atrapado.**

### D-FUND-4: Identidad y representación legal

**Hoy:**
- Alfredo es persona física dueña
- No hay entidad legal del Monstruo (verificar)
- Sin sucesión patrimonial documentada

**Si Alfredo no está:**
- Permanente: el proyecto queda en limbo legal, IP queda en sucesión patrimonial

**🔴 Sin estructura legal de continuidad.**

### D-FUND-5: Pago de costos operativos

**Hoy:**
- $30/día canonizado (DSC-MO-010 contexto)
- Tarjeta personal de Alfredo

**Si Alfredo no está:**
- 1 semana: ok
- 1 mes: provider auto-renueva, tarjeta puede rechazar
- 3 meses: cuentas suspendidas, datos potencialmente perdidos

**🔴 Sin fondo dedicado al Monstruo.**

### D-FUND-6: Decisiones de evolución estratégica

**Hoy:**
- Alfredo define dirección de los 15 Objetivos Maestros
- Alfredo decide qué hilos contratar, qué Sabios consultar

**Si Alfredo no está:**
- Sistema mantiene inercia, pero no evoluciona
- Cowork puede ejecutar pero no debe reescribir objetivos por iniciativa propia (G-09 separation of duties)

**🟡 Riesgo de stagnation o de Cowork tomando autoridad que no debe.**

### D-FUND-7: Relación con el embrión

**Hoy:**
- Alfredo es la única identidad que el embrión reconoce como guardián epistémico
- Telegram chat_id de Alfredo = identidad canónica

**Si Alfredo no está:**
- El embrión sigue corriendo pero sin "padre" para reportarle anomalías
- No hay otro humano que pueda detener el embrión via canal canónico

**🔴 Punto único de fallo en el bucle humano-agente.**

---

## Gradientes de ausencia

### G-A1: Ausencia 24h (sueño extendido, viaje corto)
**Tolerancia actual:** alta. Sistema sigue funcionando, decisiones se posponen.

**Riesgo:** mínimo si no hay incidente. Si hay incidente, nadie detiene producción.

**Mitigación:** kill switch operacional sin requerir Alfredo (cruza con D7 G-03).

### G-A2: Ausencia 1 semana (vacaciones planificadas)
**Tolerancia actual:** media. Decisiones P0 se acumulan, T3 sigue ejecutando, Cowork puede no canonizar.

**Riesgo:** drift acumulativo, decisiones tomadas con baja calidad cuando regresa.

**Mitigación:** runbook de "modo vacaciones" con scope reducido enforced.

### G-A3: Ausencia 1 mes (enfermedad, evento personal)
**Tolerancia actual:** baja. Algunos items urgentes no atendidos. Costos pueden subir sin freno si Budget Tracker no funciona.

**Riesgo:** alto. Posible degradación silenciosa de sistemas.

**Mitigación:** delegado interino con scope limitado canonizado.

### G-A4: Ausencia 3-6 meses (enfermedad seria, sabbatical forzado)
**Tolerancia actual:** crítica. Sin canonización Magna, doctrina envejece. Sin rotación de keys, riesgo de breach. Sin pago, riesgo de suspensión.

**Riesgo:** muy alto. El Monstruo puede entrar en estado vegetativo.

**Mitigación:** sucesión temporal con poder limitado pero real, fondo dedicado.

### G-A5: Ausencia permanente (fallecimiento, incapacidad permanente)
**Tolerancia actual:** **inexistente.** El proyecto muere o queda en limbo.

**Riesgo:** total.

**Mitigación:** estructura legal, sucesor designado, fondo de continuidad, doctrina suficiente para que Cowork + Sabios sigan operando bajo el sucesor.

---

## Inventario de mitigaciones existentes

| Item | Estado |
|---|---|
| Documentación pública canonizable | ✅ Existe — DSCs, Objetivos, doctrina abundante |
| Memoria persistente externalizada (Capa M5 Cowork) | ✅ Existe |
| Capa 8 Memento contra Síndrome Dory | ✅ Diseñada doctrinalmente |
| DSC-MO-007 Failover 3 capas | ✅ Diseñada para resiliencia técnica |
| Runbook para ausencia 24h | 🔴 No existe |
| Runbook para ausencia 1 semana | 🔴 No existe |
| Runbook para ausencia 1 mes | 🔴 No existe |
| Sucesor designado | 🔴 No existe |
| Estructura legal de continuidad | 🔴 No existe |
| Fondo dedicado al Monstruo | 🔴 No existe |
| Break-glass procedure para credenciales | 🔴 No existe |
| Identidad alterna para canal Telegram | 🔴 No existe |
| Captura sistemática de tribal knowledge | 🔴 No existe (M-08 GAP) |

**🟢 Conteo:** 4
**🔴 Conteo:** 9

---

## Análisis del proyecto bajo "muerte instantánea del fundador"

Ejercicio adversarial: si Alfredo desapareciera hoy a las 00:00, ¿qué pasa?

**Hora 0:** Embrión sigue corriendo. Cowork sin sesión activa (mientras no hay usuario). Hilos Manus sin instrucciones nuevas.

**+24h:** Telegram no recibe respuesta. Si hay incidente automático, nadie aprueba mitigación. Costos siguen corriendo.

**+72h:** Catastro detecta anomalías sin nadie a quien reportar.

**+1 semana:** Servicios siguen activos en Railway, pero PR pendientes acumulan. Sabios consultas se acumulan.

**+1 mes:** Tarjeta puede rechazar pago si tiene tope. Si Railway/Supabase no cobran, suspenden eventualmente.

**+3 meses:** Cuenta de Anthropic / OpenAI puede ser auto-cancelada por inactividad de pago.

**+6 meses:** Repos pueden quedar en GitHub si la cuenta sigue activa. Pero infraestructura activa = muerta.

**+1 año:** Posible recuperación si alguien encuentra el repo + credenciales. Sin eso, el Monstruo es código fósil.

**Veredicto:** el Monstruo **no sobrevive 6 meses sin Alfredo en su estado actual**. No es soberano todavía bajo la definición dura del Objetivo #12.

---

## GAPs reales identificados

### GAP S-01: Sin runbook por gradiente de ausencia
G-A1 a G-A5 sin protocolo escrito.

### GAP S-02: Sin sucesor designado
Para G-A4 / G-A5 no hay nadie con autoridad delegada.

### GAP S-03: Sin estructura legal de continuidad
IP, cuentas, decisión sobre futuro del proyecto.

### GAP S-04: Sin break-glass procedure para credenciales
Si Alfredo no puede acceder a Bitwarden, sistema queda sin rotación.

### GAP S-05: Sin fondo dedicado al Monstruo
Costos atados a tarjeta personal de Alfredo.

### GAP S-06: Sin captura sistemática de tribal knowledge
Cada conversación Telegram con conocimiento crítico que no se canoniza queda en memoria humana.

### GAP S-07: Sin identidad alterna en canal de aprobación
Telegram chat_id de Alfredo es único punto.

### GAP S-08: Embrión sin "padre alternativo"
Si Alfredo no responde, embrión no tiene a quién reportar anomalías.

### GAP S-09: Cowork sin "validador externo de cordura" cuando Alfredo no está
Sesiones sin guardián humano pueden derivar.

### GAP S-10: Documentación de "estado actual del proyecto" no autoexplicativa
Un sucesor que llegue mañana no puede ramp up rápido — DSCs son densos, sin manual de onboarding.

---

## Plan de mitigación priorizado

### Sprint 7 días — P0 base (lo crítico)

1. **Runbook "Ausencia 72h"** (G-A1+G-A2): qué hace Cowork autónomamente, qué pausa, cuándo se autoriza kill switch sin Alfredo (1 día)
2. **Lista canónica de credenciales activas** (G-FUND-2) — qué keys hay, dónde, quién las debería tener si Alfredo no puede (medio día)
3. **Designar "contacto de emergencia" humano** mínimo (G-A3+) — alguien con acceso a Bitwarden bajo condiciones específicas (decisión humana, no técnica)
4. **Manual de onboarding del sucesor** (G-S10) — un README de 1 página: "si llegaste y Alfredo no está, lee esto" (1 día)
5. **Canonizar `governance_log`** (cruza D7) para que sucesor pueda reconstruir historia (medio día)

### Sprint 30 días — P0 estructurales

6. Runbook completo G-A1 a G-A5
7. Estructura legal mínima (testamento + designación de heredero del proyecto)
8. Fondo dedicado con autofunding (tarjeta separada con saldo de 6 meses)
9. Captura sistemática: Telegram → DSC pipeline para decisiones repetidas (cruza D7 G-11)
10. Pipeline "tribal knowledge extraction" — sesiones periódicas Cowork-Alfredo para canonizar lo no canonizado

### Sprint 90 días — P0 sistémicos

11. Sucesor humano designado con onboarding documentado y revisado
12. Múltiples chat_id Telegram autorizados con quorum (cruza D12 P0-1)
13. Estructura legal completa (LLC/asociación civil/fundación según naturaleza del proyecto)
14. Plan financiero de continuidad 24 meses
15. "Cowork ramp-up doc": cómo un nuevo Cowork entiende el proyecto en N horas

### Sprint 365 días — Soberanía real

16. Doctrina suficientemente clara para que un equipo distinto pueda continuar el proyecto sin Alfredo
17. Infraestructura suficientemente auto-mantenible que sobreviva 6+ meses sin intervención humana
18. Comunidad o fundación que herede el proyecto si fundador no puede continuarlo

---

## Conexión con Objetivos Maestros

| Objetivo | Cómo se cruza con D16 |
|---|---|
| #12 Soberanía | Soberanía dura exige independencia del fundador |
| #14 Guardian de los Objetivos | El guardian no puede ser solo una persona |
| #15 Memoria Soberana | Memoria soberana incluye memoria de cómo continuar sin la persona que la creó |

---

## Pregunta incómoda canonizada

¿Es el Monstruo un proyecto **del** fundador o un proyecto **para el mundo** (Objetivo #13)?

Si es lo segundo, **D16 es bloqueante de la promesa Del Mundo**. Un proyecto que muere con su fundador no puede prometer impacto global sostenido.

Esta tensión queda registrada como input para revisión Magna posterior.

---

## Veredicto del audit

**Estado real de Dimensión 16: ~15-20% (vs no declarado explícitamente — pero crítico para Obj #12, #13, #14, #15)**

Razones del descuento:
- 9 de 13 mitigaciones inexistentes
- Bus factor 1 absoluto
- Sin runbook para ningún gradiente de ausencia
- Sin sucesor humano
- Sin estructura legal
- Sin fondo dedicado

**Esta es la dimensión más débil de las 4 auditadas hoy.** D7 (30-35%) y D12 (30-35%) son malas; D16 (15-20%) es **crítica para soberanía del proyecto**.

**Frase canónica para esta dimensión:**

> *"El Monstruo es hoy una extensión sofisticada de Alfredo, no una entidad soberana. La soberanía se construye precisamente cuando se prepara el proyecto para sobrevivir a su creador. Hasta que eso pase, todo lo demás es preparación."*

---

## Trabajo pendiente inmediato

- Confirmar con Alfredo: ¿hay testamento o disposición legal sobre IP/cuentas?
- Confirmar: ¿alguien más tiene acceso a Bitwarden bajo cualquier condición?
- Confirmar: ¿hay tarjeta separada para gastos del Monstruo o todo va en tarjeta personal?
- Próxima dimensión Plan v1.5: **D11 Doctrinal** (audit interno de los 62+ DSCs y 15 Objetivos) o **D17 Salud del fundador** (cruza directo con D16)

---

## Prompt sugerido para ChatGPT 5.5 Pro (opcional)

> *"Te paso D16 Sucesión del Monstruo. Sistema con T1=fundador único humano. Quiero adversarial sobre: (a) bus factor real considerando agentes autónomos como parte del sistema — ¿puede un embrión + Cowork mantener un proyecto vivo en ausencia humana?; (b) precedentes históricos de proyectos open source que sobrevivieron muerte del BDFL (Python/Guido es viviente, pero ¿qué pasó con Aaron Swartz proyectos? ¿Otros?); (c) qué estructura legal específica recomiendas para un proyecto experimental con IP en desarrollo activo. Sé adversarial, busca lo que no veo."*

---

*Audit firmado por Cowork como Arquitecto, 2026-05-11.*
