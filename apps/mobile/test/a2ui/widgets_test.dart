import 'package:el_monstruo_app/core/a2ui/parser.dart';
import 'package:el_monstruo_app/core/a2ui/renderer.dart';
import 'package:el_monstruo_app/core/a2ui/types/a2ui_action.dart';
import 'package:el_monstruo_app/core/a2ui/types/a2ui_node.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

Widget _wrap(A2UINode root, {A2UIActionDispatcher? dispatcher}) {
  return MaterialApp(
    home: Scaffold(
      body: SingleChildScrollView(
        child: A2UIRenderer(root: root, dispatcher: dispatcher),
      ),
    ),
  );
}

A2UINode _node(
  String type, {
  Map<String, dynamic> props = const {},
  List<A2UINode> children = const [],
  Map<String, List<A2UINode>> slots = const {},
  String? actionId,
}) =>
    A2UINode(
      type: type,
      props: props,
      children: children,
      slots: slots,
      actionId: actionId,
    );

void main() {
  group('A2UI 16 widgets whitelist', () {
    testWidgets('Stack renderiza hijos en columna', (tester) async {
      final root = _node('Stack', children: [
        _node('Text', props: {'content': 'A'}),
        _node('Text', props: {'content': 'B'}),
      ]);
      await tester.pumpWidget(_wrap(root));
      expect(find.text('A'), findsOneWidget);
      expect(find.text('B'), findsOneWidget);
    });

    testWidgets('Card con slots header/footer muestra los 3', (tester) async {
      final root = _node('Card', slots: {
        'header': [_node('Text', props: {'content': 'Header'})],
        'footer': [_node('Text', props: {'content': 'Footer'})],
      }, children: [
        _node('Text', props: {'content': 'Body'}),
      ]);
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Header'), findsOneWidget);
      expect(find.text('Body'), findsOneWidget);
      expect(find.text('Footer'), findsOneWidget);
    });

    testWidgets('Section con title + subtitle', (tester) async {
      final root = _node('Section', props: {
        'title': 'Resultados',
        'subtitle': 'Top 3',
      }, children: [
        _node('Text', props: {'content': 'item'})
      ]);
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Resultados'), findsOneWidget);
      expect(find.text('Top 3'), findsOneWidget);
      expect(find.text('item'), findsOneWidget);
    });

    testWidgets('Text muestra content', (tester) async {
      final root = _node('Text', props: {'content': 'hola monstruo'});
      await tester.pumpWidget(_wrap(root));
      expect(find.text('hola monstruo'), findsOneWidget);
    });

    testWidgets('Markdown renderiza texto plano', (tester) async {
      final root = _node('Markdown', props: {'content': 'plain markdown'});
      await tester.pumpWidget(_wrap(root));
      expect(find.textContaining('plain markdown'), findsOneWidget);
    });

    testWidgets('Image construye sin crash con src + alt', (tester) async {
      final root = _node('Image', props: {
        'src': 'https://example.com/x.png',
        'alt': 'una imagen',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.byType(Image), findsOneWidget);
    });

    testWidgets('Link dispara action_id en tap si tiene href',
        (tester) async {
      final captured = <String>[];
      final root = _node('Link',
          props: {
            'label': 'Abrir lead',
            'href': 'https://app.monstruo.local/leads/1'
          },
          actionId: 'open_lead');
      await tester.pumpWidget(
        _wrap(root, dispatcher: (a) => captured.add(a.actionId)),
      );
      await tester.tap(find.text('Abrir lead'));
      expect(captured, ['open_lead']);
    });

    testWidgets('Code muestra snippet', (tester) async {
      final root = _node('Code', props: {
        'content': 'print("hi")',
        'language': 'python',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.textContaining('print("hi")'), findsOneWidget);
    });

    testWidgets('Divider renderiza', (tester) async {
      final root = _node('Stack', children: [
        _node('Text', props: {'content': 'antes'}),
        _node('Divider'),
        _node('Text', props: {'content': 'después'}),
      ]);
      await tester.pumpWidget(_wrap(root));
      expect(find.byType(Divider), findsWidgets);
    });

    testWidgets('Button dispara action en tap', (tester) async {
      String? actionId;
      final root = _node('Button',
          props: {'label': 'Confirmar', 'variant': 'primary'},
          actionId: 'confirm');
      await tester.pumpWidget(
        _wrap(root, dispatcher: (a) => actionId = a.actionId),
      );
      await tester.tap(find.text('Confirmar'));
      expect(actionId, 'confirm');
    });

    testWidgets('ButtonGroup acepta múltiples buttons', (tester) async {
      final captured = <String>[];
      final root = _node('ButtonGroup', children: [
        _node('Button', props: {'label': 'A'}, actionId: 'a'),
        _node('Button', props: {'label': 'B'}, actionId: 'b'),
      ]);
      await tester.pumpWidget(
        _wrap(root, dispatcher: (a) => captured.add(a.actionId)),
      );
      await tester.tap(find.text('A'));
      await tester.tap(find.text('B'));
      expect(captured, containsAll(['a', 'b']));
    });

    testWidgets('KeyValueList muestra pares clave/valor', (tester) async {
      final root = _node('KeyValueList', props: {
        'items': [
          {'key': 'CEO', 'value': 'Alfredo'},
          {'key': 'Sede', 'value': 'Mérida'},
        ]
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('CEO'), findsOneWidget);
      expect(find.text('Alfredo'), findsOneWidget);
      expect(find.text('Sede'), findsOneWidget);
      expect(find.text('Mérida'), findsOneWidget);
    });

    testWidgets('Table renderiza headers y rows', (tester) async {
      final root = _node('Table', props: {
        'headers': ['Nombre', 'Score'],
        'rows': [
          ['Acme', 92],
          ['Globex', 81],
        ],
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Nombre'), findsOneWidget);
      expect(find.text('Score'), findsOneWidget);
      expect(find.text('Acme'), findsOneWidget);
      expect(find.text('92'), findsOneWidget);
    });

    testWidgets('Badge muestra label con variant', (tester) async {
      final root = _node('Badge', props: {
        'label': 'CALIENTE',
        'variant': 'danger',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('CALIENTE'), findsOneWidget);
    });

    testWidgets('Progress determinado con label', (tester) async {
      final root = _node('Progress', props: {
        'value': 0.42,
        'label': 'Procesando',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Procesando'), findsOneWidget);
    });

    testWidgets('Stepper muestra steps con title + status', (tester) async {
      final root = _node('Stepper', props: {
        'steps': [
          {'title': 'Inicio', 'status': 'done'},
          {'title': 'Análisis', 'status': 'active'},
          {'title': 'Decisión', 'status': 'pending'},
        ]
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Inicio'), findsOneWidget);
      expect(find.text('Análisis'), findsOneWidget);
      expect(find.text('Decisión'), findsOneWidget);
    });
  });

  group('A2UI 3 especializados Monstruo', () {
    testWidgets('EmpresaResultCard nombre + sector + score', (tester) async {
      final root = _node('EmpresaResultCard', props: {
        'nombre': 'TechCorp',
        'sector': 'SaaS',
        'score': 89,
        'ubicacion': 'CDMX',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('TechCorp'), findsOneWidget);
      expect(find.text('SaaS'), findsOneWidget);
      expect(find.text('89'), findsOneWidget);
    });

    testWidgets('LeadCard nombre + etapa caliente + score', (tester) async {
      final root = _node('LeadCard', props: {
        'nombre': 'Juan Pérez',
        'empresa': 'Globex',
        'etapa': 'caliente',
        'score': 91,
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Juan Pérez'), findsOneWidget);
      expect(find.text('Globex'), findsOneWidget);
      // Etapa 'caliente' se muestra como label 'Caliente' en Badge.
      expect(find.text('Caliente'), findsOneWidget);
      // Score aparece como meta junto a icon fire.
      expect(find.text('91'), findsOneWidget);
    });

    testWidgets('ContenidoCard titulo + plataforma uppercase + autor',
        (tester) async {
      final root = _node('ContenidoCard', props: {
        'titulo': 'Cómo funciona A2UI',
        'plataforma': 'LinkedIn',
        'autor': 'Cowork T2',
        'resumen': 'Explicación del protocolo.',
      });
      await tester.pumpWidget(_wrap(root));
      expect(find.text('Cómo funciona A2UI'), findsOneWidget);
      // Plataforma se renderiza en mayúsculas (Brand DNA tag style).
      expect(find.text('LINKEDIN'), findsOneWidget);
      // Autor + fecha se combinan con ' · ', autor sin fecha = solo autor.
      expect(find.textContaining('Cowork T2'), findsOneWidget);
    });
  });

  group('Parser + renderer end-to-end', () {
    testWidgets('JSON A2UI canon completo renderiza ok', (tester) async {
      const fixture = '''
{
  "a2ui_version": "1.0",
  "root": {
    "type": "Section",
    "props": {"title": "Resumen", "subtitle": "3 resultados"},
    "children": [
      {
        "type": "EmpresaResultCard",
        "props": {"nombre": "Acme", "score": 92, "sector": "Retail"}
      },
      {
        "type": "ButtonGroup",
        "children": [
          {"type": "Button", "props": {"label": "Ver más"}, "action_id": "open"}
        ]
      }
    ]
  }
}
''';
      final result = const A2UIParser().parseJson(fixture);
      expect(result.root, isNotNull);
      await tester.pumpWidget(_wrap(result.root!));
      expect(find.text('Resumen'), findsOneWidget);
      expect(find.text('Acme'), findsOneWidget);
      expect(find.text('Ver más'), findsOneWidget);
    });

    testWidgets('Tipo no whitelist cae en Markdown fallback con warning',
        (tester) async {
      const fixture = '''
{
  "a2ui_version": "1.0",
  "root": {
    "type": "EvilWidget",
    "props": {"content": "malicious payload"}
  }
}
''';
      final result = const A2UIParser().parseJson(fixture);
      expect(result.root, isNotNull);
      expect(result.root!.type, 'Markdown');
      expect(result.root!.originalType, 'EvilWidget');
      expect(result.hasFallback, isTrue);
      await tester.pumpWidget(_wrap(result.root!));
      // El parser inyecta blockquote + tipo desconocido. Confirmar que
      // renderiza markdown con el aviso textual.
      expect(find.textContaining('EvilWidget'), findsOneWidget);
    });
  });
}
