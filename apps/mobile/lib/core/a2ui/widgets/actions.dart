/// A2UI action widgets — Button + ButtonGroup.
library;

import 'package:flutter/material.dart';

import '../brand_tokens.dart';
import '../types/a2ui_action.dart';
import '../types/a2ui_node.dart';

/// Botón A2UI con variantes `primary | secondary | ghost | danger`.
class A2UIButton extends StatelessWidget {
  const A2UIButton({super.key, required this.node, this.dispatcher});

  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    final label = node.prop<String>('label') ?? '';
    final variant = node.prop<String>('variant') ?? 'primary';
    final disabled = node.prop<bool>('disabled') ?? false;

    final onPressed = disabled
        ? null
        : () {
            if (node.actionId != null) {
              dispatcher?.call(A2UIAction(
                actionId: node.actionId!,
                sourceWidget: 'Button',
                payload: node.actionPayload ?? const {},
              ));
            }
          };

    switch (variant) {
      case 'secondary':
        return OutlinedButton(
          onPressed: onPressed,
          style: OutlinedButton.styleFrom(
            foregroundColor: A2UIBrand.textPrimary,
            side: const BorderSide(color: A2UIBrand.border),
            padding: const EdgeInsets.symmetric(
                horizontal: A2UIBrand.s16, vertical: A2UIBrand.s12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(A2UIBrand.rMd),
            ),
          ),
          child: Text(label),
        );
      case 'ghost':
        return TextButton(
          onPressed: onPressed,
          style: TextButton.styleFrom(
            foregroundColor: A2UIBrand.forja,
            padding: const EdgeInsets.symmetric(
                horizontal: A2UIBrand.s12, vertical: A2UIBrand.s8),
          ),
          child: Text(label),
        );
      case 'danger':
        return ElevatedButton(
          onPressed: onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: A2UIBrand.danger,
            foregroundColor: A2UIBrand.textPrimary,
            padding: const EdgeInsets.symmetric(
                horizontal: A2UIBrand.s16, vertical: A2UIBrand.s12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(A2UIBrand.rMd),
            ),
          ),
          child: Text(label),
        );
      case 'primary':
      default:
        return ElevatedButton(
          onPressed: onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: A2UIBrand.forja,
            foregroundColor: A2UIBrand.graphite,
            padding: const EdgeInsets.symmetric(
                horizontal: A2UIBrand.s16, vertical: A2UIBrand.s12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(A2UIBrand.rMd),
            ),
          ),
          child: Text(label,
              style: const TextStyle(fontWeight: FontWeight.w600)),
        );
    }
  }
}

/// Grupo de botones inline (max 4 botones recomendados).
class A2UIButtonGroup extends StatelessWidget {
  const A2UIButtonGroup({super.key, required this.node, this.dispatcher});

  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    // children deben ser Buttons. Si no, ignoramos.
    final buttons = node.children.where((c) => c.type == 'Button').toList();
    return Wrap(
      spacing: A2UIBrand.s8,
      runSpacing: A2UIBrand.s8,
      children: [
        for (final btn in buttons)
          A2UIButton(node: btn, dispatcher: dispatcher),
      ],
    );
  }
}
