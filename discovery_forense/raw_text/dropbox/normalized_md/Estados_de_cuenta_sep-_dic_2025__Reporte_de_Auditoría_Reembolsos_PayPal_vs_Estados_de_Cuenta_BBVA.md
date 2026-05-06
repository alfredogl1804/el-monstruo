# Reporte de Auditoría: Reembolsos PayPal vs Estados de Cuenta BBVA

Titular: Alfredo Gongora Lizama
Cuenta BBVA: 1566309521 (Libretón Básico Cuenta Digital)
Cuenta PayPal: MBQDYWMTRQTJ2
Periodo auditado: Noviembre 2025 - Febrero 2026
Fecha del reporte: 27 de marzo de 2026

## Resumen Ejecutivo

Se identificaron 8 reembolsos emitidos por PayPal en el periodo noviembre 2025 a febrero 2026 por un total de MXN 171,073.77 (incluyendo la conversión del reembolso en USD). De estos, 5 se reflejaron correctamente como abonos en los estados de cuenta de BBVA y 3 no aparecen en los estados de cuenta bancarios, a pesar de que PayPal registra que fueron retirados a cuenta bancaria (transacción tipo T0600).

Monto total de reembolsos faltantes en BBVA: MXN 136,543.67

## Detalle de los 8 Reembolsos de PayPal

## Detalle de Reembolsos Faltantes

### Reembolso #1 - MXN 71,378.24

Fecha del reembolso en PayPal: 30 de noviembre de 2025

ID de reembolso (T1107): 618317969K480370F

ID de retiro a banco (T0600): 30K4015184014634M

Referencia de la compra original (T0006): 7VB50753PX394420U del 28/nov/2025 por MXN 71,378.24 (concepto: CN122AWAA-30, con descuento de MXN 28,801.76)

Estado en BBVA: No se encontró ningún abono por MXN 71,378.24 ni monto similar en el estado de cuenta de noviembre ni diciembre 2025.

Observación: PayPal registra que el monto fue retirado a cuenta bancaria el mismo 30 de noviembre, pero el depósito no aparece en BBVA.

### Reembolso #3 - USD 3,588.00 (MXN 64,467.43)

Fecha del reembolso en PayPal: 16 de diciembre de 2025

ID de reembolso (T1107): 61480523VR380513S

ID de retiro a banco (T0600): 4PS50377E8303120Y

Referencia de la compra original (T0003): 1T201169JW469341C del 10/dic/2025 por USD 3,588.00 (concepto: "Pro Plan", factura 197402, corresponde a BRAND24GLOB BR)

Conversión: USD 3,588.00 fue convertido a MXN 64,467.43 al momento del retiro

Estado en BBVA: No se encontró ningún abono por MXN 64,467.43 en el estado de cuenta de diciembre 2025 ni enero 2026. El cargo original de MXN 68,913.57 (a tipo de cambio diferente) sí aparece como cargo el 15/dic.

Observación: PayPal registra que el monto fue retirado a cuenta bancaria el 16 de diciembre, pero el depósito no aparece en BBVA.

### Reembolso #8 - MXN 698.00

Fecha del reembolso en PayPal: 20 de febrero de 2026

ID de reembolso (T1107): 8JC28074HC5455132

ID de retiro a banco (T0600): 1HV04581HW094994D

Estado en BBVA: El monto de MXN 698.00 aparece el 23/FEB como cargo (PAYPAL *ITUNESAPPST AP), no como abono. El reembolso de 698.00 como abono no fue encontrado.

Observación: PayPal registra que el monto fue retirado a cuenta bancaria el 20 de febrero, pero solo aparece un cargo por el mismo monto (nueva compra), no el abono del reembolso.

## Detalle de Reembolsos Correctamente Reflejados

## Metodología

Se consultaron las transacciones de PayPal mediante la API oficial (conector MCP PayPal para Empresas) filtrando por transacciones exitosas (status "S") en cada mes del periodo.

Se identificaron los reembolsos por su código de evento T1107 (Payment Refund).

Se verificó que cada reembolso tuviera un retiro asociado a cuenta bancaria (código T0600).

Se extrajeron los textos de los 4 estados de cuenta de BBVA (noviembre 2025 a febrero 2026) y se buscaron los montos exactos de cada reembolso.

Se distinguieron cargos de abonos mediante el análisis posicional de las columnas en los estados de cuenta (los abonos aparecen en posición ~122-124 del texto, mientras que los cargos aparecen en posición ~107-113).

## Recomendaciones

Contactar a PayPal para solicitar comprobantes de los retiros T0600 de los reembolsos #1 (MXN 71,378.24), #3 (MXN 64,467.43) y #8 (MXN 698.00), incluyendo la cuenta bancaria destino y la referencia SPEI/CLABE utilizada.

Verificar con BBVA si los depósitos fueron recibidos pero aplicados a otra cuenta, o si fueron rechazados por algún motivo.

Revisar la CLABE registrada en PayPal para confirmar que corresponde a la cuenta BBVA 1566309521.

El monto total pendiente de aclaración es de MXN 136,543.67 (71,378.24 + 64,467.43 + 698.00).



| # | Fecha PayPal | Monto Original | Monto MXN Retirado | ID Transacción PayPal | Concepto | Reflejado en BBVA |

| 1 | 30/nov/2025 | MXN 71,378.24 | MXN 71,378.24 | 618317969K480370F | CN122AWAA-30 | NO |

| 2 | 05/dic/2025 | MXN 5,199.13 | MXN 5,199.13 | 65L507625E0907902 | ITUNESAPPST | SI |

| 3 | 16/dic/2025 | USD 3,588.00 | MXN 64,467.43 | 61480523VR380513S | Pro Plan (BRAND24GLOB) | NO |

| 4 | 17/dic/2025 | MXN 5,805.81 | MXN 5,805.81 | 0LW08186JM487052M | ITUNESAPPST | SI |

| 5 | 24/dic/2025 | MXN 7,741.16 | MXN 7,741.16 | 72N63201S30325409 | ITUNESAPPST | SI |

| 6 | 14/ene/2026 | MXN 14,294.00 | MXN 14,294.00 | 2G0354981T4721350 | IKANORETAIL | SI |

| 7 | 26/ene/2026 | MXN 599.00 | MXN 599.00 | 6A406819RP896103X | IKANORETAIL | SI |

| 8 | 20/feb/2026 | MXN 698.00 | MXN 698.00 | 8JC28074HC5455132 | (sin descripción) | NO |





| # | Fecha PayPal | Monto | Fecha en BBVA | Descripción en BBVA |

| 2 | 05/dic/2025 | MXN 5,199.13 | 08/DIC (valor 30/NOV) | PAYPAL*ITUNESAPPST AP |

| 4 | 17/dic/2025 | MXN 5,805.81 | 19/DIC (valor 17/DIC) | PAYPAL *ITUNESAPPST AP |

| 5 | 24/dic/2025 | MXN 7,741.16 | 24/DIC (valor 16/DIC) | PAYPAL*ITUNESAPPST AP |

| 6 | 14/ene/2026 | MXN 14,294.00 | 19/ENE (valor 15/ENE) | PAYPAL *IKANORETAIL 63 |

| 7 | 26/ene/2026 | MXN 599.00 | 27/ENE (valor 26/ENE) | PAYPAL *IKANORETAIL 63 |

