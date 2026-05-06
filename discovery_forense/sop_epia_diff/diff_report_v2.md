# Diff semantico SOP/EPIA v2 — Drive vs Dropbox (token-level)

**Fecha:** 2026-05-05
**Generado por:** Manus (Tarea 4 Discovery Forense Fase III)
**Metodo:** strip_markdown -> tokenize -> SequenceMatcher sobre tokens (neutraliza formato)

## Resumen ejecutivo

| # | Par | Tokens Drive | Tokens DBX | Hash Drive | Hash DBX | Similaridad | Veredicto |
|---|---|---|---|---|---|---|---|
| 1 | SOP Fundacional v1.2 | 5301 | 4079 | `6b737ac387ddc7f4` | `00a00a68b7b127ce` | 0.862 | DIFERENCIAS NOTABLES |
| 2 | EPIA Fundacional v1.0 | 2447 | 3808 | `3545d556b6cbd9ee` | `fe5dbbf62a957244` | 0.762 | DIFERENCIAS NOTABLES |
| 3 | Genealogia SOP/EPIA v2 | 768 | 768 | `d9bc1fa0140a2de4` | `d9bc1fa0140a2de4` | 1.000 | IDENTICOS (token-level) |
| 4 | SOP+EPIA Reestructuracion 6 Sabios Abr2026 | 2639 | 2639 | `e0efd7cb264d2963` | `e0efd7cb264d2963` | 1.000 | IDENTICOS (token-level) |
| 5 | EPIA Fundacional (md vs md) | 2447 | 3814 | `3545d556b6cbd9ee` | `9f9e5fe7ac26ef82` | 0.765 | DIFERENCIAS NOTABLES |
| 6 | ENTREGABLE 2 SOP (md vs md) | 4090 | 5301 | `bead1694800c1ca3` | `6b737ac387ddc7f4` | 0.866 | DIFERENCIAS NOTABLES |

## Detalle por par

### 1. SOP Fundacional v1.2

- Drive: `SOP_v1.2_DRIVE.md` (5301 tokens)
- Dropbox: `ENTREGABLE_2_SOP_DBX.txt` (4079 tokens)
- Similaridad token-level: **0.862** -> **DIFERENCIAS NOTABLES**

**Bloques de diferencia (token-level):**

#### Bloque 1 (replace, drive=1 tokens, dbx=1 tokens)
```
DRIVE: 2
DBX:   0
```

#### Bloque 2 (delete, drive=8 tokens, dbx=0 tokens)
```
DRIVE: con 6 cambios de auditoría pulido fino editorial
DBX:   
```

#### Bloque 3 (replace, drive=2 tokens, dbx=1 tokens)
```
DRIVE: operativa define
DBX:   operativadefine
```

#### Bloque 4 (replace, drive=2 tokens, dbx=1 tokens)
```
DRIVE: decisión establece
DBX:   decisiónestablece
```

#### Bloque 5 (replace, drive=2 tokens, dbx=1 tokens)
```
DRIVE: trazabilidad obliga
DBX:   trazabilidadobliga
```

### 2. EPIA Fundacional v1.0

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (2447 tokens)
- Dropbox: `EPIA_FUNDACIONAL_DBX.txt` (3808 tokens)
- Similaridad token-level: **0.762** -> **DIFERENCIAS NOTABLES**

**Bloques de diferencia (token-level):**

#### Bloque 1 (replace, drive=2 tokens, dbx=1 tokens)
```
DRIVE: externas versión
DBX:   externasversión
```

#### Bloque 2 (replace, drive=2 tokens, dbx=1 tokens)
```
DRIVE: 0 estado
DBX:   0estado
```

#### Bloque 3 (replace, drive=4 tokens, dbx=2 tokens)
```
DRIVE: consolidado fecha 2026-04-04 alcance
DBX:   consolidadofecha 2026-04-04alcance
```

#### Bloque 4 (insert, drive=0 tokens, dbx=35 tokens)
```
DRIVE: 
DBX:   capas las capas son niveles funcionales del ecosistema capa de visión capa de gobierno capa de orquestación capa de memoria capa de conectividad capa de ejecución capa de validación capa
```

#### Bloque 5 (insert, drive=0 tokens, dbx=39 tokens)
```
DRIVE: 
DBX:   destino final imaginado el destino final de epia es un ecosistema capaz de operar sobre las 10 dimensiones de poder luego extenderse hacia el deep spectrum entendido como la frontera
```

### 3. Genealogia SOP/EPIA v2

- Drive: `GENEALOGIA_SOP_EPIA_v2_DRIVE.md` (768 tokens)
- Dropbox: `GENEALOGIA_SOP_EPIA_DBX.txt` (768 tokens)
- Similaridad token-level: **1.000** -> **IDENTICOS (token-level)**

Sin diferencias semanticas significativas. Solo formato.
### 4. SOP+EPIA Reestructuracion 6 Sabios Abr2026

- Drive: `SOP_EPIA_REESTRUCTURACION_DRIVE.md` (2639 tokens)
- Dropbox: `SOP_EPIA_REESTRUCTURACION_DBX.md` (2639 tokens)
- Similaridad token-level: **1.000** -> **IDENTICOS (token-level)**

Sin diferencias semanticas significativas. Solo formato.
### 5. EPIA Fundacional (md vs md)

- Drive: `EPIA_fundacional_completo_v1_DRIVE.txt` (2447 tokens)
- Dropbox: `EPIA_FUNDACIONAL_DBX.md` (3814 tokens)
- Similaridad token-level: **0.765** -> **DIFERENCIAS NOTABLES**

**Bloques de diferencia (token-level):**

#### Bloque 1 (insert, drive=0 tokens, dbx=35 tokens)
```
DRIVE: 
DBX:   capas las capas son niveles funcionales del ecosistema capa de visión capa de gobierno capa de orquestación capa de memoria capa de conectividad capa de ejecución capa de validación capa
```

#### Bloque 2 (insert, drive=0 tokens, dbx=39 tokens)
```
DRIVE: 
DBX:   destino final imaginado el destino final de epia es un ecosistema capaz de operar sobre las 10 dimensiones de poder luego extenderse hacia el deep spectrum entendido como la frontera
```

#### Bloque 3 (insert, drive=0 tokens, dbx=10 tokens)
```
DRIVE: 
DBX:   su formulación exacta podrá refinarse pero su espíritu es estable
```

#### Bloque 4 (insert, drive=0 tokens, dbx=5 tokens)
```
DRIVE: 
DBX:   es la visión de frontera
```

#### Bloque 5 (delete, drive=1 tokens, dbx=0 tokens)
```
DRIVE: capacidades
DBX:   
```

### 6. ENTREGABLE 2 SOP (md vs md)

- Drive: `ENTREGABLE_2_SOP_FUNDACIONAL_DRIVE.md` (4090 tokens)
- Dropbox: `ENTREGABLE_2_SOP_DBX.md` (5301 tokens)
- Similaridad token-level: **0.866** -> **DIFERENCIAS NOTABLES**

**Bloques de diferencia (token-level):**

#### Bloque 1 (replace, drive=1 tokens, dbx=1 tokens)
```
DRIVE: 0
DBX:   2
```

#### Bloque 2 (insert, drive=0 tokens, dbx=8 tokens)
```
DRIVE: 
DBX:   con 6 cambios de auditoría pulido fino editorial
```

#### Bloque 3 (insert, drive=0 tokens, dbx=318 tokens)
```
DRIVE: 
DBX:   2 5 glosario operativo cuantificable matriz de criticidad para evitar interpretaciones divergentes los siguientes términos se consideran operativamente definidos relevante un asunto es relevante cuando cumple al menos una de
```

#### Bloque 4 (insert, drive=0 tokens, dbx=1 tokens)
```
DRIVE: 
DBX:   final
```

#### Bloque 5 (delete, drive=1 tokens, dbx=0 tokens)
```
DRIVE: toda
DBX:   
```
