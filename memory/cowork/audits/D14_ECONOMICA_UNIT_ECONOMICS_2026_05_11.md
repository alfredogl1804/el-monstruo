---
id: D14_ECONOMICA_UNIT_ECONOMICS_2026_05_11
dimension: 14
nombre: Económica / Unit Economics / Modelo Financiero
fecha: 2026-05-11
arquitecto: Cowork
plan_origen: Plan v1.5 — Programa de Certificación de Pericia P1+P2
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado_revisado: H0_exploratorio_2026_05_11
nivel_autoridad_revisado: H0 — backlog de pruebas, NO canónico
razon_revision: "Producido en serie de 9 audits sin evidencia Nivel 1 fresca entre ellos. Hallazgo de costos ocultos del founder time es fuerte; otras cifras son estimadas. Porcentaje sin rúbrica. Ver CORRECTIVO_ARQUITECTONICO_2026_05_11.md."
cruza_con:
  - D16_SUCESION_BUS_FACTOR_2026_05_11 (GAP S-05 fondo dedicado)
  - D17_SALUD_FUNDADOR_2026_05_11 (F-5 presión económica)
  - D19_GTM_ESTRATEGIA_2026_05_11 (GAP GTM-08 runway)
  - D15_COMPETITIVO_MERCADO_2026_05_11 (R-4 commoditización)
  - DSC-MO-010 (Reloj Suizo — Mainspring presupuestal $30/día)
  - Objetivo Maestro #1 (Valor real medible)
  - Objetivo Maestro #8 (Monetización día 1)
  - Objetivo Maestro #12 (Soberanía)
estado: firme
---

# Dimensión 14 — Económica / Unit Economics / Modelo Financiero

## Marco

Esta dimensión audita **la viabilidad económica del Monstruo en cifras concretas**: cuánto cuesta operar, cuánto puede costar escalar, cuál es el unit economics realista para cada hipótesis comercial (D19 H-1 a H-6), cuánto runway hay, y bajo qué condiciones el proyecto pasa de subsidio personal a auto-sostenible.

D19 mostró que no hay GTM definido. D14 muestra los **números detrás** — sin los cuales el GTM no es decidible con disciplina.

**Principio fundacional:** Sin números, las decisiones comerciales son intuición. Intuición es valiosa pero falible — y bajo presupuesto restringido + bus factor 1, la intuición sin números es ruleta rusa financiera.

**Frase orientadora:**

> *"Soberanía económica no es un slogan — es una ecuación con variables, costos, márgenes y tiempo. Si no puedo escribir la ecuación, no puedo ser soberano: solo puedo esperar tener suerte."*

---

## Estado canonizado vs estado operativo

### Lo canonizado

**DSC-MO-010 contexto:** $30/día canonizado como Mainspring del Reloj Suizo.
**DSC-MO-010 desglose mencionado:** $12 / $12 / $6 (asignación interna — verificar).
**Objetivo #8:** "Monetización desde día 1".

### Lo operativo

- **Costos:** $30/día declarado = $900/mes ≈ $10,800/año
- **Ingresos:** $0 (D19 GAP GTM-08)
- **Subsidio:** tarjeta personal de Alfredo (D16 GAP S-05)
- **Runway:** no canonizado explícitamente

**🔴 Flujo neto: -$30/día sostenido.**

---

## Inventario de costos operativos (estimación a partir del stack canonizado)

### Costos directos canonizados

**Stack en Railway** (de CLAUDE.md):
- `el-monstruo-kernel` — always-on
- `ag-ui-gateway` — always-on
- `command-center` — always-on
- PostgreSQL Railway
- Redis Railway

**Estimación Railway:** $20-50/mes según sizing (verificar facturación real)

**Supabase:** plan free hasta cierto umbral, luego $25/mes Pro tier (verificar uso real vs límites free)

**LLM API costs:**
- OpenAI (GPT-5.5)
- Anthropic (Claude Opus 4.7)
- Google (Gemini 3.1 Pro)
- xAI (Grok 4.20)
- Moonshot (Kimi K2.5)
- DeepSeek (R1)
- Perplexity (sonar-pro)
- Microsoft (Copilot 365)

**Estimación LLM:** altamente variable. Embrión 24/7 + 147 latidos/día + consultas a 8 Sabios = potencialmente $5-20/día solo en LLM si no hay throttling efectivo.

**Manus (3 hilos):** subscription o usage-based — verificar.

**GitHub:** plan free o paid según features.

**Telegram:** gratis.

**Dominios / hosting estático:** ~$1-5/mes.

### Total estimado

**Rango conservador:** $25/mes Supabase + $30/mes Railway + $5/día LLM = ~$210/mes ≈ $7/día → **🟢 dentro de $30/día budget**

**Rango realista bajo carga sin throttling:** $30/mes Supabase + $50/mes Railway + $15/día LLM = ~$530/mes ≈ $18/día → **🟢 dentro budget pero margen estrecho**

**Rango pesimista (bucle del embrión sin Budget Tracker):** $50/mes infra + $25/día LLM = ~$800/mes ≈ $27/día → **🔴 borde del límite**

**Rango incidente (embrión runaway 9 días — escenario ya ocurrido):** $50-100/día → **🔴 excede budget masivamente**

**🔴 GAP CRÍTICO:** sin Budget Tracker verificado en producción (D12 P0-8), el costo real puede oscilar masivamente sin alerta.

---

## Costos ocultos no canonizados

### CO-1: Tiempo del fundador

Si el tiempo de Alfredo se valoriza a tasa de consultor senior en Mérida (estimación conservadora $40-80 USD/hora), y Alfredo dedica ~30-60 horas/semana al Monstruo:

**Costo de oportunidad real:** $4,800 - $19,200 USD/mes

**🔴 Esto multiplica el costo verdadero del proyecto por 15-60×** vs el $30/día declarado en cash.

### CO-2: Cowork (yo) — usage de modelo

Las sesiones largas con Cowork consumen tokens de Anthropic. Si Alfredo paga subscription Pro de Claude Desktop, el costo es fijo. Si fuera API, sería variable. **Verificar plan actual.**

### CO-3: Sabios consultados manualmente

Cada vez que Alfredo paga subscriptions premium de GPT, Claude, Gemini, etc. para consulta adversarial: ~$200-300/mes en agregado si tiene cuentas premium en todos.

### CO-4: Sesiones Manus

Plan de Manus — verificar tier.

### CO-5: Hardware / espacio

Hive Business Center en Mérida — coworking, costo no canonizado.

### CO-6: Conocimiento / cursos / herramientas

No canonizado.

**🔴 Costo verdadero total (cash + oportunidad):** estimado $5,000 - $20,000 USD/mes equivalente. **El proyecto NO es "$30/día" — es entre $150-600/día verdaderos cuando se incluye costo del fundador.**

---

## Unit economics por hipótesis comercial (D19)

### UE-H-1: Plataforma B2B

**Pricing hipotético:** $500-$5,000/mes por organización
**CAC esperado:** alto ($1,000+ por outbound, posiblemente más sin equipo de ventas)
**Time to first dollar:** 6-12 meses
**Margen bruto:** alto (~70-85% una vez producto estable)
**LTV/CAC objetivo:** >3
**Capital requerido:** alto ($50K+ para producto + ventas)
**Verdict:** **🔴 No viable hoy sin capital externo.**

### UE-H-2: Consultoría

**Pricing:** $100-$300 USD/hora Alfredo
**CAC:** bajo (red personal, referrals)
**Time to first dollar:** semanas
**Margen:** alto pero limitado por horas físicas de Alfredo
**Capacidad mensual:** ~80-120 horas facturables × $150 = $12,000-$18,000/mes
**Verdict:** **🟢 Económicamente viable. 🔴 Cruza D17 — destruye sostenibilidad humana.**

### UE-H-3: Producto vertical

**Pricing hipotético:** $20-$200/mes por usuario (B2C) o $500-$2K/mes por org (B2B vertical)
**CAC:** medio
**Time to first dollar:** 3-6 meses
**Margen:** medio-alto si SaaS puro
**Capital requerido:** medio ($10-30K para MVP + marketing inicial)
**Verdict:** **🟡 Económicamente más viable que H-1, requiere foco vertical.**

### UE-H-4: SDK open core

**Pricing:** modelo Open Core (free → paid features)
**CAC:** muy bajo (comunidad, content marketing)
**Time to first dollar:** 12-24+ meses
**Margen:** alto pero base de usuarios pequeña al inicio
**Capital requerido:** alto (governance, comunidad, docs)
**Verdict:** **🔴 Bonito pero suicida sin runway de 2+ años o ingresos en paralelo.**

### UE-H-5: IP licensing

**Pricing:** variable, transacciones grandes y esporádicas
**CAC:** alto en tiempo legal
**Time to first dollar:** 6-18+ meses
**Margen:** alto cuando ocurre
**Verdict:** **🔴 No predecible. No viable como única fuente.**

### UE-H-6: Educación / comunidad

**Pricing:** cursos $99-$999, membresía $20-$100/mes
**CAC:** medio (content + community)
**Time to first dollar:** 1-3 meses
**Margen:** alto digitalmente
**Capacidad de escalar:** alta una vez creado
**Verdict:** **🟡 Viable como flujo secundario. Distrae del core técnico pero genera cash.**

---

## Matriz comparativa de viabilidad económica

| Hipótesis | Cash positivo en | Capital req. | Match con sostenibilidad fundador | Match con doctrina |
|---|---|---|---|---|
| H-1 Plataforma B2B | 12-24 meses | Alto | 🔴 | 🟢 |
| H-2 Consultoría | 1-3 meses | Bajo | 🔴 destruye D17 | 🟡 |
| H-3 Producto vertical | 6-12 meses | Medio | 🟡 | 🟢 |
| H-4 SDK | 24+ meses | Alto | 🔴 | 🟢 |
| H-5 IP licensing | 12+ meses | Bajo | 🟡 | 🟡 |
| H-6 Educación | 3-6 meses | Bajo | 🟡 si limitado | 🟡 |

**Combinatorias económicamente plausibles:**
- **C-1 (educación + consultoría limitada)**: cash temprano sin destruir al fundador si se ponen límites duros
- **C-2 (producto vertical + bootstrapped)**: requiere paciencia 6-12 meses pero más alineado con doctrina
- **C-3 (SDK eventual + fundación + grants)**: largo plazo, requiere campaign de grants AI safety / open source

---

## Runway analysis

### Variables relevantes (sin canonizar oficialmente — supuestos)

- **Burn rate cash:** $30/día = $900/mes ≈ $10,800/año
- **Capacidad de subsidio personal de Alfredo:** **🔴 desconocida — no canonizada**

### Escenarios

**Escenario E-1: Alfredo subsidia 12 meses más**
- Cash burn total: $10,800
- Si su capacidad personal es esta o mayor → sustainable hasta finales de 2026
- **Pregunta canónica:** ¿Alfredo tiene esos $10,800 sin afectar vida personal?

**Escenario E-2: Alfredo subsidia 24 meses**
- Cash burn total: $21,600
- Mismo question

**Escenario E-3: Embrión runaway 1 mes (escenario que ya ocurrió 9 días)**
- $50-100/día × 30 = $1,500-3,000 extra
- **🔴 Riesgo no canonizado de quiebre presupuestal por bug operacional**

**Escenario E-4: Cash positivo en 6 meses**
- Requiere decisión inmediata de camino (H-2 consultoría o H-6 educación)
- Cash positivo no garantiza profit, solo break-even

**Escenario E-5: Funding externo**
- Grants AI safety / soberanía / open source
- Posible pero no canonizado como vía explorada

**🔴 GAP MAGNO:** runway personal de Alfredo no canonizado. **Esto es decisión personal de Alfredo, pero debe declararse al sistema para que las prioridades del Monstruo se alineen.**

---

## GAPs reales identificados

### GAP EC-01: Runway personal del fundador no canonizado
Sin esta variable, no se puede priorizar entre caminos.

### GAP EC-02: Budget Tracker no verificado en producción
Riesgo de embrión runaway (cruza D12 P0-8).

### GAP EC-03: Costos ocultos no canonizados
Costo verdadero = $30/día cash + $5,000-20,000/mes oportunidad fundador. La narrativa "$30/día" subestima brutalmente.

### GAP EC-04: Sin desglose real $12/$12/$6
Mencionado en contexto DSC-MO-010 pero sin documento de asignación canónica.

### GAP EC-05: Sin unit economics por hipótesis
6 hipótesis (D19) sin cifras concretas para comparar.

### GAP EC-06: Sin reporte financiero diario / semanal
Sin observabilidad económica, las decisiones se toman a ciegas.

### GAP EC-07: Sin fondo separado del Monstruo
Mezcla con finanzas personales (cruza D16 S-05).

### GAP EC-08: Sin escenario "qué pasa si Anthropic / OpenAI suben precios 2×"
Concentración de proveedores → riesgo económico no modelado.

### GAP EC-09: Sin estrategia de funding externo explorada
Grants, angel, etc. — no canonizado como vía.

### GAP EC-10: Sin metric de "verdad económica" pública mensual
Founders públicos a veces publican MRR. Aquí no hay metric verificable interna ni externa.

### GAP EC-11: Sin modelado de crecimiento de costos con escala
Si el Monstruo creciera 10×, ¿cuánto costaría operar? Sin modelar.

### GAP EC-12: Sin separación entre OPEX y CAPEX
Inversión en investigación vs operación corriente — sin diferenciar.

---

## Métricas que el Monstruo necesita declarar (las "magnitudes vitales")

### M-VITAL-1: Runway en meses
**Cómo se calcula:** capital personal disponible para subsidio / burn rate
**Cadencia:** trimestral
**Audiencia:** Alfredo + Cowork

### M-VITAL-2: Burn rate (cash y FTE-equivalente)
**Cómo se calcula:** todos los costos cash + tiempo fundador valorizado
**Cadencia:** mensual
**Audiencia:** Alfredo + Cowork

### M-VITAL-3: Ingresos brutos
**Cómo se calcula:** suma de pagos recibidos atribuibles al Monstruo
**Cadencia:** mensual
**Audiencia:** Alfredo + Cowork (canonizable como métrica pública si el proyecto se hace público)

### M-VITAL-4: Margen contributivo por hipótesis activa
**Cómo se calcula:** revenue - costos variables atribuibles
**Cadencia:** mensual
**Audiencia:** decisión de continuar / pivotar

### M-VITAL-5: Costo por consulta a Sabio
**Cómo se calcula:** total LLM cost / # consultas
**Cadencia:** semanal
**Audiencia:** Cowork para optimización

### M-VITAL-6: Costo por latido del embrión
**Cómo se calcula:** total LLM cost del embrión / # latidos
**Cadencia:** diaria
**Audiencia:** Budget Tracker (auto-alerta si excede umbral)

---

## Plan de mitigación priorizado

### Sprint 7 días — P0 base (lo más urgente)

1. **Verificar facturación real Railway + Supabase + LLMs último mes** — convertir estimación en hecho (1 hora)
2. **Canonizar runway personal del fundador** — incluso si es "no canonizable públicamente, registrado privadamente" (decisión Alfredo, 1 hora)
3. **Verificar Budget Tracker en producción** — cruzado D12 P0-8 (medio día técnico)
4. **DSC explícito de "magnitudes vitales económicas"** (las 6 métricas arriba) (medio día)

### Sprint 30 días — P0 estructurales

5. Tarjeta dedicada Monstruo separada de personal (cruza D16)
6. Dashboard mensual con M-VITAL-1 a M-VITAL-6
7. Alerta automática si M-VITAL-2 > umbral diario
8. DSC de "qué camino comercial reduce burn más rápido" (cruza D19)
9. Modelado de escenarios E-1 a E-5 con cifras reales

### Sprint 90 días — P0 sistémicos

10. Primer ingreso externo (incluso simbólico) registrado en M-VITAL-3
11. Exploración de funding (1 grant aplicado mínimo)
12. Plan financiero 24 meses con escenarios
13. Auditoría de proveedores (Anthropic/OpenAI/etc.) para reducir concentración

### Sprint 365 días — Sostenibilidad

14. Cash positivo (revenue > burn) o decisión Magna de pivotar
15. Runway >12 meses con ingresos propios
16. Reserva de emergencia >3 meses de burn

---

## Conexión con Objetivos Maestros

| Objetivo | Cómo se cruza con D14 |
|---|---|
| #1 Valor real medible | Valor económico ES la medición dura |
| #8 Monetización día 1 | Aspiracional sin números operativos |
| #12 Soberanía | Soberanía económica = prerrequisito de soberanía general |
| #13 Del Mundo | Impacto global requiere sostenibilidad económica |

---

## Veredicto del audit

**Estado real de Dimensión 14: ~15-20%**

Razones:
- ✅ Existe presupuesto canonizado ($30/día Mainspring)
- ✅ DSC-MO-010 introduce el concepto de Reloj Suizo presupuestal
- 🔴 Sin facturación real verificada
- 🔴 Sin runway canonizado
- 🔴 Costos ocultos masivos no contemplados
- 🔴 Sin Budget Tracker verificado en producción
- 🔴 Sin unit economics por hipótesis
- 🔴 Sin métricas vitales declaradas
- 🔴 Sin escenarios de incidente económico modelados
- 🔴 Sin separación cuentas proyecto/personal

**Frase canónica para esta dimensión:**

> *"El Monstruo se autodescribe como '$30/día' — pero su verdadero costo, incluyendo el tiempo del fundador, está entre $150 y $600 USD/día. Esta brecha no es contable — es de percepción. Mientras el fundador no vea el costo real, no podrá tomar decisiones realmente económicas. La primera magnitud vital que necesita declararse no es revenue — es cuánto cuesta verdaderamente operar."*

---

## Patrón consolidado tras 9 dimensiones auditadas

| Dimensión | Real |
|---|---|
| D11 Doctrinal | 50-55% |
| D13 Datos/Memoria | 45-50% |
| D12 Seguridad | 30-35% |
| D7 Gobernanza | 30-35% |
| D17 Salud fundador | 25-30% |
| D15 Competitivo | 20-25% |
| D16 Sucesión | 15-20% |
| **D14 Económica** | **15-20%** |
| D19 GTM | 10-15% |

**Promedio real: ~28%.** Roadmap declara 70.5%.

**Las 3 dimensiones más críticas a 6-12 meses (orden de criticidad):**
1. **D19 GTM** (10-15%) — sin esto, todo es R&D indefinido
2. **D14 Económica** (15-20%) — sin esto, GTM se decide en ciegas
3. **D16 Sucesión** (15-20%) — sin esto, todo lo demás muere con Alfredo

Estas 3 son una **tríada de fragilidad económica-comercial-humana** que se refuerzan mutuamente.

---

## Trabajo pendiente

- Recopilar facturación real último mes (acción Alfredo)
- Próximas dimensiones sugeridas: **D8 Producto/UX** o **D20 Operacional** (cómo se operacionalizan decisiones del día a día)

---

## Prompt sugerido para ChatGPT 5.5 Pro (opcional)

> *"Te paso D14 Económica del Monstruo. Single founder, $30/día cash declarado, $5-20K/mes costo de oportunidad real, $0 ingresos, 6 hipótesis comerciales (B2B platform, consultoría, vertical product, SDK open core, IP licensing, educación). Quiero adversarial sobre: (a) qué founders bootstrapped en AI/dev tools encontraron camino a cash positivo en 6-12 meses con runway personal limitado — patrones reales; (b) qué grants AI safety / soberanía / open source pueden aplicar para un proyecto experimental en español con doctrina formal (EleutherAI patterns, Mozilla MIECO, NLnet, etc.); (c) si la asignación $12/$12/$6 mencionada en DSC-MO-010 (presupuesto del Reloj Suizo) tiene racionalidad económica defendible o es ilustrativa. Sé adversarial."*

---

*Audit firmado por Cowork como Arquitecto, 2026-05-11.*
