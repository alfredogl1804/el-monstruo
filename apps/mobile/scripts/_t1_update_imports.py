#!/usr/bin/env python3
"""T1 Mobile Realignment — actualización masiva de imports tras renames.

Reemplazos verbatim string-a-string (no regex) para cero ambigüedad.
Ejecutar desde apps/mobile/.
"""
import pathlib

REPLACEMENTS = [
    # services/* → core/mensajeros/* (3 niveles de relatividad + root)
    ("'../../services/kernel_service.dart'", "'../../core/mensajeros/kernel_messenger.dart'"),
    ("'../../services/agent_service.dart'", "'../../core/mensajeros/agent_messenger.dart'"),
    ("'../../services/voice_service.dart'", "'../../core/mensajeros/voice_messenger.dart'"),
    ("'../../services/notification_service.dart'", "'../../core/mensajeros/notification_messenger.dart'"),
    ("'../../services/thread_persistence.dart'", "'../../core/mensajeros/thread_persistence.dart'"),
    ("'../../../services/kernel_service.dart'", "'../../../core/mensajeros/kernel_messenger.dart'"),
    ("'../../../services/agent_service.dart'", "'../../../core/mensajeros/agent_messenger.dart'"),
    ("'../../../services/voice_service.dart'", "'../../../core/mensajeros/voice_messenger.dart'"),
    ("'../../../services/notification_service.dart'", "'../../../core/mensajeros/notification_messenger.dart'"),
    ("'../../../services/thread_persistence.dart'", "'../../../core/mensajeros/thread_persistence.dart'"),
    ("'../services/kernel_service.dart'", "'../core/mensajeros/kernel_messenger.dart'"),
    ("'../services/agent_service.dart'", "'../core/mensajeros/agent_messenger.dart'"),
    ("'../services/voice_service.dart'", "'../core/mensajeros/voice_messenger.dart'"),
    ("'../services/notification_service.dart'", "'../core/mensajeros/notification_messenger.dart'"),
    ("'../services/thread_persistence.dart'", "'../core/mensajeros/thread_persistence.dart'"),
    # main.dart root-level imports
    ("'services/kernel_service.dart'", "'core/mensajeros/kernel_messenger.dart'"),
    ("'services/agent_service.dart'", "'core/mensajeros/agent_messenger.dart'"),
    ("'services/voice_service.dart'", "'core/mensajeros/voice_messenger.dart'"),
    ("'services/notification_service.dart'", "'core/mensajeros/notification_messenger.dart'"),
    ("'services/thread_persistence.dart'", "'core/mensajeros/thread_persistence.dart'"),
    # theme/monstruo_theme.dart → core/theme/brand_dna.dart
    ("'../../theme/monstruo_theme.dart'", "'../../core/theme/brand_dna.dart'"),
    ("'../../../theme/monstruo_theme.dart'", "'../../../core/theme/brand_dna.dart'"),
    ("'../theme/monstruo_theme.dart'", "'../core/theme/brand_dna.dart'"),
    ("'theme/monstruo_theme.dart'", "'core/theme/brand_dna.dart'"),
    # features/genui/* → core/a2ui/*
    ("'../features/genui/genui_screen.dart'", "'../core/a2ui/a2ui_screen.dart'"),
    ("'../features/genui/genui_renderer.dart'", "'../core/a2ui/a2ui_renderer.dart'"),
    ("'../../features/genui/genui_screen.dart'", "'../../core/a2ui/a2ui_screen.dart'"),
    # imports internos a2ui_screen → a2ui_renderer
    ("'genui_renderer.dart'", "'a2ui_renderer.dart'"),
]


def main() -> int:
    count = 0
    for base in ("lib", "test"):
        for f in pathlib.Path(base).rglob("*.dart"):
            txt = f.read_text()
            orig = txt
            for old, new in REPLACEMENTS:
                txt = txt.replace(old, new)
            if txt != orig:
                f.write_text(txt)
                count += 1
                print(f"updated: {f}")
    print(f"\nTotal archivos actualizados: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
