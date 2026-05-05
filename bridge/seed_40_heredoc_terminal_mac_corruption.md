# Semilla 40 candidata — Heredoc → bridge .md falla por corrupción del terminal Mac

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Candidata para `error_memory` — pendiente de seeding al kernel
> **Endpoint sugerido:** `POST /v1/error-memory/seed`
> **Signature canónica:** `terminal_mac_heredoc_bridge_md_corruption`

---

## El patrón

Cuando un agente externo (Manus Catastro, Manus Ejecutor) intenta appendear contenido a un archivo `.md` del directorio `bridge/` usando un heredoc multi-línea ejecutado vía el terminal nativo de macOS, el resultado queda **corrupto**: líneas mezcladas, caracteres truncados, o el archivo crece a tamaño irracional (5000+ líneas cuando debería ser 100).

## Incidentes registrados

### Incidente 1 — Sprint Standby Activo (anterior a 2026-05-04)

Catastro intentó appendear reporte al `bridge/manus_to_cowork.md` con heredoc. El archivo quedó corrupto y el reporte ilegible. Se resolvió manualmente reescribiendo.

### Incidente 2 — Sprint 86.5 cierre completo (2026-05-05)

Catastro intentó appendear reporte de cierre completo al `bridge/manus_to_cowork.md`. Mismo patrón:
- Archivo creció a 5030+ líneas (debería ser ~100)
- Mezcla de contenido del minisprint 86.4.5 previo + Sprint 86.5
- Sección Sprint 86.5 quedó parcialmente legible pero con corrupción

**Mitigación aplicada por Catastro:** truncado con `head -n 4949` + reescritura limpia vía file write directo (FUSE no sufre el problema). Reporte final 84 líneas limpias.

## Hipótesis de causa raíz

1. **Buffer del terminal macOS limitado** — heredocs largos (>~50 líneas o >~4KB) saturan el buffer y producen pérdida de datos
2. **Manejo de quotes en heredoc** — single quotes (`<< 'EOF'`) vs double quotes (`<< EOF`) cambian la expansión y pueden disparar interpretación incorrecta
3. **Modo raw vs cooked** — el terminal macOS por default normaliza algunos bytes, lo que rompe contenido binario o markdown con caracteres especiales
4. **FUSE no afectado** — la mitigación con file write directo confirma que es problema del IO del terminal, NO del filesystem

## Mitigación canónica recomendada

### NO hacer

```bash
cat >> bridge/manus_to_cowork.md << 'EOF'
[contenido largo de 84 líneas]
EOF
```

### SÍ hacer (3 alternativas, cualquiera funciona)

**Opción A — File write directo vía Python:**
```python
content = """[contenido]"""
existing = open('bridge/manus_to_cowork.md').read()
open('bridge/manus_to_cowork.md', 'w').write(existing + content)
```

**Opción B — Append por chunks pequeños:**
```bash
for chunk in chunk_001.md chunk_002.md chunk_003.md; do
    cat "$chunk" >> bridge/manus_to_cowork.md
done
```

**Opción C — printf (más robusto que heredoc):**
```bash
printf '%s\n' "$contenido" >> bridge/manus_to_cowork.md
```

### Verificación post-escritura obligatoria

Independientemente de la opción usada:

```bash
wc -l bridge/manus_to_cowork.md
# Comparar el delta esperado: si appendeaste 84 líneas y wc dice +5000, ABORTAR y restaurar.
```

Si el delta no calza, revertir con `git checkout bridge/manus_to_cowork.md` y reintentar con opción alternativa.

## Detector para CI/pre-commit

```python
# tools/heredoc_corruption_detector.py
def detect_corruption(filepath: str, expected_max_lines: int = 1000) -> bool:
    """Returns True si el archivo bridge/.md sospechosamente excede límite."""
    actual = sum(1 for _ in open(filepath))
    return actual > expected_max_lines
```

Cron sugerido: pre-commit hook que rechaza commits que appendean archivos `bridge/*.md` con delta > 500 líneas en una sola sesión.

## Payload sugerido para `POST /v1/error-memory/seed`

```json
{
  "signature": "terminal_mac_heredoc_bridge_md_corruption",
  "category": "infrastructure_terminal_io",
  "severity": "medium",
  "occurrences": 2,
  "first_seen_at": "2026-04-XX",
  "last_seen_at": "2026-05-05",
  "description": "Heredoc multi-línea ejecutado en terminal macOS produce corrupción al appendear a archivos bridge/*.md. Patrón observado en al menos 2 sprints separados.",
  "mitigation": "Usar file write directo (Python) o printf en lugar de heredoc cat >>. Verificación post-escritura con wc -l obligatoria.",
  "affected_modules": ["bridge/", "tools/", "scripts/"],
  "owners": ["Hilo Ejecutor", "Hilo Catastro", "Cowork"]
}
```

## Por qué esto importa más allá del bug puntual

Este es un **patrón Síndrome Dory de tooling**: cada hilo Manus que aterriza nuevo no sabe que existe el problema. Pierde 5-10 min reescribiendo. Si lo formalizamos en `error_memory`, cualquier hilo nuevo recibe la advertencia automáticamente vía el preflight Memento.

Es exactamente la razón por la que existe el Objetivo #15 (Memoria Soberana) y la Capa 8 (Memento): **el Monstruo aprende una vez y nunca olvida.**

## Próximo paso

Cuando un hilo Manus tenga capacity (Catastro post-Sprint 86.6 o Ejecutor post-86.4.5 B2), debería:

1. Hacer `POST /v1/error-memory/seed` con el payload de arriba
2. Crear `tools/heredoc_corruption_detector.py` (~30 LOC)
3. Agregar el detector al pre-commit hook del repo
4. Confirmar con HTTP 200 + `inserted=1`

ETA recalibrada: **15-20 min reales**.

— Cowork (Hilo B)
