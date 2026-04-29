---
name: proyecto-renders
description: Pipeline multiagente de inteligencia inmobiliaria que analiza terrenos, investiga benchmarks, genera modelo de negocio, plan financiero y 8 renders fotorrealistas. Usar cuando la tarea implique analizar un terreno, proponer uso de suelo, crear plan de negocio inmobiliario, o generar renders arquitectónicos.
---

# Proyecto Renders

Pipeline de 7 módulos que transforma una descripción de terreno en un paquete de inversión completo con plan de negocio y renders fotorrealistas.

## Cuándo usar

Usar cuando la tarea implique: analizar un terreno o propiedad, proponer mejor uso de suelo, crear plan de negocio inmobiliario, generar renders arquitectónicos, o preparar presentación para inversionistas.

## Dependencias

- Skill `consulta-sabios` (conectores de API a los 6 sabios)
- PyYAML: `sudo pip3 install pyyaml`

## Pipeline de 7 módulos

### Módulo 1: Intake (`intake_normalize.py`)

Captura la descripción del proyecto y genera `project_brief.yaml` normalizado usando GPT-5.4.

```bash
python3.11 scripts/intake_normalize.py \
  --description "Descripción del terreno y objetivo" \
  --address "Dirección" \
  --output project_brief.yaml
```

### Módulo 2: Site Intelligence (`site_intelligence.py`)

Investiga contexto urbano, clima, demografía, competencia y regulación usando Perplexity + GPT-5.4.

```bash
python3.11 scripts/site_intelligence.py \
  --brief project_brief.yaml \
  --output-dir ./
```

Salida: `site_report.md`, `site_data.yaml`

### Módulo 3: Benchmark Research (`benchmark_research.py`)

Investiga proyectos de referencia mundiales similares usando Perplexity + GPT-5.4.

```bash
python3.11 scripts/benchmark_research.py \
  --brief project_brief.yaml \
  --site-report site_report.md \
  --output-dir ./
```

Salida: `benchmarks.md`, `benchmarks_data.yaml`

### Módulo 4: HBU + Escenarios (`hbu_scenarios.py`)

Análisis Highest and Best Use. Genera 3 escenarios con modelo financiero rápido y recomienda el mejor.

```bash
python3.11 scripts/hbu_scenarios.py \
  --brief project_brief.yaml \
  --site-report site_report.md \
  --benchmarks benchmarks.md \
  --output-dir ./
```

Salida: `hbu_analysis.md`, `scenarios.yaml`

### Módulo 5: Business Plan (`business_plan.py`)

Genera plan de negocio ejecutivo completo (10 secciones) y validación financiera por Gemini.

```bash
python3.11 scripts/business_plan.py \
  --brief project_brief.yaml \
  --site-report site_report.md \
  --benchmarks benchmarks.md \
  --hbu hbu_analysis.md \
  --scenarios scenarios.yaml \
  --output-dir ./
```

Salida: `business_plan.md`, `financial_validation.md`

### Módulo 6: Render Pipeline (`render_pipeline.py`)

Genera Style Bible y 8 prompts optimizados para renders fotorrealistas. El agente genera las imágenes usando `generate` mode.

```bash
python3.11 scripts/render_pipeline.py \
  --brief project_brief.yaml \
  --scenarios scenarios.yaml \
  --benchmarks benchmarks.md \
  --site-data site_data.yaml \
  --output-dir ./
```

Salida: `style_bible.md`, `render_prompts.yaml`, `render_instructions.md`

Después de ejecutar este módulo, el agente DEBE entrar en modo `generate` y crear cada imagen usando los prompts de `render_prompts.yaml`. Guardar en `renders/`.

### Módulo 7: QA & Packaging (`qa_packaging.py`)

Verifica completitud, valida consistencia entre documentos, genera resumen ejecutivo y empaqueta ZIP.

```bash
python3.11 scripts/qa_packaging.py \
  --project-dir ./
```

Salida: `qa_report.md`, `executive_summary.md`, `proyecto_completo.zip`

## Entrypoint unificado

Ejecuta los 7 módulos en secuencia:

```bash
cd /home/ubuntu/skills/proyecto-renders/scripts && \
python3.11 run_proyecto.py \
  --description "Descripción completa del proyecto" \
  --address "Dirección del terreno" \
  --output-dir /tmp/proyecto_renders
```

Flags opcionales: `--lat`, `--lng`, `--drive-folder`, `--local-files`, `--skip-renders`, `--skip-qa`

## Flujo post-pipeline

1. Ejecutar `run_proyecto.py` (módulos 1-7)
2. Leer `render_prompts.yaml` del output
3. Entrar en modo `generate` y crear los 8 renders
4. Guardar renders en `{output_dir}/renders/`
5. Re-ejecutar QA si se desea: `python3.11 qa_packaging.py --project-dir {output_dir}`

## Reglas

- PROHIBIDO improvisar código de conexión a APIs. Usar `conector_sabios.py` de la skill `consulta-sabios`.
- Los renders se generan con la herramienta `generate` de Manus, NO con código.
- Todas las cifras financieras deben etiquetarse: `[VERIFICADO]`, `[BENCHMARK]`, `[ESTIMADO]`, `[SUPUESTO]`.
- El plan de negocio debe incluir análisis de sensibilidad con 3 escenarios.
