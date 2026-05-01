import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../models/tool_event.dart';
import '../../../theme/monstruo_theme.dart';

class ToolActivityBar extends StatelessWidget {
  const ToolActivityBar({super.key, required this.tools});

  final List<ToolEvent> tools;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: MonstruoTheme.spacingMd,
        vertical: MonstruoTheme.spacingSm,
      ),
      decoration: const BoxDecoration(
        color: MonstruoTheme.surface,
        border: Border(
          bottom: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            const Icon(
              Icons.auto_awesome,
              size: 14,
              color: MonstruoTheme.primary,
            ),
            const SizedBox(width: 8),
            const Text(
              'Ejecutando:',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: MonstruoTheme.onSurfaceDim,
              ),
            ),
            const SizedBox(width: 8),
            ...tools.map((tool) => Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _ToolChip(tool: tool),
                )),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 200.ms).slideY(begin: -0.3, end: 0);
  }
}

class _ToolChip extends StatelessWidget {
  const _ToolChip({required this.tool});

  final ToolEvent tool;

  /// Sprint 48: Extended icon mapping for all tools
  IconData get _icon {
    return switch (tool.toolName) {
      'browse_web' => Icons.language,
      'code_exec' => Icons.terminal,
      'github' => Icons.code,
      'search' => Icons.search,
      'memory_store' => Icons.save,
      'memory_recall' => Icons.psychology,
      'manus_bridge' => Icons.hub,
      'file_ops' => Icons.description,
      'web_dev' => Icons.web,
      'web_dev.scaffold' => Icons.architecture,
      'web_dev.build' => Icons.build_circle,
      'web_dev.deploy' => Icons.rocket_launch,
      'sandbox' => Icons.cloud,
      'consult_sabios' => Icons.groups,
      _ => Icons.build,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: MonstruoTheme.primary.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusFull),
        border: Border.all(
          color: MonstruoTheme.primary.withValues(alpha: 0.3),
          width: 0.5,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 12,
            height: 12,
            child: CircularProgressIndicator(
              strokeWidth: 1.5,
              color: MonstruoTheme.primary,
            ),
          ),
          const SizedBox(width: 6),
          Icon(_icon, size: 12, color: MonstruoTheme.primary),
          const SizedBox(width: 4),
          Text(
            tool.displayName,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: MonstruoTheme.primary,
            ),
          ),
        ],
      ),
    );
  }
}
