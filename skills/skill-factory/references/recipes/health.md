# Recipe: Health

## Dominio
Skills que tocan salud, medicina, bienestar, nutrición, fitness, salud mental, telemedicina.

## Regulado
Sí — siempre. Datos de salud son la categoría más protegida en GDPR y LFPDPPP.

## Investigación Obligatoria
- HIPAA (EE.UU.) y equivalentes locales
- NOM-024-SSA3 (expediente clínico electrónico México)
- COFEPRIS para software como dispositivo médico
- Consentimiento informado digital

## Disclaimers Obligatorios
- "No constituye diagnóstico ni tratamiento médico"
- "Consulte a un profesional de salud certificado"
- "En caso de emergencia, llame al número de emergencias local"

## Scripts Recomendados
- `health_disclaimer.py` — inyecta disclaimers de salud en todos los outputs
- `emergency_detector.py` — detecta situaciones de emergencia y redirige
- `evidence_grader.py` — clasifica evidencia según nivel (meta-análisis > caso clínico)

## Quality Gates Específicos
1. Jamás diagnosticar ni prescribir
2. Detectar y escalar emergencias (suicidio, infarto, etc.)
3. Citar nivel de evidencia de toda afirmación
4. No almacenar datos de salud sin consentimiento explícito
5. Anonimización obligatoria de cualquier dato de paciente

## APIs Comunes
- PubMed/NCBI (literatura médica)
- OpenFDA (medicamentos y dispositivos)
- WHO APIs (estadísticas globales)

## Errores Comunes
- Dar información que se interpreta como diagnóstico
- No detectar emergencias médicas en el input del usuario
- Mezclar evidencia anecdótica con evidencia científica
- Almacenar datos de salud sin cifrado
