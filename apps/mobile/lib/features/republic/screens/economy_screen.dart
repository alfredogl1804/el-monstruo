/// Economy Screen — Cognitive P&L de la república.
///
/// Endpoint: GET /v1/factory/economy?window=24h|lifetime
/// KPIs económicos del Monstruo: artifacts/h, evidence ratio, costo USD, etc.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/mensajeros/factory_messenger.dart';
import '../../../core/theme/republic_theme.dart';
import '../../../models/cognitive_republic.dart';
import '../widgets/republic_widgets.dart';

class EconomyScreen extends ConsumerStatefulWidget {
  const EconomyScreen({super.key});

  @override
  ConsumerState<EconomyScreen> createState() => _EconomyScreenState();
}

class _EconomyScreenState extends ConsumerState<EconomyScreen> {
  String _window = '24h';

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(economyProvider(_window));

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: RepublicAppBar(
        title: 'Cognitive P&L',
        caption: 'Economía de la república cognitiva',
        showBackButton: true,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: RepublicSpacing.md),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: '24h', label: Text('24h')),
                ButtonSegment(value: 'lifetime', label: Text('All')),
              ],
              selected: {_window},
              showSelectedIcon: false,
              onSelectionChanged: (s) {
                HapticFeedback.selectionClick();
                setState(() => _window = s.first);
              },
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        color: RepublicColors.iosBlue,
        onRefresh: () async {
          HapticFeedback.lightImpact();
          ref.invalidate(economyProvider(_window));
          await ref.read(economyProvider(_window).future);
        },
        child: async.when(
          loading: () => _skeleton(),
          error: (e, _) => EmptyState(
            icon: Icons.cloud_off_outlined,
            title: 'No pude cargar la economía',
            subtitle: e.toString(),
            action: FilledButton.tonal(
              onPressed: () => ref.invalidate(economyProvider(_window)),
              child: const Text('Reintentar'),
            ),
          ),
          data: (eco) => _EconomyBody(data: eco),
        ),
      ),
    );
  }

  Widget _skeleton() => GridView.count(
        padding: const EdgeInsets.all(RepublicSpacing.lg),
        crossAxisCount: 2,
        crossAxisSpacing: RepublicSpacing.md,
        mainAxisSpacing: RepublicSpacing.md,
        children: List.generate(
          6,
          (_) => LoadingShimmer(
            height: 120,
            borderRadius: BorderRadius.circular(RepublicRadius.md),
          ),
        ),
      );
}

class _EconomyBody extends StatelessWidget {
  final CognitiveEconomy data;
  const _EconomyBody({required this.data});

  @override
  Widget build(BuildContext context) {
    final realKpis = data.realKpis();
    final missing = data.missingMetrics;

    return ListView(
      padding: const EdgeInsets.fromLTRB(
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        32,
      ),
      children: [
        if (realKpis.isEmpty)
          const EmptyState(
            icon: Icons.bar_chart_outlined,
            title: 'Sin métricas reales todavía',
            subtitle:
                'El kernel está construyendo el Cognitive P&L. Vuelve pronto.',
          )
        else
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: RepublicSpacing.md,
            mainAxisSpacing: RepublicSpacing.md,
            childAspectRatio: 1.4,
            children: realKpis.entries
                .map(
                  (e) => KpiTile(
                    label: _humanLabel(e.key),
                    value: _formatValue(e.value),
                    sublabel: _kpiHint(e.key),
                  ),
                )
                .toList(),
          ),
        if (missing.isNotEmpty) ...[
          const SizedBox(height: RepublicSpacing.xl),
          Container(
            padding: const EdgeInsets.all(RepublicSpacing.md),
            decoration: BoxDecoration(
              color: RepublicColors.iosOrangeSoft,
              borderRadius: BorderRadius.circular(RepublicRadius.md),
              border: Border.all(
                color: RepublicColors.iosOrange.withValues(alpha: 0.3),
                width: 0.5,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.info_outline,
                      size: 14,
                      color: RepublicColors.iosOrange,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Métricas pendientes',
                      style: RepublicTypography.labelSmall.copyWith(
                        color: RepublicColors.iosOrange,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  missing.join(', '),
                  style: RepublicTypography.bodySmall,
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: RepublicSpacing.lg),
        Text(
          'Generado: ${data.generatedAt}',
          style: RepublicTypography.labelSmall,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  String _humanLabel(String key) {
    return key.replaceAll('_', ' ').toUpperCase();
  }

  String _formatValue(dynamic v) {
    if (v == null) return '—';
    if (v is num) {
      if (v == v.truncate()) return v.toInt().toString();
      return v.toStringAsFixed(2);
    }
    return v.toString();
  }

  String? _kpiHint(String key) {
    if (key.contains('cost')) return 'USD';
    if (key.contains('ratio')) return 'proporción';
    if (key.contains('artifacts')) return 'artefactos';
    if (key.contains('evidence')) return 'recibos firmados';
    return null;
  }
}
