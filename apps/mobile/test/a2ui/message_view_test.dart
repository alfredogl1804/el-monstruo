// Tests T7 — A2UIMessageView (integración renderer A2UI dentro del chat).
//
// Verifica:
// 1. tryBuild devuelve null si payload no tiene a2ui_version.
// 2. tryBuild devuelve null si payload es null.
// 3. tryBuild parsea correctamente payload v1.0 y renderiza el árbol.
// 4. warning del parser se muestra como banner sobre el árbol.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:el_monstruo_app/core/a2ui/a2ui_message_view.dart';

void main() {
  group('A2UIMessageView.tryBuild', () {
    test('devuelve null si payload es null', () {
      expect(A2UIMessageView.tryBuild(payload: null), isNull);
    });

    test('devuelve null si payload no tiene a2ui_version (legacy GenUI)', () {
      final view = A2UIMessageView.tryBuild(payload: const {
        'component_type': 'legacy_dashboard',
        'data': {'metric': 42},
      });
      expect(view, isNull);
    });

    test('parsea y devuelve view si payload tiene a2ui_version', () {
      final view = A2UIMessageView.tryBuild(payload: const {
        'a2ui_version': '1.0',
        'root': {
          'type': 'Text',
          'props': {'content': 'Hola Monstruo'},
        },
      });
      expect(view, isNotNull);
    });

    testWidgets('renderiza Text dentro de un MaterialApp', (tester) async {
      final view = A2UIMessageView.tryBuild(payload: const {
        'a2ui_version': '1.0',
        'root': {
          'type': 'Card',
          'children': [
            {
              'type': 'Text',
              'props': {'content': 'Operación completa'},
            },
          ],
        },
      });
      expect(view, isNotNull);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: view!)));
      expect(find.text('Operación completa'), findsOneWidget);
    });

    testWidgets('muestra warning banner cuando parser advierte', (tester) async {
      // Tipo no whitelist → parser produce fallback Markdown con warning.
      final view = A2UIMessageView.tryBuild(payload: const {
        'a2ui_version': '1.0',
        'root': {
          'type': 'WidgetInexistente',
          'props': {'content': 'fallback'},
        },
      });
      expect(view, isNotNull);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: view!)));
      // El warning banner debe estar presente con icono warning_amber.
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
    });
  });
}
