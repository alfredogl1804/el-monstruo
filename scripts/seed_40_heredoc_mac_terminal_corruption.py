"""
Semilla #40 — Heredoc → Bridge .md Corruption en Mac Terminal
              (Sprint 86.6 — Catastro Visión Quorum 2-de-3 anti-gaming v2)

Lección a sembrar en la base error_memory:
  Cuando se appendea contenido multilínea complejo (con tildes, emojis,
  pipes Markdown, fences ```, comillas mixtas, líneas vacías) a un archivo
  vivo del bridge usando heredocs (`cat << EOF >> file`) ejecutados en
  terminales Mac (Terminal.app, iTerm con compatibility mode), el contenido
  llega CORRUPTO al archivo: líneas duplicadas, fragmentos pegados, EOF
  detectado prematuramente, encoding UTF-8 roto.

  Origen del incidente:
    - 1ra ocurrencia: Sprint 86.5 cierre — append a manus_to_cowork.md
      vía heredoc resultó en líneas duplicadas y bloque corrupto.
    - 2da ocurrencia: Sprint 86.6 cierre (mismo patrón). Confirmado el
      patrón.

  Patrón ganador (anti-corruption):
    1. NUNCA usar `cat << EOF >> /mnt/.../bridge/*.md` desde shell de Mac.
    2. Usar `file_write` o `file_append` (FUSE write) que NO sufre el bug.
    3. Si necesario shell: usar `printf '%s\\n' "linea1" "linea2" >> file`
       (printf cada línea individual, sin heredoc).
    4. Para reportes largos: escribir a archivo temporal con file_write,
       luego `cat tmp >> bridge.md` (cat de archivo SÍ es seguro).

  Disciplina anti-Dory aplicada:
    - 1ra ocurrencia se reportó en bridge sin formalizar como semilla.
    - 2da ocurrencia (este sprint) la formaliza para que el Guardian
      detecte futuros intentos de heredoc → bridge y rechace antes de
      ejecutar.

  Impacto si NO se mitiga:
    - Bridge .md corrupto → audits Cowork no pueden parsearlo.
    - Pérdida silenciosa de checkpoints.
    - Tiempo perdido en re-truncamiento + reescritura.

  Capa Memento:
    - Esta semilla la consume error_memory en su próximo refresh.
    - El Guardian (Sprint 89+) debería rechazar heredocs sobre paths
      `**/bridge/**.md` automáticamente.

[Hilo Manus Catastro] · Sprint 86.6 · 2026-05-05
"""
from __future__ import annotations

# Esta semilla NO ejecuta nada. Es metadata consumida por el sistema
# de error_memory en su próximo refresh.

SEMILLA_ID = "40_heredoc_mac_terminal_corruption"
SEMILLA_TITULO = "Heredoc Mac terminal corrompe bridge .md appends multilinea"
SEMILLA_SPRINT = "86.6"
SEMILLA_FECHA = "2026-05-05"
SEMILLA_AUTORIA = "Manus Catastro (Hilo B)"

LECCION_PRINCIPAL = (
    "NUNCA usar heredoc (cat << EOF >> file) en terminales Mac para "
    "appendear contenido multilinea con tildes/emojis/pipes/fences a "
    "archivos del bridge. Usar file_append (FUSE) o printf por linea. "
    "Si necesario, escribir a tmp file y concatenar con cat tmp >> bridge."
)


def get_semilla_metadata() -> dict:
    """Retorna metadata para que error_memory la consuma."""
    return {
        "id": SEMILLA_ID,
        "titulo": SEMILLA_TITULO,
        "sprint": SEMILLA_SPRINT,
        "fecha": SEMILLA_FECHA,
        "autoria": SEMILLA_AUTORIA,
        "leccion": LECCION_PRINCIPAL,
        "anti_pattern": "cat << EOF >> /mnt/.../bridge/*.md (en Mac terminal)",
        "patron_ganador": (
            "file_append via FUSE OR printf '%s\\n' linea por linea "
            "OR file_write tmp + cat tmp >> bridge.md"
        ),
        "incidentes": [
            {
                "sprint": "86.5",
                "fecha": "2026-05-05",
                "descripcion": "Append cierre Sprint 86.5 a manus_to_cowork.md - lineas duplicadas",
            },
            {
                "sprint": "86.6",
                "fecha": "2026-05-05",
                "descripcion": "2da ocurrencia mismo patron - confirmado pattern, semilla creada",
            },
        ],
        "guardian_rule_propuesta": (
            "Sprint 89+: Guardian rechaza heredoc sobre paths "
            "**/bridge/**.md automaticamente."
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_semilla_metadata(), indent=2, ensure_ascii=False))
