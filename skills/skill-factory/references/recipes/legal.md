# Recipe: Legal Domain Skills

## Perfil del Dominio
- Complejidad típica: advanced a expert
- APIs frecuentes: Perplexity Sonar (regulación vigente), Claude (análisis legal), GPT-5.4
- Regulación: SIEMPRE alta (es el dominio mismo)
- Investigación: profunda + regulatoria obligatoria
- Compliance: alto a crítico

## Componentes Típicos

### Scripts Comunes
- Investigador regulatorio (Perplexity + fuentes oficiales)
- Analizador de documentos legales (Claude para precisión)
- Generador de borradores (contratos, políticas, términos)
- Validador de compliance (checklist automatizado)
- Redactor de PII (obligatorio)
- Comparador de jurisdicciones

### Referencias Comunes
- Marco regulatorio por jurisdicción (MX, US, EU)
- Glosario legal del subdominio
- Templates de documentos legales
- Checklist de compliance por tipo de documento
- Fuentes oficiales (DOF, Federal Register, EUR-Lex)

### Templates Comunes
- Contrato base (con placeholders)
- Política de privacidad
- Términos y condiciones
- NDA template
- Aviso legal

## Modelo Recomendado por Tarea

| Tarea | Modelo | Justificación |
|-------|--------|---------------|
| Análisis de regulación | Claude Sonnet 4.6 | Precisión, matices legales |
| Investigación regulatoria actual | Perplexity Sonar | Datos en tiempo real |
| Redacción de documentos | GPT-5.4 | Fluidez + estructura |
| Revisión crítica | Claude (si redactó GPT) | Separar crear de juzgar |
| Comparativa jurisdiccional | Gemini 3.1 Pro | Contexto largo para múltiples marcos |

## Quality Gate Específico (ESTRICTO)
- TODA afirmación regulatoria debe tener fuente oficial
- Jurisdicción explícita en cada sección
- Fecha de vigencia de cada regulación citada
- Disclaimer obligatorio: "No constituye asesoría legal"
- PII redactado antes de enviar a APIs
- Trazabilidad completa de qué se envió a qué API

## Requisitos de Compliance
- Nivel de sensibilidad: alto mínimo
- PII redaction: obligatorio
- Audit trail: obligatorio
- Transferencia a terceros: documentada
- Retención de datos: política explícita

## Anti-patrones
- Afirmar regulaciones sin verificar vigencia actual
- No especificar jurisdicción
- Mezclar regulaciones de diferentes países sin distinción
- Omitir disclaimer legal
- Enviar datos de clientes a APIs sin redactar PII
- Hardcodear interpretaciones legales como hechos
