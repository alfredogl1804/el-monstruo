# Recipe: Finance

## Dominio
Skills que tocan inversiones, pagos, contabilidad, impuestos, cripto, fintech, banca.

## Regulado
Sí — siempre.

## Investigación Obligatoria
- Marco regulatorio de la jurisdicción (CNBV, SEC, FCA, ESMA)
- Ley Fintech México (si aplica)
- KYC/AML requirements
- Protección al consumidor financiero (CONDUSEF)

## Disclaimers Obligatorios
- "No constituye asesoría financiera"
- "Consulte a un asesor financiero certificado"
- "Rendimientos pasados no garantizan rendimientos futuros"

## Scripts Recomendados
- `disclaimer_injector.py` — inyecta disclaimers en todos los outputs
- `risk_classifier.py` — clasifica nivel de riesgo de recomendaciones
- `source_validator.py` — valida fuentes de datos financieros

## Quality Gates Específicos
1. Ningún output puede dar consejo de inversión directo
2. Todos los datos numéricos deben tener fuente y fecha
3. Disclaimers presentes en cada output al usuario
4. No almacenar datos financieros personales

## APIs Comunes
- Yahoo Finance, Alpha Vantage (datos de mercado)
- Banxico API (tipo de cambio, tasas)
- CoinGecko (cripto)

## Errores Comunes
- Dar "recomendaciones" que son consejo financiero encubierto
- Usar datos desactualizados sin advertir
- No considerar impuestos y comisiones
- Ignorar diferencias jurisdiccionales
