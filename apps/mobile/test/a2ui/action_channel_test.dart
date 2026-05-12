import 'package:el_monstruo_app/core/a2ui/action_channel.dart';
import 'package:el_monstruo_app/core/a2ui/types/a2ui_action.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('BufferedA2UIActionSender — test double', () {
    test('captura cada action enviado en orden', () async {
      final sender = BufferedA2UIActionSender();
      final a1 = A2UIAction(actionId: 'a1', payload: {'k': 1});
      final a2 = A2UIAction(actionId: 'a2', payload: {'k': 2});

      final r1 = await sender.send(a1);
      final r2 = await sender.send(a2);

      expect(r1.ok, isTrue);
      expect(r2.ok, isTrue);
      expect(sender.received, hasLength(2));
      expect(sender.received[0].actionId, 'a1');
      expect(sender.received[1].actionId, 'a2');
    });

    test('shouldFail=true devuelve failure y no captura', () async {
      final sender = BufferedA2UIActionSender(shouldFail: true);
      final r = await sender.send(A2UIAction(actionId: 'x'));
      expect(r.ok, isFalse);
      expect(r.error, 'mock failure');
      expect(sender.received, isEmpty);
    });
  });

  group('dispatcherFromSender — contract', () {
    test('dispatcher es fire-and-forget pero el sender recibe el action',
        () async {
      final sender = BufferedA2UIActionSender();
      final dispatcher = dispatcherFromSender(sender);

      dispatcher(A2UIAction(actionId: 'click', sourceWidget: 'Button'));
      // Ceder al event loop para que la Future interna corra.
      await Future<void>.delayed(Duration.zero);

      expect(sender.received, hasLength(1));
      expect(sender.received.first.actionId, 'click');
      expect(sender.received.first.sourceWidget, 'Button');
    });

    test('onResult callback recibe el resultado del envío', () async {
      final sender = BufferedA2UIActionSender();
      final results = <A2UISendResult>[];
      final dispatcher = dispatcherFromSender(
        sender,
        onResult: (action, result) => results.add(result),
      );

      dispatcher(A2UIAction(actionId: 'ok'));
      await Future<void>.delayed(Duration.zero);

      expect(results, hasLength(1));
      expect(results.first.ok, isTrue);
    });

    test('onResult propaga failure cuando sender falla', () async {
      final sender = BufferedA2UIActionSender(shouldFail: true);
      final results = <A2UISendResult>[];
      final dispatcher = dispatcherFromSender(
        sender,
        onResult: (a, r) => results.add(r),
      );

      dispatcher(A2UIAction(actionId: 'nope'));
      await Future<void>.delayed(Duration.zero);

      expect(results, hasLength(1));
      expect(results.first.ok, isFalse);
      expect(results.first.error, 'mock failure');
    });
  });

  group('WebSocketA2UIActionSender — offline buffering', () {
    test('sin connect bufferiza con bufferOnDisconnect=true', () async {
      final sender = WebSocketA2UIActionSender(
        url: 'ws://localhost:0',
        threadId: 't1',
        bufferOnDisconnect: true,
        maxBuffer: 4,
      );

      final r = await sender.send(A2UIAction(actionId: 'a'));
      expect(r.ok, isFalse);
      expect(r.buffered, isTrue);
    });

    test('respeta maxBuffer y rechaza overflow', () async {
      final sender = WebSocketA2UIActionSender(
        url: 'ws://localhost:0',
        threadId: 't1',
        bufferOnDisconnect: true,
        maxBuffer: 2,
      );

      final r1 = await sender.send(A2UIAction(actionId: 'a'));
      final r2 = await sender.send(A2UIAction(actionId: 'b'));
      final r3 = await sender.send(A2UIAction(actionId: 'c'));

      expect(r1.buffered, isTrue);
      expect(r2.buffered, isTrue);
      expect(r3.ok, isFalse);
      expect(r3.buffered, isFalse);
      expect(r3.error, 'buffer overflow');
    });

    test('bufferOnDisconnect=false devuelve failure directo si offline',
        () async {
      final sender = WebSocketA2UIActionSender(
        url: 'ws://localhost:0',
        threadId: 't1',
        bufferOnDisconnect: false,
      );
      final r = await sender.send(A2UIAction(actionId: 'a'));
      expect(r.ok, isFalse);
      expect(r.buffered, isFalse);
      expect(r.error, 'not connected');
    });

    test('close() previene envíos posteriores', () async {
      final sender = WebSocketA2UIActionSender(
        url: 'ws://localhost:0',
        threadId: 't1',
      );
      await sender.close();
      final r = await sender.send(A2UIAction(actionId: 'a'));
      expect(r.ok, isFalse);
      expect(r.error, 'sender closed');
    });
  });

  group('A2UIAction serialization wire', () {
    test('toJson produce el shape canon firmado', () {
      final a = A2UIAction(
        actionId: 'open_modal',
        payload: {'modal': 'lead_detail', 'id': 42},
        sourceWidget: 'Button',
        timestamp: '2026-05-11T12:00:00.000Z',
      );
      final j = a.toJson();
      expect(j['type'], 'a2ui_action');
      expect(j['action_id'], 'open_modal');
      expect(j['source_widget'], 'Button');
      expect(j['timestamp'], '2026-05-11T12:00:00.000Z');
      expect(j['payload'], {'modal': 'lead_detail', 'id': 42});
    });
  });
}
