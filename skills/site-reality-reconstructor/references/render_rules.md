# Reglas de Validación de Renders

## Reglas Críticas (fallo automático)

| ID | Regla | Descripción |
|----|-------|-------------|
| C01 | No inventar edificios | No colocar edificios donde hay lotes vacíos o estacionamientos |
| C02 | No escalar alturas | No subir contexto de 1-2 niveles a 5+ niveles |
| C03 | No inventar paisajismo | No añadir jardines, fuentes o paisajismo exuberante inexistente |
| C04 | No upgradar superficies | No cambiar tierra/estacionamiento por boulevard premium |
| C05 | No omitir must_include | No omitir elementos marcados como obligatorios en el SRD |
| C06 | No inventar agua | No añadir lagos, ríos o fuentes donde no existen |
| C07 | No inventar transporte | No añadir metro, tranvía o infraestructura de transporte inexistente |
| C08 | No inventar skyline | No crear skyline de ciudad grande donde hay contexto suburbano |

## Reglas Mayores

| ID | Regla | Descripción |
|----|-------|-------------|
| M01 | Materiales correctos | Los materiales dominantes deben coincidir con la realidad |
| M02 | Vegetación proporcional | La vegetación debe ser proporcional a la realidad |
| M03 | Vialidades correctas | Las calles deben tener el ancho y tipo correcto |
| M04 | Escala humana | Los elementos deben estar a escala humana correcta |
| M05 | Orientación solar | La iluminación debe ser coherente con la orientación |
| M06 | Densidad urbana | La densidad del contexto debe coincidir con la realidad |

## Reglas Menores

| ID | Regla | Descripción |
|----|-------|-------------|
| m01 | Colores aproximados | Los colores deben ser similares a la realidad |
| m02 | Mobiliario genérico | El mobiliario urbano puede ser genérico si no hay datos |
| m03 | Vehículos genéricos | Los vehículos pueden ser genéricos |
| m04 | Personas genéricas | Las personas pueden ser genéricas |

## Scoring

- **Score base**: 1.0
- **Critical violation**: -0.3 cada una (y auto-FAIL)
- **Major violation**: -0.1 cada una
- **Minor violation**: -0.03 cada una
- **Positive match**: +0.02 cada uno (max 0.2 bonus)
- **PASS threshold**: >= 0.65 Y 0 critical violations

## Política de Blind Spots en Renders

| Status del blind spot | Qué puede aparecer en el render |
|----------------------|--------------------------------|
| confirmed_visible | Renderizar como se observó |
| mapped_not_visible | Masa neutra sin detalle (gris/beige, sin textura) |
| high_confidence_inferred | Contexto de bajo detalle (tipología regional genérica) |
| low_confidence_inferred | Masa neutra mínima |
| unknown_do_not_detail | Omitir o fondo difuso |
