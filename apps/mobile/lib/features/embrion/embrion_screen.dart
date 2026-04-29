import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../theme/monstruo_theme.dart';
import '../../services/kernel_service.dart';

/// Monitor screen for the Embrión — the autonomous agent.
///
/// Shows:
/// - Current status (running/sleeping/thinking)
/// - Today's thought count and cost
/// - Budget usage
/// - Recent thoughts/actions log
/// - Manual directive input
class EmbrionScreen extends ConsumerStatefulWidget {
  const EmbrionScreen({super.key});

  @override
  ConsumerState<EmbrionScreen> createState() => _EmbrionScreenState();
}

class _EmbrionScreenState extends ConsumerState<EmbrionScreen> {
  Map<String, dynamic>? _embrionData;
  bool _loading = true;
  String? _error;
  Timer? _refreshTimer;
  final _directiveController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
    // Auto-refresh every 30 seconds
    _refreshTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _loadData(),
    );
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    _directiveController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final data = await KernelService().getEmbrionStatus();
      if (mounted) {
        setState(() {
          _embrionData = data;
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: const Row(
          children: [
            Text('🥒', style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text(
              'Embrión',
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
    final data = _embrionData ?? {};
    final status = data['status'] as String? ?? 'unknown';
    final thoughts = data['thoughts_today'] as int? ?? 0;
    final cycles = data['cycles_today'] as int? ?? 0;
    final costToday = (data['cost_today'] as num?)?.toDouble() ?? 0.0;
    final budgetDaily = (data['budget_daily'] as num?)?.toDouble() ?? 2.0;
    final budgetUsage = (costToday / budgetDaily).clamp(0.0, 1.0);
    final recentThoughts = List<Map<String, dynamic>>.from(
      data['recent_thoughts'] ?? [],
    );

    final isActive = status == 'running' || status == 'active' || status == 'thinking';

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
                colors: isActive
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
                color: isActive
                    ? MonstruoTheme.primary.withValues(alpha: 0.3)
                    : MonstruoTheme.divider,
                width: 1,
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    // Pulsing dot
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: isActive ? MonstruoTheme.success : MonstruoTheme.onSurfaceDim,
                        shape: BoxShape.circle,
                        boxShadow: isActive
                            ? [
                                BoxShadow(
                                  color: MonstruoTheme.success.withValues(alpha: 0.4),
                                  blurRadius: 8,
                                  spreadRadius: 2,
                                ),
                              ]
                            : null,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      status.toUpperCase(),
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: isActive ? MonstruoTheme.success : MonstruoTheme.onSurfaceDim,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                // Metrics row
                Row(
                  children: [
                    _MetricTile(
                      label: 'Pensamientos',
                      value: '$thoughts',
                      icon: Icons.psychology,
                    ),
                    const SizedBox(width: 12),
                    _MetricTile(
                      label: 'Ciclos',
                      value: '$cycles',
                      icon: Icons.loop,
                    ),
                    const SizedBox(width: 12),
                    _MetricTile(
                      label: 'Costo hoy',
                      value: '\$${costToday.toStringAsFixed(2)}',
                      icon: Icons.attach_money,
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Budget bar
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
                    const Text(
                      'Presupuesto diario',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: MonstruoTheme.onSurface,
                      ),
                    ),
                    Text(
                      '\$${costToday.toStringAsFixed(2)} / \$${budgetDaily.toStringAsFixed(2)}',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: budgetUsage > 0.8 ? MonstruoTheme.warning : MonstruoTheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: budgetUsage,
                    backgroundColor: MonstruoTheme.surfaceVariant,
                    color: budgetUsage > 0.8 ? MonstruoTheme.warning : MonstruoTheme.primary,
                    minHeight: 6,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Directive input
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
                const Text(
                  'Enviar directiva al Embrión',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: MonstruoTheme.onBackground,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _directiveController,
                        style: const TextStyle(
                          fontSize: 14,
                          color: MonstruoTheme.onBackground,
                        ),
                        decoration: InputDecoration(
                          hintText: 'Ej: Investiga el estado del PR #23...',
                          hintStyle: TextStyle(
                            color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.5),
                            fontSize: 13,
                          ),
                          filled: true,
                          fillColor: MonstruoTheme.surfaceVariant,
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 10,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: () {
                        final text = _directiveController.text.trim();
                        if (text.isNotEmpty) {
                          // TODO: Send directive to kernel
                          _directiveController.clear();
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Directiva enviada al Embrión'),
                              backgroundColor: MonstruoTheme.surface,
                            ),
                          );
                        }
                      },
                      icon: const Icon(Icons.send, size: 20),
                      color: MonstruoTheme.primary,
                    ),
                  ],
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Recent thoughts
          const Text(
            'Pensamientos recientes',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 12),

          if (recentThoughts.isEmpty)
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: MonstruoTheme.surface,
                borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
              ),
              child: const Center(
                child: Text(
                  'Sin pensamientos recientes',
                  style: TextStyle(
                    fontSize: 14,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ),
            )
          else
            ...recentThoughts.map((thought) => _ThoughtCard(thought: thought)),
        ],
      ),
    );
  }
}

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
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: MonstruoTheme.surface.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(8),
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

class _ThoughtCard extends StatelessWidget {
  const _ThoughtCard({required this.thought});
  final Map<String, dynamic> thought;

  @override
  Widget build(BuildContext context) {
    final content = thought['content'] as String? ?? '';
    final type = thought['type'] as String? ?? 'reflexion';
    final timestamp = thought['timestamp'] as String? ?? '';
    final cost = (thought['cost'] as num?)?.toDouble();

    final isAction = type == 'action' || type == 'tool_use';

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        border: Border(
          left: BorderSide(
            color: isAction ? MonstruoTheme.primary : MonstruoTheme.onSurfaceDim,
            width: 3,
          ),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isAction
                      ? MonstruoTheme.primary.withValues(alpha: 0.15)
                      : MonstruoTheme.surfaceVariant,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  type.toUpperCase(),
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                    color: isAction ? MonstruoTheme.primary : MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ),
              const Spacer(),
              if (cost != null)
                Text(
                  '\$${cost.toStringAsFixed(3)}',
                  style: const TextStyle(
                    fontSize: 10,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              const SizedBox(width: 8),
              Text(
                timestamp,
                style: const TextStyle(
                  fontSize: 10,
                  color: MonstruoTheme.onSurfaceDim,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            content,
            style: const TextStyle(
              fontSize: 13,
              color: MonstruoTheme.onSurface,
              height: 1.4,
            ),
            maxLines: 5,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.error, required this.onRetry});
  final String error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.error_outline, size: 48, color: MonstruoTheme.error),
          const SizedBox(height: 16),
          Text(
            'Error al conectar con el Embrión',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            error,
            style: const TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh, size: 18),
            label: const Text('Reintentar'),
            style: ElevatedButton.styleFrom(
              backgroundColor: MonstruoTheme.primary,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}
