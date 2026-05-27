/// AguiMessenger — Sprint SPR-MOBILE-HILO-AGUI-001.
///
/// Cliente streaming SSE para el "Hilo de Manus": tareas complejas
/// end-to-end con visualización en vivo de cada paso (thinking → tool_call
/// → tool_result → message → done).
///
/// Implementación: usa `package:http` con `http.Client.send()` en modo
/// stream y parsea SSE manualmente (Dio no maneja SSE nativo bien en
/// Flutter móvil). El parser respeta el formato canónico:
///
///     data: {"type": "TEXT_MESSAGE_CONTENT", "delta": "..."}\n\n
///     data: {"type": "TOOL_CALL_START", "name": "..."}\n\n
///     : heartbeat\n\n
///
/// Cada evento se emite como `AguiEvent` por el Stream que devuelve
/// `runTask()`. La cancelación del Stream cierra la conexión SSE.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:logging/logging.dart';
import 'package:uuid/uuid.dart';

import '../config.dart';
import '../../models/embrion_models.dart';

final _log = Logger('AguiMessenger');
const _uuid = Uuid();

class AguiMessenger {
  AguiMessenger({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  /// Lanza una tarea AG-UI y emite eventos en tiempo real.
  ///
  /// [message] es la instrucción en lenguaje natural.
  /// [threadId] permite continuar un hilo previo; si es null se crea uno nuevo.
  /// [forwardedProps] permite pasar dispatch_agent y otros hints al kernel.
  Stream<AguiEvent> runTask(
    String message, {
    String? threadId,
    String? dispatchAgent,
    Map<String, dynamic>? forwardedProps,
  }) async* {
    final url = Uri.parse(
      '${AppConfig.gatewayBaseUrl}${AppConfig.aguiRunEndpoint}',
    );

    final body = <String, dynamic>{
      'thread_id': threadId ?? _uuid.v4(),
      'run_id': _uuid.v4(),
      'messages': [
        {'role': 'user', 'content': message}
      ],
      'tools': const [],
      'context': const [],
      'forwarded_props': {
        if (dispatchAgent != null) 'dispatch_agent': dispatchAgent,
        ...?forwardedProps,
      },
    };

    final request = http.Request('POST', url)
      ..headers['Content-Type'] = 'application/json'
      ..headers['Accept'] = 'text/event-stream'
      ..body = jsonEncode(body);

    _log.info('AG-UI run → $url (agent=$dispatchAgent)');

    try {
      final response = await _client.send(request).timeout(
            const Duration(seconds: 30),
            onTimeout: () => throw TimeoutException(
              'gateway connect timeout (30s)',
            ),
          );

      if (response.statusCode != 200) {
        final body = await response.stream.bytesToString();
        _log.warning('AG-UI gateway returned ${response.statusCode}: $body');
        yield AguiEvent(
          type: AguiEventType.runError,
          raw: {
            'type': 'RUN_ERROR',
            'error': 'gateway returned ${response.statusCode}',
            'detail': body,
          },
        );
        return;
      }

      // Buffer para acumular bytes parciales antes del separador SSE (\n\n).
      final buffer = StringBuffer();

      await for (final chunk in response.stream
          .transform(utf8.decoder)
          .timeout(const Duration(seconds: 180))) {
        buffer.write(chunk);
        var bufStr = buffer.toString();

        // Procesar todos los eventos completos en el buffer.
        while (true) {
          final idx = bufStr.indexOf('\n\n');
          if (idx < 0) break;
          final eventBlock = bufStr.substring(0, idx);
          bufStr = bufStr.substring(idx + 2);

          final parsed = _parseSseBlock(eventBlock);
          if (parsed != null) {
            yield parsed;
            if (parsed.type == AguiEventType.runFinished ||
                parsed.type == AguiEventType.runError) {
              buffer
                ..clear()
                ..write(bufStr);
              return;
            }
          }
        }

        buffer
          ..clear()
          ..write(bufStr);
      }

      // Stream cerrado sin RUN_FINISHED — emitir done sintético.
      yield const AguiEvent(
        type: AguiEventType.runFinished,
        raw: {'type': 'RUN_FINISHED', 'reason': 'stream_closed'},
      );
    } catch (e, st) {
      _log.severe('AG-UI stream failed', e, st);
      yield AguiEvent(
        type: AguiEventType.runError,
        raw: {'type': 'RUN_ERROR', 'error': e.toString()},
      );
    }
  }

  /// Cierra el cliente HTTP. Llamar en dispose si se mantiene como singleton.
  void close() {
    try {
      _client.close();
    } catch (_) {}
  }

  /// Parsea un bloque SSE crudo. Maneja:
  ///   data: {...json...}
  ///   : heartbeat   ← comentario, ignorar
  ///   event: name
  static AguiEvent? _parseSseBlock(String block) {
    final lines = const LineSplitter().convert(block);
    final dataLines = <String>[];
    var isHeartbeat = false;

    for (final raw in lines) {
      final line = raw.trim();
      if (line.isEmpty) continue;
      if (line.startsWith(':')) {
        // SSE comment — heartbeat del gateway.
        isHeartbeat = true;
        continue;
      }
      if (line.startsWith('data:')) {
        dataLines.add(line.substring(5).trim());
      }
    }

    if (dataLines.isEmpty) {
      if (isHeartbeat) {
        return const AguiEvent(
          type: AguiEventType.heartbeat,
          raw: {'type': 'HEARTBEAT'},
        );
      }
      return null;
    }

    final dataStr = dataLines.join('\n');
    try {
      final parsed = jsonDecode(dataStr);
      if (parsed is Map<String, dynamic>) {
        return AguiEvent.fromJson(parsed);
      }
      return AguiEvent(
        type: AguiEventType.unknown,
        raw: {'type': 'UNKNOWN', 'raw': dataStr},
      );
    } catch (_) {
      return AguiEvent(
        type: AguiEventType.unknown,
        raw: {'type': 'UNKNOWN', 'raw': dataStr},
      );
    }
  }
}

final aguiMessengerProvider = Provider<AguiMessenger>((ref) {
  final messenger = AguiMessenger();
  ref.onDispose(messenger.close);
  return messenger;
});
