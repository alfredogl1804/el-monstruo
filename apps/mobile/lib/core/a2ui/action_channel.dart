/// A2UI Action Channel — transporte de acciones de UI hacia el kernel.
///
/// Diseño:
///   * `A2UIActionSender`: interfaz abstracta — un solo método `send(action)`.
///   * `WebSocketA2UIActionSender`: adapter canónico que envía la acción por
///     WebSocket hacia el endpoint `WS /v1/chat/stream` del kernel (mismo
///     wire que el chat).
///   * `BufferedA2UIActionSender`: in-memory test double + buffering local
///     cuando la conexión está caída (reintento opcional).
///   * `dispatcherFromSender(sender)`: helper para construir el callback
///     `A2UIActionDispatcher` que el renderer espera.
///
/// Protocolo canon firmado:
/// `{"type":"a2ui_action","action_id":"...","payload":{...},"source_widget":"...","timestamp":"..."}`
///
/// El kernel responde con un nuevo mensaje (texto o A2UI) que llega vía la
/// misma stream WS — no tratamos respuesta aquí, eso es responsabilidad del
/// chat existente.
library;

import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import 'types/a2ui_action.dart';

/// Resultado de un intento de envío.
class A2UISendResult {
  final bool ok;
  final String? error;
  final bool buffered;

  const A2UISendResult({required this.ok, this.error, this.buffered = false});

  factory A2UISendResult.success() => const A2UISendResult(ok: true);
  factory A2UISendResult.failure(String reason) =>
      A2UISendResult(ok: false, error: reason);
  factory A2UISendResult.queued() =>
      const A2UISendResult(ok: false, buffered: true);
}

/// Interfaz abstracta que cualquier transporte A2UI debe implementar.
abstract class A2UIActionSender {
  Future<A2UISendResult> send(A2UIAction action);
  Future<void> close();
}

/// Adapter canónico WebSocket. Abre y mantiene una conexión persistente.
///
/// Uso típico desde el chat existente:
///
/// ```dart
/// final sender = WebSocketA2UIActionSender(
///   url: 'wss://kernel.../v1/chat/stream',
///   threadId: currentThreadId,
/// );
/// await sender.connect();
/// final dispatcher = dispatcherFromSender(sender);
/// // ...pass dispatcher to A2UIRenderer.
/// ```
class WebSocketA2UIActionSender implements A2UIActionSender {
  WebSocketA2UIActionSender({
    required this.url,
    required this.threadId,
    this.headers,
    this.bufferOnDisconnect = true,
    this.maxBuffer = 64,
  });

  final String url;
  final String threadId;
  final Map<String, dynamic>? headers;
  final bool bufferOnDisconnect;
  final int maxBuffer;

  WebSocketChannel? _channel;
  final _buffer = <A2UIAction>[];
  bool _closed = false;

  /// Abre la conexión. Idempotente.
  Future<void> connect() async {
    if (_channel != null || _closed) return;
    _channel = WebSocketChannel.connect(Uri.parse(url));
    // Flush buffer cuando la conexión queda viva.
    await Future<void>.delayed(const Duration(milliseconds: 50));
    await _flushBuffer();
  }

  Future<void> _flushBuffer() async {
    if (_channel == null) return;
    final pending = List<A2UIAction>.from(_buffer);
    _buffer.clear();
    for (final a in pending) {
      _send(a);
    }
  }

  void _send(A2UIAction action) {
    final payload = action.toJson();
    payload['thread_id'] = threadId;
    _channel!.sink.add(jsonEncode(payload));
  }

  @override
  Future<A2UISendResult> send(A2UIAction action) async {
    if (_closed) {
      return A2UISendResult.failure('sender closed');
    }
    if (_channel == null) {
      if (bufferOnDisconnect) {
        if (_buffer.length >= maxBuffer) {
          return A2UISendResult.failure('buffer overflow');
        }
        _buffer.add(action);
        return A2UISendResult.queued();
      }
      return A2UISendResult.failure('not connected');
    }
    try {
      _send(action);
      return A2UISendResult.success();
    } catch (e) {
      return A2UISendResult.failure(e.toString());
    }
  }

  @override
  Future<void> close() async {
    _closed = true;
    await _channel?.sink.close();
    _channel = null;
  }
}

/// Test double que mantiene en memoria todos los actions enviados.
class BufferedA2UIActionSender implements A2UIActionSender {
  BufferedA2UIActionSender({this.shouldFail = false});

  final bool shouldFail;
  final List<A2UIAction> received = [];

  @override
  Future<A2UISendResult> send(A2UIAction action) async {
    if (shouldFail) return A2UISendResult.failure('mock failure');
    received.add(action);
    return A2UISendResult.success();
  }

  @override
  Future<void> close() async {}
}

/// Construye un dispatcher síncrono que la jerarquía de widgets espera.
A2UIActionDispatcher dispatcherFromSender(
  A2UIActionSender sender, {
  void Function(A2UIAction action, A2UISendResult result)? onResult,
}) {
  return (A2UIAction action) {
    // Fire-and-forget: la UI no espera el roundtrip, el kernel responderá vía
    // streaming en su propio canal.
    unawaited(
      sender.send(action).then((res) {
        onResult?.call(action, res);
      }),
    );
  };
}
