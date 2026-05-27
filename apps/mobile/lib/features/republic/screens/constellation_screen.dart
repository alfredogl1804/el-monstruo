/// Constellation Screen — Vista federada de la Cognitive Republic.
///
/// Endpoint: GET /v1/factory/constellation
/// Renderiza los nodos federados (12+) agrupados por tier: core, inner, mid, outer.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/mensajeros/factory_messenger.dart';
import '../../../core/theme/republic_theme.dart';
import '../../../models/cognitive_republic.dart';
import '../widgets/republic_widgets.dart';

class ConstellationScreen extends ConsumerWidget {
  const ConstellationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(constellationProvider);

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: const RepublicAppBar(
        title: 'Forge Constellation',
        caption: 'Nodos federados de la república cognitiva',
        showBackButton: true,
      ),
      body: RefreshIndicator(
        color: RepublicColors.iosBlue,
        onRefresh: () async {
          HapticFeedback.lightImpact();
          ref.invalidate(constellationProvider);
          await ref.read(constellationProvider.future);
        },
        child: async.when(
          loading: () => const _ConstellationSkeleton(),
          error: (e, _) => _ConstellationError(
            error: e.toString(),
            onRetry: () => ref.invalidate(constellationProvider),
          ),
          data: (data) => _ConstellationBody(data: data),
        ),
      ),
    );
  }
}

class _ConstellationBody extends StatelessWidget {
  final ConstellationResponse data;
  const _ConstellationBody({required this.data});

  @override
  Widget build(BuildContext context) {
    // Agrupar nodos por tier
    final byTier = <String, List<ForgeNode>>{};
    for (final n in data.nodes) {
      byTier.putIfAbsent(n.tier, () => []).add(n);
    }
    const tierOrder = ['core', 'inner', 'mid', 'outer'];
    const tierLabels = {
      'core': 'Núcleo soberano',
      'inner': 'Anillo interior',
      'mid': 'Anillo medio',
      'outer': 'Anillo exterior',
    };

    return ListView(
      padding: const EdgeInsets.only(bottom: 32),
      children: [
        // Hero KPIs
        Padding(
          padding: const EdgeInsets.all(RepublicSpacing.lg),
          child: Row(
            children: [
              Expanded(
                child: KpiTile(
                  label: 'Nodos',
                  value: '${data.totals.nodesTotal}',
                  sublabel: '${data.edges.length} conexiones',
                  icon: Icons.hub_outlined,
                  isHero: true,
                ),
              ),
              const SizedBox(width: RepublicSpacing.md),
              Expanded(
                child: KpiTile(
                  label: 'Binario 100',
                  value: data.binario100 ? '✓' : '×',
                  sublabel: data.binario100
                      ? 'Genoma íntegro'
                      : 'Drift detectado',
                  accentColor: data.binario100
                      ? RepublicColors.iosGreen
                      : RepublicColors.teslaRed,
                  isHero: true,
                ),
              ),
            ],
          ),
        ),
        // Por tier
        for (final tier in tierOrder)
          if (byTier[tier]?.isNotEmpty ?? false) ...[
            SectionHeader(
              label: tier,
              title: tierLabels[tier] ?? tier,
              caption: '${byTier[tier]!.length} nodos',
            ),
            ...byTier[tier]!.map(
              (n) => Padding(
                padding: const EdgeInsets.fromLTRB(
                  RepublicSpacing.lg,
                  0,
                  RepublicSpacing.lg,
                  RepublicSpacing.sm,
                ),
                child: NodeCard(
                  forgeId: n.forgeId,
                  name: n.name,
                  tier: n.tier,
                  status: n.status,
                  subtitle: n.substrate.endpoint ?? n.substrate.runtime,
                  tags: [
                    if (n.sovereignty.envelopeSupported) 'envelope',
                    if (n.sovereignty.courtBound) 'court-bound',
                    if (n.memory.writesToMemory) 'memory',
                    ...n.production.activeLines.take(2),
                  ],
                ),
              ),
            ),
          ],
      ],
    );
  }
}

class _ConstellationSkeleton extends StatelessWidget {
  const _ConstellationSkeleton();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(RepublicSpacing.lg),
      children: List.generate(
        6,
        (i) => Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: LoadingShimmer(
            height: 88,
            borderRadius: BorderRadius.circular(RepublicRadius.md),
          ),
        ),
      ),
    );
  }
}

class _ConstellationError extends StatelessWidget {
  final String error;
  final VoidCallback onRetry;
  const _ConstellationError({required this.error, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return EmptyState(
      icon: Icons.cloud_off_outlined,
      title: 'No pude cargar la constelación',
      subtitle: error,
      action: FilledButton.tonal(
        onPressed: onRetry,
        child: const Text('Reintentar'),
      ),
    );
  }
}
