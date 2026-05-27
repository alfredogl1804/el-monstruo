/// Tests específicos S5a (HITL approval) + S5b (artifact panel)
/// =============================================================
///
/// Cubre Ítem 6 del plan original del hilo `nXXobvfnqpoWAwEd5truX8`
/// (Manus A — Spec técnico onboarding):
///   - "Tests Flutter para S5a + S5b + flutter build iOS"
///
/// Verifica que:
///   1. Un `tool_call_end` con output JSON `{"hitl_required": true, ...}`
///      genera una `_HitlRequestCard` con botones Aprobar/Rechazar.
///   2. Un `tool_call_end` con marker `HITL_REQUIRED:` en texto plano
///      también genera la card.
///   3. Un `tool_call_end` con output que contenga URLs de PR/issue/deploy
///      genera tarjetas `_ArtifactCard` clickables.
///   4. Una mezcla HITL + artifact en el mismo output genera ambos cards.
///
/// NO toca la red real ni el navegador (los handlers de los botones
/// reciben sus callbacks pero no se invocan en estos tests; basta con
/// verificar que el widget se renderiza con la estructura esperada).
library;

import 'dart:async';

import 'package:el_monstruo_app/core/mensajeros/agui_messenger.dart';
import 'package:el_monstruo_app/features/hilo/hilo_screen.dart';
import 'package:el_monstruo_app/models/embrion_models.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAguiMessenger implements AguiMessenger {
  _FakeAguiMessenger(this.events);
  final List<AguiEvent> events;
  String? lastPrompt;

  @override
  Stream<AguiEvent> runTask(
    String message, {
    String? threadId,
    String? dispatchAgent,
    Map<String, dynamic>? forwardedProps,
  }) async* {
    lastPrompt = message;
    for (final ev in events) {
      await Future<void>.delayed(const Duration(milliseconds: 5));
      yield ev;
    }
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

AguiEvent _event(AguiEventType type, Map<String, dynamic> raw) {
  return AguiEvent(type: type, raw: raw);
}

Widget _wrap({required Widget child, required _FakeAguiMessenger messenger}) {
  return ProviderScope(
    overrides: [
      aguiMessengerProvider.overrideWithValue(messenger),
    ],
    child: MaterialApp(
      home: child,
    ),
  );
}

Future<void> _sendPrompt(WidgetTester tester, String text) async {
  await tester.enterText(find.byType(TextField).first, text);
  await tester.pump();
  await tester.tap(find.byIcon(Icons.arrow_upward_rounded).first);
  for (var i = 0; i < 12; i++) {
    await tester.pump(const Duration(milliseconds: 10));
  }
}

void main() {
  group('S5a — HITL approval card', () {
    testWidgets(
      'tool_call_end con JSON hitl_required:true renderiza la HITL card',
      (tester) async {
        final fake = _FakeAguiMessenger([
          _event(AguiEventType.runStarted, {}),
          _event(AguiEventType.toolCallStart, {'name': 'github_ops'}),
          _event(AguiEventType.toolCallEnd, {
            'name': 'github_ops',
            'result': '{"hitl_required": true, '
                '"action": "create_pr", '
                '"payload": {"branch": "feat/test", "title": "Test PR"}, '
                '"message": "Confirma para crear el PR"}'
          }),
          _event(AguiEventType.runFinished, {}),
        ]);

        await tester.pumpWidget(
          _wrap(child: const HiloScreen(), messenger: fake),
        );
        await tester.pump();
        await _sendPrompt(tester, 'Crea un PR de prueba');

        // La card debe mostrar el mensaje y los dos botones de acción.
        expect(find.textContaining('Confirma'), findsWidgets);
        expect(find.text('Aprobar'), findsOneWidget);
        expect(find.text('Rechazar'), findsOneWidget);
      },
    );

    testWidgets(
      'tool_call_end con marker HITL_REQUIRED en texto plano renderiza la card',
      (tester) async {
        final fake = _FakeAguiMessenger([
          _event(AguiEventType.runStarted, {}),
          _event(AguiEventType.toolCallStart, {'name': 'deploy_ops'}),
          _event(AguiEventType.toolCallEnd, {
            'name': 'deploy_ops',
            'result':
                'Listo el deploy candidato.\nHITL_REQUIRED: confirma despliegue a producción.',
          }),
          _event(AguiEventType.runFinished, {}),
        ]);

        await tester.pumpWidget(
          _wrap(child: const HiloScreen(), messenger: fake),
        );
        await tester.pump();
        await _sendPrompt(tester, 'Despliega a producción');

        expect(find.text('Aprobar'), findsOneWidget);
        expect(find.text('Rechazar'), findsOneWidget);
      },
    );
  });

  group('S5b — Artifact card', () {
    testWidgets(
      'tool_call_end con URL de PR de GitHub renderiza ArtifactCard clickable',
      (tester) async {
        final fake = _FakeAguiMessenger([
          _event(AguiEventType.runStarted, {}),
          _event(AguiEventType.toolCallStart, {'name': 'github_ops'}),
          _event(AguiEventType.toolCallEnd, {
            'name': 'github_ops',
            'result': '{"ok": true, '
                '"url": "https://github.com/alfredogl1804/el-monstruo/pull/1234"}'
          }),
          _event(AguiEventType.runFinished, {}),
        ]);

        await tester.pumpWidget(
          _wrap(child: const HiloScreen(), messenger: fake),
        );
        await tester.pump();
        await _sendPrompt(tester, 'Abre el PR');

        // La card debe mostrar la URL o un label derivado.
        expect(
          find.textContaining('pull/1234'),
          findsWidgets,
          reason: 'la artifact card debe mostrar el path del PR',
        );
      },
    );

    testWidgets(
      'tool_call_end con URL embebida en texto plano (regex fallback) renderiza ArtifactCard',
      (tester) async {
        final fake = _FakeAguiMessenger([
          _event(AguiEventType.runStarted, {}),
          _event(AguiEventType.toolCallStart, {'name': 'deploy_ops'}),
          _event(AguiEventType.toolCallEnd, {
            'name': 'deploy_ops',
            'result':
                'Deploy listo. Revisa el preview en https://el-monstruo.up.railway.app/health para confirmar.',
          }),
          _event(AguiEventType.runFinished, {}),
        ]);

        await tester.pumpWidget(
          _wrap(child: const HiloScreen(), messenger: fake),
        );
        await tester.pump();
        await _sendPrompt(tester, 'Verifica el deploy');

        expect(
          find.textContaining('railway.app'),
          findsWidgets,
          reason: 'la URL del deploy debe quedar visible como artifact',
        );
      },
    );

    testWidgets(
      'mezcla HITL + artifact en el mismo output renderiza ambos cards',
      (tester) async {
        final fake = _FakeAguiMessenger([
          _event(AguiEventType.runStarted, {}),
          _event(AguiEventType.toolCallStart, {'name': 'github_ops'}),
          _event(AguiEventType.toolCallEnd, {
            'name': 'github_ops',
            'result': '{"hitl_required": true, '
                '"action": "merge_pr", '
                '"message": "Confirma merge", '
                '"url": "https://github.com/alfredogl1804/el-monstruo/pull/9999"}'
          }),
          _event(AguiEventType.runFinished, {}),
        ]);

        await tester.pumpWidget(
          _wrap(child: const HiloScreen(), messenger: fake),
        );
        await tester.pump();
        await _sendPrompt(tester, 'Mergea el PR 9999');

        // Ambos cards deben aparecer en el mismo run.
        expect(find.text('Aprobar'), findsOneWidget);
        expect(find.text('Rechazar'), findsOneWidget);
        expect(find.textContaining('pull/9999'), findsWidgets);
      },
    );
  });
}
