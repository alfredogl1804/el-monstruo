# METODOLOGÍA DE RANKING — Para aplicar DESPUÉS de tener las 61 biblias

## FASE 1: Scoring por capacidad (cuantitativo)

### Categorías y pesos

| Categoría | Peso | # Capacidades | Justificación del peso |
|---|---|---|---|
| A. Navegación/Browser Control | 10% | 9 | Base necesaria pero commodity |
| B. Shopping & E-commerce | 15% | 9 | Alta diferenciación, alto valor práctico |
| C. Email & Comunicación | 12% | 8 | Productividad diaria crítica |
| D. Calendario & Scheduling | 8% | 7 | Importante pero secundario |
| E. CRM & Business | 10% | 7 | Alto valor para profesionales |
| F. Social Media | 5% | 5 | Nicho, no todos lo necesitan |
| G. Research & Análisis | 15% | 8 | Core de lo que hacía Comet beta |
| H. Coding & Deployment | 8% | 7 | Solo relevante para carril extremo |
| I. Automatización & Workflows | 12% | 6 | Diferenciador clave vs chat simple |
| J. UX & Accesibilidad | 5% | 11 | Experiencia de usuario |

### Scoring por capacidad individual
- ✅ Confirmado y funcional = 2 puntos
- 🟡 Parcial, limitado o en beta = 1 punto
- ❌ No disponible = 0 puntos
- ❓ Sin información = 0 puntos (penaliza falta de transparencia)

### Score ponderado
Score_herramienta = Σ (score_capacidad × peso_categoría) / max_posible × 100

## FASE 2: Factores multiplicadores (cualitativos)

| Factor | Multiplicador | Criterio |
|---|---|---|
| Benchmark SOTA (top 3 en al menos 1 benchmark mayor) | ×1.15 | GAIA, OSWorld, WebVoyager, WebArena, SWE-bench |
| Disponibilidad real (público, no waitlist) | ×1.10 | Poder usarlo HOY |
| Precio accesible (≤$30/mo o free) | ×1.05 | Accesibilidad económica |
| Multiplataforma (3+ plataformas) | ×1.05 | Flexibilidad |
| Riesgo de seguridad alto | ×0.90 | Penalización por riesgo |
| Riesgo de discontinuación | ×0.85 | Penalización por inestabilidad |

### Score final
Score_final = Score_ponderado × Π(multiplicadores_aplicables)

## FASE 3: Ranking por caso de uso

No solo un ranking general, sino rankings específicos:

1. **"Reemplazar Comet beta"**: Peso extra en shopping, email, calendar, research, background tasks
2. **"Máxima productividad profesional"**: Peso extra en CRM, email, calendar, workflows
3. **"Máxima capacidad técnica"**: Peso extra en coding, deployment, multi-agent, benchmarks
4. **"Mejor relación capacidad/precio"**: Score dividido por costo mensual
5. **"Menor riesgo"**: Solo herramientas con riesgo ≤2 y disponibilidad pública

## FASE 4: Cross-validation

Alimentar las 61 biblias + esta metodología a 2-3 IAs diferentes:
- GPT-5.2 (o modelo más capaz disponible)
- Claude (Opus 4.5/4.6)
- Gemini 3 Deep Research

Cada una aplica la metodología independientemente. Donde los 3 rankings coinciden = alta confianza. Donde difieren = investigar más.

## OUTPUT ESPERADO

1. Ranking general (top 20 de cada carril)
2. Rankings por caso de uso (5 rankings × top 10)
3. Matriz de coincidencia entre las 3 IAs
4. Recomendación final con justificación
