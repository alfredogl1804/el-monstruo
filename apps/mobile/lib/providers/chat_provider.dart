import 'dart:async';

import 'package:flutter/scheduler.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';

import '../features/chat/widgets/typing_indicator.dart';
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
    this.isThinking = false,
    this.thinkingModel,
    this.thinkingIntent,
    this.thinkingStartTime,
    this.thinkingSteps = const [],
    this.currentThreadId,
    this.error,
  });

  final List<ChatMessage> messages;
  final List<ToolEvent> activeTools;
  final bool isConnected;
  final bool isStreaming;
  final bool isThinking;
  final String? thinkingModel;
  final String? thinkingIntent;
  final DateTime? thinkingStartTime;
  final List<ThinkingStep> thinkingSteps;
  final String? currentThreadId;
  final String? error;

  ChatState copyWith({
    List<ChatMessage>? messages,
    List<ToolEvent>? activeTools,
    bool? isConnected,
    bool? isStreaming,
    bool? isThinking,
    String? thinkingModel,
    String? thinkingIntent,
    DateTime? thinkingStartTime,
    List<ThinkingStep>? thinkingSteps,
    String? currentThreadId,
    String? error,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      activeTools: activeTools ?? this.activeTools,
      isConnected: isConnected ?? this.isConnected,
      isStreaming: isStreaming ?? this.isStreaming,
      isThinking: isThinking ?? this.isThinking,
      thinkingModel: thinkingModel ?? this.thinkingModel,
      thinkingIntent: thinkingIntent ?? this.thinkingIntent,
      thinkingStartTime: thinkingStartTime ?? this.thinkingStartTime,
      thinkingSteps: thinkingSteps ?? this.thinkingSteps,
      currentThreadId: currentThreadId ?? this.currentThreadId,
      error: error,
    );
  }
}

/// Main chat notifier that manages conversation state.
///
/// Sprint 45: Frame-aligned token batching for streaming speed.
/// Instead of rebuilding state on every single token (40-80 rebuilds/sec),
/// we accumulate tokens in a buffer and flush once per animation frame (60fps).
/// This reduces UI rebuilds from ~50/sec to ~60/sec max (frame-aligned),
/// eliminates jank from Markdown AST rebuilds, and creates a smooth
/// "typewriter" effect matching ChatGPT/Manus perceived speed.
class ChatNotifier extends StateNotifier<ChatState> {
  ChatNotifier(this._kernelService) : super(const ChatState()) {
    _init();
  }

  final KernelService _kernelService;
  StreamSubscription? _messageSub;
  StreamSubscription? _toolSub;
  StreamSubscription? _connectionSub;
  StreamSubscription? _thinkingSub;
  StreamSubscription? _stepSub;

  // ── Sprint 45: Token Jitter Buffer ──────────────────────────────────
  // Accumulates incoming tokens and flushes them aligned to vsync frames.
  // This eliminates per-token state rebuilds and creates smooth rendering.
  final StringBuffer _tokenBuffer = StringBuffer();
  String? _activeStreamingMessageId;
  bool _isFirstToken = true;
  bool _frameCallbackScheduled = false;

  void _init() {
    // Listen to incoming messages
    _messageSub = _kernelService.messageStream.listen((message) {
      // First token arrived — stop thinking indicator
      if (state.isThinking) {
        state = state.copyWith(isThinking: false);
      }
      if (message.type == MessageType.streamChunk) {
        _handleStreamChunk(message);
      } else {
        // Flush any pending tokens before handling complete message
        _flushTokenBuffer();
        _handleCompleteMessage(message);
      }
    });

    // Listen to tool events
    _toolSub = _kernelService.toolEventStream.listen((event) {
      _handleToolEvent(event);
    });

    // Listen to thinking state (legacy — backward compat)
    _thinkingSub = _kernelService.thinkingStream.listen((data) {
      _handleThinkingState(data);
    });

    // Listen to step events (Sprint 43 — structured thinking steps)
    _stepSub = _kernelService.stepStream.listen((data) {
      _handleStepEvent(data);
    });

    // Listen to connection state
    _connectionSub = _kernelService.connectionStream.listen((connState) {
      state = state.copyWith(
        isConnected: connState == KernelConnectionState.connected,
      );
    });

    // Connect WebSocket
    _kernelService.connectStreaming();
  }

  void _handleThinkingState(Map<String, dynamic> data) {
    final model = data['model'] as String? ?? '';
    final intent = data['intent'] as String? ?? '';
    state = state.copyWith(
      isThinking: true,
      isStreaming: true,
      thinkingModel: model.isNotEmpty ? model : null,
      thinkingIntent: intent.isNotEmpty ? intent : null,
      thinkingStartTime: state.thinkingStartTime ?? DateTime.now(),
    );
  }

  /// Sprint 43: Handle structured step events from the kernel pipeline.
  void _handleStepEvent(Map<String, dynamic> data) {
    final stepId = data['step_id'] as String? ?? '';
    final status = data['status'] as String? ?? 'in_progress';
    final label = data['label'] as String? ?? '';
    final icon = data['icon'] as String? ?? '';

    if (stepId.isEmpty) return;

    final steps = List<ThinkingStep>.from(state.thinkingSteps);

    // Find existing step by id
    final existingIdx = steps.indexWhere((s) => s.id == stepId);

    if (existingIdx >= 0) {
      // Update existing step (e.g., in_progress → completed)
      steps[existingIdx] = steps[existingIdx].copyWith(
        status: status,
        label: label.isNotEmpty ? label : null,
      );
    } else {
      // Add new step
      steps.add(ThinkingStep(
        id: stepId,
        label: label,
        icon: icon,
        status: status,
      ));
    }

    state = state.copyWith(
      isThinking: true,
      isStreaming: true,
      thinkingSteps: steps,
      thinkingStartTime: state.thinkingStartTime ?? DateTime.now(),
    );
  }

  /// Sprint 45: Frame-aligned token batching.
  /// Instead of rebuilding state per token, we buffer tokens and flush
  /// on the next animation frame. The FIRST token is flushed immediately
  /// to preserve TTFT (time-to-first-token) perception.
  void _handleStreamChunk(ChatMessage chunk) {
    final chunkContent = chunk.content;
    final chunkId = chunk.id;

    // Track active streaming message
    if (_activeStreamingMessageId == null || _activeStreamingMessageId != chunkId) {
      // New streaming message — flush any previous buffer
      _flushTokenBuffer();
      _activeStreamingMessageId = chunkId;
      _isFirstToken = true;
    }

    // Accumulate token in buffer
    _tokenBuffer.write(chunkContent);

    if (_isFirstToken) {
      // FIRST TOKEN: flush immediately to break the "waiting" barrier.
      // This preserves TTFT perception — user sees response start instantly.
      _isFirstToken = false;
      _flushTokenBuffer();
    } else {
      // SUBSEQUENT TOKENS: schedule flush on next animation frame.
      // This batches 2-5 tokens per frame (at 60fps = 16ms batches),
      // reducing state rebuilds from ~50/sec to max 60/sec (frame-aligned).
      _scheduleFrameFlush();
    }
  }

  /// Schedule a flush on the next vsync frame (if not already scheduled).
  void _scheduleFrameFlush() {
    if (_frameCallbackScheduled) return;
    _frameCallbackScheduled = true;

    SchedulerBinding.instance.addPostFrameCallback((_) {
      _frameCallbackScheduled = false;
      _flushTokenBuffer();
    });
  }

  /// Flush accumulated tokens to state in a single rebuild.
  void _flushTokenBuffer() {
    if (_tokenBuffer.isEmpty) return;

    final bufferedContent = _tokenBuffer.toString();
    _tokenBuffer.clear();

    final messageId = _activeStreamingMessageId;
    if (messageId == null) return;

    final messages = List<ChatMessage>.from(state.messages);

    // Find existing streaming message or create new one
    final existingIdx = messages.indexWhere(
      (m) => m.id == messageId && m.isStreaming,
    );

    if (existingIdx >= 0) {
      messages[existingIdx].appendChunk(bufferedContent);
      state = state.copyWith(
        messages: List.from(messages),
        isStreaming: true,
      );
    } else {
      // Create new streaming message with buffered content
      messages.add(ChatMessage(
        id: messageId,
        role: MessageRole.assistant,
        content: bufferedContent,
        type: MessageType.streamChunk,
        isStreaming: true,
      ));
      state = state.copyWith(
        messages: messages,
        isStreaming: true,
      );
    }
  }

  void _handleCompleteMessage(ChatMessage message) {
    // Reset streaming state
    _activeStreamingMessageId = null;
    _isFirstToken = true;

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


  /// Stop current streaming / thinking
  void stopStreaming() {
    // Flush any pending tokens before stopping
    _flushTokenBuffer();
    _activeStreamingMessageId = null;
    _isFirstToken = true;

    // Disconnect and reconnect WebSocket to cancel the in-flight request
    _kernelService.connectStreaming();
    
    // Mark any streaming messages as complete
    final messages = List<ChatMessage>.from(state.messages);
    for (var i = 0; i < messages.length; i++) {
      if (messages[i].isStreaming) {
        messages[i] = messages[i].copyWith(isStreaming: false);
      }
    }
    
    state = state.copyWith(
      messages: messages,
      isStreaming: false,
      isThinking: false,
      thinkingModel: null,
      thinkingIntent: null,
      thinkingStartTime: null,
      thinkingSteps: [],
      activeTools: [],
    );
  }

  /// Send a user message
  Future<void> sendMessage(String content) async {
    if (content.trim().isEmpty) return;

    // Add user message immediately
    final userMessage = ChatMessage.user(content);
    state = state.copyWith(
      messages: [...state.messages, userMessage],
      isStreaming: true,
      isThinking: true,
      thinkingStartTime: DateTime.now(),
      thinkingSteps: [], // Reset steps for new message
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
    _flushTokenBuffer();
    _activeStreamingMessageId = null;
    _isFirstToken = true;
    state = const ChatState();
    _kernelService.connectStreaming();
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }

  @override
  void dispose() {
    _flushTokenBuffer();
    _messageSub?.cancel();
    _toolSub?.cancel();
    _connectionSub?.cancel();
    _thinkingSub?.cancel();
    _stepSub?.cancel();
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

final isThinkingProvider = Provider<bool>((ref) {
  return ref.watch(chatProvider).isThinking;
});

final thinkingModelProvider = Provider<String?>((ref) {
  return ref.watch(chatProvider).thinkingModel;
});

final thinkingStartTimeProvider = Provider<DateTime?>((ref) {
  return ref.watch(chatProvider).thinkingStartTime;
});

final thinkingStepsProvider = Provider<List<ThinkingStep>>((ref) {
  return ref.watch(chatProvider).thinkingSteps;
});

final activeToolsProvider = Provider<List<ToolEvent>>((ref) {
  return ref.watch(chatProvider).activeTools;
});

final messagesProvider = Provider<List<ChatMessage>>((ref) {
  return ref.watch(chatProvider).messages;
});
