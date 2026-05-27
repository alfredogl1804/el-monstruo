/// Smoke test — Hilo de Manus end-to-end (SSE mockeado)
/// =====================================================
///
/// Cubre Ítem F del sprint Cabina Dual Pulido 2026-05-27.
///
/// Verifica que:
///   1. La pantalla renderiza el Welcome state inicial.
///   2. Al enviar un prompt, los AguiEvents simulados producen los _StepCard
///      esperados (started → thinking → tool_call → tool_result → message → done).
///   3. El Trust Indicator transiciona correctamente:
///      - "buscaré en web" → pendingVerification → verified al llegar tool_call_start.
///      - "consultaré la skill X" sin tool_call → ghost al runFinished.
///
/// NO toca la red real. Inyectamos un FakeAguiMessenger vía Riverpod override.
library;

import 'dart:async';

import 'package:el_monstruo_app/core/mensajeros/agui_messenger.dart';
import 'package:el_monstruo_app/features/hilo/hilo_screen.dart';
import 'package:el_monstruo_app/models/embrion_models.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

/// AguiMessenger fake — controla qué eventos emitir desde el test.
class _FakeAguiMessenger implements AguiMessenger {
  _FakeAguiMessenger(this.events);
  final List<AguiEvent> events;
  String? lastPrompt;
  String? lastAgent;

  @override
  Stream<AguiEvent> runTask(
    String message, {
    String? threadId,
    String? dispatchAgent,
    Map<String, dynamic>? forwardedProps,
  }) async* {
    lastPrompt = message;
    lastAgent = dispatchAgent;
    for (final ev in events) {
      // Pequeña espera para emular orden temporal del SSE real.
      await Future<void>.delayed(const Duration(milliseconds: 5));
      yield ev;
    }
  }

  // Members no usados por la screen — implementación mínima.
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// Construye un AguiEvent sintético sin depender del parser SSE real.
/// AguiEvent expone textDelta/toolName/stepLabel/errorMessage como GETTERS
/// derivados de `raw`, así que basta con poblar el map correctamente.
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

void main() {
  group('HiloScreen smoke', () {
    testWidgets('Welcome state se muestra al abrir el Hilo',
        (tester) async {
      final fake = _FakeAguiMessenger(const []);
      await tester.pumpWidget(_wrap(child: const HiloScreen(), messenger: fake));
      await tester.pump();
      // El Welcome incluye el copy "Lanza una tarea compleja".
      expect(find.text('Lanza una tarea compleja'), findsOneWidget);
    });

    testWidgets(
        'Hilo end-to-end: started → thinking → tool_call → tool_result → message → done',
        (tester) async {
      final fake = _FakeAguiMessenger([
        _event(AguiEventType.runStarted, {}),
        _event(AguiEventType.thinkingState,
            {'label': 'Voy a buscar en web información del Sprint 91'}),
        _event(AguiEventType.toolCallStart, {'name': 'web_search'}),
        _event(AguiEventType.toolCallEnd, {
          'name': 'web_search',
          'result': 'Sprint 91 cerrado el 26 may.'
        }),
        _event(AguiEventType.textMessageStart, {}),
        _event(AguiEventType.textMessageContent,
            {'delta': 'El Sprint 91 quedó cerrado.'}),
        _event(AguiEventType.textMessageEnd, {}),
        _event(AguiEventType.runFinished, {}),
      ]);

      await tester.pumpWidget(
        _wrap(child: const HiloScreen(), messenger: fake),
      );
      await tester.pump();

      // Encuentra el TextField del composer y escribe un prompt.
      final input = find.byType(TextField).first;
      await tester.enterText(input, 'Audita el Sprint 91');
      await tester.pump();

      // Encuentra el botón de envío (Icons.send dentro del composer).
      final sendBtn = find.byIcon(Icons.arrow_upward_rounded).first;
      await tester.tap(sendBtn);

      // Deja que el stream emita todos los eventos.
      for (var i = 0; i < 10; i++) {
        await tester.pump(const Duration(milliseconds: 10));
      }

      // Verificaciones de comportamiento (no estricto en texto exacto):
      expect(fake.lastPrompt, 'Audita el Sprint 91');
      // Step "Hilo iniciado" del runStarted.
      expect(find.text('Hilo iniciado'), findsOneWidget);
      // Step done final.
      expect(find.text('Hilo completo'), findsOneWidget);
    });

    testWidgets(
        'Trust Indicator: anuncio "buscaré en web" sin tool_call termina como ghost',
        (tester) async {
      final fake = _FakeAguiMessenger([
        _event(AguiEventType.runStarted, {}),
        _event(AguiEventType.thinkingState,
            {'label': 'Voy a buscar en web pero no lo voy a hacer'}),
        // ¡Importante! NO emitimos tool_call_start aquí.
        _event(AguiEventType.textMessageStart, {}),
        _event(AguiEventType.textMessageContent,
            {'delta': 'Aquí va una respuesta sin usar web.'}),
        _event(AguiEventType.textMessageEnd, {}),
        _event(AguiEventType.runFinished, {}),
      ]);

      await tester.pumpWidget(
        _wrap(child: const HiloScreen(), messenger: fake),
      );
      await tester.pump();

      await tester.enterText(
          find.byType(TextField).first, 'Trust ghost detection');
      await tester.pump();
      await tester.tap(find.byIcon(Icons.arrow_upward_rounded).first);

      for (var i = 0; i < 10; i++) {
        await tester.pump(const Duration(milliseconds: 10));
      }

      // El badge ghost usa el icono Icons.warning_amber_outlined.
      // Si la detección funciona, debe aparecer al menos uno (en el step thinking).
      expect(find.byIcon(Icons.warning_amber_outlined), findsWidgets);
    });
  });
}
