# Recipe: Evaluación de Skills del Marketplace

## Cuándo Usar Esta Recipe

Cuando el benchmark_before_build.py recomienda `install` o `fork_and_harden`,
o cuando el usuario pide evaluar skills externas del marketplace.

## Fuentes de Skills Externas

| Fuente | URL | Volumen | Calidad |
|--------|-----|---------|---------|
| SkillsMP | skillsmp.com | 784,822+ skills | Variable — requiere evaluación |
| awesome-agent-skills | github.com/heilcheng/awesome-agent-skills | 3.8K stars, curado | Alta — verificado por comunidad |
| MCP Market | Rankings diarios | Variable | Media-alta |
| skills.sh | CLI + leaderboard | Variable | Media |
| GitHub directo | github.com/topics/manus-skills | Variable | Requiere evaluación |

## Metodología TRUST+FIT

Antes de instalar cualquier skill externa, evaluar con la metodología TRUST+FIT
definida en `/home/ubuntu/skills/api-context-injector/routing/trust_fit_evaluator.yaml`.

### Hard Gates (cualquier fallo = REJECT)

| Gate | Criterio | Verificación |
|------|----------|-------------|
| HG1 | No malware/backdoors | Escaneo de código |
| HG2 | No credenciales hardcodeadas | grep + AST |
| HG3 | No acceso no autorizado | Revisión de permisos |
| HG4 | Licencia compatible | MIT/Apache/BSD |

### TRUST Score (0-50)

| Dimensión | Peso | Qué Medir |
|-----------|------|-----------|
| T — Track Record | 10 | Stars, forks, contributors, issues resueltos |
| R — Recency | 10 | Último commit < 90 días |
| U — Usability | 10 | Docs claros, SKILL.md presente, ejemplos |
| S — Security | 10 | Sin vulnerabilidades, dependencias actualizadas |
| T — Testing | 10 | Tests presentes, CI/CD, coverage |

### FIT Score (0-50)

| Dimensión | Peso | Qué Medir |
|-----------|------|-----------|
| F — Functionality | 15 | Cubre >80% de la necesidad |
| I — Integration | 15 | Compatible con nuestro ecosistema (env vars, MCPs) |
| T — Total Cost | 20 | Costo de adopción vs construir |

### Decisiones por Score

| Score Total | Acción |
|-------------|--------|
| 85-100 | INSTALL directamente |
| 70-84 | FORK y endurecer |
| 50-69 | COMPOSE (tomar partes útiles) |
| 30-49 | BUILD (inspirarse pero construir propio) |
| 0-29 | REJECT (no vale la pena) |

## Flujo de Evaluación

```
1. Identificar candidatos (skill_scout.py --search)
2. Evaluar top 3 (skill_scout.py --evaluate-url)
3. Aplicar Hard Gates
4. Calcular TRUST+FIT score
5. Decidir: install / fork / compose / build / reject
6. Si install: verificar compatibilidad de env vars
7. Si fork: clonar, endurecer, adaptar
8. Registrar decisión en creation_history.jsonl
```

## Señales de Alerta

- Skill con >1000 stars pero sin actualización en 6 meses → posible abandonware
- Skill que requiere API keys que no tenemos → costo oculto
- Skill sin SKILL.md → no compatible con ecosistema Manus
- Skill con dependencias pesadas (Docker, GPU) → posible incompatibilidad sandbox
- Skill con licencia GPL → restricciones de uso comercial

## Integración con skill-factory

El script `benchmark_before_build.py` ejecuta automáticamente esta evaluación
antes de iniciar el pipeline de construcción. Si encuentra un candidato viable,
recomienda la acción apropiada y el pipeline puede:

1. **install**: Descargar e instalar directamente
2. **fork_and_harden**: Clonar, aplicar security hardening, adaptar a nuestro ecosistema
3. **compose**: Tomar componentes útiles y combinar con código propio
4. **build**: Construir desde cero (el flujo normal del pipeline)
