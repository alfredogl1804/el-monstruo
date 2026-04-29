# Recipe: Software Development Skills

## Perfil del Dominio
- Complejidad típica: standard a advanced
- APIs frecuentes: GitHub (gh), OpenAI/Claude para codegen, Supabase para DB
- Regulación: baja (excepto fintech, healthtech)
- Investigación: herramientas, frameworks, mejores prácticas

## Componentes Típicos

### Scripts Comunes
- CLI principal (argparse/click)
- Generador de código (usa GPT-5.4 o Claude)
- Validador/linter (ejecuta tests)
- Deployer (usa gh, Cloudflare, Vercel)
- Config loader (YAML/JSON)

### Referencias Comunes
- Stack técnico y versiones
- Patrones de arquitectura del proyecto
- API docs de servicios integrados
- Coding standards

### Templates Comunes
- Boilerplate del framework (React, FastAPI, etc.)
- Dockerfile / docker-compose
- CI/CD config (.github/workflows)
- .env.example

## Modelo de Codegen Recomendado
- Primario: GPT-5.4 (código complejo, arquitectura)
- Secundario: Claude Sonnet 4.6 (refactoring, review)
- Económico: DeepSeek R1 (scripts simples, boilerplate)

## Quality Gate Específico
- Todos los scripts deben ejecutar sin errores de importación
- Tests unitarios si complejidad >= standard
- Linting con ruff/pylint si Python
- Type hints si TypeScript

## Anti-patrones
- Hardcodear credenciales en scripts
- No manejar errores de APIs externas
- Scripts que requieren input interactivo
- Dependencias no documentadas
- Paths relativos en vez de absolutos
