/// Timeline Screen — Sovereign Time Axis.
///
/// Endpoint: GET /v1/factory/timeline
/// Eventos civilizacionales firmados: DSCs, sprints, milestones, P0 incidents.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/mensajeros/factory_messenger.dart';
import '../../../core/theme/republic_theme.dart';
import '../../../models/cognitive_republic.dart';
import '../widgets/republic_widgets.dart';

class TimelineScreen extends ConsumerWidget {
  const TimelineScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(timelineProvider);

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: const RepublicAppBar(
        title: 'Sovereign Time Axis',
        caption: 'Eventos civilizacionales firmados',
        showBackButton: true,
      ),
      body: RefreshIndicator(
        color: RepublicColors.iosBlue,
        onRefresh: () async {
          HapticFeedback.lightImpact();
          ref.invalidate(timelineProvider);
          await ref.read(timelineProvider.future);
        },
        child: async.when(
          loading: () => _skeletonList(),
          error: (e, _) => EmptyState(
            icon: Icons.cloud_off_outlined,
            title: 'No pude cargar la línea soberana',
            subtitle: e.toString(),
            action: FilledButton.tonal(
              onPressed: () => ref.invalidate(timelineProvider),
              child: const Text('Reintentar'),
            ),
          ),
          data: (events) {
            if (events.isEmpty) {
              return const EmptyState(
                icon: Icons.timeline_outlined,
                title: 'Sin eventos en la línea soberana',
                subtitle: 'El kernel aún no tiene firmas registradas.',
              );
            }
            return ListView.builder(
              padding: const EdgeInsets.fromLTRB(
                RepublicSpacing.lg,
                RepublicSpacing.lg,
                RepublicSpacing.lg,
                32,
              ),
              itemCount: events.length,
              itemBuilder: (_, i) =>
                  _TimelineEntry(event: events[i], isFirst: i == 0),
            );
          },
        ),
      ),
    );
  }

  Widget _skeletonList() => ListView(
        padding: const EdgeInsets.all(RepublicSpacing.lg),
        children: List.generate(
          5,
          (_) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: LoadingShimmer(
              height: 96,
              borderRadius: BorderRadius.circular(RepublicRadius.md),
            ),
          ),
        ),
      );
}

class _TimelineEntry extends StatelessWidget {
  final SovereignTimelineEvent event;
  final bool isFirst;
  const _TimelineEntry({required this.event, required this.isFirst});

  Color _kindColor(String kind) {
    switch (kind) {
      case 'dsc_signed':
        return RepublicColors.iosPurple;
      case 'sprint_completed':
        return RepublicColors.iosGreen;
      case 'incident_p0':
        return RepublicColors.teslaRed;
      case 'doctrine_revision':
        return RepublicColors.iosIndigo;
      case 'embrion_milestone':
        return RepublicColors.iosBlue;
      default:
        return RepublicColors.textTertiary;
    }
  }

  IconData _kindIcon(String kind) {
    switch (kind) {
      case 'dsc_signed':
        return Icons.verified_outlined;
      case 'sprint_completed':
        return Icons.check_circle_outlined;
      case 'incident_p0':
        return Icons.warning_amber_outlined;
      case 'doctrine_revision':
        return Icons.auto_stories_outlined;
      case 'embrion_milestone':
        return Icons.psychology_outlined;
      default:
        return Icons.fiber_manual_record_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _kindColor(event.kind);
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Rail
          SizedBox(
            width: 36,
            child: Column(
              children: [
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    shape: BoxShape.circle,
                    border: Border.all(color: color, width: 1.2),
                  ),
                  child: Icon(_kindIcon(event.kind), color: color, size: 14),
                ),
                Expanded(
                  child: Container(
                    width: 1,
                    color: RepublicColors.hairline,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: RepublicSpacing.sm),
          // Card
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: Container(
                padding: const EdgeInsets.all(RepublicSpacing.md),
                decoration: BoxDecoration(
                  color: RepublicColors.surface,
                  borderRadius: BorderRadius.circular(RepublicRadius.md),
                  border: Border.all(
                    color: RepublicColors.hairline,
                    width: 0.5,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            event.kind.toUpperCase().replaceAll('_', ' '),
                            style:
                                RepublicTypography.labelSmall.copyWith(color: color),
                          ),
                        ),
                        Text(
                          _shortDate(event.at),
                          style: RepublicTypography.labelSmall,
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      event.title,
                      style: RepublicTypography.bodyLarge,
                    ),
                    if (event.summary != null && event.summary!.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        event.summary!,
                        style: RepublicTypography.bodySmall,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    if (event.signedBy != null) ...[
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          const Icon(
                            Icons.draw_outlined,
                            size: 12,
                            color: RepublicColors.textTertiary,
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'Firmado por ${event.signedBy}',
                            style: RepublicTypography.labelSmall,
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  String _shortDate(String iso) {
    try {
      final d = DateTime.parse(iso).toLocal();
      return '${d.day}/${d.month}/${d.year}';
    } catch (_) {
      return iso.length > 10 ? iso.substring(0, 10) : iso;
    }
  }
}
