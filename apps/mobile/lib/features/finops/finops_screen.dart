import 'package:flutter/material.dart';

import '../../theme/monstruo_theme.dart';
import '../../services/kernel_service.dart';

/// FinOps dashboard — cost tracking and model usage.
///
/// Shows:
/// - Daily/weekly/monthly cost
/// - Cost by model (GPT-5.5, Claude, Gemini, Grok)
/// - Cost by component (Embrion, chat, tools)
/// - Budget alerts
class FinOpsScreen extends StatefulWidget {
  const FinOpsScreen({super.key});

  @override
  State<FinOpsScreen> createState() => _FinOpsScreenState();
}

class _FinOpsScreenState extends State<FinOpsScreen> {
  bool _loading = true;
  Map<String, dynamic>? _finopsData;
  String _period = 'today';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    try {
      final data = await KernelService().getFinOps(period: _period);
      if (mounted) {
        setState(() {
          _finopsData = data;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loading = false);
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
            Icon(Icons.analytics, size: 20, color: MonstruoTheme.warning),
            SizedBox(width: 8),
            Text(
              'FinOps',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
          ],
        ),
        actions: [
          // Period selector
          PopupMenuButton<String>(
            icon: const Icon(Icons.calendar_today, size: 18, color: MonstruoTheme.onSurfaceDim),
            onSelected: (period) {
              setState(() => _period = period);
              _loadData();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'today', child: Text('Hoy')),
              const PopupMenuItem(value: 'week', child: Text('Esta semana')),
              const PopupMenuItem(value: 'month', child: Text('Este mes')),
              const PopupMenuItem(value: 'all', child: Text('Todo')),
            ],
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: MonstruoTheme.primary))
          : _buildContent(),
    );
  }

  Widget _buildContent() {
    final data = _finopsData ?? {};
    final totalCost = (data['total_cost'] as num?)?.toDouble() ?? 0.0;
    final budget = (data['budget'] as num?)?.toDouble() ?? 10.0;
    final models = Map<String, dynamic>.from(data['by_model'] ?? {});
    final components = Map<String, dynamic>.from(data['by_component'] ?? {});

    return RefreshIndicator(
      onRefresh: _loadData,
      color: MonstruoTheme.primary,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Total cost card
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  MonstruoTheme.surface,
                  MonstruoTheme.surfaceVariant,
                ],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: MonstruoTheme.divider, width: 0.5),
            ),
            child: Column(
              children: [
                Text(
                  _periodLabel(_period),
                  style: const TextStyle(
                    fontSize: 12,
                    color: MonstruoTheme.onSurfaceDim,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '\$${totalCost.toStringAsFixed(2)}',
                  style: const TextStyle(
                    fontSize: 40,
                    fontWeight: FontWeight.w800,
                    color: MonstruoTheme.onBackground,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'de \$${budget.toStringAsFixed(2)} presupuesto',
                  style: const TextStyle(
                    fontSize: 13,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
                const SizedBox(height: 16),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: (totalCost / budget).clamp(0.0, 1.0),
                    backgroundColor: MonstruoTheme.surfaceVariant,
                    color: totalCost / budget > 0.8
                        ? MonstruoTheme.error
                        : totalCost / budget > 0.5
                            ? MonstruoTheme.warning
                            : MonstruoTheme.success,
                    minHeight: 8,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // By model
          const Text(
            'Por modelo',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 12),
          ...models.entries.map((entry) {
            final modelName = entry.key;
            final cost = (entry.value as num?)?.toDouble() ?? 0.0;
            final percentage = totalCost > 0 ? (cost / totalCost * 100) : 0.0;
            final color = _modelColor(modelName);

            return Container(
              margin: const EdgeInsets.only(bottom: 8),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: MonstruoTheme.surface,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: MonstruoTheme.divider, width: 0.5),
              ),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 36,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          modelName,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: MonstruoTheme.onSurface,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          '${percentage.toStringAsFixed(1)}%',
                          style: const TextStyle(
                            fontSize: 11,
                            color: MonstruoTheme.onSurfaceDim,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '\$${cost.toStringAsFixed(3)}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: color,
                    ),
                  ),
                ],
              ),
            );
          }),

          const SizedBox(height: 24),

          // By component
          const Text(
            'Por componente',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 12),
          ...components.entries.map((entry) {
            final name = entry.key;
            final cost = (entry.value as num?)?.toDouble() ?? 0.0;

            return Container(
              margin: const EdgeInsets.only(bottom: 6),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              decoration: BoxDecoration(
                color: MonstruoTheme.surface,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      fontSize: 13,
                      color: MonstruoTheme.onSurface,
                    ),
                  ),
                  Text(
                    '\$${cost.toStringAsFixed(3)}',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: MonstruoTheme.onBackground,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  String _periodLabel(String period) {
    return switch (period) {
      'today' => 'HOY',
      'week' => 'ESTA SEMANA',
      'month' => 'ESTE MES',
      'all' => 'TOTAL ACUMULADO',
      _ => period.toUpperCase(),
    };
  }

  Color _modelColor(String model) {
    final m = model.toLowerCase();
    if (m.contains('gpt') || m.contains('openai')) return const Color(0xFF10A37F);
    if (m.contains('claude') || m.contains('anthropic')) return const Color(0xFFD97706);
    if (m.contains('gemini') || m.contains('google')) return const Color(0xFF4285F4);
    if (m.contains('grok') || m.contains('xai')) return const Color(0xFFEF4444);
    if (m.contains('sonar') || m.contains('perplexity')) return const Color(0xFF7C3AED);
    return MonstruoTheme.onSurfaceDim;
  }
}
