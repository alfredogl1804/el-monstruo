---
name: media-crisis-control
description: Sistema avanzado de alerta temprana, diagnóstico y recomendación táctica para control de crisis en medios, especializado en políticos y figuras públicas en LATAM. Utiliza el framework LATAM-POLICRIS v1.
---

# Media Crisis Control Skill

## Propósito
Este skill no es un simple resumidor de noticias, sino un **sistema de alerta temprana, diagnóstico y recomendación táctica**. Responde a las 5 preguntas clave en una crisis:
1. ¿Qué está pasando?
2. ¿Qué tan grave es?
3. ¿Quién está empujando la crisis?
4. ¿Qué narrativa está ganando?
5. ¿Qué hacemos en las próximas 2h / 24h / 72h / 7 días?

## Arquitectura y Framework

Utiliza el framework **LATAM-POLICRIS v1**, diseñado específicamente para la política latinoamericana, evaluando:
- **Daño:** Reputacional, legal, electoral, institucional.
- **Acusación:** Criminal, corrupción, moral, política pública.
- **Evidencia:** Rumor, documento, proceso abierto.
- **Propagación:** Orgánica, coordinada, mediática.
- **Contagio:** Local, regional, nacional.

## Estructura del Skill

- `app/`: Orquestador principal y gestión de estado.
- `ingestion/`: Recolección de datos (Search, News, Social).
- `analysis/`: Análisis de sentimiento, narrativas, vectores de ataque, riesgos legales.
- `scoring/`: Evaluación de severidad (Spread, Legitimacy, Actor Power, Volatility).
- `strategy/`: Playbooks de respuesta según tipo de crisis.
- `reporting/`: Generación de reportes ejecutivos.
- `monitoring/`: Reglas de alerta y seguimiento continuo.

## Ejecución Principal

El orquestador maestro (`app/orchestrator.py`) ejecuta el ciclo completo: ingesta, enriquecimiento, análisis, scoring, estrategia y reporte.

```bash
python3.11 /home/ubuntu/skills/media-crisis-control/app/orchestrator.py --target "Nombre del Político"
```

## Dependencias
- APIs: OpenAI (GPT-5.4/5.4-mini), Anthropic (Claude), Perplexity Sonar.
- Librerías: `aiohttp`, `beautifulsoup4`, `pandas`.
