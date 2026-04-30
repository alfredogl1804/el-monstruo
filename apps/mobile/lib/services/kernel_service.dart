import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../core/config.dart';
import '../models/chat_message.dart';
import '../models/kernel_health.dart';
import '../models/tool_event.dart';

final _log = Logger('KernelService');

/// Manages all communication with El Monstruo via the AG-UI Gateway.
///
/// Architecture:
///   [This Service] → [Gateway (REST + WS)] → [Kernel /v1/*]
///
/// REST: Simple request/response for commands and queries.
/// WebSocket: Real-time streaming for chat (AG-UI events).
class KernelService {
  KernelService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: AppConfig.gatewayBaseUrl,
              connectTimeout: AppConfig.connectTimeout,
              receiveTimeout: AppConfig.receiveTimeout,
              headers: {
                'Content-Type': 'application/json',
              },
            ));

  final Dio _dio;
  WebSocketChannel? _wsChannel;
  Timer? _heartbeatTimer;
  int _reconnectAttempts = 0;

  // ─── Stream Controllers ───
  final _messageController = StreamController<ChatMessage>.broadcast();
  final _toolEventController = StreamController<ToolEvent>.broadcast();
  final _connectionStateController = StreamController<KernelConnectionState>.broadcast();
  final _thinkingStateController = StreamController<Map<String, dynamic>>.broadcast();
  final _stepController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<ChatMessage> get messageStream => _messageController.stream;
  Stream<ToolEvent> get toolEventStream => _toolEventController.stream;
  Stream<KernelConnectionState> get connectionStream => _connectionStateController.stream;
  Stream<Map<String, dynamic>> get thinkingStream => _thinkingStateController.stream;
  Stream<Map<String, dynamic>> get stepStream => _stepController.stream;

  // ─── Health Check ───
  Future<KernelHealth> checkHealth() async {
    try {
      final response = await _dio.get(AppConfig.healthEndpoint);
      return KernelHealth.fromJson(response.data);
    } catch (e) {
      _log.severe('Health check failed', e);
      return KernelHealth.offline();
    }
  }

  // ─── Send Message (REST, non-streaming) ───
  Future<void> sendMessage(String message, {String? threadId}) async {
    try {
      final response = await _dio.post(
        AppConfig.chatEndpoint,
        data: {
          'message': message,
          'thread_id': threadId,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        _messageController.add(ChatMessage.fromKernelResponse(data));
      }
    } catch (e) {
      _log.severe('Failed to send message', e);
      rethrow;
    }
  }

  // ─── WebSocket Streaming Connection ───
  Future<void> connectStreaming({String? threadId}) async {
    _connectionStateController.add(KernelConnectionState.connecting);

    try {
      final uri = Uri.parse(AppConfig.gatewayWsUrl);
      _wsChannel = WebSocketChannel.connect(uri);
      await _wsChannel!.ready;

      _reconnectAttempts = 0;
      _connectionStateController.add(KernelConnectionState.connected);
      _startHeartbeat();

      _wsChannel!.stream.listen(
        (data) => _handleWsMessage(data),
        onError: (error) {
          _log.warning('WebSocket error', error);
          _connectionStateController.add(KernelConnectionState.error);
          _attemptReconnect(threadId: threadId);
        },
        onDone: () {
          _log.info('WebSocket closed');
          _connectionStateController.add(KernelConnectionState.disconnected);
          _attemptReconnect(threadId: threadId);
        },
      );
    } catch (e) {
      _log.severe('WebSocket connection failed', e);
      _connectionStateController.add(KernelConnectionState.error);
      _attemptReconnect(threadId: threadId);
    }
  }

  void _handleWsMessage(dynamic rawData) {
    try {
      final data = jsonDecode(rawData as String) as Map<String, dynamic>;
      final eventType = data['type'] as String?;

      switch (eventType) {
        // Text streaming
        case 'text_chunk':
          _messageController.add(ChatMessage.streamChunk(data));
          break;
        case 'message_start':
          // New message starting
          break;
        case 'message_end':
          _messageController.add(ChatMessage.streamEnd(data));
          break;

        // Tool calls
        case 'tool_start':
        case 'tool_args':
        case 'tool_end':
          _toolEventController.add(ToolEvent.fromJson(data));
          break;

        // Thinking/routing state from kernel
        case 'thinking_state':
          _thinkingStateController.add(data);
          break;

        // Sprint 43: Structured thinking step events
        case 'step':
          _stepController.add(data);
          break;

        // Run lifecycle (not tool events)
        case 'run_start':
        case 'run_end':
          break;

        // Errors
        case 'error':
          _toolEventController.add(ToolEvent.fromJson({
            'type': 'run_error',
            'message': data['message'] ?? 'Unknown error',
          }));
          break;

        // GenUI component
        case 'genui_component':
          _messageController.add(ChatMessage.genuiComponent(data));
          break;

        // Heartbeat
        case 'heartbeat':
        case 'pong':
          break;

        default:
          _log.warning('Unknown WS event type: $eventType');
      }
    } catch (e) {
      _log.warning('Failed to parse WS message', e);
    }
  }

  // ─── Send via WebSocket ───
  void sendWsMessage(String message, {String? threadId}) {
    if (_wsChannel == null) {
      _log.warning('WebSocket not connected, cannot send');
      return;
    }

    _wsChannel!.sink.add(jsonEncode({
      'type': 'message',
      'content': message,
      'thread_id': threadId,
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    }));
  }

  // ─── Heartbeat ───
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(
      const Duration(seconds: 25),
      (_) {
        if (_wsChannel != null) {
          _wsChannel!.sink.add(jsonEncode({'type': 'ping'}));
        }
      },
    );
  }

  // ─── Reconnection ───
  void _attemptReconnect({String? threadId}) {
    _heartbeatTimer?.cancel();

    if (_reconnectAttempts >= AppConfig.wsMaxReconnectAttempts) {
      _log.severe('Max reconnect attempts reached');
      _connectionStateController.add(KernelConnectionState.failed);
      return;
    }

    _reconnectAttempts++;
    final delay = AppConfig.wsReconnectDelay * _reconnectAttempts;
    _log.info('Reconnecting in ${delay.inSeconds}s (attempt $_reconnectAttempts)');

    _connectionStateController.add(KernelConnectionState.reconnecting);

    Future.delayed(delay, () {
      connectStreaming(threadId: threadId);
    });
  }

  // ─── Memory Stats ───
  Future<Map<String, dynamic>> getMemoryStats() async {
    try {
      final response = await _dio.get(AppConfig.memoryStatsEndpoint);
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get memory stats', e);
      return {};
    }
  }

  // ─── Memory Search ───
  Future<List<dynamic>> searchMemory(String query) async {
    try {
      final response = await _dio.post(
        AppConfig.memorySearchEndpoint,
        data: {'query': query, 'limit': 20},
      );
      return response.data['results'] as List<dynamic>? ?? [];
    } catch (e) {
      _log.warning('Failed to search memory', e);
      return [];
    }
  }

  // ─── Tools List ───
  Future<List<Map<String, dynamic>>> getAvailableTools() async {
    try {
      final response = await _dio.get(AppConfig.toolsEndpoint);
      return List<Map<String, dynamic>>.from(response.data['tools'] ?? []);
    } catch (e) {
      _log.warning('Failed to get tools', e);
      return [];
    }
  }

  // ─── Embrion Status ───
  Future<Map<String, dynamic>> getEmbrionStatus() async {
    try {
      final response = await _dio.get(AppConfig.embrionEndpoint);
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get embrion status', e);
      return {};
    }
  }

  // ─── FinOps ───
  Future<Map<String, dynamic>> getFinOps({String period = 'today'}) async {
    try {
      final response = await _dio.get(
        AppConfig.finopsEndpoint,
        queryParameters: {'period': period},
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get finops data', e);
      return {};
    }
  }

  // ─── MOC (Motor de Orquestación Central) ───
  Future<Map<String, dynamic>> getMocStatus() async {
    try {
      final response = await _dio.get(AppConfig.mocEndpoint);
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get MOC status', e);
      return {};
    }
  }

  Future<Map<String, dynamic>> triggerMocSynthesis() async {
    try {
      final response = await _dio.post('${AppConfig.mocEndpoint}/sintetizar');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to trigger MOC synthesis', e);
      return {'error': e.toString()};
    }
  }

  // ─── AG-UI Info ───
  Future<Map<String, dynamic>> getAGUIInfo() async {
    try {
      final response = await _dio.get(AppConfig.aguiInfoEndpoint);
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get AG-UI info', e);
      return {};
    }
  }

  // ─── Push Token Registration ───
  Future<void> registerPushToken(String token, String platform, {String? deviceId}) async {
    try {
      await _dio.post(
        AppConfig.pushRegisterEndpoint,
        data: {
          'token': token,
          'platform': platform,
          'device_id': deviceId,
        },
      );
    } catch (e) {
      _log.warning('Failed to register push token', e);
    }
  }

  // ─── Cleanup ───
  void dispose() {
    _heartbeatTimer?.cancel();
    _wsChannel?.sink.close();
    _messageController.close();
    _toolEventController.close();
    _connectionStateController.close();
    _thinkingStateController.close();
    _stepController.close();
  }
}

enum KernelConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
  failed,
}

// ─── Riverpod Providers ───
final kernelServiceProvider = Provider<KernelService>((ref) {
  final service = KernelService();
  ref.onDispose(() => service.dispose());
  return service;
});

final kernelHealthProvider = FutureProvider<KernelHealth>((ref) async {
  final service = ref.watch(kernelServiceProvider);
  return service.checkHealth();
});

final connectionStateProvider = StreamProvider<KernelConnectionState>((ref) {
  final service = ref.watch(kernelServiceProvider);
  return service.connectionStream;
});
