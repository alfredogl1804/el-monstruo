import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';

import '../models/chat_message.dart';
import '../models/tool_event.dart';
import '../services/kernel_service.dart';

final _log = Logger('ChatProvider');

/// State for the chat conversation
class ChatState {
  const ChatState({
    this.messages = const [],
    this.activeTools = const [],
    this.isConnected = false,
    this.isStreaming = false,
    this.currentThreadId,
    this.error,
  });

  final List<ChatMessage> messages;
  final List<ToolEvent> activeTools;
  final bool isConnected;
  final bool isStreaming;
  final String? currentThreadId;
  final String? error;

  ChatState copyWith({
    List<ChatMessage>? messages,
    List<ToolEvent>? activeTools,
    bool? isConnected,
    bool? isStreaming,
    String? currentThreadId,
    String? error,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      activeTools: activeTools ?? this.activeTools,
      isConnected: isConnected ?? this.isConnected,
      isStreaming: isStreaming ?? this.isStreaming,
      currentThreadId: currentThreadId ?? this.currentThreadId,
      error: error,
    );
  }
}

/// Main chat notifier that manages conversation state
class ChatNotifier extends StateNotifier<ChatState> {
  ChatNotifier(this._kernelService) : super(const ChatState()) {
    _init();
  }

  final KernelService _kernelService;
  StreamSubscription? _messageSub;
  StreamSubscription? _toolSub;
  StreamSubscription? _connectionSub;

  void _init() {
    // Listen to incoming messages
    _messageSub = _kernelService.messageStream.listen((message) {
      if (message.type == MessageType.streamChunk) {
        _handleStreamChunk(message);
      } else {
        _handleCompleteMessage(message);
      }
    });

    // Listen to tool events
    _toolSub = _kernelService.toolEventStream.listen((event) {
      _handleToolEvent(event);
    });

    // Listen to connection state
    _connectionSub = _kernelService.connectionStream.listen((connState) {
      state = state.copyWith(
        isConnected: connState == ConnectionState.connected,
      );
    });

    // Connect WebSocket
    _kernelService.connectStreaming();
  }

  void _handleStreamChunk(ChatMessage chunk) {
    final messages = List<ChatMessage>.from(state.messages);

    // Find existing streaming message or create new one
    final existingIdx = messages.indexWhere(
      (m) => m.id == chunk.id && m.isStreaming,
    );

    if (existingIdx >= 0) {
      messages[existingIdx].appendChunk(chunk.content);
      // Force state update
      state = state.copyWith(
        messages: List.from(messages),
        isStreaming: true,
      );
    } else {
      messages.add(chunk);
      state = state.copyWith(
        messages: messages,
        isStreaming: true,
      );
    }
  }

  void _handleCompleteMessage(ChatMessage message) {
    final messages = List<ChatMessage>.from(state.messages);

    // Replace streaming message with complete one, or add new
    final streamingIdx = messages.indexWhere(
      (m) => m.id == message.id && m.isStreaming,
    );

    if (streamingIdx >= 0) {
      messages[streamingIdx] = message.copyWith(isStreaming: false);
    } else {
      messages.add(message);
    }

    state = state.copyWith(
      messages: messages,
      isStreaming: false,
    );
  }

  void _handleToolEvent(ToolEvent event) {
    final activeTools = List<ToolEvent>.from(state.activeTools);

    if (event.isStart) {
      activeTools.add(event);
    } else {
      // Remove completed/errored tool
      activeTools.removeWhere((t) => t.toolName == event.toolName);

      // Add a tool result message to the chat
      if (event.isComplete && event.result != null) {
        final messages = List<ChatMessage>.from(state.messages);
        messages.add(ChatMessage(
          role: MessageRole.tool,
          content: event.result!,
          type: MessageType.toolResult,
          toolName: event.toolName,
        ));
        state = state.copyWith(messages: messages);
      }
    }

    state = state.copyWith(activeTools: activeTools);
  }

  /// Send a user message
  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;

    // Add user message immediately
    final userMessage = ChatMessage.user(content);
    state = state.copyWith(
      messages: [...state.messages, userMessage],
      isStreaming: true,
      error: null,
    );

    try {
      if (state.isConnected) {
        // Use WebSocket for streaming
        _kernelService.sendWsMessage(
          content,
          threadId: state.currentThreadId,
        );
      } else {
        // Fallback to REST
        await _kernelService.sendMessage(
          content,
          threadId: state.currentThreadId,
        );
        state = state.copyWith(isStreaming: false);
      }
    } catch (e) {
      _log.severe('Failed to send message', e);
      state = state.copyWith(
        messages: [
          ...state.messages,
          ChatMessage.error('Error al enviar: ${e.toString()}'),
        ],
        isStreaming: false,
        error: e.toString(),
      );
    }
  }

  /// Start a new conversation thread
  void newThread() {
    state = const ChatState();
    _kernelService.connectStreaming();
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }

  @override
  void dispose() {
    _messageSub?.cancel();
    _toolSub?.cancel();
    _connectionSub?.cancel();
    super.dispose();
  }
}

// ─── Riverpod Providers ───

final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  final kernelService = ref.watch(kernelServiceProvider);
  return ChatNotifier(kernelService);
});

final isStreamingProvider = Provider<bool>((ref) {
  return ref.watch(chatProvider).isStreaming;
});

final activeToolsProvider = Provider<List<ToolEvent>>((ref) {
  return ref.watch(chatProvider).activeTools;
});

final messagesProvider = Provider<List<ChatMessage>>((ref) {
  return ref.watch(chatProvider).messages;
});
