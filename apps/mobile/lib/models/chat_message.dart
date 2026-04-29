import 'package:uuid/uuid.dart';

const _uuid = Uuid();

enum MessageRole { user, assistant, system, tool }
enum MessageType { text, streamChunk, genuiComponent, toolResult, error }

class ChatMessage {
  ChatMessage({
    String? id,
    required this.role,
    required this.content,
    this.type = MessageType.text,
    this.toolName,
    this.toolArgs,
    this.genuiPayload,
    this.isStreaming = false,
    this.model,
    this.tokenCount,
    this.cost,
    DateTime? timestamp,
  })  : id = id ?? _uuid.v4(),
        timestamp = timestamp ?? DateTime.now();

  final String id;
  final MessageRole role;
  String content;
  final MessageType type;
  final String? toolName;
  final Map<String, dynamic>? toolArgs;
  final Map<String, dynamic>? genuiPayload;
  bool isStreaming;
  final String? model;
  final int? tokenCount;
  final double? cost;
  final DateTime timestamp;

  // ─── Factory Constructors ───

  factory ChatMessage.user(String content) {
    return ChatMessage(
      role: MessageRole.user,
      content: content,
      type: MessageType.text,
    );
  }

  factory ChatMessage.fromKernelResponse(Map<String, dynamic> data) {
    return ChatMessage(
      id: data['id'] as String? ?? _uuid.v4(),
      role: MessageRole.assistant,
      content: data['content'] as String? ?? data['message'] as String? ?? '',
      type: MessageType.text,
      model: data['model'] as String?,
      tokenCount: data['token_count'] as int?,
      cost: (data['cost'] as num?)?.toDouble(),
    );
  }

  factory ChatMessage.streamChunk(Map<String, dynamic> data) {
    return ChatMessage(
      id: data['message_id'] as String? ?? _uuid.v4(),
      role: MessageRole.assistant,
      content: data['chunk'] as String? ?? data['content'] as String? ?? '',
      type: MessageType.streamChunk,
      isStreaming: true,
    );
  }

  factory ChatMessage.genuiComponent(Map<String, dynamic> data) {
    return ChatMessage(
      id: data['id'] as String? ?? _uuid.v4(),
      role: MessageRole.assistant,
      content: data['description'] as String? ?? 'Generative UI Component',
      type: MessageType.genuiComponent,
      genuiPayload: data['component'] as Map<String, dynamic>?,
    );
  }

  factory ChatMessage.toolResult(Map<String, dynamic> data) {
    return ChatMessage(
      id: data['id'] as String? ?? _uuid.v4(),
      role: MessageRole.tool,
      content: data['result'] as String? ?? '',
      type: MessageType.toolResult,
      toolName: data['tool_name'] as String?,
    );
  }

  factory ChatMessage.error(String errorMessage) {
    return ChatMessage(
      role: MessageRole.system,
      content: errorMessage,
      type: MessageType.error,
    );
  }

  // ─── Helpers ───

  bool get isUser => role == MessageRole.user;
  bool get isAssistant => role == MessageRole.assistant;
  bool get isGenUI => type == MessageType.genuiComponent;
  bool get isError => type == MessageType.error;

  void appendChunk(String chunk) {
    content += chunk;
  }

  ChatMessage copyWith({
    String? content,
    bool? isStreaming,
  }) {
    return ChatMessage(
      id: id,
      role: role,
      content: content ?? this.content,
      type: type,
      toolName: toolName,
      toolArgs: toolArgs,
      genuiPayload: genuiPayload,
      isStreaming: isStreaming ?? this.isStreaming,
      model: model,
      tokenCount: tokenCount,
      cost: cost,
      timestamp: timestamp,
    );
  }
}
