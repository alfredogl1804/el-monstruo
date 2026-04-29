---
name: simulador-escenarios-ia
description: Simulador Universal de Escenarios con motor externo en Railway. Diseña, configura y ejecuta simulaciones de alta fidelidad en cualquier dominio (electoral, financiero, crisis, legal, supply chain, tecnología, marketing, inmobiliario, estratégico, personal). Combina Agent-Based Modeling (agentes LLM) con Monte Carlo estocástico. Usar cuando el usuario pida simular escenarios, evaluar candidatos, analizar riesgos, predecir resultados, hacer wargaming, stress-testing, o cualquier análisis tipo "¿Qué pasaría si...?".
---

# Simulador Universal de Escenarios

## Arquitectura

Motor Externo (FastAPI) desplegado en Railway + Supabase para persistencia.

- **API Base URL:** `https://simulador-api-production.up.railway.app`
- **Repo:** `alfredogl1804/simulador-universal`
- **Supabase:** Tablas `simulations`, `simulation_rounds`, `simulation_results`

Dos engines combinables:
1. **ABM (Agent-Based Modeling):** Agentes LLM que actúan como personas reales (votantes, inversores, stakeholders). Cada agente tiene demografía, personalidad y posiciones. Interactúan en rondas (discurso, ataque, debate, crisis, votación).
2. **Monte Carlo:** Simulación estocástica con variables probabilísticas (1,000+ iteraciones). Calcula distribuciones de resultados, percentiles, sensibilidad.

## Flujo de Uso

### Paso 1: Interpretar el escenario del usuario

Convertir el prompt del usuario en configuración estructurada. Identificar:
- **Dominio:** electoral, financial, crisis, legal, supply_chain, technology, political, personal, real_estate, marketing, strategic, custom
- **Actores:** Quiénes participan (candidatos, empresas, stakeholders)
- **Variables:** Qué factores influyen (participación, mercado, opinión pública)
- **Pregunta central:** Qué quiere saber el usuario

### Paso 2: Verificar estado del motor

```python
import requests
resp = requests.get("https://simulador-api-production.up.railway.app/api/v1/health")
```

Si el motor no responde, ejecutar la simulación localmente con los engines (ver Paso 2b).

### Paso 3: Configurar y lanzar simulación

Construir el JSON de request según el dominio. Ejemplo electoral:

```python
import requests, json

payload = {
    "name": "Simulación Electoral Alcaldía 2026",
    "profile": "electoral",
    "user_prompt": "Evaluar qué candidato tiene mejor probabilidad",
    "abm": {
        "max_agents": 30,
        "agents": [
            {
                "name": "Candidato_A",
                "role": "candidate",
                "count": 1,
                "demographics": {"age": 45, "profession": "economista"},
                "personality": {"charisma": 5, "competence": 9, "empathy": 6},
                "positions": {"economia": 9, "seguridad": 6, "educacion": 7}
            }
        ],
        "rounds": [
            {"type": "speech", "description": "Discurso de apertura"},
            {"type": "attack", "description": "Red Team"},
            {"type": "debate", "description": "Debate público"},
            {"type": "crisis", "description": "Crisis sorpresa"},
            {"type": "vote", "description": "Votación final"}
        ]
    },
    "monte_carlo": {
        "iterations": 1000,
        "variables": [
            {"name": "turnout_rate", "distribution": "beta", "params": {"a": 8, "b": 3}},
            {"name": "undecided_swing", "distribution": "normal", "params": {"mean": 0, "std": 0.05}}
        ]
    },
    "seed": 42
}

resp = requests.post("https://simulador-api-production.up.railway.app/api/v1/simulations", json=payload)
sim_id = resp.json()["simulation_id"]
```

### Paso 4: Monitorear y obtener resultados

```python
import time
while True:
    status = requests.get(f"https://simulador-api-production.up.railway.app/api/v1/simulations/{sim_id}/status").json()
    if status["status"] != "running":
        break
    time.sleep(10)
results = requests.get(f"https://simulador-api-production.up.railway.app/api/v1/simulations/{sim_id}/results").json()
```

### Paso 5: Sintetizar y presentar

Generar reporte ejecutivo con: recomendación principal, probabilidades con intervalos de confianza, variables más sensibles, riesgos identificados, recomendaciones tácticas.

### Paso 2b: Ejecución Local (Fallback)

Si Railway no responde, ejecutar directamente:

```python
import sys
sys.path.insert(0, "/home/ubuntu/simulador-universal")
from engines.montecarlo import MonteCarloEngine, Variable
from engines.abm import ABMEngine, AgentPersona

mc = MonteCarloEngine(seed=42)
mc.add_variable(Variable(name="turnout", distribution="beta", params={"a": 8, "b": 3}))
mc.set_result_function(lambda v: v["turnout"])
result = mc.run(iterations=1000)
```

## Perfiles Disponibles

Para detalles de cada perfil, leer `references/profiles-guide.md`.

| Perfil | Dominio | Agentes típicos |
|--------|---------|------------------|
| electoral | Campañas, candidatos | Votantes, candidatos, medios |
| financial | Inversiones, mercados | Inversores, reguladores |
| crisis | Gestión de crisis | Stakeholders, medios, público |
| legal | Litigios, regulación | Jueces, abogados, testigos |
| supply_chain | Cadena de suministro | Proveedores, logística |
| technology | Adopción tech | Usuarios, competidores |
| real_estate | Inmobiliario | Compradores, desarrolladores |
| marketing | Campañas, posicionamiento | Consumidores, competidores |
| strategic | Estrategia corporativa | Directivos, competidores |
| custom | Cualquier dominio | Definidos por usuario |

## Endpoints de la API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/v1/health | Estado del servicio |
| GET | /api/v1/profiles | Lista perfiles disponibles |
| POST | /api/v1/simulations | Crear y lanzar simulación |
| GET | /api/v1/simulations/{id}/status | Estado de simulación |
| GET | /api/v1/simulations/{id}/results | Resultados completos |
| GET | /api/v1/simulations | Listar simulaciones recientes |

## Integración con Ecosistema

- **consulta-sabios:** Validar hallazgos con el Consejo de Sabios
- **api-context-injector:** Credenciales LLM inyectadas automáticamente al motor
- **Perplexity (SONAR_API_KEY):** Enriquecer escenarios con datos reales antes de simular
- **El Monstruo:** El motor es una capa activable vía API
