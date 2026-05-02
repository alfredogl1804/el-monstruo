import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/agent_service.dart';
import '../../../theme/monstruo_theme.dart';

/// Compact agent selector button that opens a bottom sheet with agent options.
class AgentSelector extends ConsumerWidget {
  const AgentSelector({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selected = ref.watch(selectedAgentProvider);

    return GestureDetector(
      onTap: () {
        HapticFeedback.lightImpact();
        _showAgentPicker(context, ref);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: selected == ExternalAgentId.auto
              ? MonstruoTheme.surfaceVariant
              : MonstruoTheme.primary.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: selected == ExternalAgentId.auto
                ? MonstruoTheme.divider
                : MonstruoTheme.primary.withValues(alpha: 0.4),
            width: 0.5,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              selected.icon,
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(width: 4),
            Text(
              selected.displayName,
              style: TextStyle(
                color: selected == ExternalAgentId.auto
                    ? MonstruoTheme.onSurfaceDim
                    : MonstruoTheme.primary,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(width: 2),
            Icon(
              Icons.expand_more_rounded,
              size: 14,
              color: selected == ExternalAgentId.auto
                  ? MonstruoTheme.onSurfaceDim
                  : MonstruoTheme.primary,
            ),
          ],
        ),
      ),
    );
  }

  void _showAgentPicker(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      backgroundColor: MonstruoTheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => _AgentPickerSheet(
        onSelect: (agent) {
          ref.read(selectedAgentProvider.notifier).state = agent;
          Navigator.of(ctx).pop();
        },
        current: ref.read(selectedAgentProvider),
      ),
    );
  }
}

class _AgentPickerSheet extends StatelessWidget {
  const _AgentPickerSheet({
    required this.onSelect,
    required this.current,
  });

  final ValueChanged<ExternalAgentId> onSelect;
  final ExternalAgentId current;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle bar
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: MonstruoTheme.divider,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Title
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                'Seleccionar Agente',
                style: TextStyle(
                  color: MonstruoTheme.onBackground,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 4),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20),
              child: Text(
                'Elige quién ejecuta tu siguiente mensaje',
                style: TextStyle(
                  color: MonstruoTheme.onSurfaceDim,
                  fontSize: 13,
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Agent list (scrollable)
            Flexible(
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: ExternalAgentId.values.map((agent) => _AgentTile(
                    agent: agent,
                    isSelected: agent == current,
                    onTap: () {
                      HapticFeedback.selectionClick();
                      onSelect(agent);
                    },
                  )).toList(),
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}

class _AgentTile extends StatelessWidget {
  const _AgentTile({
    required this.agent,
    required this.isSelected,
    required this.onTap,
  });

  final ExternalAgentId agent;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        color: isSelected
            ? MonstruoTheme.primary.withValues(alpha: 0.08)
            : Colors.transparent,
        child: Row(
          children: [
            // Agent icon
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: isSelected
                    ? MonstruoTheme.primary.withValues(alpha: 0.15)
                    : MonstruoTheme.surfaceVariant,
                borderRadius: BorderRadius.circular(12),
              ),
              alignment: Alignment.center,
              child: Text(
                agent.icon,
                style: const TextStyle(fontSize: 20),
              ),
            ),
            const SizedBox(width: 12),
            // Name + description
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    agent.displayName,
                    style: TextStyle(
                      color: isSelected
                          ? MonstruoTheme.primary
                          : MonstruoTheme.onBackground,
                      fontSize: 15,
                      fontWeight:
                          isSelected ? FontWeight.w600 : FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    agent.description,
                    style: const TextStyle(
                      color: MonstruoTheme.onSurfaceDim,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            // Check mark
            if (isSelected)
              const Icon(
                Icons.check_circle_rounded,
                color: MonstruoTheme.primary,
                size: 20,
              ),
          ],
        ),
      ),
    );
  }
}
