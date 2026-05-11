/// A2UI Action — modelo de eventos que el renderer envía al kernel.
///
/// Protocolo WebSocket canon firmado:
/// `{"type":"a2ui_action","action_id":"...","payload":{...}}`
library;

import 'package:flutter/foundation.dart';

/// Evento accionable disparado por un widget A2UI (Button, Link, Stepper).
@immutable
class A2UIAction {
  /// ID canónico del action declarado por el kernel.
  final String actionId;

  /// Payload arbitrario asociado al action.
  final Map<String, dynamic> payload;

  /// Tipo de origen — debugging/observabilidad.
  final String sourceWidget;

  /// Timestamp cuando se generó el action (UTC ISO 8601).
  final String timestamp;

  A2UIAction({
    required this.actionId,
    this.payload = const {},
    this.sourceWidget = 'Unknown',
    String? timestamp,
  }) : timestamp = timestamp ?? DateTime.now().toUtc().toIso8601String();

  /// Serialización canon para WebSocket.
  Map<String, dynamic> toJson() => {
        'type': 'a2ui_action',
        'action_id': actionId,
        'payload': payload,
        'source_widget': sourceWidget,
        'timestamp': timestamp,
      };

  @override
  String toString() => 'A2UIAction(id=$actionId, src=$sourceWidget)';
}

/// Callback que el renderer invoca cuando un widget A2UI dispara un action.
typedef A2UIActionDispatcher = void Function(A2UIAction action);
