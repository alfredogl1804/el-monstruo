# Protocolo de Investigación de Dominio

## Cuándo Investigar

| Complejidad | Investigación |
|-------------|---------------|
| minimal | No requerida |
| standard | Básica (herramientas, APIs disponibles) |
| advanced | Completa (dominio + herramientas + regulación) |
| expert | Profunda (+ consulta a sabios) |

## Flujo de Investigación

### Paso 1: Identificar Ejes de Investigación
Usar GPT-5.4 para extraer del skill_spec:
- Dominio principal y subdominios
- Herramientas y APIs necesarias
- Regulaciones aplicables
- Mejores prácticas del área
- Skills existentes similares

### Paso 2: Investigar con Perplexity Sonar
Para cada eje, consultar Perplexity Sonar (sonar-reasoning-pro) con queries específicas:
- "Best practices for [domain] automation 2026"
- "[domain] APIs and tools available"
- "[domain] regulatory requirements [jurisdiction]"
- "Common pitfalls in [domain] software"

### Paso 3: Investigar Herramientas Disponibles
Verificar contra el inventario del agente:
- APIs disponibles (OpenAI, Anthropic, Gemini, etc.)
- MCPs configurados (Asana, Zapier, Supabase, Notion, etc.)
- CLIs disponibles (gh, gws, etc.)
- Paquetes Python/Node preinstalados

### Paso 4: Compilar Dossier de Dominio
Generar `domain_dossier.md` con:
- Estado del arte del dominio
- Herramientas recomendadas (con justificación)
- Regulaciones vigentes (si aplica)
- Anti-patrones conocidos
- Skills existentes que pueden reutilizarse

## Integración con consulta-sabios

Para skills de complejidad advanced/expert, usar la skill `consulta-sabios`:

```bash
cd /home/ubuntu/skills/consulta-sabios/scripts
python3.11 run_consulta_sabios.py \
    --prompt /path/to/skill_spec_prompt.md \
    --output-dir /path/to/research/ \
    --modo enjambre \
    --profundidad-pre normal
```

## Caché de Investigación

Investigaciones se cachean por fingerprint del dominio + fecha. TTL: 7 días para herramientas, 30 días para regulaciones estables, 1 día para precios/disponibilidad.
