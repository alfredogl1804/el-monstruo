# Seguridad y Compliance para Skills

## Checklist de Privacidad por Skill

Cada skill_spec debe responder:

| Pregunta | Opciones |
|----------|----------|
| ¿Procesa datos personales? | sí / no / posible |
| ¿Envía datos a APIs externas? | sí (cuáles) / no |
| ¿Almacena datos localmente? | sí (qué tipo) / no |
| ¿Jurisdicción del usuario? | MX / US / EU / global |
| ¿Dominio regulado? | salud / finanzas / legal / educación / no |
| ¿Requiere trazabilidad? | sí / no |

## Niveles de Sensibilidad

| Nivel | Descripción | Requisitos |
|-------|-------------|------------|
| bajo | Sin datos personales, sin regulación | Logging básico |
| medio | Datos personales posibles, no regulado | + PII redaction, + DPA check |
| alto | Datos personales confirmados O dominio regulado | + Compliance check, + audit trail |
| crítico | Datos sensibles + dominio regulado + multi-jurisdicción | + Legal review, + encryption, + retention policy |

## PII: Patrones a Detectar y Redactar

- Emails: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Teléfonos: `\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}`
- CURP (MX): `[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d`
- RFC (MX): `[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}`
- SSN (US): `\d{3}-\d{2}-\d{4}`
- Tarjetas: `\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}`

## Transferencia a APIs de Terceros

Antes de enviar datos a una API externa, verificar:
1. Base jurídica para la transferencia
2. El proveedor tiene DPA (Data Processing Agreement)
3. Minimización: solo enviar lo estrictamente necesario
4. Redactar PII antes de enviar si es posible
5. Documentar qué se envió, a quién, cuándo

## EU AI Act (referencia agosto 2026)

Para skills que operan en EU:
- Logging automático obligatorio
- Transparencia: el usuario debe saber que interactúa con IA
- Explicabilidad: capacidad de explicar decisiones (separado de logging)
- Evaluación de riesgo si la skill toma decisiones automatizadas
