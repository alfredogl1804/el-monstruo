/// A2UI progress widgets — Progress, Stepper.
library;

import 'package:flutter/material.dart';

import '../brand_tokens.dart';
import '../types/a2ui_node.dart';

/// Progress lineal o circular según `mode = linear | circular`.
class A2UIProgress extends StatelessWidget {
  const A2UIProgress({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final mode = node.prop<String>('mode') ?? 'linear';
    final value = node.prop<num>('value')?.toDouble();
    final label = node.prop<String>('label');
    final indeterminate = value == null;
    final clamped = value?.clamp(0.0, 1.0);

    if (mode == 'circular') {
      return Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 36,
            height: 36,
            child: CircularProgressIndicator(
              value: indeterminate ? null : clamped,
              strokeWidth: 3,
              color: A2UIBrand.forja,
              backgroundColor: A2UIBrand.border,
            ),
          ),
          if (label != null) ...[
            const SizedBox(height: A2UIBrand.s8),
            Text(label, style: A2UIBrand.caption),
          ],
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null) ...[
          Text(label, style: A2UIBrand.caption),
          const SizedBox(height: A2UIBrand.s4),
        ],
        ClipRRect(
          borderRadius: BorderRadius.circular(A2UIBrand.rSm),
          child: LinearProgressIndicator(
            value: indeterminate ? null : clamped,
            color: A2UIBrand.forja,
            backgroundColor: A2UIBrand.border,
            minHeight: 6,
          ),
        ),
      ],
    );
  }
}

/// Stepper de pasos. Props: `steps: [{title, status}]`, status ∈ done|active|pending|failed.
class A2UIStepper extends StatelessWidget {
  const A2UIStepper({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final steps = node.propList('steps');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 0; i < steps.length; i++)
          _StepRow(
            index: i + 1,
            title: steps[i]['title']?.toString() ?? '',
            status: steps[i]['status']?.toString() ?? 'pending',
            isLast: i == steps.length - 1,
          ),
      ],
    );
  }
}

class _StepRow extends StatelessWidget {
  const _StepRow({
    required this.index,
    required this.title,
    required this.status,
    required this.isLast,
  });
  final int index;
  final String title;
  final String status;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    final (icon, color) = switch (status) {
      'done' => (Icons.check_circle, A2UIBrand.success),
      'active' => (Icons.radio_button_checked, A2UIBrand.forja),
      'failed' => (Icons.error, A2UIBrand.danger),
      _ => (Icons.radio_button_unchecked, A2UIBrand.acero),
    };
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Icon(icon, color: color, size: 18),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 1,
                    color: A2UIBrand.border,
                  ),
                ),
            ],
          ),
          const SizedBox(width: A2UIBrand.s12),
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : A2UIBrand.s12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Paso $index', style: A2UIBrand.caption),
                  const SizedBox(height: 2),
                  Text(title, style: A2UIBrand.body),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
