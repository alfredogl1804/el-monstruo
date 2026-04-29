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

/// Manages all communication with El Monstruo's kernel on Railway.
/// Supports both REST (for commands) and WebSocket (for streaming).
class KernelService {
  KernelService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: AppConfig.kernelBaseUrl,
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
  final _connectionStateController = StreamController<ConnectionState>.broadcast();

  Stream<ChatMessage> get messageStream => _messageController.stream;
  Stream<ToolEvent> get toolEventStream => _toolEventController.stream;
  Stream<ConnectionState> get connectionStream => _connectionStateController.stream;

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

  // ─── Send Message (REST) ───
  Future<void> sendMessage(String message, {String? threadId}) async {
    try {
      final response = await _dio.post(
        AppConfig.chatEndpoint,
        data: {
          'message': message,
          'thread_id': threadId,
          'source': 'mobile_app',
          'stream': false,
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

  // ─── Start Run (LangGraph with tools) ───
  Future<String> startRun(String directive, {String? threadId}) async {
    try {
      final response = await _dio.post(
        AppConfig.runEndpoint,
        data: {
          'directive': directive,
          'thread_id': threadId,
          'source': 'mobile_app',
        },
      );

      return response.data['run_id'] as String;
    } catch (e) {
      _log.severe('Failed to start run', e);
      rethrow;
    }
  }

  // ─── WebSocket Streaming Connection ───
  Future<void> connectStreaming({String? threadId}) async {
    _connectionStateController.add(ConnectionState.connecting);

    try {
      final uri = Uri.parse(
        '${AppConfig.gatewayWsUrl}${threadId != null ? '?thread_id=$threadId' : ''}',
      );

      _wsChannel = WebSocketChannel.connect(uri);
      await _wsChannel!.ready;

      _reconnectAttempts = 0;
      _connectionStateController.add(ConnectionState.connected);
      _startHeartbeat();

      _wsChannel!.stream.listen(
        (data) => _handleWsMessage(data),
        onError: (error) {
          _log.warning('WebSocket error', error);
          _connectionStateController.add(ConnectionState.error);
          _attemptReconnect(threadId: threadId);
        },
        onDone: () {
          _log.info('WebSocket closed');
          _connectionStateController.add(ConnectionState.disconnected);
          _attemptReconnect(threadId: threadId);
        },
      );
    } catch (e) {
      _log.severe('WebSocket connection failed', e);
      _connectionStateController.add(ConnectionState.error);
      _attemptReconnect(threadId: threadId);
    }
  }

  void _handleWsMessage(dynamic rawData) {
    try {
      final data = jsonDecode(rawData as String) as Map<String, dynamic>;
      final eventType = data['type'] as String?;

      switch (eventType) {
        case 'message_chunk':
          _messageController.add(ChatMessage.streamChunk(data));
          break;
        case 'message_complete':
          _messageController.add(ChatMessage.fromKernelResponse(data));
          break;
        case 'tool_call_start':
        case 'tool_call_result':
        case 'tool_call_error':
          _toolEventController.add(ToolEvent.fromJson(data));
          break;
        case 'run_start':
        case 'run_complete':
        case 'run_error':
          _toolEventController.add(ToolEvent.fromJson(data));
          break;
        case 'genui_component':
          // A2UI component — forward to GenUI renderer
          _messageController.add(ChatMessage.genuiComponent(data));
          break;
        case 'heartbeat':
          // Keep-alive, ignore
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
      'type': 'user_message',
      'content': message,
      'thread_id': threadId,
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    }));
  }

  // ─── Heartbeat ───
  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(
      const Duration(seconds: 30),
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
      _connectionStateController.add(ConnectionState.failed);
      return;
    }

    _reconnectAttempts++;
    final delay = AppConfig.wsReconnectDelay * _reconnectAttempts;
    _log.info('Reconnecting in ${delay.inSeconds}s (attempt $_reconnectAttempts)');

    _connectionStateController.add(ConnectionState.reconnecting);

    Future.delayed(delay, () {
      connectStreaming(threadId: threadId);
    });
  }

  // ─── Memory ───
  Future<Map<String, dynamic>> getMemoryContext() async {
    try {
      final response = await _dio.get(AppConfig.memoryEndpoint);
      return response.data as Map<String, dynamic>;
    } catch (e) {
      _log.warning('Failed to get memory context', e);
      return {};
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

  // ─── Cleanup ───
  void dispose() {
    _heartbeatTimer?.cancel();
    _wsChannel?.sink.close();
    _messageController.close();
    _toolEventController.close();
    _connectionStateController.close();
  }
}

enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
  failed,
}

// ─── Riverpod Provider ───
final kernelServiceProvider = Provider<KernelService>((ref) {
  final service = KernelService();
  ref.onDispose(() => service.dispose());
  return service;
});

final kernelHealthProvider = FutureProvider<KernelHealth>((ref) async {
  final service = ref.watch(kernelServiceProvider);
  return service.checkHealth();
});

final connectionStateProvider = StreamProvider<ConnectionState>((ref) {
  final service = ref.watch(kernelServiceProvider);
  return service.connectionStream;
});
