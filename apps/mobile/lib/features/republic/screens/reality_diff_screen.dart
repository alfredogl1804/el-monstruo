/// Reality Diff Screen — Declarado vs vivo.
///
/// Endpoint: GET /v1/factory/diff
/// Drift entre el genoma declarado y la realidad observada en producción.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/mensajeros/factory_messenger.dart';
import '../../../core/theme/republic_theme.dart';
import '../../../models/cognitive_republic.dart';
import '../widgets/republic_widgets.dart';

class RealityDiffScreen extends ConsumerWidget {
  const RealityDiffScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(realityDiffProvider);

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: const RepublicAppBar(
        title: 'Reality Diff',
        caption: 'Declarado vs vivo',
        showBackButton: true,
      ),
      body: RefreshIndicator(
        color: RepublicColors.iosBlue,
        onRefresh: () async {
          HapticFeedback.lightImpact();
          ref.invalidate(realityDiffProvider);
          await ref.read(realityDiffProvider.future);
        },
        child: async.when(
          loading: () => _skeleton(),
          error: (e, _) => EmptyState(
            icon: Icons.cloud_off_outlined,
            title: 'No pude cargar el diff',
            subtitle: e.toString(),
            action: FilledButton.tonal(
              onPressed: () => ref.invalidate(realityDiffProvider),
              child: const Text('Reintentar'),
            ),
          ),
          data: (diff) => _DiffBody(diff: diff),
        ),
      ),
    );
  }

  Widget _skeleton() => ListView(
        padding: const EdgeInsets.all(RepublicSpacing.lg),
        children: List.generate(
          5,
          (_) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: LoadingShimmer(
              height: 88,
              borderRadius: BorderRadius.circular(RepublicRadius.md),
            ),
          ),
        ),
      );
}

class _DiffBody extends StatelessWidget {
  final RealityDiff diff;
  const _DiffBody({required this.diff});

  Color _severityColor(String s) {
    switch (s) {
      case 'error':
        return RepublicColors.teslaRed;
      case 'warn':
        return RepublicColors.iosOrange;
      default:
        return RepublicColors.iosBlue;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isHealthy = diff.binario100 && diff.driftCount == 0;
    return ListView(
      padding: const EdgeInsets.fromLTRB(
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        RepublicSpacing.lg,
        32,
      ),
      children: [
        // Hero: estado global
        Container(
          padding: const EdgeInsets.all(RepublicSpacing.lg),
          decoration: BoxDecoration(
            color: isHealthy
                ? RepublicColors.iosGreenSoft
                : RepublicColors.teslaRedSoft,
            borderRadius: BorderRadius.circular(RepublicRadius.lg),
            border: Border.all(
              color: (isHealthy
                      ? RepublicColors.iosGreen
                      : RepublicColors.teslaRed)
                  .withValues(alpha: 0.3),
              width: 0.5,
            ),
          ),
          child: Row(
            children: [
              Icon(
                isHealthy ? Icons.check_circle : Icons.warning_amber_rounded,
                color: isHealthy
                    ? RepublicColors.iosGreen
                    : RepublicColors.teslaRed,
                size: 32,
              ),
              const SizedBox(width: RepublicSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isHealthy
                          ? 'Realidad alineada con doctrina'
                          : '${diff.driftCount} drift${diff.driftCount == 1 ? '' : 's'} detectado${diff.driftCount == 1 ? '' : 's'}',
                      style: RepublicTypography.headlineSmall,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'binario_100 = ${diff.binario100}',
                      style: RepublicTypography.labelSmall,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: RepublicSpacing.lg),
        // Coverage match
        if (diff.coverageMatch.isNotEmpty) ...[
          const SectionHeader(
            label: 'cobertura',
            title: 'Coverage match por dominio',
          ),
          ...diff.coverageMatch.entries.map(
            (e) => Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(RepublicSpacing.md),
              decoration: BoxDecoration(
                color: RepublicColors.surface,
                borderRadius: BorderRadius.circular(RepublicRadius.md),
                border: Border.all(
                  color: RepublicColors.hairline,
                  width: 0.5,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    e.value
                        ? Icons.check_circle_outlined
                        : Icons.cancel_outlined,
                    size: 18,
                    color: e.value
                        ? RepublicColors.iosGreen
                        : RepublicColors.teslaRed,
                  ),
                  const SizedBox(width: RepublicSpacing.md),
                  Expanded(
                    child: Text(
                      e.key,
                      style: RepublicTypography.bodyMedium,
                    ),
                  ),
                  Text(
                    e.value ? 'OK' : 'DRIFT',
                    style: RepublicTypography.labelSmall.copyWith(
                      color: e.value
                          ? RepublicColors.iosGreen
                          : RepublicColors.teslaRed,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
        // Discrepancies
        if (diff.discrepancies.isNotEmpty) ...[
          const SectionHeader(
            label: 'discrepancias',
            title: 'Drifts puntuales',
          ),
          ...diff.discrepancies.map(
            (d) => Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(RepublicSpacing.md),
              decoration: BoxDecoration(
                color: RepublicColors.surface,
                borderRadius: BorderRadius.circular(RepublicRadius.md),
                border: Border.all(
                  color: _severityColor(d.severity).withValues(alpha: 0.3),
                  width: 0.5,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color:
                              _severityColor(d.severity).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          d.severity.toUpperCase(),
                          style: RepublicTypography.labelSmall.copyWith(
                            color: _severityColor(d.severity),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          d.domain,
                          style: RepublicTypography.bodyMedium,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Declarado: ${d.declared}',
                    style: RepublicTypography.bodySmall,
                  ),
                  Text(
                    'Vivo: ${d.live}',
                    style: RepublicTypography.bodySmall.copyWith(
                      color: _severityColor(d.severity),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
        // Kernel health
        if (diff.kernelHealth != null) ...[
          const SectionHeader(label: 'kernel', title: 'Salud del kernel'),
          Container(
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
                if (diff.kernelHealth!.status != null)
                  Text(
                    'Status: ${diff.kernelHealth!.status}',
                    style: RepublicTypography.bodyMedium,
                  ),
                if (diff.kernelHealth!.uptimeSeconds != null)
                  Text(
                    'Uptime: ${diff.kernelHealth!.uptimeSeconds}s',
                    style: RepublicTypography.bodySmall,
                  ),
                if (diff.kernelHealth!.version != null)
                  Text(
                    'Versión: ${diff.kernelHealth!.version}',
                    style: RepublicTypography.bodySmall,
                  ),
              ],
            ),
          ),
        ],
        const SizedBox(height: RepublicSpacing.lg),
        Text(
          'Generado: ${diff.generatedAt}',
          style: RepublicTypography.labelSmall,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
