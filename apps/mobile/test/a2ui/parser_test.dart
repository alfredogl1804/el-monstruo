import 'package:el_monstruo_app/core/a2ui/parser.dart';
import 'package:el_monstruo_app/core/a2ui/types/a2ui_node.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const parser = A2UIParser();

  group('A2UIParser — whitelist v1.0', () {
    test('parses minimal Text node', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {'type': 'Text', 'props': {'content': 'Hola Monstruo'}},
      });
      expect(r.root, isNotNull);
      expect(r.root!.type, 'Text');
      expect(r.root!.prop<String>('content'), 'Hola Monstruo');
      expect(r.isClean, isTrue);
    });

    test('parses Card with header/footer slots and Stack children', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {
          'type': 'Card',
          'slots': {
            'header': [
              {'type': 'Text', 'props': {'content': 'Encabezado'}},
            ],
            'footer': [
              {'type': 'Divider'},
              {'type': 'Text', 'props': {'content': 'Pie'}},
            ],
          },
          'children': [
            {
              'type': 'Stack',
              'children': [
                {'type': 'Badge', 'props': {'label': 'OK', 'variant': 'success'}},
                {'type': 'Text', 'props': {'content': 'Body'}},
              ],
            },
          ],
        },
      });
      expect(r.root!.type, 'Card');
      expect(r.root!.slots['header']!.length, 1);
      expect(r.root!.slots['footer']!.length, 2);
      expect(r.root!.children.first.type, 'Stack');
      expect(r.root!.children.first.children.first.type, 'Badge');
      expect(r.isClean, isTrue);
    });

    test('handles all 19 whitelisted types', () {
      for (final t in kA2UIWhitelist) {
        final r = parser.parse({
          'a2ui_version': '1.0',
          'root': {'type': t, 'props': {'content': 'x'}},
        });
        expect(r.root!.type, t, reason: 'whitelist type $t should pass');
      }
    });
  });

  group('A2UIParser — fallback markdown', () {
    test('unknown type → Markdown fallback with warning', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {
          'type': 'MysteryWidget',
          'props': {'content': 'Hint'},
        },
      });
      expect(r.root!.type, 'Markdown');
      expect(r.root!.originalType, 'MysteryWidget');
      expect(r.hasFallback, isTrue);
      expect(
        r.warnings.first.message,
        contains('not in whitelist'),
      );
    });

    test('non-string type → fallback Text error', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {'type': 42},
      });
      expect(r.root!.type, 'Text');
      expect(r.root!.prop<String>('content'), contains('missing type'));
    });
  });

  group('A2UIParser — security', () {
    test('rejects payload over 256 KB', () {
      final big = 'x' * (256 * 1024 + 1);
      final r = parser.parseJson('{"a2ui_version":"1.0","root":{"type":"Text","props":{"content":"$big"}}}');
      expect(r.root, isNull);
      expect(r.warnings.first.level, A2UIWarningLevel.fatal);
    });

    test('rejects invalid JSON', () {
      final r = parser.parseJson('not json at all');
      expect(r.root, isNull);
      expect(r.warnings.first.message, contains('Invalid JSON'));
    });

    test('rejects missing a2ui_version', () {
      final r = parser.parse({'root': {'type': 'Text'}});
      expect(r.root, isNull);
    });

    test('rejects missing root', () {
      final r = parser.parse({'a2ui_version': '1.0'});
      expect(r.root, isNull);
    });

    test('truncates beyond max depth (32)', () {
      Map<String, dynamic> nested = {'type': 'Text', 'props': {'content': 'leaf'}};
      for (var i = 0; i < 40; i++) {
        nested = {
          'type': 'Stack',
          'children': [nested],
        };
      }
      final r = parser.parse({'a2ui_version': '1.0', 'root': nested});
      expect(r.root, isNotNull);
      final truncated = r.warnings.any(
        (w) => w.message.contains('Max depth'),
      );
      expect(truncated, isTrue);
    });

    test('mismatched version produces ignored warning but still parses', () {
      final r = parser.parse({
        'a2ui_version': '99.9',
        'root': {'type': 'Text', 'props': {'content': 'ok'}},
      });
      expect(r.root, isNotNull);
      expect(
        r.warnings.any((w) => w.level == A2UIWarningLevel.ignored),
        isTrue,
      );
    });
  });

  group('A2UIParser — action protocol', () {
    test('parses action_id and action_payload', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {
          'type': 'Button',
          'props': {'label': 'Aceptar'},
          'action_id': 'accept_lead',
          'action_payload': {'lead_id': 'L-001'},
        },
      });
      expect(r.root!.actionId, 'accept_lead');
      expect(r.root!.actionPayload!['lead_id'], 'L-001');
    });

    test('ignores non-string action_id', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {
          'type': 'Button',
          'props': {'label': 'x'},
          'action_id': 123,
        },
      });
      expect(r.root!.actionId, isNull);
    });
  });

  group('A2UIParser — children/slots edge cases', () {
    test('ignores non-object children with warning', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {
          'type': 'Stack',
          'children': [
            {'type': 'Text', 'props': {'content': 'ok'}},
            'invalid string',
            null,
            42,
          ],
        },
      });
      expect(r.root!.children.length, 1);
      expect(
        r.warnings.where((w) => w.level == A2UIWarningLevel.ignored).length,
        3,
      );
    });

    test('empty children/slots are tolerated', () {
      final r = parser.parse({
        'a2ui_version': '1.0',
        'root': {'type': 'Section', 'children': [], 'slots': {}},
      });
      expect(r.root!.type, 'Section');
      expect(r.root!.children, isEmpty);
      expect(r.root!.slots, isEmpty);
    });
  });
}
