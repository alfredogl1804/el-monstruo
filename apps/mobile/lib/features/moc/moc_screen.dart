import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../theme/monstruo_theme.dart';
import '../../services/kernel_service.dart';

/// MOC Panel — Motor de Orquestación Central
///
/// Shows:
/// - MOC status (running/stopped)
/// - Priorization stats (jobs prioritized, reorders)
/// - Latest AI-generated insights
/// - Manual synthesis trigger
class MocScreen extends ConsumerStatefulWidget {
  const MocScreen({super.key});

  @override
  ConsumerState<MocScreen> createState() => _MocScreenState();
}

class _MocScreenState extends ConsumerState<MocScreen> {
  Map<String, dynamic>? _mocData;
  bool _loading = true;
  bool _synthesizing = false;
  String? _error;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _loadData();
    // Auto-refresh every 60 seconds
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 60),
      (_) => _loadData(),
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final data = await KernelService().getMocStatus();
      if (mounted) {
        setState(() {
          _mocData = data;
          _loading = false;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString();
        });
      }
    }
  }

  Future<void> _triggerSynthesis() async {
    setState(() => _synthesizing = true);
    try {
      final result = await KernelService().triggerMocSynthesis();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result['error'] != null
                  ? 'Error: ${result['error']}'
                  : 'Síntesis iniciada. Los insights estarán listos en unos segundos.',
            ),
            backgroundColor: result['error'] != null
                ? MonstruoTheme.error
                : MonstruoTheme.success,
            duration: const Duration(seconds: 3),
          ),
        );
        // Reload after synthesis
        await Future.delayed(const Duration(seconds: 2));
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al sintetizar: $e'),
            backgroundColor: MonstruoTheme.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _synthesizing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: const Row(
          children: [
            Text('🧠', style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text(
              'MOC',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, size: 20),
            color: MonstruoTheme.onSurfaceDim,
            onPressed: _loadData,
          ),
        ],
      ),
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(color: MonstruoTheme.primary),
            )
          : _error != null
              ? _ErrorView(error: _error!, onRetry: _loadData)
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    final data = _mocData ?? {};
    final status = data['status'] as String? ?? 'unknown';
    final stats = data['stats'] as Map<String, dynamic>? ?? {};
    final insights = List<Map<String, dynamic>>.from(
      data['latest_insights'] ?? [],
    );

    final isRunning = status == 'active' || stats['running'] == true;
    final jobsPrioritized = stats['jobs_prioritized'] as int? ?? 0;
    final mocReorders = stats['moc_reorders'] as int? ?? 0;
    final insightsGenerated = stats['insights_generated'] as int? ?? 0;
    final lastSynthesis = stats['last_synthesis_at'] as String?;
    final synthIntervalH = stats['synthesis_interval_h'] as int? ?? 6;

    return RefreshIndicator(
      onRefresh: _loadData,
      color: MonstruoTheme.primary,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Status card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: isRunning
                    ? [
                        MonstruoTheme.primary.withValues(alpha: 0.15),
                        MonstruoTheme.secondary.withValues(alpha: 0.1),
                      ]
                    : [
                        MonstruoTheme.surfaceVariant,
                        MonstruoTheme.surface,
                      ],
              ),
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
              border: Border.all(
                color: isRunning
                    ? MonstruoTheme.primary.withValues(alpha: 0.3)
                    : MonstruoTheme.divider,
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: isRunning
                            ? MonstruoTheme.success
                            : MonstruoTheme.onSurfaceDim,
                        shape: BoxShape.circle,
                        boxShadow: isRunning
                            ? [
                                BoxShadow(
                                  color: MonstruoTheme.success
                                      .withValues(alpha: 0.4),
                                  blurRadius: 8,
                                  spreadRadius: 2,
                                ),
                              ]
                            : null,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      isRunning ? 'ACTIVO' : 'INACTIVO',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: isRunning
                            ? MonstruoTheme.success
                            : MonstruoTheme.onSurfaceDim,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      'Síntesis cada ${synthIntervalH}h',
                      style: const TextStyle(
                        fontSize: 12,
                        color: MonstruoTheme.onSurfaceDim,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    _MetricTile(
                      label: 'Jobs priorizados',
                      value: '$jobsPrioritized',
                      icon: Icons.sort,
                    ),
                    const SizedBox(width: 12),
                    _MetricTile(
                      label: 'Reordenamientos',
                      value: '$mocReorders',
                      icon: Icons.swap_vert,
                    ),
                    const SizedBox(width: 12),
                    _MetricTile(
                      label: 'Insights',
                      value: '$insightsGenerated',
                      icon: Icons.lightbulb_outline,
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Synthesis trigger
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: MonstruoTheme.surface,
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
              border: Border.all(color: MonstruoTheme.divider, width: 0.5),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Síntesis de insights',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: MonstruoTheme.onBackground,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          lastSynthesis != null
                              ? 'Última: ${_formatDate(lastSynthesis)}'
                              : 'Sin síntesis previa',
                          style: const TextStyle(
                            fontSize: 11,
                            color: MonstruoTheme.onSurfaceDim,
                          ),
                        ),
                      ],
                    ),
                    ElevatedButton.icon(
                      onPressed: _synthesizing ? null : _triggerSynthesis,
                      icon: _synthesizing
                          ? const SizedBox(
                              width: 14,
                              height: 14,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.auto_awesome, size: 16),
                      label: Text(_synthesizing ? 'Sintetizando...' : 'Sintetizar'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: MonstruoTheme.primary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        textStyle: const TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Insights list
          if (insights.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: MonstruoTheme.surface,
                borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
                border: Border.all(color: MonstruoTheme.divider, width: 0.5),
              ),
              child: const Column(
                children: [
                  Icon(
                    Icons.lightbulb_outline,
                    size: 32,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Sin insights todavía',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: MonstruoTheme.onSurface,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'El MOC genera insights automáticamente cada 6h,\no puedes disparar una síntesis manual.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 12,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                ],
              ),
            )
          else ...[
            const Text(
              'Últimos insights',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: 8),
            ...insights.map((insight) => _InsightCard(insight: insight)),
          ],
        ],
      ),
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso).toLocal();
      return '${dt.day}/${dt.month} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return iso;
    }
  }
}

// ── Widgets ───────────────────────────────────────────────────────────

class _MetricTile extends StatelessWidget {
  const _MetricTile({
    required this.label,
    required this.value,
    required this.icon,
  });

  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        ),
        child: Column(
          children: [
            Icon(icon, size: 18, color: MonstruoTheme.primary),
            const SizedBox(height: 6),
            Text(
              value,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 10,
                color: MonstruoTheme.onSurfaceDim,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InsightCard extends StatelessWidget {
  const _InsightCard({required this.insight});

  final Map<String, dynamic> insight;

  @override
  Widget build(BuildContext context) {
    final summary = insight['summary'] as String? ?? '';
    final patterns = List<String>.from(insight['patterns'] ?? []);
    final alerts = List<String>.from(insight['alerts'] ?? []);
    final recommendations = List<String>.from(insight['recommendations'] ?? []);
    final createdAt = insight['created_at'] as String? ?? '';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.lightbulb,
                size: 14,
                color: MonstruoTheme.primary,
              ),
              const SizedBox(width: 6),
              const Text(
                'Insight',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.primary,
                ),
              ),
              const Spacer(),
              if (createdAt.isNotEmpty)
                Text(
                  _formatDate(createdAt),
                  style: const TextStyle(
                    fontSize: 10,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
            ],
          ),
          if (summary.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              summary,
              style: const TextStyle(
                fontSize: 13,
                color: MonstruoTheme.onBackground,
                height: 1.4,
              ),
            ),
          ],
          if (alerts.isNotEmpty) ...[
            const SizedBox(height: 10),
            ...alerts.map(
              (a) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.warning_amber,
                      size: 13,
                      color: MonstruoTheme.warning,
                    ),
                    const SizedBox(width: 4),
                    Expanded(
                      child: Text(
                        a,
                        style: const TextStyle(
                          fontSize: 12,
                          color: MonstruoTheme.warning,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          if (recommendations.isNotEmpty) ...[
            const SizedBox(height: 8),
            ...recommendations.take(2).map(
              (r) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.arrow_right,
                      size: 14,
                      color: MonstruoTheme.success,
                    ),
                    const SizedBox(width: 2),
                    Expanded(
                      child: Text(
                        r,
                        style: const TextStyle(
                          fontSize: 12,
                          color: MonstruoTheme.onSurface,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          if (patterns.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: patterns
                  .take(3)
                  .map(
                    (p) => Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 3,
                      ),
                      decoration: BoxDecoration(
                        color: MonstruoTheme.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: MonstruoTheme.primary.withValues(alpha: 0.2),
                        ),
                      ),
                      child: Text(
                        p,
                        style: const TextStyle(
                          fontSize: 10,
                          color: MonstruoTheme.primary,
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso).toLocal();
      return '${dt.day}/${dt.month} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (_) {
      return iso;
    }
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});

  final String error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 48,
              color: MonstruoTheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: MonstruoTheme.onSurface,
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: onRetry,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }
}
