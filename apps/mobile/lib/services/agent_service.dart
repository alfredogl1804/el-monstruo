import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';
import '../core/config.dart';

final _log = Logger('AgentService');

/// Available external agents for dispatch.
enum ExternalAgentId {
  auto('auto', 'Auto', '🎯', 'Selección automática'),
  manus('manus', 'Manus', '🤖', 'End-to-end: browser, código, deploy'),
  kimi('kimi', 'Kimi K2.5', '🌙', 'Código rápido y barato'),
  perplexity('perplexity', 'Perplexity', '🔍', 'Investigación en tiempo real'),
  gemini('gemini', 'Gemini 3.1', '💎', 'Análisis profundo, multimodal'),
  grok('grok', 'Grok 4.20', '⚡', 'Respuestas rápidas y directas');

  const ExternalAgentId(this.id, this.displayName, this.icon, this.description);
  final String id;
  final String displayName;
  final String icon;
  final String description;
}

/// Response from an external agent dispatch.
class AgentDispatchResponse {
  AgentDispatchResponse({
    required this.success,
    required this.agentId,
    required this.agentName,
    required this.content,
    required this.modelUsed,
    required this.latencyMs,
    this.tokensUsed = 0,
    this.sources = const [],
    this.error,
  });

  final bool success;
  final String agentId;
  final String agentName;
  final String content;
  final String modelUsed;
  final int latencyMs;
  final int tokensUsed;
  final List<String> sources;
  final String? error;

  factory AgentDispatchResponse.fromJson(Map<String, dynamic> json) {
    return AgentDispatchResponse(
      success: json['success'] ?? false,
      agentId: json['agent_id'] ?? '',
      agentName: json['agent_name'] ?? '',
      content: json['content'] ?? '',
      modelUsed: json['model_used'] ?? '',
      latencyMs: json['latency_ms'] ?? 0,
      tokensUsed: json['tokens_used'] ?? 0,
      sources: List<String>.from(json['sources'] ?? []),
      error: json['error'],
    );
  }
}

/// Service for dispatching tasks to external agents.
class AgentService {
  AgentService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: AppConfig.kernelBaseUrl,
              connectTimeout: AppConfig.connectTimeout,
              receiveTimeout: const Duration(seconds: 180), // Agents can be slow
              headers: {'Content-Type': 'application/json'},
            ));

  final Dio _dio;

  /// Get list of available agents and their status.
  Future<List<Map<String, dynamic>>> getAvailableAgents() async {
    try {
      final response = await _dio.get(AppConfig.agentsListEndpoint);
      if (response.statusCode == 200) {
        final data = response.data;
        return List<Map<String, dynamic>>.from(data['agents'] ?? []);
      }
      return [];
    } catch (e) {
      _log.severe('Failed to get agents list', e);
      return [];
    }
  }

  /// Dispatch a message to a specific external agent.
  Future<AgentDispatchResponse> dispatch({
    required String message,
    required ExternalAgentId agent,
    String? threadId,
    String? systemPrompt,
  }) async {
    try {
      _log.info('Dispatching to ${agent.id}: ${message.substring(0, message.length.clamp(0, 50))}...');
      
      final response = await _dio.post(
        AppConfig.agentsDispatchEndpoint,
        data: {
          'agent': agent.id,
          'message': message,
          'thread_id': threadId ?? '',
          'system_prompt': systemPrompt ?? '',
        },
      );

      if (response.statusCode == 200) {
        return AgentDispatchResponse.fromJson(response.data);
      }
      
      return AgentDispatchResponse(
        success: false,
        agentId: agent.id,
        agentName: agent.displayName,
        content: '',
        modelUsed: '',
        latencyMs: 0,
        error: 'HTTP ${response.statusCode}',
      );
    } catch (e) {
      _log.severe('Dispatch failed', e);
      return AgentDispatchResponse(
        success: false,
        agentId: agent.id,
        agentName: agent.displayName,
        content: '',
        modelUsed: '',
        latencyMs: 0,
        error: e.toString(),
      );
    }
  }
}

/// Riverpod provider for AgentService.
final agentServiceProvider = Provider<AgentService>((ref) => AgentService());

/// Provider for the currently selected agent.
final selectedAgentProvider = StateProvider<ExternalAgentId>(
  (ref) => ExternalAgentId.auto,
);
