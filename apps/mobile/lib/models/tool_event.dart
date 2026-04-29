enum ToolEventType {
  toolCallStart,
  toolCallResult,
  toolCallError,
  runStart,
  runComplete,
  runError,
}

class ToolEvent {
  ToolEvent({
    required this.type,
    required this.toolName,
    this.args,
    this.result,
    this.error,
    this.runId,
    this.duration,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  final ToolEventType type;
  final String toolName;
  final Map<String, dynamic>? args;
  final String? result;
  final String? error;
  final String? runId;
  final Duration? duration;
  final DateTime timestamp;

  bool get isStart => type == ToolEventType.toolCallStart || type == ToolEventType.runStart;
  bool get isComplete => type == ToolEventType.toolCallResult || type == ToolEventType.runComplete;
  bool get isError => type == ToolEventType.toolCallError || type == ToolEventType.runError;

  factory ToolEvent.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String;
    final type = switch (typeStr) {
      'tool_call_start' => ToolEventType.toolCallStart,
      'tool_call_result' => ToolEventType.toolCallResult,
      'tool_call_error' => ToolEventType.toolCallError,
      'run_start' => ToolEventType.runStart,
      'run_complete' => ToolEventType.runComplete,
      'run_error' => ToolEventType.runError,
      _ => ToolEventType.toolCallStart,
    };

    return ToolEvent(
      type: type,
      toolName: json['tool_name'] as String? ?? json['name'] as String? ?? 'unknown',
      args: json['args'] as Map<String, dynamic>?,
      result: json['result'] as String?,
      error: json['error'] as String?,
      runId: json['run_id'] as String?,
      duration: json['duration_ms'] != null
          ? Duration(milliseconds: json['duration_ms'] as int)
          : null,
    );
  }

  /// Human-readable description of the tool action
  String get displayName {
    return switch (toolName) {
      'browse_web' => 'Navegando web',
      'code_exec' => 'Ejecutando código',
      'github' => 'GitHub',
      'search' => 'Buscando',
      'memory_store' => 'Guardando en memoria',
      'memory_recall' => 'Recordando',
      'manus_bridge' => 'Manus Bridge',
      _ => toolName,
    };
  }

  /// Icon name for the tool
  String get iconName {
    return switch (toolName) {
      'browse_web' => 'language',
      'code_exec' => 'terminal',
      'github' => 'code',
      'search' => 'search',
      'memory_store' => 'save',
      'memory_recall' => 'psychology',
      'manus_bridge' => 'hub',
      _ => 'build',
    };
  }
}
