// A2UIMessageView: integración del renderer A2UI dentro del chat existente.
//
// Sprint MOBILE_1B (Hilo Ejecutor) — T7.
//
// Diseño:
// - Recibe el `payload` crudo del mensaje (lo que llega del gateway en el
//   campo `genui_component.component`).
// - Si detecta `a2ui_version` (v1.0+), parsea con [A2UIParser] y renderiza
//   con [A2UIRenderer].
// - Si no detecta version (payload legacy GenUI), devuelve `null` para
//   que el caller use su renderer legacy. Cero ruptura de flujo existente.
// - Acepta un [dispatcher] opcional; si no se provee, las acciones se
//   capturan en un `BufferedA2UIActionSender` interno (para tests y dev).
//
// Uso desde `message_bubble.dart`:
// ```dart
// final a2uiView = A2UIMessageView.tryBuild(
//   payload: message.genuiPayload,
//   dispatcher: ref.read(a2uiActionDispatcherProvider),
// );
// if (a2uiView != null) return a2uiView;
// ```
//
// No depende de Riverpod ni de ningún provider concreto.

import 'package:flutter/material.dart';

import 'brand_tokens.dart';
import 'parser.dart';
import 'renderer.dart';
import 'types/a2ui_action.dart';
import 'types/a2ui_node.dart';

/// Renderiza un payload `a2ui_version` dentro del chat.
class A2UIMessageView extends StatelessWidget {
  const A2UIMessageView({
    super.key,
    required this.node,
    this.dispatcher,
    this.warning,
  });

  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;
  final String? warning;

  /// Factory que detecta versión y parsea, o devuelve `null` si el payload
  /// no es A2UI (para dejar paso al renderer legacy).
  static A2UIMessageView? tryBuild({
    required Map<String, dynamic>? payload,
    A2UIActionDispatcher? dispatcher,
  }) {
    if (payload == null) return null;
    if (!_isA2UIPayload(payload)) return null;

    const parser = A2UIParser();
    final result = parser.parse(payload);
    if (result.root == null) return null;

    final warningMsg = result.warnings.isNotEmpty
        ? result.warnings.map((w) => w.message).join('; ')
        : null;

    return A2UIMessageView(
      node: result.root!,
      dispatcher: dispatcher,
      warning: warningMsg,
    );
  }

  static bool _isA2UIPayload(Map<String, dynamic> payload) {
    final version = payload['a2ui_version'];
    if (version is String && version.isNotEmpty) return true;
    if (version is num) return true;
    return false;
  }

  @override
  Widget build(BuildContext context) {
    final activeDispatcher = dispatcher ?? _noopDispatcher;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (warning != null && warning!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: A2UIBrand.s8),
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: A2UIBrand.s12,
                vertical: A2UIBrand.s8,
              ),
              decoration: BoxDecoration(
                color: A2UIBrand.graphiteSurface,
                borderRadius: BorderRadius.circular(A2UIBrand.rSm),
                border: Border.all(color: A2UIBrand.border),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded,
                      size: 16, color: A2UIBrand.warning),
                  const SizedBox(width: A2UIBrand.s8),
                  Expanded(
                    child: Text(
                      warning!,
                      style: A2UIBrand.caption
                          .copyWith(color: A2UIBrand.acero),
                    ),
                  ),
                ],
              ),
            ),
          ),
        A2UIRenderer(root: node, dispatcher: activeDispatcher),
      ],
    );
  }
}

void _noopDispatcher(A2UIAction _) {
  // intentionally empty: in production wire to A2UIActionSender from gateway.
}
