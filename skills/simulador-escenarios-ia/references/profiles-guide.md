# Guía de Perfiles del Simulador Universal

## Electoral

**Caso de uso:** Selección de candidatos, predicción electoral, wargaming de campaña.

**Agentes típicos:**
- Votantes (urbano joven, urbano adulto, rural, senior) con demografía calibrada al censo
- Candidatos con personalidad (carisma, competencia, empatía) y posiciones (economía, seguridad, etc.)
- Medios con sesgo y alcance
- Generador de eventos (crisis, escándalos)

**Rondas predefinidas:** speech → attack → debate → crisis → vote

**Variables Monte Carlo:** turnout_rate (beta), undecided_swing (normal), last_minute_effect (normal), polling_error (normal)

**Métricas clave:** win_probability, vote_share, margin_of_victory, swing_voter_capture, enthusiasm_index

## Financial

**Caso de uso:** Evaluación de inversiones, stress-testing de portafolios, análisis de riesgo.

**Agentes típicos:**
- Inversores (conservador, moderado, agresivo)
- Reguladores
- Analistas de mercado

**Variables Monte Carlo:** market_return (normal), inflation_rate (normal), interest_rate (normal), volatility (lognormal), gdp_growth (normal)

**Métricas clave:** expected_return, VaR_95, max_drawdown, sharpe_ratio

## Crisis

**Caso de uso:** Preparación ante crisis, evaluación de respuesta, simulacros.

**Agentes típicos:**
- Stakeholders internos (CEO, comité de crisis, comunicaciones)
- Medios de comunicación
- Público general
- Reguladores

**Rondas:** crisis_trigger → initial_response → media_reaction → escalation → resolution

**Variables Monte Carlo:** severity (uniform), spread_speed (exponential), reputation_damage (beta), recovery_time (lognormal)

## Legal

**Caso de uso:** Predicción de litigios, evaluación de estrategias legales.

**Agentes:** Juez, abogados (demandante/demandado), testigos, jurado.

**Variables MC:** judge_favorability (beta), evidence_strength (normal), settlement_probability (beta)

## Supply Chain

**Caso de uso:** Optimización de cadena de suministro, análisis de disrupciones.

**Agentes:** Proveedores, transportistas, almacenes, clientes.

**Variables MC:** demand_forecast (normal), lead_time (lognormal), disruption_probability (bernoulli), cost_variation (normal)

## Technology

**Caso de uso:** Lanzamiento de productos, adopción tecnológica, competencia.

**Agentes:** Early adopters, mainstream users, laggards, competidores.

**Variables MC:** adoption_rate (logistic), churn_rate (beta), market_share (dirichlet), development_cost (lognormal)

## Real Estate

**Caso de uso:** Viabilidad de proyectos inmobiliarios, análisis de mercado.

**Agentes:** Compradores, desarrolladores, bancos, reguladores.

**Variables MC:** price_per_sqm (normal), absorption_rate (beta), cap_rate (normal), construction_cost (lognormal)

## Marketing

**Caso de uso:** Evaluación de campañas, posicionamiento de marca.

**Agentes:** Consumidores (segmentos), competidores, influencers.

**Variables MC:** conversion_rate (beta), awareness_lift (normal), ROI (normal), market_share_change (normal)

## Strategic

**Caso de uso:** Planificación estratégica, análisis competitivo, M&A.

**Agentes:** Directivos, competidores, reguladores, mercado.

**Variables MC:** market_growth (normal), competitive_response (categorical), synergy_realization (beta)

## Custom

Perfil vacío para definir agentes, rondas y variables completamente personalizadas. Usar cuando ningún perfil predefinido aplica.
